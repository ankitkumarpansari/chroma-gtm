#!/usr/bin/env python3
"""
HubSpot Master Sync - Consolidate All GTM Data into HubSpot

This script orchestrates syncing data from all sources:
1. Chroma Signal Database (companies hiring AI engineers)
2. Deep Research Pipeline (curated target companies)
3. Competitor Customers (Pinecone, Weaviate, Qdrant, etc.)
4. Tiered User Lists (product signups)
5. LinkedIn Target Companies
6. AI Engineer Speakers
7. Dormant Business Users

Usage:
    python hubspot_master_sync.py                    # Sync all sources
    python hubspot_master_sync.py --test             # Test connection only
    python hubspot_master_sync.py --source signal    # Sync specific source
    python hubspot_master_sync.py --source competitors
    python hubspot_master_sync.py --source tiers
    python hubspot_master_sync.py --dry-run          # Preview without syncing
    python hubspot_master_sync.py --report           # Generate sync report
"""

import os
import json
import csv
import requests
import time
import argparse
from datetime import datetime
from typing import Optional, Dict, List, Set
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# =============================================================================
# Configuration
# =============================================================================

HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
HUBSPOT_BASE_URL = "https://api.hubapi.com"

# Project root directory
PROJECT_ROOT = Path(__file__).parent

# Data source files
DATA_SOURCES = {
    "competitors": {
        "langchain": PROJECT_ROOT / "langchain_COMPANIES_FINAL.json",
        "qdrant": PROJECT_ROOT / "qdrant_COMPANIES_FINAL.json",
        "weaviate": PROJECT_ROOT / "weaviate_COMPANIES_FINAL.json",
        "vespa": PROJECT_ROOT / "vespa_COMPANIES_FINAL.json",
        "pinecone": PROJECT_ROOT / "pinecone_customers_llm.json",
    },
    "tiers": {
        "tier1": PROJECT_ROOT / "tier1_enterprise_tech.csv",
        "tier2": PROJECT_ROOT / "tier2_ai_ml_startups.csv",
        "tier3": PROJECT_ROOT / "tier3_tech_agencies.csv",
        "tier4": PROJECT_ROOT / "tier4_other_business.csv",
    },
    "linkedin": PROJECT_ROOT / "LINKEDIN_TARGET_COMPANIES_CONSOLIDATED.json",
    "ai_speakers": PROJECT_ROOT / "ai_engineer_speakers_enriched.json",
    "dormant_users": PROJECT_ROOT / "dormant_business_users_identified.json",
    "chroma_signal": PROJECT_ROOT / "chroma_signal_companies.json",
}

# Source priority for deduplication (higher = preferred)
SOURCE_PRIORITY = {
    "product_signup": 10,
    "chroma_signal": 8,
    "deep_research": 7,
    "competitor_customer": 6,
    "linkedin_sales_nav": 5,
    "ai_speakers": 4,
    "dormant_user": 3,
}


# =============================================================================
# HubSpot API Client
# =============================================================================

class HubSpotClient:
    """HubSpot API client with rate limiting and error handling."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or HUBSPOT_API_KEY
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            print("❌ HUBSPOT_API_KEY not set in .env")
            print("   Get your private app access token from:")
            print("   https://app.hubspot.com/private-apps/YOUR_PORTAL_ID")
        else:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
    
    def _request(self, method: str, endpoint: str, json_data: dict = None, 
                 retries: int = 3) -> Optional[dict]:
        """Make API request with retry logic."""
        if not self.enabled:
            return None
            
        url = f"{HUBSPOT_BASE_URL}{endpoint}"
        
        for attempt in range(retries):
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
                    return {"conflict": True, "response": response.json()}
                elif response.status_code == 429:
                    wait_time = int(response.headers.get("Retry-After", 10))
                    print(f"   ⏳ Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    if attempt == retries - 1:
                        print(f"   ⚠️ API error: {response.status_code} - {response.text[:200]}")
                    return None
                    
            except Exception as e:
                if attempt == retries - 1:
                    print(f"   ❌ Request failed: {e}")
                return None
        
        return None
    
    def test_connection(self) -> bool:
        """Test HubSpot API connection."""
        response = self._request("GET", "/crm/v3/objects/companies?limit=1")
        return response is not None
    
    def get_existing_companies(self) -> Dict[str, str]:
        """Get all existing companies as domain -> id mapping."""
        companies = {}
        after = None
        
        print("   Fetching existing companies from HubSpot...")
        
        while True:
            endpoint = "/crm/v3/objects/companies?limit=100&properties=domain,name"
            if after:
                endpoint += f"&after={after}"
            
            response = self._request("GET", endpoint)
            if not response:
                break
            
            for company in response.get("results", []):
                props = company.get("properties", {})
                domain = props.get("domain", "").lower().strip()
                name = props.get("name", "").lower().strip()
                company_id = company.get("id")
                
                if domain:
                    companies[domain] = company_id
                if name:
                    companies[f"name:{name}"] = company_id
            
            paging = response.get("paging", {})
            after = paging.get("next", {}).get("after")
            if not after:
                break
        
        print(f"   Found {len(companies)} existing records")
        return companies
    
    def create_or_update_company(self, company_data: dict, 
                                  existing_companies: Dict[str, str]) -> tuple:
        """Create or update a company record.
        
        Returns: (success, status, company_id)
        """
        domain = company_data.get("domain", "").lower().strip()
        name = company_data.get("name", "").lower().strip()
        
        # Check if exists
        existing_id = None
        if domain and domain in existing_companies:
            existing_id = existing_companies[domain]
        elif name and f"name:{name}" in existing_companies:
            existing_id = existing_companies[f"name:{name}"]
        
        properties = self._build_properties(company_data)
        
        if existing_id:
            # Update existing
            response = self._request(
                "PATCH",
                f"/crm/v3/objects/companies/{existing_id}",
                {"properties": properties}
            )
            if response:
                return True, "updated", existing_id
            return False, "update_failed", existing_id
        else:
            # Create new
            response = self._request(
                "POST",
                "/crm/v3/objects/companies",
                {"properties": properties}
            )
            if response:
                company_id = response.get("id")
                # Add to existing cache
                if domain:
                    existing_companies[domain] = company_id
                if name:
                    existing_companies[f"name:{name}"] = company_id
                return True, "created", company_id
            return False, "create_failed", None
    
    def _build_properties(self, data: dict) -> dict:
        """Build HubSpot properties from company data."""
        props = {}
        
        # Standard properties
        if data.get("name"):
            props["name"] = data["name"]
        if data.get("domain"):
            props["domain"] = data["domain"]
        if data.get("website"):
            # Extract domain from website
            domain = data["website"].replace("https://", "").replace("http://", "")
            domain = domain.replace("www.", "").split("/")[0]
            props["domain"] = domain
        
        # Build description
        desc_parts = []
        if data.get("category"):
            desc_parts.append(f"Category: {data['category']}")
        if data.get("tier"):
            desc_parts.append(f"Tier: {data['tier']}")
        if data.get("use_case"):
            desc_parts.append(f"Use Case: {data['use_case']}")
        if data.get("signal_strength"):
            desc_parts.append(f"Signal: {data['signal_strength']}")
        if data.get("source_type"):
            desc_parts.append(f"Source: {data['source_type']}")
        if data.get("current_vector_db"):
            desc_parts.append(f"Vector DB: {data['current_vector_db']}")
        if data.get("competitor_source"):
            desc_parts.append(f"Competitor: {data['competitor_source']}")
        if data.get("valuation"):
            desc_parts.append(f"Valuation: {data['valuation']}")
        if data.get("description"):
            desc_parts.append(f"\n{data['description'][:500]}")
        
        desc_parts.append(f"\nSynced: {datetime.now().isoformat()}")
        
        if desc_parts:
            props["description"] = "\n".join(desc_parts)
        
        # Lifecycle stage
        props["lifecyclestage"] = "lead"
        
        # Industry (if available)
        if data.get("industry"):
            props["industry"] = data["industry"]
        
        return props


# =============================================================================
# Data Loaders
# =============================================================================

def normalize_domain(url: str) -> str:
    """Normalize a URL/domain to consistent format."""
    if not url:
        return ""
    domain = url.lower().strip()
    domain = domain.replace("https://", "").replace("http://", "")
    domain = domain.replace("www.", "")
    domain = domain.split("/")[0]
    return domain


def load_chroma_signal_companies() -> List[dict]:
    """Load companies from Chroma Signal JSON file."""
    file_path = DATA_SOURCES["chroma_signal"]
    if not file_path.exists():
        print(f"   ⚠️ File not found: {file_path}")
        return []
    
    with open(file_path, "r") as f:
        data = json.load(f)
    
    companies = []
    for key, company in data.get("companies", {}).items():
        companies.append({
            "name": company.get("company_name", ""),
            "domain": normalize_domain(company.get("website", "")),
            "website": company.get("website", ""),
            "tier": company.get("tier", ""),
            "category": company.get("category", ""),
            "use_case": company.get("use_case", ""),
            "signal_strength": company.get("signal_strength", ""),
            "source_type": "chroma_signal",
            "source_channel": company.get("source_channel", ""),
        })
    
    return companies


def load_competitor_customers() -> List[dict]:
    """Load competitor customer data from JSON files."""
    companies = []
    
    for competitor, file_path in DATA_SOURCES["competitors"].items():
        if not file_path.exists():
            print(f"   ⚠️ File not found: {file_path}")
            continue
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                items = data.get("companies", data.get("customers", []))
                if isinstance(items, dict):
                    items = list(items.values())
            else:
                continue
            
            for item in items:
                if isinstance(item, str):
                    # Simple list of company names
                    companies.append({
                        "name": item,
                        "competitor_source": competitor,
                        "source_type": "competitor_customer",
                        "current_vector_db": competitor,
                    })
                elif isinstance(item, dict):
                    companies.append({
                        "name": item.get("company_name", item.get("name", "")),
                        "domain": normalize_domain(item.get("website", item.get("domain", ""))),
                        "website": item.get("website", ""),
                        "use_case": item.get("use_case", item.get("context", "")),
                        "competitor_source": competitor,
                        "source_type": "competitor_customer",
                        "current_vector_db": competitor,
                    })
            
            print(f"   Loaded {len(items)} companies from {competitor}")
            
        except Exception as e:
            print(f"   ❌ Error loading {file_path}: {e}")
    
    return companies


def load_tiered_users() -> List[dict]:
    """Load tiered user data from CSV files."""
    companies = []
    
    for tier_name, file_path in DATA_SOURCES["tiers"].items():
        if not file_path.exists():
            print(f"   ⚠️ File not found: {file_path}")
            continue
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                tier_companies = []
                
                for row in reader:
                    company_name = row.get("enriched_company", row.get("team_name", ""))
                    if not company_name or company_name == "default":
                        continue
                    
                    tier_companies.append({
                        "name": company_name,
                        "tier": tier_name.replace("tier", "Tier "),
                        "source_type": "product_signup",
                        "description": row.get("enriched_description", ""),
                        "industry": "",  # Could be extracted from description
                    })
                
                # Deduplicate within tier
                seen = set()
                unique = []
                for c in tier_companies:
                    if c["name"].lower() not in seen:
                        seen.add(c["name"].lower())
                        unique.append(c)
                
                companies.extend(unique)
                print(f"   Loaded {len(unique)} companies from {tier_name}")
                
        except Exception as e:
            print(f"   ❌ Error loading {file_path}: {e}")
    
    return companies


def load_linkedin_targets() -> List[dict]:
    """Load LinkedIn target companies."""
    file_path = DATA_SOURCES["linkedin"]
    if not file_path.exists():
        print(f"   ⚠️ File not found: {file_path}")
        return []
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        
        companies = []
        items = data if isinstance(data, list) else data.get("companies", [])
        
        for item in items:
            if isinstance(item, str):
                companies.append({
                    "name": item,
                    "source_type": "linkedin_sales_nav",
                })
            elif isinstance(item, dict):
                companies.append({
                    "name": item.get("company_name", item.get("name", "")),
                    "domain": normalize_domain(item.get("website", item.get("domain", ""))),
                    "source_type": "linkedin_sales_nav",
                })
        
        return companies
        
    except Exception as e:
        print(f"   ❌ Error loading LinkedIn targets: {e}")
        return []


def load_ai_speakers() -> List[dict]:
    """Load AI engineer speaker companies."""
    file_path = DATA_SOURCES["ai_speakers"]
    if not file_path.exists():
        print(f"   ⚠️ File not found: {file_path}")
        return []
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        
        companies = []
        items = data if isinstance(data, list) else data.get("speakers", [])
        
        seen_companies = set()
        for item in items:
            company = item.get("company", "")
            if company and company.lower() not in seen_companies:
                seen_companies.add(company.lower())
                companies.append({
                    "name": company,
                    "source_type": "ai_speakers",
                    "use_case": f"AI Engineer Speaker: {item.get('name', '')}",
                })
        
        return companies
        
    except Exception as e:
        print(f"   ❌ Error loading AI speakers: {e}")
        return []


def load_dormant_users() -> List[dict]:
    """Load dormant business user companies."""
    file_path = DATA_SOURCES["dormant_users"]
    if not file_path.exists():
        print(f"   ⚠️ File not found: {file_path}")
        return []
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        
        companies = []
        items = data if isinstance(data, list) else data.get("users", [])
        
        seen_companies = set()
        for item in items:
            company = item.get("company", item.get("enriched_company", ""))
            if company and company.lower() not in seen_companies:
                seen_companies.add(company.lower())
                companies.append({
                    "name": company,
                    "source_type": "dormant_user",
                    "category": "reactivation_target",
                })
        
        return companies
        
    except Exception as e:
        print(f"   ❌ Error loading dormant users: {e}")
        return []


# =============================================================================
# Deduplication
# =============================================================================

def deduplicate_companies(companies: List[dict]) -> List[dict]:
    """Deduplicate companies, keeping highest priority source."""
    seen = {}  # domain/name -> company data
    
    for company in companies:
        domain = company.get("domain", "").lower().strip()
        name = company.get("name", "").lower().strip()
        source = company.get("source_type", "")
        priority = SOURCE_PRIORITY.get(source, 0)
        
        key = domain if domain else name
        if not key:
            continue
        
        if key in seen:
            existing_priority = SOURCE_PRIORITY.get(seen[key].get("source_type", ""), 0)
            if priority > existing_priority:
                # Merge data, keeping new as primary
                merged = {**seen[key], **company}
                seen[key] = merged
            else:
                # Merge data, keeping existing as primary
                for k, v in company.items():
                    if v and not seen[key].get(k):
                        seen[key][k] = v
        else:
            seen[key] = company
    
    return list(seen.values())


# =============================================================================
# Sync Functions
# =============================================================================

def sync_companies(client: HubSpotClient, companies: List[dict], 
                   source_name: str, dry_run: bool = False) -> dict:
    """Sync a list of companies to HubSpot."""
    results = {
        "source": source_name,
        "total": len(companies),
        "created": 0,
        "updated": 0,
        "failed": 0,
        "skipped": 0,
    }
    
    if not companies:
        print(f"   No companies to sync from {source_name}")
        return results
    
    print(f"\n📤 Syncing {len(companies)} companies from {source_name}...")
    
    if dry_run:
        print("   [DRY RUN] Would sync:")
        for c in companies[:10]:
            print(f"      • {c.get('name', 'Unknown')}")
        if len(companies) > 10:
            print(f"      ... and {len(companies) - 10} more")
        return results
    
    existing = client.get_existing_companies()
    
    for i, company in enumerate(companies):
        name = company.get("name", "Unknown")
        
        if not name or name.lower() in ["unknown", "default", ""]:
            results["skipped"] += 1
            continue
        
        success, status, company_id = client.create_or_update_company(company, existing)
        
        if status == "created":
            results["created"] += 1
            if results["created"] <= 20:  # Only show first 20
                print(f"   [{i+1}/{len(companies)}] ✅ {name} - created")
        elif status == "updated":
            results["updated"] += 1
            if results["updated"] <= 5:  # Only show first 5 updates
                print(f"   [{i+1}/{len(companies)}] 🔄 {name} - updated")
        else:
            results["failed"] += 1
            print(f"   [{i+1}/{len(companies)}] ❌ {name} - {status}")
        
        # Rate limiting
        time.sleep(0.1)
    
    return results


# =============================================================================
# Main Orchestrator
# =============================================================================

def run_full_sync(client: HubSpotClient, sources: List[str] = None, 
                  dry_run: bool = False) -> List[dict]:
    """Run sync for specified sources or all sources."""
    all_results = []
    all_companies = []
    
    # Determine which sources to sync
    if not sources:
        sources = ["signal", "competitors", "tiers", "linkedin", "speakers", "dormant"]
    
    print("\n" + "=" * 60)
    print("📊 LOADING DATA SOURCES")
    print("=" * 60)
    
    # Load data from each source
    if "signal" in sources:
        print("\n📡 Loading Chroma Signal companies...")
        signal_companies = load_chroma_signal_companies()
        print(f"   Loaded {len(signal_companies)} companies")
        all_companies.extend(signal_companies)
    
    if "competitors" in sources:
        print("\n🎯 Loading competitor customers...")
        competitor_companies = load_competitor_customers()
        print(f"   Total: {len(competitor_companies)} companies")
        all_companies.extend(competitor_companies)
    
    if "tiers" in sources:
        print("\n📋 Loading tiered user companies...")
        tier_companies = load_tiered_users()
        print(f"   Total: {len(tier_companies)} companies")
        all_companies.extend(tier_companies)
    
    if "linkedin" in sources:
        print("\n💼 Loading LinkedIn targets...")
        linkedin_companies = load_linkedin_targets()
        print(f"   Loaded {len(linkedin_companies)} companies")
        all_companies.extend(linkedin_companies)
    
    if "speakers" in sources:
        print("\n🎤 Loading AI speaker companies...")
        speaker_companies = load_ai_speakers()
        print(f"   Loaded {len(speaker_companies)} companies")
        all_companies.extend(speaker_companies)
    
    if "dormant" in sources:
        print("\n😴 Loading dormant user companies...")
        dormant_companies = load_dormant_users()
        print(f"   Loaded {len(dormant_companies)} companies")
        all_companies.extend(dormant_companies)
    
    # Deduplicate
    print("\n" + "=" * 60)
    print("🔄 DEDUPLICATING")
    print("=" * 60)
    print(f"   Total before dedup: {len(all_companies)}")
    
    deduped = deduplicate_companies(all_companies)
    print(f"   Total after dedup: {len(deduped)}")
    print(f"   Removed {len(all_companies) - len(deduped)} duplicates")
    
    # Sync to HubSpot
    print("\n" + "=" * 60)
    print("📤 SYNCING TO HUBSPOT")
    print("=" * 60)
    
    results = sync_companies(client, deduped, "All Sources", dry_run)
    all_results.append(results)
    
    return all_results


def generate_report(results: List[dict]) -> None:
    """Generate and print sync report."""
    print("\n" + "=" * 60)
    print("📊 SYNC REPORT")
    print("=" * 60)
    
    total_created = sum(r["created"] for r in results)
    total_updated = sum(r["updated"] for r in results)
    total_failed = sum(r["failed"] for r in results)
    total_skipped = sum(r["skipped"] for r in results)
    total_processed = sum(r["total"] for r in results)
    
    print(f"\n   Total Processed: {total_processed}")
    print(f"   ✅ Created: {total_created}")
    print(f"   🔄 Updated: {total_updated}")
    print(f"   ⏭️  Skipped: {total_skipped}")
    print(f"   ❌ Failed: {total_failed}")
    
    print("\n   By Source:")
    for r in results:
        print(f"      {r['source']}: {r['total']} total, "
              f"{r['created']} created, {r['updated']} updated")
    
    print(f"\n🔗 View in HubSpot: https://app.hubspot.com/contacts/YOUR_PORTAL_ID/objects/0-2/views/all/list")


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Master sync script for HubSpot GTM data consolidation"
    )
    parser.add_argument("--test", action="store_true", 
                        help="Test HubSpot connection only")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview sync without making changes")
    parser.add_argument("--source", type=str, 
                        choices=["signal", "competitors", "tiers", "linkedin", 
                                 "speakers", "dormant", "all"],
                        help="Sync specific source only")
    parser.add_argument("--report", action="store_true",
                        help="Generate data source report without syncing")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔄 HUBSPOT MASTER SYNC")
    print("=" * 60)
    print(f"   Started: {datetime.now().isoformat()}")
    
    # Initialize client
    client = HubSpotClient()
    
    if not client.enabled:
        return
    
    print(f"   API Key: {client.api_key[:20]}...")
    
    # Test connection
    print("\n🔗 Testing HubSpot connection...")
    if not client.test_connection():
        print("❌ HubSpot connection failed")
        return
    print("✅ HubSpot connection successful!")
    
    if args.test:
        return
    
    # Determine sources
    sources = None
    if args.source and args.source != "all":
        sources = [args.source]
    
    # Run sync
    results = run_full_sync(client, sources, dry_run=args.dry_run)
    
    # Generate report
    generate_report(results)
    
    print(f"\n   Completed: {datetime.now().isoformat()}")


if __name__ == "__main__":
    main()

