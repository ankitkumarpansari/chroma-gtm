#!/usr/bin/env python3
"""
Sync Chroma Signal Companies to HubSpot

Syncs all companies from the Chroma Signal database to your HubSpot Companies module.

Usage:
    python sync_chroma_signal_to_hubspot.py              # Sync all companies
    python sync_chroma_signal_to_hubspot.py --test       # Test connection only
    python sync_chroma_signal_to_hubspot.py --limit 10   # Sync first 10 only
    python sync_chroma_signal_to_hubspot.py --tier 1     # Sync only Tier 1 companies
    python sync_chroma_signal_to_hubspot.py --competitors # Sync only competitor accounts
"""

import os
import json
import requests
import time
import argparse
import chromadb
from datetime import datetime
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

# HubSpot Configuration
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")  # Private app access token
HUBSPOT_BASE_URL = "https://api.hubapi.com"

# Chroma Configuration
CHROMA_API_KEY = os.environ.get('CHROMA_API_KEY', 'ck-A1VwR2zrmYsA3YvHqxahBTbmzqkrKB49hZ7UYSckwPfx')
CHROMA_TENANT = 'f23eab93-f8a3-493b-b775-a29c3582dee4'
CHROMA_DATABASE = 'GTM Signal'
CHROMA_COLLECTION = 'chroma_signal_list'


def fetch_chroma_companies(tier_filter: str = None, competitors_only: bool = False) -> List[Dict]:
    """Fetch all companies from Chroma Signal database."""
    print("🔗 Connecting to Chroma Cloud...")
    
    client = chromadb.CloudClient(
        api_key=CHROMA_API_KEY,
        tenant=CHROMA_TENANT,
        database=CHROMA_DATABASE
    )
    
    collection = client.get_collection(CHROMA_COLLECTION)
    total_count = collection.count()
    print(f"✅ Connected! Total records in Chroma: {total_count}")
    
    # Fetch all companies in batches
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
    
    print(f"📊 Retrieved {len(all_companies)} companies from Chroma")
    
    # Apply filters
    if tier_filter:
        all_companies = [c for c in all_companies if c.get('tier') == tier_filter]
        print(f"   Filtered to {len(all_companies)} Tier {tier_filter} companies")
    
    if competitors_only:
        all_companies = [c for c in all_companies if c.get('category') == 'competitor_customer']
        print(f"   Filtered to {len(all_companies)} competitor accounts")
    
    # Sort by tier then company name
    all_companies.sort(key=lambda x: (x.get('tier', '9'), x.get('company_name', '')))
    
    return all_companies


class HubSpotSync:
    """Sync companies to HubSpot CRM."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or HUBSPOT_API_KEY
        if not self.api_key:
            print("❌ HUBSPOT_API_KEY not set in .env")
            print("   Get your private app access token from:")
            print("   https://app.hubspot.com/private-apps/YOUR_PORTAL_ID")
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
            else:
                raise ValueError(f"Unknown method: {method}")
            
            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 409:
                # Conflict - company already exists
                return {"conflict": True, "response": response.json()}
            elif response.status_code == 429:
                # Rate limited - wait and retry
                print("   ⏳ Rate limited, waiting 10 seconds...")
                time.sleep(10)
                return self._request(method, endpoint, json_data)
            else:
                print(f"   ⚠️ API error: {response.status_code} - {response.text[:300]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test HubSpot API connection."""
        response = self._request("GET", "/crm/v3/objects/companies?limit=1")
        return response is not None
    
    def find_company_by_name(self, name: str) -> Optional[dict]:
        """Search for existing company by name."""
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
    
    def create_company(self, company: dict) -> Optional[str]:
        """Create a new company record in HubSpot."""
        company_name = company.get('company_name', 'Unknown')
        
        # Build description from available metadata
        desc_parts = []
        if company.get('category'):
            desc_parts.append(f"Category: {company['category']}")
        if company.get('tier'):
            desc_parts.append(f"Tier: {company['tier']}")
        if company.get('signal_strength'):
            desc_parts.append(f"Signal Strength: {company['signal_strength']}")
        if company.get('source_type'):
            desc_parts.append(f"Source: {company['source_type']}")
        if company.get('source_channel'):
            desc_parts.append(f"Source Channel: {company['source_channel']}")
        if company.get('current_vector_db'):
            desc_parts.append(f"Current Vector DB: {company['current_vector_db']}")
        
        # Add document description if available
        if company.get('document'):
            desc_parts.append(f"\n{company['document']}")
        
        desc_parts.append("\nSource: Chroma Signal Database")
        
        properties = {
            "name": company_name,
            "description": "\n".join(desc_parts),
            "lifecyclestage": "lead"
        }
        
        # Map tier to lead status
        tier = company.get('tier', '3')
        if tier == '1':
            properties["hs_lead_status"] = "NEW"  # High priority
        elif tier == '2':
            properties["hs_lead_status"] = "OPEN"  # Medium priority
        
        # Add industry if available (only for non-"other" categories)
        if company.get('category') and company.get('category') != 'other':
            category_map = {
                'enterprise': 'COMPUTER_SOFTWARE',
                'ai_native': 'COMPUTER_SOFTWARE',
                'competitor_customer': 'COMPUTER_SOFTWARE',
                'partner': 'COMPUTER_SOFTWARE'
            }
            industry = category_map.get(company['category'])
            if industry:
                properties["industry"] = industry
        
        response = self._request(
            "POST",
            "/crm/v3/objects/companies",
            {"properties": properties}
        )
        
        if response:
            if response.get("conflict"):
                # Company already exists
                existing = self.find_company_by_name(company_name)
                if existing:
                    return existing.get("id")
                return None
            return response.get("id")
        return None
    
    def get_all_company_names(self) -> List[str]:
        """Get all existing company names."""
        names = []
        after = None
        
        while True:
            endpoint = "/crm/v3/objects/companies?limit=100&properties=name"
            if after:
                endpoint += f"&after={after}"
            
            response = self._request("GET", endpoint)
            
            if not response:
                break
            
            for company in response.get("results", []):
                name = company.get("properties", {}).get("name", "")
                if name:
                    names.append(name.lower())
            
            # Check for pagination
            paging = response.get("paging", {})
            next_page = paging.get("next", {})
            after = next_page.get("after")
            
            if not after:
                break
        
        return names
    
    def sync_company(self, company: dict, existing_names: List[str]) -> tuple:
        """Sync a single company. Returns (success, status, company_id)."""
        company_name = company.get('company_name', 'Unknown')
        
        # Check if already exists
        if company_name.lower() in existing_names:
            return True, "already_exists", None
        
        # Create company
        company_id = self.create_company(company)
        
        if company_id:
            return True, "created", company_id
        else:
            return False, "create_failed", None
    
    def sync_all(self, companies: List[dict], delay: float = 0.15, limit: int = None) -> dict:
        """Sync all companies to HubSpot."""
        if not self.enabled:
            return {"error": "HubSpot not configured"}
        
        if limit:
            companies = companies[:limit]
        
        print(f"\n📤 Syncing {len(companies)} companies to HubSpot...")
        
        # Get existing companies
        print("   Fetching existing companies from HubSpot...")
        existing_names = self.get_all_company_names()
        print(f"   Found {len(existing_names)} existing companies in HubSpot")
        
        results = {
            "total": len(companies),
            "created": 0,
            "already_exists": 0,
            "failed": 0,
            "created_companies": [],
            "failed_companies": []
        }
        
        for i, company in enumerate(companies):
            company_name = company.get('company_name', 'Unknown')
            success, status, company_id = self.sync_company(company, existing_names)
            
            if status == "created":
                results["created"] += 1
                results["created_companies"].append(company_name)
                tier = company.get('tier', '?')
                print(f"   [{i+1}/{len(companies)}] ✅ T{tier} {company_name} - created")
                # Add to existing list to avoid duplicates in same run
                existing_names.append(company_name.lower())
            elif status == "already_exists":
                results["already_exists"] += 1
                if (i + 1) % 50 == 0:  # Only print every 50 to reduce noise
                    print(f"   [{i+1}/{len(companies)}] ⏭️  Skipping existing companies...")
            else:
                results["failed"] += 1
                results["failed_companies"].append(company_name)
                print(f"   [{i+1}/{len(companies)}] ❌ {company_name} - failed")
            
            time.sleep(delay)
        
        return results


def main():
    parser = argparse.ArgumentParser(description="Sync Chroma Signal companies to HubSpot")
    parser.add_argument("--test", action="store_true", help="Test connection only")
    parser.add_argument("--limit", type=int, help="Limit number of companies to sync")
    parser.add_argument("--tier", type=str, choices=['1', '2', '3'], help="Filter by tier")
    parser.add_argument("--competitors", action="store_true", help="Sync only competitor accounts")
    args = parser.parse_args()
    
    print("=" * 60)
    print("CHROMA SIGNAL → HUBSPOT SYNC")
    print("=" * 60)
    
    # Test HubSpot connection
    print("\n🔗 Testing HubSpot connection...")
    sync = HubSpotSync()
    
    if not sync.enabled:
        return
    
    print(f"   API key: {sync.api_key[:20]}...")
    
    if not sync.test_connection():
        print("❌ HubSpot connection failed")
        print("   Make sure your HUBSPOT_API_KEY is a valid private app access token")
        return
    
    print("✅ HubSpot connection successful!")
    
    if args.test:
        return
    
    # Fetch companies from Chroma
    print("\n" + "-" * 60)
    companies = fetch_chroma_companies(
        tier_filter=args.tier,
        competitors_only=args.competitors
    )
    
    if not companies:
        print("❌ No companies found matching criteria")
        return
    
    # Show summary before syncing
    print("\n" + "-" * 60)
    print("📊 COMPANIES TO SYNC")
    print("-" * 60)
    
    by_tier = {}
    by_category = {}
    for c in companies:
        tier = c.get('tier', 'unknown')
        cat = c.get('category', 'unknown')
        by_tier[tier] = by_tier.get(tier, 0) + 1
        by_category[cat] = by_category.get(cat, 0) + 1
    
    print(f"   Total: {len(companies)}")
    print(f"\n   By Tier:")
    for tier in sorted(by_tier.keys()):
        print(f"      Tier {tier}: {by_tier[tier]}")
    print(f"\n   By Category:")
    for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
        print(f"      {cat}: {count}")
    
    # Sync to HubSpot
    print("\n" + "-" * 60)
    results = sync.sync_all(companies, limit=args.limit)
    
    if "error" in results:
        print(f"\n❌ Error: {results['error']}")
        return
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 SYNC COMPLETE")
    print("=" * 60)
    print(f"   Total processed: {results['total']}")
    print(f"   ✅ Created: {results['created']}")
    print(f"   ⏭️  Already existed: {results['already_exists']}")
    print(f"   ❌ Failed: {results['failed']}")
    
    if results["created_companies"]:
        print(f"\n   New companies created:")
        for name in results["created_companies"][:30]:
            print(f"      • {name}")
        if len(results["created_companies"]) > 30:
            print(f"      ... and {len(results['created_companies']) - 30} more")
    
    if results["failed_companies"]:
        print(f"\n   Failed companies:")
        for name in results["failed_companies"][:20]:
            print(f"      • {name}")
        if len(results["failed_companies"]) > 20:
            print(f"      ... and {len(results['failed_companies']) - 20} more")
    
    print(f"\n🔗 View in HubSpot: https://app.hubspot.com/contacts/YOUR_PORTAL_ID/objects/0-2/views/all/list")


if __name__ == "__main__":
    main()

