#!/usr/bin/env python3
"""
Create Vector DB Stack custom property in HubSpot and enrich companies.

This script:
1. Creates a "Vector DB Stack" multiple checkbox property
2. Enriches companies with their known vector DB usage

Usage:
    python create_vector_db_property.py
    python create_vector_db_property.py --test       # Test connection only
    python create_vector_db_property.py --enrich     # Only enrich (property already exists)
"""

import os
import requests
import time
import json
import chromadb
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

# HubSpot Configuration
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
HUBSPOT_BASE_URL = "https://api.hubapi.com"

# Chroma Configuration
CHROMA_API_KEY = os.environ.get('CHROMA_API_KEY', 'ck-A1VwR2zrmYsA3YvHqxahBTbmzqkrKB49hZ7UYSckwPfx')
CHROMA_TENANT = 'f23eab93-f8a3-493b-b775-a29c3582dee4'
CHROMA_DATABASE = 'GTM Signal'
CHROMA_COLLECTION = 'chroma_signal_list'

# Vector DB options for the property
VECTOR_DB_OPTIONS = [
    {"label": "Pinecone", "value": "pinecone", "displayOrder": 1},
    {"label": "Weaviate", "value": "weaviate", "displayOrder": 2},
    {"label": "Qdrant", "value": "qdrant", "displayOrder": 3},
    {"label": "Milvus", "value": "milvus", "displayOrder": 4},
    {"label": "Vespa", "value": "vespa", "displayOrder": 5},
    {"label": "pgvector", "value": "pgvector", "displayOrder": 6},
    {"label": "Elasticsearch", "value": "elasticsearch", "displayOrder": 7},
    {"label": "OpenSearch", "value": "opensearch", "displayOrder": 8},
    {"label": "LanceDB", "value": "lancedb", "displayOrder": 9},
    {"label": "MongoDB Atlas", "value": "mongodb_atlas", "displayOrder": 10},
    {"label": "Redis", "value": "redis", "displayOrder": 11},
    {"label": "Chroma", "value": "chroma", "displayOrder": 12},
    {"label": "FAISS", "value": "faiss", "displayOrder": 13},
    {"label": "Other", "value": "other", "displayOrder": 14},
]


class HubSpotPropertyManager:
    """Manage HubSpot custom properties and enrich companies."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or HUBSPOT_API_KEY
        if not self.api_key:
            print("❌ HUBSPOT_API_KEY not set in .env")
            self.enabled = False
        else:
            self.enabled = True
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
    
    def _request(self, method: str, endpoint: str, json_data: dict = None) -> Optional[dict]:
        """Make API request to HubSpot."""
        url = f"{HUBSPOT_BASE_URL}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=json_data)
            elif method == "PATCH":
                response = requests.patch(url, headers=self.headers, json=json_data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=json_data)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 409:
                return {"conflict": True, "message": "Already exists"}
            elif response.status_code == 429:
                print("   ⏳ Rate limited, waiting 10 seconds...")
                time.sleep(10)
                return self._request(method, endpoint, json_data)
            else:
                print(f"   ⚠️ API error: {response.status_code} - {response.text[:500]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test HubSpot API connection."""
        response = self._request("GET", "/crm/v3/objects/companies?limit=1")
        return response is not None
    
    def check_property_exists(self, property_name: str) -> bool:
        """Check if a company property already exists."""
        response = self._request("GET", f"/crm/v3/properties/companies/{property_name}")
        return response is not None and not response.get("conflict")
    
    def create_vector_db_property(self) -> bool:
        """Create the Vector DB Stack multiple checkbox property."""
        
        # First check if it already exists
        if self.check_property_exists("vector_db_stack"):
            print("   ℹ️ Property 'vector_db_stack' already exists")
            return True
        
        property_data = {
            "name": "vector_db_stack",
            "label": "Vector DB Stack",
            "type": "enumeration",
            "fieldType": "checkbox",
            "groupName": "companyinformation",
            "description": "Vector databases used by this company (for competitor intelligence)",
            "options": VECTOR_DB_OPTIONS,
            "formField": True
        }
        
        response = self._request(
            "POST",
            "/crm/v3/properties/companies",
            property_data
        )
        
        if response:
            if response.get("conflict"):
                print("   ℹ️ Property already exists")
                return True
            print(f"   ✅ Created property: vector_db_stack")
            return True
        return False
    
    def create_additional_properties(self) -> dict:
        """Create additional competitor intel properties."""
        results = {"created": [], "existed": [], "failed": []}
        
        properties = [
            {
                "name": "vector_db_primary",
                "label": "Primary Vector DB",
                "type": "enumeration",
                "fieldType": "select",
                "groupName": "companyinformation",
                "description": "The primary vector database used by this company",
                "options": VECTOR_DB_OPTIONS
            },
            {
                "name": "competitor_signal_source",
                "label": "Competitor Signal Source",
                "type": "string",
                "fieldType": "text",
                "groupName": "companyinformation",
                "description": "Where we found competitor intelligence (YouTube, GitHub, job posting, etc.)"
            },
            {
                "name": "displacement_priority",
                "label": "Displacement Priority",
                "type": "enumeration",
                "fieldType": "select",
                "groupName": "companyinformation",
                "description": "Priority for displacing competitor vector DB",
                "options": [
                    {"label": "🔥 Hot", "value": "hot", "displayOrder": 1},
                    {"label": "🎯 Warm", "value": "warm", "displayOrder": 2},
                    {"label": "❄️ Cold", "value": "cold", "displayOrder": 3},
                ]
            },
            {
                "name": "chroma_signal_tier",
                "label": "Chroma Signal Tier",
                "type": "enumeration",
                "fieldType": "select",
                "groupName": "companyinformation",
                "description": "Lead tier from Chroma Signal database",
                "options": [
                    {"label": "Tier 1 - High Priority", "value": "1", "displayOrder": 1},
                    {"label": "Tier 2 - Medium Priority", "value": "2", "displayOrder": 2},
                    {"label": "Tier 3 - Lower Priority", "value": "3", "displayOrder": 3},
                ]
            },
            {
                "name": "signal_strength",
                "label": "Signal Strength",
                "type": "enumeration",
                "fieldType": "select",
                "groupName": "companyinformation",
                "description": "Strength of the buying signal",
                "options": [
                    {"label": "High", "value": "high", "displayOrder": 1},
                    {"label": "Medium", "value": "medium", "displayOrder": 2},
                    {"label": "Low", "value": "low", "displayOrder": 3},
                ]
            }
        ]
        
        for prop in properties:
            if self.check_property_exists(prop["name"]):
                results["existed"].append(prop["name"])
                continue
            
            response = self._request("POST", "/crm/v3/properties/companies", prop)
            if response and not response.get("conflict"):
                results["created"].append(prop["name"])
            elif response and response.get("conflict"):
                results["existed"].append(prop["name"])
            else:
                results["failed"].append(prop["name"])
            
            time.sleep(0.2)  # Rate limiting
        
        return results
    
    def find_company_by_name(self, name: str) -> Optional[dict]:
        """Search for company by name."""
        response = self._request(
            "POST",
            "/crm/v3/objects/companies/search",
            {
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "name",
                        "operator": "EQ",
                        "value": name
                    }]
                }],
                "limit": 1
            }
        )
        
        if response and response.get("results"):
            return response["results"][0]
        return None
    
    def update_company_properties(self, company_id: str, properties: dict) -> bool:
        """Update a company's properties."""
        response = self._request(
            "PATCH",
            f"/crm/v3/objects/companies/{company_id}",
            {"properties": properties}
        )
        return response is not None


def fetch_chroma_companies_with_vector_db() -> List[Dict]:
    """Fetch companies from Chroma that have vector DB information."""
    print("🔗 Connecting to Chroma Cloud...")
    
    client = chromadb.CloudClient(
        api_key=CHROMA_API_KEY,
        tenant=CHROMA_TENANT,
        database=CHROMA_DATABASE
    )
    
    collection = client.get_collection(CHROMA_COLLECTION)
    total_count = collection.count()
    print(f"✅ Connected! Total records: {total_count}")
    
    # Fetch all companies
    all_companies = []
    batch_size = 100
    offset = 0
    
    while offset < total_count:
        batch = collection.get(
            limit=batch_size,
            offset=offset,
            include=['metadatas', 'documents']
        )
        for i, meta in enumerate(batch['metadatas']):
            meta['id'] = batch['ids'][i]
            if batch['documents'] and i < len(batch['documents']):
                meta['document'] = batch['documents'][i]
            all_companies.append(meta)
        offset += batch_size
        if len(batch['ids']) < batch_size:
            break
    
    # Filter to those with vector DB info or competitor category
    companies_with_intel = []
    for c in all_companies:
        has_vector_db = c.get('current_vector_db') and c.get('current_vector_db') != 'unknown'
        is_competitor_customer = c.get('category') == 'competitor_customer'
        has_tier = c.get('tier') in ['1', '2', '3']
        
        if has_vector_db or is_competitor_customer or has_tier:
            companies_with_intel.append(c)
    
    print(f"📊 Found {len(companies_with_intel)} companies with enrichment data")
    return companies_with_intel


def normalize_vector_db(value: str) -> Optional[str]:
    """Normalize vector DB name to HubSpot option value."""
    if not value:
        return None
    
    value_lower = value.lower().strip()
    
    mapping = {
        'pinecone': 'pinecone',
        'weaviate': 'weaviate',
        'qdrant': 'qdrant',
        'milvus': 'milvus',
        'vespa': 'vespa',
        'pgvector': 'pgvector',
        'pg_vector': 'pgvector',
        'elasticsearch': 'elasticsearch',
        'elastic': 'elasticsearch',
        'opensearch': 'opensearch',
        'lancedb': 'lancedb',
        'lance': 'lancedb',
        'mongodb': 'mongodb_atlas',
        'mongo': 'mongodb_atlas',
        'mongodb atlas': 'mongodb_atlas',
        'redis': 'redis',
        'chroma': 'chroma',
        'chromadb': 'chroma',
        'faiss': 'faiss',
    }
    
    return mapping.get(value_lower, 'other')


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Create Vector DB property and enrich companies")
    parser.add_argument("--test", action="store_true", help="Test connection only")
    parser.add_argument("--enrich", action="store_true", help="Skip property creation, only enrich")
    parser.add_argument("--limit", type=int, help="Limit number of companies to enrich")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🏷️  HUBSPOT VECTOR DB PROPERTY SETUP")
    print("=" * 60)
    
    # Initialize HubSpot client
    hs = HubSpotPropertyManager()
    
    if not hs.enabled:
        return
    
    print(f"\n🔗 Testing HubSpot connection...")
    if not hs.test_connection():
        print("❌ HubSpot connection failed")
        return
    print("✅ HubSpot connection successful!")
    
    if args.test:
        return
    
    # Step 1: Create custom properties
    if not args.enrich:
        print("\n" + "-" * 60)
        print("📝 STEP 1: Creating Custom Properties")
        print("-" * 60)
        
        # Create main vector_db_stack property
        print("\n   Creating 'vector_db_stack' (multiple checkbox)...")
        if hs.create_vector_db_property():
            print("   ✅ vector_db_stack ready")
        else:
            print("   ❌ Failed to create vector_db_stack")
            return
        
        # Create additional properties
        print("\n   Creating additional properties...")
        results = hs.create_additional_properties()
        
        if results["created"]:
            print(f"   ✅ Created: {', '.join(results['created'])}")
        if results["existed"]:
            print(f"   ℹ️ Already existed: {', '.join(results['existed'])}")
        if results["failed"]:
            print(f"   ❌ Failed: {', '.join(results['failed'])}")
    
    # Step 2: Fetch companies with vector DB intel
    print("\n" + "-" * 60)
    print("📊 STEP 2: Fetching Companies with Intel")
    print("-" * 60)
    
    companies = fetch_chroma_companies_with_vector_db()
    
    if not companies:
        print("   No companies found with vector DB information")
        return
    
    if args.limit:
        companies = companies[:args.limit]
        print(f"   Limited to {len(companies)} companies")
    
    # Count by vector DB
    by_vector_db = {}
    for c in companies:
        vdb = c.get('current_vector_db', 'unknown')
        by_vector_db[vdb] = by_vector_db.get(vdb, 0) + 1
    
    print(f"\n   By Vector DB:")
    for vdb, count in sorted(by_vector_db.items(), key=lambda x: -x[1])[:10]:
        print(f"      {vdb}: {count}")
    
    # Step 3: Enrich companies in HubSpot
    print("\n" + "-" * 60)
    print("🔄 STEP 3: Enriching Companies in HubSpot")
    print("-" * 60)
    
    stats = {"updated": 0, "not_found": 0, "failed": 0, "skipped": 0}
    
    for i, company in enumerate(companies):
        company_name = company.get('company_name', 'Unknown')
        
        # Find company in HubSpot
        hs_company = hs.find_company_by_name(company_name)
        
        if not hs_company:
            stats["not_found"] += 1
            if (i + 1) % 100 == 0:
                print(f"   [{i+1}/{len(companies)}] Processing...")
            continue
        
        company_id = hs_company.get("id")
        
        # Build properties to update
        properties = {}
        
        # Vector DB stack
        vector_db = company.get('current_vector_db')
        if vector_db and vector_db != 'unknown':
            normalized = normalize_vector_db(vector_db)
            if normalized:
                properties["vector_db_stack"] = normalized
                properties["vector_db_primary"] = normalized
        
        # Tier
        tier = company.get('tier')
        if tier in ['1', '2', '3']:
            properties["chroma_signal_tier"] = tier
        
        # Signal strength
        signal = company.get('signal_strength')
        if signal:
            properties["signal_strength"] = signal.lower()
        
        # Source
        source = company.get('source_type') or company.get('source_channel')
        if source:
            properties["competitor_signal_source"] = source
        
        # Displacement priority based on tier and vector DB
        if vector_db and vector_db != 'unknown' and tier == '1':
            properties["displacement_priority"] = "hot"
        elif vector_db and vector_db != 'unknown' and tier == '2':
            properties["displacement_priority"] = "warm"
        elif vector_db and vector_db != 'unknown':
            properties["displacement_priority"] = "cold"
        
        if not properties:
            stats["skipped"] += 1
            continue
        
        # Update company
        if hs.update_company_properties(company_id, properties):
            stats["updated"] += 1
            if stats["updated"] % 25 == 0:
                print(f"   ✅ Updated {stats['updated']} companies...")
        else:
            stats["failed"] += 1
        
        time.sleep(0.15)  # Rate limiting
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ ENRICHMENT COMPLETE")
    print("=" * 60)
    print(f"""
   Total processed: {len(companies)}
   ✅ Updated: {stats['updated']}
   ⏭️ Skipped (no data): {stats['skipped']}
   🔍 Not found in HubSpot: {stats['not_found']}
   ❌ Failed: {stats['failed']}

   Properties created:
   • vector_db_stack (multiple checkbox)
   • vector_db_primary (dropdown)
   • chroma_signal_tier (dropdown)
   • signal_strength (dropdown)
   • displacement_priority (dropdown)
   • competitor_signal_source (text)

🔗 View in HubSpot and filter by 'Vector DB Stack' to see competitor intel!
""")


if __name__ == "__main__":
    main()

