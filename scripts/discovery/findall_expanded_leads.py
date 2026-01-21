"""
Expanded FindAll Queries for Vector Database Leads

Runs multiple targeted queries and AUTOMATICALLY saves results to Chroma
after each query completes.

Features:
- Incremental saving to Chroma (no data loss if interrupted)
- Deduplication before saving
- Multiple query strategies for comprehensive coverage
- Slack notifications for new leads
"""

import os
import sys
import json
import time
import requests
import chromadb
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Import Slack notifier (optional - works without it)
try:
    from slack_lead_notifier import SlackLeadNotifier, is_hot_lead
    SLACK_ENABLED = True
except ImportError:
    SLACK_ENABLED = False
    print("ℹ️  Slack notifications disabled (slack_lead_notifier not found)")

# Import Attio sync (optional - works without it)
try:
    from attio_sync import AttioSync
    ATTIO_ENABLED = True
except ImportError:
    ATTIO_ENABLED = False
    print("ℹ️  Attio sync disabled (attio_sync not found)")

# Flush output immediately
sys.stdout.reconfigure(line_buffering=True)

# ============================================================
# CONFIGURATION
# ============================================================
PARALLEL_API_KEY = os.getenv("PARALLEL_API_KEY")
BASE_URL = "https://api.parallel.ai/v1beta/findall"
BETA_HEADER = "findall-2025-09-15"

# Chroma Config
CHROMA_API_KEY = 'ck-2i6neFLSKhd5pEqLP3jZKUkG6tX3yo4RVUZEeRxs4fHm'
CHROMA_TENANT = 'aa8f571e-03dc-4cd8-b888-723bd00b83f0'
CHROMA_DATABASE = 'customer'
COLLECTION_NAME = 'hiring_leads'


class ChromaSaver:
    """Handles saving leads to Chroma Cloud."""
    
    def __init__(self):
        print("🔗 Connecting to Chroma Cloud...")
        self.client = chromadb.CloudClient(
            api_key=CHROMA_API_KEY,
            tenant=CHROMA_TENANT,
            database=CHROMA_DATABASE
        )
        
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={
                "description": "Companies with active job postings mentioning vector database technologies",
                "source": "Parallel FindAll API"
            }
        )
        print(f"✅ Connected! Collection '{COLLECTION_NAME}' has {self.collection.count()} records")
        
        # Track what's already in the collection to avoid duplicates
        self._load_existing_companies()
    
    def _load_existing_companies(self):
        """Load existing company names to avoid duplicates."""
        self.existing_companies = set()
        try:
            results = self.collection.get()
            if results and results.get('metadatas'):
                for meta in results['metadatas']:
                    name = meta.get('company_name', '').lower().strip()
                    if name:
                        self.existing_companies.add(name)
            print(f"   Loaded {len(self.existing_companies)} existing companies for dedup")
        except Exception as e:
            print(f"   Warning: Could not load existing companies: {e}")
    
    def save_candidates(self, candidates: List[Dict], query_name: str) -> int:
        """
        Save matched candidates to Chroma.
        
        Args:
            candidates: List of candidate dicts from FindAll
            query_name: Name of the query (for tagging)
            
        Returns:
            Number of NEW candidates saved (after dedup)
        """
        matched = [c for c in candidates if c.get("match_status") == "matched"]
        
        if not matched:
            return 0
        
        # Vector database companies to IGNORE (competitors, not prospects)
        IGNORE_COMPANIES = {
            # Vector DB companies
            "chroma", "trychroma", "chroma ai",
            "pinecone", "pinecone systems", "pinecone.io",
            "weaviate", "weaviate.io",
            "qdrant", "qdrant.tech",
            "milvus", "zilliz",  # Zilliz is the company behind Milvus
            "turbopuffer",
            "vespa", "vespa.ai",
            "marqo",
            "vald",
            "activeloop", "deeplake",
            # Embedding/AI infrastructure companies
            "cohere", "cohere.ai",
            "voyage", "voyage ai", "voyageai",
            "jina", "jina ai",
            "nomic", "nomic ai",
            # Cloud DB with vector features (not primary prospects)
            "mongodb", "mongo",
            "redis", "redis labs",
            "elasticsearch", "elastic",
            "postgresql", "postgres",
            "supabase",
            "neon",
            "cockroachdb", "cockroach labs",
            "singlestore",
            "clickhouse",
            "rockset",
            "tigris",
        }
        
        ids = []
        documents = []
        metadatas = []
        new_count = 0
        
        for candidate in matched:
            company_name = candidate.get("name", "Unknown")
            company_key = company_name.lower().strip()
            
            # Skip vector DB companies (competitors, not prospects)
            if any(ignore in company_key for ignore in IGNORE_COMPANIES):
                print(f"   🚫 Skipping vector DB company: {company_name}")
                continue
            
            # Skip if already exists
            if company_key in self.existing_companies:
                print(f"   ⏭️  Skipping duplicate: {company_name}")
                continue
            
            # Mark as seen
            self.existing_companies.add(company_key)
            new_count += 1
            
            # Generate ID
            doc_id = f"hiring_{company_key.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            
            # Extract enrichments
            output = candidate.get("output", {})
            
            def get_value(field_name):
                field = output.get(field_name, {})
                if isinstance(field, dict):
                    return field.get("value", "")
                return str(field) if field else ""
            
            # Build metadata
            metadata = {
                "company_name": company_name,
                "website": candidate.get("url", ""),
                "description": candidate.get("description", ""),
                "industry": get_value("industry"),
                "vector_db_mentioned": get_value("vector_db_mentioned"),
                "job_titles": get_value("job_titles"),
                "funding_stage": get_value("funding_stage"),
                "company_size": get_value("company_size"),
                "headquarters": get_value("headquarters"),
                "use_case": get_value("use_case"),
                "source": "parallel_findall",
                "query_name": query_name,
                "match_status": "matched",
                "category": "hiring_lead",
                "added_at": datetime.now().isoformat(),
            }
            
            # Extract job posting URLs and additional info from citations/basis
            job_urls = []
            job_titles_from_citations = []
            
            for basis in candidate.get("basis", []):
                reasoning = basis.get("reasoning", "")
                
                for citation in basis.get("citations", []):
                    url = citation.get("url", "")
                    title = citation.get("title", "")
                    
                    # Extract job URLs
                    if url and any(x in url.lower() for x in ["job", "career", "indeed", "linkedin", "ziprecruiter", "glassdoor", "lever", "greenhouse", "volition"]):
                        job_urls.append(url)
                        # Use citation title as job title if it looks like one
                        if title and any(x in title.lower() for x in ["engineer", "scientist", "developer", "architect", "lead", "manager", "director"]):
                            job_titles_from_citations.append(title)
            
            if job_urls:
                metadata["job_posting_urls"] = "; ".join(list(set(job_urls))[:3])
            
            # If enrichment fields are empty, try to fill from citations
            if not metadata["job_titles"] and job_titles_from_citations:
                metadata["job_titles"] = job_titles_from_citations[0]
            
            # Extract vector DB mentions from description if enrichment is empty
            if not metadata["vector_db_mentioned"]:
                desc_lower = metadata["description"].lower()
                found_tech = []
                for tech in ["pinecone", "weaviate", "qdrant", "milvus", "chroma", "faiss", "pgvector", "rag", "vector database", "embeddings", "llm"]:
                    if tech in desc_lower:
                        found_tech.append(tech)
                if found_tech:
                    metadata["vector_db_mentioned"] = ", ".join(found_tech)
            
            # Build searchable document
            doc_parts = [company_name]
            if metadata["description"]:
                doc_parts.append(metadata["description"])
            if metadata["industry"]:
                doc_parts.append(f"Industry: {metadata['industry']}")
            if metadata["vector_db_mentioned"]:
                doc_parts.append(f"Vector DB: {metadata['vector_db_mentioned']}")
            if metadata["job_titles"]:
                doc_parts.append(f"Hiring: {metadata['job_titles']}")
            if metadata["use_case"]:
                doc_parts.append(f"Use case: {metadata['use_case']}")
            
            ids.append(doc_id)
            documents.append(". ".join(doc_parts))
            metadatas.append(metadata)
        
        # Save to Chroma
        if ids:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
        
        # Send Slack notifications for new leads
        if SLACK_ENABLED and metadatas:
            self._send_slack_notifications(metadatas, query_name)
        
        # Sync to Attio CRM
        if ATTIO_ENABLED and metadatas:
            self._sync_to_attio(metadatas)
        
        return new_count
    
    def _send_slack_notifications(self, new_leads: List[Dict], query_name: str):
        """Send Slack notifications for new leads."""
        try:
            notifier = SlackLeadNotifier()
            if not notifier.enabled:
                return
            
            # Check for hot leads first
            for lead in new_leads:
                is_hot, reason = is_hot_lead(lead)
                if is_hot:
                    print(f"   🔥 Hot lead detected: {lead.get('company_name')}")
                    notifier.notify_hot_lead(lead, reason)
            
            # Send batch summary
            notifier.notify_batch_summary(
                new_leads=new_leads,
                query_name=query_name,
                total_in_db=self.get_total_count()
            )
            print(f"   📤 Slack notification sent for {len(new_leads)} leads")
            
        except Exception as e:
            print(f"   ⚠️ Slack notification failed: {e}")
    
    def _sync_to_attio(self, new_leads: List[Dict]):
        """Sync new leads to Attio CRM."""
        try:
            attio = AttioSync()
            if not attio.enabled:
                return
            
            print(f"   📤 Syncing {len(new_leads)} leads to Attio...")
            
            created = 0
            for lead in new_leads:
                success, message = attio.sync_lead(lead)
                if success and "Created" in message:
                    created += 1
            
            print(f"   ✅ Attio: {created} new companies added")
            
        except Exception as e:
            print(f"   ⚠️ Attio sync failed: {e}")
    
    def get_total_count(self) -> int:
        """Get total records in collection."""
        return self.collection.count()


class ExpandedLeadsFinder:
    """Run multiple FindAll queries with auto-save to Chroma."""
    
    def __init__(self, chroma_saver: ChromaSaver):
        self.api_key = PARALLEL_API_KEY
        if not self.api_key:
            raise ValueError("PARALLEL_API_KEY not found in .env")
        
        self.headers = {
            "x-api-key": self.api_key,
            "parallel-beta": BETA_HEADER,
            "Content-Type": "application/json"
        }
        
        self.chroma = chroma_saver
        self.total_new = 0
    
    def create_run(
        self,
        objective: str,
        match_conditions: List[Dict],
        enrichments: List[Dict],
        match_limit: int = 25,
        generator: str = "core"
    ) -> str:
        """Start a FindAll run."""
        payload = {
            "objective": objective,
            "entity_type": "companies",
            "match_conditions": match_conditions,
            "enrichments": enrichments,
            "generator": generator,
            "match_limit": match_limit
        }
        
        response = requests.post(
            f"{BASE_URL}/runs",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()["findall_id"]
    
    def poll_until_complete(self, findall_id: str, timeout: int = 480) -> Dict:
        """Poll until run completes."""
        start_time = time.time()
        last_matched = -1
        
        while True:
            response = requests.get(
                f"{BASE_URL}/runs/{findall_id}",
                headers=self.headers
            )
            response.raise_for_status()
            status = response.json()
            
            metrics = status.get("status", {}).get("metrics", {})
            current_status = status.get("status", {}).get("status", "unknown")
            generated = metrics.get("generated_candidates_count", 0)
            matched = metrics.get("matched_candidates_count", 0)
            
            elapsed = int(time.time() - start_time)
            
            if matched > last_matched:
                print(f"   [{elapsed}s] {current_status} | Gen: {generated} | Match: {matched} ✨")
                last_matched = matched
            else:
                print(f"   [{elapsed}s] {current_status} | Gen: {generated} | Match: {matched}")
            
            sys.stdout.flush()
            
            if not status.get("status", {}).get("is_active", True):
                return status
            
            if time.time() - start_time > timeout:
                print(f"   ⚠️ Timeout after {timeout}s")
                return status
            
            time.sleep(10)
    
    def get_results(self, findall_id: str) -> List[Dict]:
        """Get results from a completed run."""
        response = requests.get(
            f"{BASE_URL}/runs/{findall_id}/result",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json().get("candidates", [])
    
    def run_query_and_save(
        self,
        name: str,
        objective: str,
        match_conditions: List[Dict],
        match_limit: int = 25
    ) -> int:
        """
        Run a query and IMMEDIATELY save results to Chroma.
        
        Returns:
            Number of NEW companies added
        """
        print(f"\n{'='*70}")
        print(f"🔍 QUERY: {name}")
        print(f"{'='*70}")
        print(f"Objective: {objective[:100]}...")
        sys.stdout.flush()
        
        # Standard enrichments
        enrichments = [
            {"name": "industry", "description": "Primary industry (AI/ML, FinTech, Healthcare, E-commerce, SaaS, etc.)"},
            {"name": "vector_db_mentioned", "description": "Vector database or embedding tech mentioned (Pinecone, Weaviate, Qdrant, Milvus, Chroma, FAISS, pgvector, RAG, embeddings)"},
            {"name": "job_titles", "description": "Relevant job titles from postings"},
            {"name": "funding_stage", "description": "Funding stage (Seed, Series A/B/C, Public, Bootstrapped)"},
            {"name": "company_size", "description": "Employee count range"},
            {"name": "headquarters", "description": "HQ location"},
            {"name": "use_case", "description": "How they're using vector databases or AI"}
        ]
        
        try:
            # Create run
            findall_id = self.create_run(
                objective=objective,
                match_conditions=match_conditions,
                enrichments=enrichments,
                match_limit=match_limit
            )
            print(f"✓ Run started: {findall_id}")
            sys.stdout.flush()
            
            # Poll until complete
            self.poll_until_complete(findall_id, timeout=480)
            
            # Get results
            candidates = self.get_results(findall_id)
            matched = [c for c in candidates if c.get("match_status") == "matched"]
            
            print(f"📥 Retrieved {len(matched)} matched companies")
            
            # ⭐ IMMEDIATELY SAVE TO CHROMA
            new_count = self.chroma.save_candidates(candidates, name)
            self.total_new += new_count
            
            print(f"✅ Saved {new_count} NEW companies to Chroma")
            print(f"📊 Total in collection: {self.chroma.get_total_count()}")
            sys.stdout.flush()
            
            return new_count
            
        except Exception as e:
            print(f"❌ Error in query '{name}': {e}")
            sys.stdout.flush()
            return 0


def run_all_queries():
    """Run all expanded queries with auto-save."""
    
    # Initialize Chroma saver
    chroma = ChromaSaver()
    finder = ExpandedLeadsFinder(chroma)
    
    initial_count = chroma.get_total_count()
    print(f"\n📊 Starting with {initial_count} leads in Chroma\n")
    
    # ================================================================
    # QUERY 1: Pinecone Users
    # ================================================================
    finder.run_query_and_save(
        name="Pinecone Users",
        objective="Find companies with job postings from the last 90 days that specifically mention Pinecone vector database experience as a requirement or preferred skill",
        match_conditions=[
            {"name": "mentions_pinecone", "description": "Company has active job postings that specifically mention Pinecone vector database"},
            {"name": "is_hiring_tech_roles", "description": "Company is hiring for engineering, ML, data science, or AI roles"}
        ],
        match_limit=20
    )
    
    # ================================================================
    # QUERY 2: RAG Builders
    # ================================================================
    finder.run_query_and_save(
        name="RAG Builders",
        objective="Find companies with job postings that mention building RAG (Retrieval Augmented Generation) pipelines, semantic search systems, or LLM applications with retrieval",
        match_conditions=[
            {"name": "building_rag_systems", "description": "Company has job postings mentioning RAG pipelines, retrieval augmented generation, or semantic search with LLMs"},
            {"name": "active_ai_development", "description": "Company is actively developing AI/ML products or features"}
        ],
        match_limit=20
    )
    
    # ================================================================
    # QUERY 3: Weaviate/Qdrant Users
    # ================================================================
    finder.run_query_and_save(
        name="Weaviate/Qdrant Users",
        objective="Find companies with job postings mentioning Weaviate or Qdrant vector database experience",
        match_conditions=[
            {"name": "mentions_weaviate_or_qdrant", "description": "Company has job postings mentioning Weaviate or Qdrant vector databases"},
            {"name": "building_search_or_ai", "description": "Company is building search, recommendation, or AI systems"}
        ],
        match_limit=20
    )
    
    # ================================================================
    # QUERY 4: ML Infrastructure Startups
    # ================================================================
    finder.run_query_and_save(
        name="ML Infrastructure",
        objective="Find AI startups and tech companies hiring for ML infrastructure, MLOps, or AI platform engineering roles that involve embeddings or vector search",
        match_conditions=[
            {"name": "ml_infrastructure_hiring", "description": "Company has job postings for ML infrastructure, MLOps, AI platform, or ML systems engineering roles"},
            {"name": "works_with_embeddings", "description": "Role involves working with embeddings, vector search, or similarity systems"}
        ],
        match_limit=20
    )
    
    # ================================================================
    # QUERY 5: Enterprise AI
    # ================================================================
    finder.run_query_and_save(
        name="Enterprise AI",
        objective="Find Fortune 500 or large enterprise companies with job postings for AI engineers or data scientists that mention vector databases, embeddings, or semantic search",
        match_conditions=[
            {"name": "enterprise_company", "description": "Company is a Fortune 500, large enterprise, or well-established corporation"},
            {"name": "ai_vector_db_hiring", "description": "Company has AI/ML job postings mentioning vector databases, embeddings, or semantic search"}
        ],
        match_limit=20
    )
    
    # ================================================================
    # QUERY 6: Healthcare AI
    # ================================================================
    finder.run_query_and_save(
        name="Healthcare AI",
        objective="Find healthcare, biotech, or life sciences companies with job postings mentioning vector databases, embeddings, or AI for medical/clinical applications",
        match_conditions=[
            {"name": "healthcare_or_biotech", "description": "Company operates in healthcare, biotech, pharma, or life sciences"},
            {"name": "ai_ml_hiring", "description": "Company has AI/ML job postings that could involve vector search or embeddings"}
        ],
        match_limit=15
    )
    
    # ================================================================
    # QUERY 7: FinTech AI
    # ================================================================
    finder.run_query_and_save(
        name="FinTech AI",
        objective="Find fintech, banking, or financial services companies with job postings mentioning vector databases, embeddings, semantic search, or AI for financial applications",
        match_conditions=[
            {"name": "fintech_or_financial", "description": "Company operates in fintech, banking, insurance, or financial services"},
            {"name": "ai_search_hiring", "description": "Company has job postings for AI, search, or data roles that could use vector databases"}
        ],
        match_limit=15
    )
    
    # Final summary
    final_count = chroma.get_total_count()
    
    print(f"\n{'='*70}")
    print("✅ ALL QUERIES COMPLETE")
    print(f"{'='*70}")
    print(f"\n📊 Summary:")
    print(f"   Started with: {initial_count} leads")
    print(f"   Added: {finder.total_new} new leads")
    print(f"   Total now: {final_count} leads")
    print(f"\n🎯 Collection '{COLLECTION_NAME}' is up to date!")
    
    return finder.total_new


if __name__ == "__main__":
    print("\n" + "🚀" * 35)
    print("\n   EXPANDED FINDALL QUERIES - AUTO-SAVE TO CHROMA")
    print("\n" + "🚀" * 35)
    sys.stdout.flush()
    
    start_time = time.time()
    
    try:
        new_leads = run_all_queries()
        
        elapsed = int(time.time() - start_time)
        print(f"\n⏱️  Total time: {elapsed // 60}m {elapsed % 60}s")
        print(f"🆕 New leads added: {new_leads}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted! But don't worry - all completed queries were already saved to Chroma.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("   Partial results (if any) were saved to Chroma.")
        raise




