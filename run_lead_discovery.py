#!/usr/bin/env python3
"""
Chroma Lead Discovery Engine

Automated pipeline that:
1. Runs FindAll queries to discover companies hiring for vector DB roles
2. Filters out competitors and large enterprises  
3. Saves qualified leads to Chroma
4. Sends Slack notifications
5. Syncs to Attio CRM

Usage:
    # Run once
    python3 run_lead_discovery.py
    
    # Run with cron (daily at 9am):
    # Add to crontab: 0 9 * * * cd /path/to/Chroma GTM && python3 run_lead_discovery.py

    # Run with custom match limit
    python3 run_lead_discovery.py --limit 20
"""

import os
import sys
import time
import argparse
import requests
import chromadb
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================
PARALLEL_API_KEY = os.getenv("PARALLEL_API_KEY")
PARALLEL_BASE_URL = "https://api.parallel.ai/v1beta/findall"
PARALLEL_BETA_HEADER = "findall-2025-09-15"

CHROMA_API_KEY = 'ck-2i6neFLSKhd5pEqLP3jZKUkG6tX3yo4RVUZEeRxs4fHm'
CHROMA_TENANT = 'aa8f571e-03dc-4cd8-b888-723bd00b83f0'
CHROMA_DATABASE = 'customer'
CHROMA_COLLECTION = 'hiring_leads'

# Import filters and notifiers
from slack_lead_notifier import (
    SlackLeadNotifier, 
    is_hot_lead, 
    should_ignore_company,
    should_ignore_large_enterprise
)
from attio_sync import AttioSync


def log(message: str):
    """Print timestamped log message."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()


class LeadDiscoveryEngine:
    """Automated lead discovery and sync pipeline."""
    
    def __init__(self, match_limit: int = 10):
        self.match_limit = match_limit
        self.parallel_headers = {
            "x-api-key": PARALLEL_API_KEY,
            "parallel-beta": PARALLEL_BETA_HEADER,
            "Content-Type": "application/json"
        }
        
        # Initialize services
        log("🔗 Connecting to services...")
        
        self.chroma_client = chromadb.CloudClient(
            api_key=CHROMA_API_KEY,
            tenant=CHROMA_TENANT,
            database=CHROMA_DATABASE
        )
        self.collection = self.chroma_client.get_or_create_collection(CHROMA_COLLECTION)
        log(f"   ✅ Chroma: {self.collection.count()} existing leads")
        
        self.slack = SlackLeadNotifier()
        log(f"   ✅ Slack: {'enabled' if self.slack.enabled else 'disabled'}")
        
        self.attio = AttioSync()
        log(f"   ✅ Attio: {'enabled' if self.attio.enabled else 'disabled'}")
        
        # Load existing companies for dedup
        self._load_existing()
    
    def _load_existing(self):
        """Load existing company names for deduplication."""
        self.existing_companies = set()
        try:
            results = self.collection.get()
            for meta in results.get('metadatas', []):
                name = meta.get('company_name', '').lower().strip()
                if name:
                    self.existing_companies.add(name)
            log(f"   📋 Loaded {len(self.existing_companies)} companies for dedup")
        except Exception as e:
            log(f"   ⚠️ Could not load existing: {e}")
    
    def run_findall_query(self, objective: str, match_conditions: List[Dict]) -> List[Dict]:
        """Run a FindAll query and return matched candidates."""
        log(f"🔍 Running FindAll query...")
        log(f"   Objective: {objective[:80]}...")
        
        payload = {
            "objective": objective,
            "entity_type": "companies",
            "match_conditions": match_conditions,
            "enrichments": [
                {"name": "industry", "description": "Primary industry"},
                {"name": "vector_db_mentioned", "description": "Vector DB tech mentioned"},
                {"name": "job_titles", "description": "Job titles from postings"},
                {"name": "headquarters", "description": "HQ location"},
            ],
            "generator": "base",
            "match_limit": self.match_limit
        }
        
        # Create run
        response = requests.post(
            f"{PARALLEL_BASE_URL}/runs",
            headers=self.parallel_headers,
            json=payload
        )
        
        if response.status_code != 200:
            log(f"   ❌ API Error: {response.status_code} - {response.text[:200]}")
            return []
        
        findall_id = response.json()["findall_id"]
        log(f"   ✅ Run started: {findall_id}")
        
        # Poll until complete
        start_time = time.time()
        while True:
            status = requests.get(
                f"{PARALLEL_BASE_URL}/runs/{findall_id}",
                headers=self.parallel_headers
            ).json()
            
            metrics = status.get("status", {}).get("metrics", {})
            generated = metrics.get("generated_candidates_count", 0)
            matched = metrics.get("matched_candidates_count", 0)
            
            elapsed = int(time.time() - start_time)
            log(f"   [{elapsed}s] Generated: {generated} | Matched: {matched}")
            
            if not status.get("status", {}).get("is_active", True):
                break
            if elapsed > 300:  # 5 min timeout
                log("   ⚠️ Timeout")
                break
            
            time.sleep(10)
        
        # Get results
        results = requests.get(
            f"{PARALLEL_BASE_URL}/runs/{findall_id}/result",
            headers=self.parallel_headers
        ).json()
        
        candidates = [c for c in results.get("candidates", []) if c.get("match_status") == "matched"]
        log(f"   ✅ Found {len(candidates)} matched companies")
        
        return candidates
    
    def process_candidates(self, candidates: List[Dict], query_name: str) -> List[Dict]:
        """Filter, save, and notify for new candidates."""
        new_leads = []
        
        for candidate in candidates:
            company_name = candidate.get("name", "")
            company_key = company_name.lower().strip()
            
            # Filter: Vector DB competitors
            if should_ignore_company(company_name):
                log(f"   🚫 Competitor: {company_name}")
                continue
            
            # Filter: Large enterprises
            if should_ignore_large_enterprise(company_name):
                log(f"   🏢 Enterprise: {company_name}")
                continue
            
            # Filter: Duplicates
            if company_key in self.existing_companies:
                log(f"   ⏭️  Duplicate: {company_name}")
                continue
            
            # Mark as seen
            self.existing_companies.add(company_key)
            
            # Extract data
            output = candidate.get("output", {})
            def get_val(f):
                v = output.get(f, {})
                return v.get("value", "") if isinstance(v, dict) else str(v) if v else ""
            
            # Extract job URLs from citations
            job_urls = []
            job_titles_from_citations = []
            for basis in candidate.get("basis", []):
                for cit in basis.get("citations", []):
                    url = cit.get("url", "")
                    title = cit.get("title", "")
                    if url and any(x in url.lower() for x in ["job", "career", "indeed", "linkedin", "lever", "greenhouse"]):
                        job_urls.append(url)
                        if title and any(x in title.lower() for x in ["engineer", "scientist", "developer"]):
                            job_titles_from_citations.append(title)
            
            # Build metadata
            metadata = {
                "company_name": company_name,
                "website": candidate.get("url", ""),
                "description": candidate.get("description", ""),
                "industry": get_val("industry"),
                "vector_db_mentioned": get_val("vector_db_mentioned"),
                "job_titles": get_val("job_titles") or (job_titles_from_citations[0] if job_titles_from_citations else ""),
                "headquarters": get_val("headquarters"),
                "job_posting_urls": "; ".join(list(set(job_urls))[:3]) if job_urls else "",
                "source": "parallel_findall",
                "query_name": query_name,
                "category": "hiring_lead",
                "added_at": datetime.now().isoformat()
            }
            
            # Fill missing tech from description
            if not metadata["vector_db_mentioned"]:
                desc = candidate.get("description", "").lower()
                found = [t for t in ["pinecone", "weaviate", "qdrant", "milvus", "rag", "vector", "embedding"] if t in desc]
                if found:
                    metadata["vector_db_mentioned"] = ", ".join(found)
            
            # Save to Chroma
            doc_id = f"hiring_{company_key.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            doc = f"{company_name}. {metadata['description']}"
            self.collection.add(ids=[doc_id], documents=[doc], metadatas=[metadata])
            
            new_leads.append(metadata)
            log(f"   ✅ NEW: {company_name}")
        
        return new_leads
    
    def notify_and_sync(self, new_leads: List[Dict], query_name: str):
        """Send Slack notifications and sync to Attio."""
        if not new_leads:
            log("📭 No new leads to notify")
            return
        
        log(f"📤 Processing {len(new_leads)} new leads...")
        
        # First sync to Attio to get record IDs
        attio_record_ids = {}  # company_name -> record_id
        
        if self.attio.enabled:
            log("   📊 Syncing to Attio...")
            for lead in new_leads:
                success, message, record_id = self.attio.sync_lead(lead)
                if record_id:
                    attio_record_ids[lead.get('company_name', '')] = record_id
                time.sleep(0.3)  # Rate limit
            
            created = sum(1 for lead in new_leads if lead.get('company_name') in attio_record_ids)
            log(f"   ✅ Attio: {created} companies synced")
        
        # Then send Slack notifications with Attio links
        if self.slack.enabled:
            log("   📱 Sending Slack notifications...")
            for lead in new_leads:
                company_name = lead.get('company_name', '')
                attio_id = attio_record_ids.get(company_name)
                
                # Check for hot leads
                is_hot, reason = is_hot_lead(lead)
                if is_hot:
                    log(f"   🔥 Hot lead: {company_name} - {reason}")
                    self.slack.notify_hot_lead(lead, reason, attio_record_id=attio_id)
                else:
                    self.slack.notify_new_lead(lead, attio_record_id=attio_id)
                time.sleep(0.5)  # Rate limit
            
            log(f"   ✅ Slack: {len(new_leads)} notifications sent")
    
    def run(self):
        """Run the full discovery pipeline."""
        log("=" * 60)
        log("🚀 CHROMA LEAD DISCOVERY ENGINE")
        log("=" * 60)
        log(f"Match limit: {self.match_limit}")
        log(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Define queries
        queries = [
            {
                "name": "Vector DB Job Postings",
                "objective": "Find companies with job postings for AI engineers, ML engineers, or data scientists that mention vector databases, RAG pipelines, semantic search, or embeddings",
                "conditions": [
                    {"name": "has_vector_job", "description": "Company has job postings mentioning vector databases, RAG, embeddings, or semantic search"},
                    {"name": "hiring_tech", "description": "Company is hiring technical roles"}
                ]
            }
        ]
        
        total_new = 0
        
        for query in queries:
            log(f"\n{'='*60}")
            log(f"📋 Query: {query['name']}")
            log("=" * 60)
            
            # Run query
            candidates = self.run_findall_query(query["objective"], query["conditions"])
            
            # Process candidates
            new_leads = self.process_candidates(candidates, query["name"])
            total_new += len(new_leads)
            
            # Notify and sync
            self.notify_and_sync(new_leads, query["name"])
        
        # Summary
        log(f"\n{'='*60}")
        log("✅ PIPELINE COMPLETE")
        log("=" * 60)
        log(f"   New leads discovered: {total_new}")
        log(f"   Total in Chroma: {self.collection.count()}")
        log(f"   Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return total_new


def main():
    parser = argparse.ArgumentParser(description="Chroma Lead Discovery Engine")
    parser.add_argument("--limit", type=int, default=10, help="Match limit for FindAll queries")
    args = parser.parse_args()
    
    if not PARALLEL_API_KEY:
        print("❌ PARALLEL_API_KEY not set in .env")
        sys.exit(1)
    
    engine = LeadDiscoveryEngine(match_limit=args.limit)
    engine.run()


if __name__ == "__main__":
    main()

