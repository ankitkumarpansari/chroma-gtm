#!/usr/bin/env python3
"""
Save Parallel FindAll Hiring Leads to Chroma Cloud

Creates a new 'hiring_leads' collection for companies with active job postings
mentioning vector database technologies.

Data Source: Parallel FindAll API (job postings)
"""

import chromadb
import json
import os
import csv
from datetime import datetime
from typing import Optional
from glob import glob

# ============================================================
# CONFIGURATION
# ============================================================
API_KEY = 'ck-2i6neFLSKhd5pEqLP3jZKUkG6tX3yo4RVUZEeRxs4fHm'
TENANT = 'aa8f571e-03dc-4cd8-b888-723bd00b83f0'
DATABASE = 'customer'
COLLECTION_NAME = 'hiring_leads'


class HiringLeadsChroma:
    """Manage hiring leads in Chroma Cloud."""
    
    def __init__(self):
        """Connect to Chroma Cloud."""
        print("🔗 Connecting to Chroma Cloud...")
        self.client = chromadb.CloudClient(
            api_key=API_KEY,
            tenant=TENANT,
            database=DATABASE
        )
        print("✅ Connected to Chroma Cloud!")
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={
                "description": "Companies with active job postings mentioning vector database technologies",
                "source": "Parallel FindAll API",
                "created_at": datetime.now().isoformat()
            }
        )
        print(f"📦 Collection: '{COLLECTION_NAME}' (current count: {self.collection.count()})")
    
    def import_from_json(self, json_file: str) -> int:
        """
        Import hiring leads from Parallel FindAll JSON results.
        
        Args:
            json_file: Path to the JSON file from FindAll
            
        Returns:
            Number of leads imported
        """
        print(f"\n📂 Loading {json_file}...")
        
        with open(json_file, 'r') as f:
            candidates = json.load(f)
        
        # Filter to matched candidates only
        matched = [c for c in candidates if c.get("match_status") == "matched"]
        print(f"   Found {len(matched)} matched companies (out of {len(candidates)} total)")
        
        if not matched:
            print("   ⚠️ No matched candidates to import")
            return 0
        
        ids = []
        documents = []
        metadatas = []
        
        for candidate in matched:
            company_name = candidate.get("name", "Unknown")
            
            # Generate unique ID
            doc_id = f"hiring_{company_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            
            # Extract output fields (enrichments)
            output = candidate.get("output", {})
            
            # Helper to get enrichment value
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
                "source": "parallel_findall",
                "source_file": os.path.basename(json_file),
                "match_status": "matched",
                "category": "hiring_lead",
                "added_at": datetime.now().isoformat(),
            }
            
            # Extract job posting URLs from basis/citations
            job_urls = []
            for basis in candidate.get("basis", []):
                for citation in basis.get("citations", []):
                    url = citation.get("url", "")
                    if url and ("job" in url.lower() or "career" in url.lower() or 
                               "indeed" in url.lower() or "linkedin" in url.lower() or
                               "ziprecruiter" in url.lower() or "glassdoor" in url.lower()):
                        job_urls.append(url)
            
            if job_urls:
                metadata["job_posting_urls"] = "; ".join(job_urls[:3])  # Store up to 3 URLs
            
            # Build searchable document text
            doc_parts = [f"{company_name}"]
            if metadata["description"]:
                doc_parts.append(metadata["description"])
            if metadata["industry"]:
                doc_parts.append(f"Industry: {metadata['industry']}")
            if metadata["vector_db_mentioned"]:
                doc_parts.append(f"Vector DB tech: {metadata['vector_db_mentioned']}")
            if metadata["job_titles"]:
                doc_parts.append(f"Hiring for: {metadata['job_titles']}")
            
            document_text = ". ".join(doc_parts)
            
            ids.append(doc_id)
            documents.append(document_text)
            metadatas.append(metadata)
        
        # Add to collection
        if ids:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            print(f"✅ Imported {len(ids)} hiring leads to Chroma")
        
        return len(ids)
    
    def import_from_csv(self, csv_file: str) -> int:
        """
        Import hiring leads from CSV file.
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            Number of leads imported
        """
        print(f"\n📂 Loading {csv_file}...")
        
        ids = []
        documents = []
        metadatas = []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        print(f"   Found {len(rows)} rows")
        
        for row in rows:
            company_name = row.get("company_name", "Unknown")
            
            # Skip if already matched check
            if row.get("match_status") and row.get("match_status") != "matched":
                continue
            
            doc_id = f"hiring_{company_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            
            metadata = {
                "company_name": company_name,
                "website": row.get("website", ""),
                "description": row.get("description", ""),
                "industry": row.get("industry", ""),
                "vector_db_mentioned": row.get("vector_db_mentioned", ""),
                "job_titles": row.get("job_titles", ""),
                "funding_stage": row.get("funding_stage", ""),
                "company_size": row.get("company_size", ""),
                "headquarters": row.get("headquarters", ""),
                "source": "parallel_findall",
                "source_file": os.path.basename(csv_file),
                "match_status": "matched",
                "category": "hiring_lead",
                "added_at": datetime.now().isoformat(),
            }
            
            # Build document text
            doc_parts = [company_name]
            if metadata["description"]:
                doc_parts.append(metadata["description"])
            if metadata["industry"]:
                doc_parts.append(f"Industry: {metadata['industry']}")
            if metadata["vector_db_mentioned"]:
                doc_parts.append(f"Vector DB: {metadata['vector_db_mentioned']}")
            
            ids.append(doc_id)
            documents.append(". ".join(doc_parts))
            metadatas.append(metadata)
        
        if ids:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            print(f"✅ Imported {len(ids)} hiring leads from CSV")
        
        return len(ids)
    
    def search(self, query: str, n_results: int = 10) -> list:
        """Search hiring leads."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        leads = []
        if results and results['metadatas']:
            for i, metadata in enumerate(results['metadatas'][0]):
                lead = metadata.copy()
                lead['relevance_score'] = 1 - results['distances'][0][i] if results['distances'] else None
                leads.append(lead)
        
        return leads
    
    def get_all(self) -> list:
        """Get all hiring leads."""
        results = self.collection.get()
        return results.get('metadatas', [])
    
    def get_by_vector_db(self, vector_db: str) -> list:
        """Get leads mentioning a specific vector DB."""
        results = self.collection.query(
            query_texts=[f"vector database {vector_db}"],
            n_results=50
        )
        
        leads = []
        if results and results['metadatas']:
            for metadata in results['metadatas'][0]:
                if vector_db.lower() in metadata.get('vector_db_mentioned', '').lower():
                    leads.append(metadata)
        
        return leads
    
    def get_stats(self) -> dict:
        """Get collection statistics."""
        all_leads = self.get_all()
        
        stats = {
            "total_leads": len(all_leads),
            "by_industry": {},
            "by_vector_db": {},
            "by_funding_stage": {}
        }
        
        for lead in all_leads:
            # Count by industry
            industry = lead.get('industry', 'Unknown')
            if industry:
                stats['by_industry'][industry] = stats['by_industry'].get(industry, 0) + 1
            
            # Count by vector DB mentioned
            vdb = lead.get('vector_db_mentioned', '')
            if vdb:
                for db in ['Pinecone', 'Weaviate', 'Qdrant', 'Milvus', 'Chroma', 'FAISS', 'pgvector']:
                    if db.lower() in vdb.lower():
                        stats['by_vector_db'][db] = stats['by_vector_db'].get(db, 0) + 1
            
            # Count by funding stage
            funding = lead.get('funding_stage', 'Unknown')
            if funding:
                stats['by_funding_stage'][funding] = stats['by_funding_stage'].get(funding, 0) + 1
        
        return stats
    
    def clear_collection(self):
        """Delete all documents in the collection."""
        print(f"🗑️ Clearing collection '{COLLECTION_NAME}'...")
        try:
            self.client.delete_collection(name=COLLECTION_NAME)
            self.collection = self.client.create_collection(
                name=COLLECTION_NAME,
                metadata={
                    "description": "Companies with active job postings mentioning vector database technologies",
                    "source": "Parallel FindAll API",
                    "created_at": datetime.now().isoformat()
                }
            )
            print("✅ Collection cleared")
        except Exception as e:
            print(f"⚠️ Error clearing collection: {e}")


def main():
    """Import the latest FindAll results to Chroma."""
    print("=" * 70)
    print("SAVE HIRING LEADS TO CHROMA CLOUD")
    print("=" * 70)
    
    # Initialize
    db = HiringLeadsChroma()
    
    # Find the latest JSON file from FindAll
    json_files = sorted(glob("vector_db_leads_*.json"), reverse=True)
    
    if not json_files:
        print("\n❌ No vector_db_leads_*.json files found!")
        print("   Run findall_vector_db_leads.py first to generate leads.")
        return
    
    latest_file = json_files[0]
    print(f"\n📄 Latest FindAll results: {latest_file}")
    
    # Import
    count = db.import_from_json(latest_file)
    
    # Show stats
    print("\n" + "=" * 70)
    print("📊 COLLECTION STATS")
    print("=" * 70)
    
    stats = db.get_stats()
    print(f"\nTotal hiring leads: {stats['total_leads']}")
    
    if stats['by_vector_db']:
        print("\n🗄️ By Vector DB Technology:")
        for db_name, count in sorted(stats['by_vector_db'].items(), key=lambda x: -x[1]):
            print(f"   {db_name}: {count}")
    
    if stats['by_industry']:
        print("\n🏢 By Industry (top 10):")
        for industry, count in sorted(stats['by_industry'].items(), key=lambda x: -x[1])[:10]:
            print(f"   {industry}: {count}")
    
    # Test search
    print("\n" + "=" * 70)
    print("🔍 SAMPLE SEARCH: 'RAG pipeline'")
    print("=" * 70)
    
    results = db.search("RAG pipeline", n_results=5)
    for i, lead in enumerate(results, 1):
        print(f"\n{i}. {lead['company_name']}")
        print(f"   {lead['website']}")
        if lead.get('vector_db_mentioned'):
            print(f"   Tech: {lead['vector_db_mentioned'][:60]}...")
    
    print("\n" + "=" * 70)
    print("✅ COMPLETE")
    print("=" * 70)
    print(f"\nCollection: '{COLLECTION_NAME}'")
    print(f"Total leads: {stats['total_leads']}")
    print("\nYou can now query these leads using semantic search!")


if __name__ == "__main__":
    main()




