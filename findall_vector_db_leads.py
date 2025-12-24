"""
FindAll Vector Database Leads Discovery

Uses Parallel.ai FindAll API to discover companies with job postings
mentioning vector database technologies - potential customers for Chroma.
"""

import os
import csv
import json
import time
import requests
from datetime import datetime
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

# API Configuration
PARALLEL_API_KEY = os.getenv("PARALLEL_API_KEY")
BASE_URL = "https://api.parallel.ai/v1beta/findall"
BETA_HEADER = "findall-2025-09-15"


class VectorDBLeadsFinder:
    """Find companies hiring for vector database roles - potential Chroma customers."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or PARALLEL_API_KEY
        if not self.api_key:
            raise ValueError("PARALLEL_API_KEY not found")
        
        self.headers = {
            "x-api-key": self.api_key,
            "parallel-beta": BETA_HEADER,
            "Content-Type": "application/json"
        }
    
    def ingest(self, objective: str) -> Dict[str, Any]:
        """Convert natural language query to structured schema."""
        print(f"📝 Ingesting objective...")
        response = requests.post(
            f"{BASE_URL}/ingest",
            headers=self.headers,
            json={"objective": objective}
        )
        response.raise_for_status()
        result = response.json()
        print(f"   ✓ Entity type: {result.get('entity_type')}")
        print(f"   ✓ Match conditions: {len(result.get('match_conditions', []))}")
        return result
    
    def create_run(
        self,
        objective: str,
        entity_type: str,
        match_conditions: List[Dict[str, str]],
        enrichments: List[Dict[str, str]],
        generator: str = "core",
        match_limit: int = 50
    ) -> str:
        """Start a FindAll run with enrichments."""
        print(f"\n🚀 Creating FindAll run...")
        print(f"   Generator: {generator}")
        print(f"   Match limit: {match_limit}")
        print(f"   Enrichments: {len(enrichments)}")
        
        payload = {
            "objective": objective,
            "entity_type": entity_type,
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
        findall_id = response.json()["findall_id"]
        print(f"   ✓ Run started: {findall_id}")
        return findall_id
    
    def get_status(self, findall_id: str) -> Dict[str, Any]:
        """Check run status."""
        response = requests.get(
            f"{BASE_URL}/runs/{findall_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_results(self, findall_id: str) -> Dict[str, Any]:
        """Get final results."""
        response = requests.get(
            f"{BASE_URL}/runs/{findall_id}/result",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def poll_until_complete(
        self,
        findall_id: str,
        poll_interval: int = 10,
        timeout: int = 600
    ) -> Dict[str, Any]:
        """Poll until run completes."""
        print(f"\n⏳ Polling for results (timeout: {timeout}s)...")
        start_time = time.time()
        last_matched = 0
        
        while True:
            status = self.get_status(findall_id)
            status_info = status.get("status", {})
            metrics = status_info.get("metrics", {})
            
            generated = metrics.get("generated_candidates_count", 0)
            matched = metrics.get("matched_candidates_count", 0)
            current_status = status_info.get("status", "unknown")
            
            # Show progress
            elapsed = int(time.time() - start_time)
            if matched > last_matched:
                print(f"   [{elapsed}s] Status: {current_status} | Generated: {generated} | Matched: {matched} ✨")
                last_matched = matched
            else:
                print(f"   [{elapsed}s] Status: {current_status} | Generated: {generated} | Matched: {matched}")
            
            # Check if complete
            if not status_info.get("is_active", True):
                print(f"\n✅ Run completed!")
                return status
            
            # Check timeout
            if time.time() - start_time > timeout:
                print(f"\n⚠️  Timeout reached after {timeout}s")
                return status
            
            time.sleep(poll_interval)
    
    def find_vector_db_leads(
        self,
        match_limit: int = 50,
        generator: str = "core"
    ) -> List[Dict[str, Any]]:
        """
        Main method: Find companies with vector DB job postings.
        
        Returns list of companies with enriched data.
        """
        # Objective focused on job postings mentioning vector DB tech
        objective = """Find companies with active job postings from the last 60 days 
        that mention vector database technologies including Pinecone, Weaviate, Qdrant, 
        Milvus, Chroma, or terms like embeddings infrastructure, RAG pipeline, 
        semantic search, or vector embeddings"""
        
        # Step 1: Ingest to get schema (or use custom)
        print("=" * 70)
        print("🔍 FindAll: Vector Database Leads Discovery")
        print("=" * 70)
        print(f"\nObjective: {objective[:100]}...")
        
        # Custom match conditions for precision
        match_conditions = [
            {
                "name": "has_vector_db_job_posting",
                "description": "Company has active job postings from the last 60 days that mention vector database technologies (Pinecone, Weaviate, Qdrant, Milvus, Chroma), embeddings infrastructure, RAG pipeline, semantic search, or vector embeddings"
            },
            {
                "name": "is_hiring_engineers",
                "description": "Company is actively hiring software engineers, ML engineers, data engineers, or AI/ML roles"
            }
        ]
        
        # Enrichments to extract additional data
        enrichments = [
            {
                "name": "industry",
                "description": "The primary industry or sector the company operates in (e.g., AI/ML, FinTech, Healthcare, E-commerce, SaaS)"
            },
            {
                "name": "vector_db_mentioned",
                "description": "Which specific vector database or embedding technology was mentioned in their job postings (e.g., Pinecone, Weaviate, Qdrant, Milvus, Chroma, FAISS, or general terms like RAG, embeddings)"
            },
            {
                "name": "job_titles",
                "description": "The job titles from relevant postings (e.g., ML Engineer, AI Engineer, Data Engineer, Backend Engineer)"
            },
            {
                "name": "funding_stage",
                "description": "The company's funding stage if known (e.g., Seed, Series A, Series B, Series C+, Public, Bootstrapped)"
            },
            {
                "name": "company_size",
                "description": "Approximate company size or employee count range"
            },
            {
                "name": "headquarters",
                "description": "Company headquarters location (city, country)"
            }
        ]
        
        print(f"\nMatch conditions:")
        for mc in match_conditions:
            print(f"   • {mc['name']}")
        
        print(f"\nEnrichments to extract:")
        for e in enrichments:
            print(f"   • {e['name']}")
        
        # Step 2: Create run
        findall_id = self.create_run(
            objective=objective,
            entity_type="companies",
            match_conditions=match_conditions,
            enrichments=enrichments,
            generator=generator,
            match_limit=match_limit
        )
        
        # Step 3: Poll until complete
        self.poll_until_complete(findall_id, poll_interval=10, timeout=600)
        
        # Step 4: Get results
        print(f"\n📥 Fetching results...")
        results = self.get_results(findall_id)
        
        candidates = results.get("candidates", [])
        print(f"   ✓ Retrieved {len(candidates)} matched companies")
        
        return candidates, findall_id


def extract_enrichment_value(candidate: Dict, field_name: str) -> str:
    """Extract enrichment value from candidate output."""
    output = candidate.get("output", {})
    field_data = output.get(field_name, {})
    
    if isinstance(field_data, dict):
        return field_data.get("value", "")
    return str(field_data) if field_data else ""


def save_to_csv(candidates: List[Dict], filepath: str):
    """Save candidates to CSV with specified columns."""
    print(f"\n💾 Saving to CSV: {filepath}")
    
    rows = []
    for c in candidates:
        # Only include matched candidates
        if c.get("match_status") != "matched":
            continue
            
        row = {
            "company_name": c.get("name", ""),
            "website": c.get("url", ""),
            "description": c.get("description", ""),
            "industry": extract_enrichment_value(c, "industry"),
            "vector_db_mentioned": extract_enrichment_value(c, "vector_db_mentioned"),
            "job_titles": extract_enrichment_value(c, "job_titles"),
            "funding_stage": extract_enrichment_value(c, "funding_stage"),
            "company_size": extract_enrichment_value(c, "company_size"),
            "headquarters": extract_enrichment_value(c, "headquarters"),
            "match_status": c.get("match_status", "")
        }
        rows.append(row)
    
    if not rows:
        print("   ⚠️  No matched candidates to save")
        return
    
    # Write CSV
    fieldnames = [
        "company_name", "website", "description", "industry", 
        "vector_db_mentioned", "job_titles", "funding_stage",
        "company_size", "headquarters", "match_status"
    ]
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"   ✓ Saved {len(rows)} companies to {filepath}")


def save_to_json(candidates: List[Dict], filepath: str):
    """Save full candidate data to JSON."""
    print(f"💾 Saving full data to JSON: {filepath}")
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(candidates, f, indent=2)
    
    print(f"   ✓ Saved {len(candidates)} candidates")


def print_summary(candidates: List[Dict]):
    """Print summary of results."""
    matched = [c for c in candidates if c.get("match_status") == "matched"]
    
    print("\n" + "=" * 70)
    print("📊 RESULTS SUMMARY")
    print("=" * 70)
    print(f"\nTotal matched companies: {len(matched)}")
    
    if not matched:
        return
    
    # Count by vector DB mentioned
    vector_dbs = {}
    industries = {}
    funding_stages = {}
    
    for c in matched:
        vdb = extract_enrichment_value(c, "vector_db_mentioned")
        if vdb:
            for db in ["Pinecone", "Weaviate", "Qdrant", "Milvus", "Chroma", "FAISS", "RAG", "embeddings"]:
                if db.lower() in vdb.lower():
                    vector_dbs[db] = vector_dbs.get(db, 0) + 1
        
        industry = extract_enrichment_value(c, "industry")
        if industry:
            industries[industry] = industries.get(industry, 0) + 1
        
        funding = extract_enrichment_value(c, "funding_stage")
        if funding:
            funding_stages[funding] = funding_stages.get(funding, 0) + 1
    
    if vector_dbs:
        print("\n🗄️  Vector DB Technologies Mentioned:")
        for db, count in sorted(vector_dbs.items(), key=lambda x: -x[1]):
            print(f"   {db}: {count}")
    
    if industries:
        print("\n🏢 Industries:")
        for ind, count in sorted(industries.items(), key=lambda x: -x[1])[:10]:
            print(f"   {ind}: {count}")
    
    if funding_stages:
        print("\n💰 Funding Stages:")
        for stage, count in sorted(funding_stages.items(), key=lambda x: -x[1]):
            print(f"   {stage}: {count}")
    
    # Show top 10 companies
    print("\n🏆 Top Companies Found:")
    for i, c in enumerate(matched[:10], 1):
        name = c.get("name", "Unknown")
        url = c.get("url", "")
        vdb = extract_enrichment_value(c, "vector_db_mentioned")
        print(f"   {i}. {name}")
        print(f"      {url}")
        if vdb:
            print(f"      Tech: {vdb[:80]}...")


def main():
    """Main entry point."""
    print("\n" + "🚀" * 35)
    print("\n   PARALLEL FINDALL - VECTOR DATABASE LEADS DISCOVERY")
    print("\n" + "🚀" * 35)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # Initialize finder
        finder = VectorDBLeadsFinder()
        
        # Run FindAll query
        candidates, findall_id = finder.find_vector_db_leads(
            match_limit=50,
            generator="core"
        )
        
        # Print summary
        print_summary(candidates)
        
        # Save results
        csv_path = f"vector_db_leads_{timestamp}.csv"
        json_path = f"vector_db_leads_{timestamp}.json"
        
        save_to_csv(candidates, csv_path)
        save_to_json(candidates, json_path)
        
        print("\n" + "=" * 70)
        print("✅ COMPLETE")
        print("=" * 70)
        print(f"\nFindAll ID: {findall_id}")
        print(f"CSV file: {csv_path}")
        print(f"JSON file: {json_path}")
        print(f"\nUse these leads to reach out to companies actively building with vector databases!")
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ API Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()




