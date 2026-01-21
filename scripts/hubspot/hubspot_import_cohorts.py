#!/usr/bin/env python3
"""
HubSpot Cohort Data Import

Imports existing company data into the 4 cohorts:
- Cohort 1: Current Chroma Customers (from tier CSVs - active users)
- Cohort 2: In-Market Companies (from chroma_signal_companies.json)
- Cohort 3: Competitor Customers (from *_COMPANIES_FINAL.json files)
- Cohort 4: SI Partners (from si_program_charts_data.csv)

Usage:
    python3 hubspot_import_cohorts.py                    # Import all cohorts
    python3 hubspot_import_cohorts.py --cohort 1        # Import only Cohort 1
    python3 hubspot_import_cohorts.py --cohort 2        # Import only Cohort 2
    python3 hubspot_import_cohorts.py --cohort 3        # Import only Cohort 3
    python3 hubspot_import_cohorts.py --cohort 4        # Import only Cohort 4
    python3 hubspot_import_cohorts.py --dry-run         # Preview without importing
    python3 hubspot_import_cohorts.py --limit 10        # Import first 10 only
"""

import os
import json
import csv
import requests
import time
import argparse
from datetime import datetime
from typing import Optional, Dict, List, Set
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
HUBSPOT_BASE_URL = "https://api.hubapi.com"
PROJECT_ROOT = Path(__file__).parent

# =============================================================================
# Data Source Files
# =============================================================================

DATA_SOURCES = {
    # Cohort 1: Current Customers (from product signups)
    "cohort_1": {
        "tier1": PROJECT_ROOT / "tier1_enterprise_tech.csv",
        "tier2": PROJECT_ROOT / "tier2_ai_ml_startups.csv",
        "tier3": PROJECT_ROOT / "tier3_tech_agencies.csv",
        "tier4": PROJECT_ROOT / "tier4_other_business.csv",
    },
    # Cohort 2: In-Market (from signal database)
    "cohort_2": {
        "signals": PROJECT_ROOT / "chroma_signal_companies.json",
    },
    # Cohort 3: Competitor Customers
    "cohort_3": {
        "langchain": PROJECT_ROOT / "langchain_COMPANIES_FINAL.json",
        "qdrant": PROJECT_ROOT / "qdrant_COMPANIES_FINAL.json",
        "weaviate": PROJECT_ROOT / "weaviate_COMPANIES_FINAL.json",
        "vespa": PROJECT_ROOT / "vespa_COMPANIES_FINAL.json",
        "pinecone": PROJECT_ROOT / "pinecone_customers_llm.json",
    },
    # Cohort 4: SI Partners
    "cohort_4": {
        "si_partners": PROJECT_ROOT / "si_program_charts_data.csv",
    },
}


# =============================================================================
# HubSpot Client
# =============================================================================

class HubSpotClient:
    """HubSpot API client for importing companies."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or HUBSPOT_API_KEY
        self.enabled = bool(self.api_key)
        self.existing_companies: Dict[str, str] = {}  # domain/name -> id
        
        if not self.enabled:
            print("❌ HUBSPOT_API_KEY not set in .env")
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
                        print(f"   ⚠️ API error: {response.status_code}")
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
    
    def load_existing_companies(self) -> None:
        """Load all existing companies for deduplication."""
        print("   Loading existing companies from HubSpot...")
        after = None
        
        while True:
            endpoint = "/crm/v3/objects/companies?limit=100&properties=domain,name"
            if after:
                endpoint += f"&after={after}"
            
            response = self._request("GET", endpoint)
            if not response:
                break
            
            for company in response.get("results", []):
                props = company.get("properties", {})
                domain = (props.get("domain") or "").lower().strip()
                name = (props.get("name") or "").lower().strip()
                company_id = company.get("id")
                
                if domain:
                    self.existing_companies[domain] = company_id
                if name:
                    self.existing_companies[f"name:{name}"] = company_id
            
            paging = response.get("paging", {})
            after = paging.get("next", {}).get("after")
            if not after:
                break
        
        print(f"   Found {len(self.existing_companies)} existing records")
    
    def create_or_update_company(self, properties: dict) -> tuple:
        """Create or update a company.
        
        Returns: (success, status, company_id)
        """
        domain = properties.get("domain", "").lower().strip()
        name = properties.get("name", "").lower().strip()
        
        # Check if exists
        existing_id = None
        if domain and domain in self.existing_companies:
            existing_id = self.existing_companies[domain]
        elif name and f"name:{name}" in self.existing_companies:
            existing_id = self.existing_companies[f"name:{name}"]
        
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
                # Add to cache
                if domain:
                    self.existing_companies[domain] = company_id
                if name:
                    self.existing_companies[f"name:{name}"] = company_id
                return True, "created", company_id
            return False, "create_failed", None


# =============================================================================
# Data Loaders
# =============================================================================

def normalize_domain(url: str) -> str:
    """Normalize URL to domain."""
    if not url:
        return ""
    domain = url.lower().strip()
    domain = domain.replace("https://", "").replace("http://", "")
    domain = domain.replace("www.", "")
    domain = domain.split("/")[0]
    return domain


def load_cohort_1_data() -> List[dict]:
    """Load Cohort 1: Current Chroma Customers from tier CSVs."""
    companies = []
    seen_companies: Set[str] = set()
    
    # Map tier files to usage tier values (must match HubSpot property options)
    tier_mapping = {
        "tier1": ("enterprise", "active_paid"),
        "tier2": ("growth", "active_free"),
        "tier3": ("starter", "trial"),
        "tier4": ("free", "pipeline"),
    }
    
    for tier_key, (tier_label, status) in tier_mapping.items():
        file_path = DATA_SOURCES["cohort_1"].get(tier_key)
        if not file_path or not file_path.exists():
            print(f"   ⚠️ File not found: {file_path}")
            continue
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    company_name = row.get("enriched_company", row.get("team_name", ""))
                    if not company_name or company_name.lower() in ["default", "", "unknown"]:
                        continue
                    
                    # Skip internal Chroma entries
                    if "chroma" in company_name.lower():
                        continue
                    
                    # Deduplicate
                    key = company_name.lower().strip()
                    if key in seen_companies:
                        continue
                    seen_companies.add(key)
                    
                    companies.append({
                        "name": company_name,
                        "customer_cohort": "cohort_1_current_customer",
                        "chroma_customer_status": status,
                        "chroma_usage_tier": tier_label,  # Now uses correct values: enterprise, growth, starter, free
                        "lead_source": "product_signup",
                        "description": row.get("enriched_description", "")[:500],
                    })
            
            print(f"   Loaded {tier_key}: {len([c for c in companies if c.get('chroma_usage_tier') == tier_label])} companies")
            
        except Exception as e:
            print(f"   ❌ Error loading {file_path}: {e}")
    
    return companies


def load_cohort_2_data() -> List[dict]:
    """Load Cohort 2: In-Market Companies from signal database."""
    companies = []
    
    file_path = DATA_SOURCES["cohort_2"]["signals"]
    if not file_path.exists():
        print(f"   ⚠️ File not found: {file_path}")
        return companies
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        
        for key, company in data.get("companies", {}).items():
            company_name = company.get("company_name", "")
            if not company_name:
                continue
            
            # Map signal strength (must match HubSpot options: high, medium, low)
            signal_strength = company.get("signal_strength", "medium")
            if signal_strength == "high":
                strength_value = "high"
            elif signal_strength == "medium":
                strength_value = "medium"
            else:
                strength_value = "low"
            
            # Map tier to AI hiring status
            tier = company.get("tier", "3")
            if tier == "1":
                hiring_status = "actively_hiring_high"
            elif tier == "2":
                hiring_status = "hiring"
            else:
                hiring_status = "jobs_detected"
            
            # Determine company type
            category = company.get("category", "").lower()
            if "startup" in category or "ai" in category:
                company_type = "ai_native_startup"
            elif "enterprise" in category:
                company_type = "enterprise_ai"
            else:
                company_type = "tech_adding_ai"
            
            # Map use case to valid options
            use_case_raw = company.get("use_case", "").lower()
            use_case_value = ""
            if "rag" in use_case_raw or "retrieval" in use_case_raw:
                use_case_value = "rag"
            elif "agent" in use_case_raw:
                use_case_value = "agent"
            elif "search" in use_case_raw:
                use_case_value = "search"
            elif "chat" in use_case_raw or "copilot" in use_case_raw:
                use_case_value = "chatbot"
            elif "document" in use_case_raw or "doc" in use_case_raw:
                use_case_value = "doc_analysis"
            elif "code" in use_case_raw:
                use_case_value = "code_search"
            
            # Map signal source to valid options
            source_type = company.get("source_type", "").lower()
            if source_type == "youtube":
                signal_source = "inbound"  # Map youtube to inbound
            elif source_type in ["sumble", "reodev", "linkedin", "factors", "conference", "inbound", "referral"]:
                signal_source = source_type
            else:
                signal_source = "inbound"
            
            company_data = {
                "name": company_name,
                "domain": normalize_domain(company.get("website", "")),
                "customer_cohort": "cohort_2_in_market",
                "signal_strength": strength_value,
                "ai_hiring_status": hiring_status,
                "company_type": company_type,
                "lead_source": "chroma_signal",
            }
            
            # Only add optional fields if they have valid values
            if use_case_value:
                company_data["use_case_detected"] = use_case_value
            if signal_source:
                company_data["signal_source"] = signal_source
            
            companies.append(company_data)
        
        print(f"   Loaded {len(companies)} in-market companies")
        
    except Exception as e:
        print(f"   ❌ Error loading signal data: {e}")
    
    return companies


def load_cohort_3_data() -> List[dict]:
    """Load Cohort 3: Competitor Customers from JSON files."""
    companies = []
    seen_companies: Set[str] = set()
    
    for competitor, file_path in DATA_SOURCES["cohort_3"].items():
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
            
            count = 0
            for item in items:
                if isinstance(item, str):
                    company_name = item
                    use_case = ""
                elif isinstance(item, dict):
                    company_name = item.get("company_name", item.get("name", ""))
                    use_case = item.get("use_case", item.get("context", ""))
                else:
                    continue
                
                if not company_name:
                    continue
                
                # Deduplicate
                key = company_name.lower().strip()
                if key in seen_companies:
                    continue
                seen_companies.add(key)
                
                companies.append({
                    "name": company_name,
                    "customer_cohort": "cohort_3_competitor",
                    "current_vector_db": competitor,
                    "competitor_source_channel": "youtube" if "youtube" in str(file_path).lower() else "case_study",
                    "competitor_relationship_status": "unknown",
                    "follow_up_cadence": "monthly",
                    "use_case_detected": use_case[:200] if use_case else "",
                    "lead_source": "competitor_research",
                })
                count += 1
            
            print(f"   Loaded {competitor}: {count} companies")
            
        except Exception as e:
            print(f"   ❌ Error loading {file_path}: {e}")
    
    return companies


def load_cohort_4_data() -> List[dict]:
    """Load Cohort 4: SI Partners from CSV."""
    companies = []
    
    file_path = DATA_SOURCES["cohort_4"]["si_partners"]
    if not file_path.exists():
        print(f"   ⚠️ File not found: {file_path}")
        return companies
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Parse the specific format of si_program_charts_data.csv
        # Look for the "RECOMMENDED PARTNER TIERS" section
        lines = content.split("\n")
        in_partners_section = False
        
        for line in lines:
            if "RECOMMENDED PARTNER TIERS" in line:
                in_partners_section = True
                continue
            
            if in_partners_section and line.strip():
                parts = line.split(",")
                if len(parts) >= 3 and parts[0].startswith("Tier"):
                    tier = parts[0].strip()
                    company_name = parts[1].strip()
                    
                    if not company_name or company_name == "Company":
                        continue
                    
                    # Map tier to partner tier
                    if "Strategic" in tier or "Tier 1" in tier:
                        partner_tier = "gold"
                        partner_status = "active_signed"
                    elif "Technology" in tier or "Tier 2" in tier:
                        partner_tier = "silver"
                        partner_status = "signed_up"
                    else:
                        partner_tier = "bronze"
                        partner_status = "prospect"
                    
                    # Determine SI type
                    major_sis = ["infosys", "cognizant", "deloitte", "ibm", "accenture", 
                                 "tcs", "wipro", "capgemini", "mckinsey", "thoughtworks", 
                                 "publicis", "epam", "ntt"]
                    
                    if any(si in company_name.lower() for si in major_sis):
                        si_type = "global_si"
                    else:
                        si_type = "boutique_ai"
                    
                    companies.append({
                        "name": company_name,
                        "customer_cohort": "cohort_4_si_partner",
                        "si_partner_status": partner_status,
                        "si_partner_tier": partner_tier,
                        "si_company_type": si_type,
                        "lead_source": "si_referral",
                    })
        
        print(f"   Loaded {len(companies)} SI partners")
        
    except Exception as e:
        print(f"   ❌ Error loading SI data: {e}")
    
    return companies


# =============================================================================
# Import Functions
# =============================================================================

def import_cohort(client: HubSpotClient, companies: List[dict], 
                  cohort_name: str, dry_run: bool = False, limit: int = None) -> dict:
    """Import companies for a cohort."""
    results = {
        "cohort": cohort_name,
        "total": len(companies),
        "created": 0,
        "updated": 0,
        "failed": 0,
    }
    
    if limit:
        companies = companies[:limit]
        results["total"] = len(companies)
    
    if not companies:
        print(f"   No companies to import for {cohort_name}")
        return results
    
    print(f"\n📤 Importing {len(companies)} companies for {cohort_name}...")
    
    if dry_run:
        print("   [DRY RUN] Would import:")
        for c in companies[:10]:
            print(f"      • {c.get('name', 'Unknown')}")
        if len(companies) > 10:
            print(f"      ... and {len(companies) - 10} more")
        return results
    
    for i, company in enumerate(companies):
        name = company.get("name", "Unknown")
        
        # Build properties
        properties = {
            "name": name,
            "lifecyclestage": "lead",
        }
        
        # Add all cohort-specific properties
        for key, value in company.items():
            if key != "name" and value:
                properties[key] = str(value) if not isinstance(value, str) else value
        
        success, status, company_id = client.create_or_update_company(properties)
        
        if status == "created":
            results["created"] += 1
            if results["created"] <= 10:
                print(f"   [{i+1}/{len(companies)}] ✅ {name} - created")
        elif status == "updated":
            results["updated"] += 1
            if results["updated"] <= 5:
                print(f"   [{i+1}/{len(companies)}] 🔄 {name} - updated")
        else:
            results["failed"] += 1
            print(f"   [{i+1}/{len(companies)}] ❌ {name} - {status}")
        
        # Rate limiting
        time.sleep(0.1)
    
    return results


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Import company data into HubSpot cohorts")
    parser.add_argument("--cohort", type=int, choices=[1, 2, 3, 4],
                        help="Import only specific cohort (1-4)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without importing")
    parser.add_argument("--limit", type=int,
                        help="Limit number of companies per cohort")
    args = parser.parse_args()
    
    print("=" * 70)
    print("📥 HUBSPOT COHORT DATA IMPORT")
    print("=" * 70)
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
    
    # Load existing companies for deduplication
    if not args.dry_run:
        client.load_existing_companies()
    
    all_results = []
    
    # Import each cohort
    cohorts_to_import = [args.cohort] if args.cohort else [1, 2, 3, 4]
    
    for cohort_num in cohorts_to_import:
        print(f"\n{'=' * 70}")
        
        if cohort_num == 1:
            print("🔴 COHORT 1: Current Chroma Customers")
            print("=" * 70)
            companies = load_cohort_1_data()
            results = import_cohort(client, companies, "Cohort 1: Current Customers", 
                                   args.dry_run, args.limit)
            
        elif cohort_num == 2:
            print("🟠 COHORT 2: In-Market Companies")
            print("=" * 70)
            companies = load_cohort_2_data()
            results = import_cohort(client, companies, "Cohort 2: In-Market", 
                                   args.dry_run, args.limit)
            
        elif cohort_num == 3:
            print("🟡 COHORT 3: Competitor Customers")
            print("=" * 70)
            companies = load_cohort_3_data()
            results = import_cohort(client, companies, "Cohort 3: Competitors", 
                                   args.dry_run, args.limit)
            
        elif cohort_num == 4:
            print("🟢 COHORT 4: SI Partners")
            print("=" * 70)
            companies = load_cohort_4_data()
            results = import_cohort(client, companies, "Cohort 4: SI Partners", 
                                   args.dry_run, args.limit)
        
        all_results.append(results)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 IMPORT SUMMARY")
    print("=" * 70)
    
    total_created = sum(r["created"] for r in all_results)
    total_updated = sum(r["updated"] for r in all_results)
    total_failed = sum(r["failed"] for r in all_results)
    
    for r in all_results:
        print(f"\n   {r['cohort']}:")
        print(f"      Total: {r['total']}")
        print(f"      ✅ Created: {r['created']}")
        print(f"      🔄 Updated: {r['updated']}")
        print(f"      ❌ Failed: {r['failed']}")
    
    print(f"\n   GRAND TOTAL:")
    print(f"      ✅ Created: {total_created}")
    print(f"      🔄 Updated: {total_updated}")
    print(f"      ❌ Failed: {total_failed}")
    
    print(f"\n   Completed: {datetime.now().isoformat()}")
    print("\n🔗 View in HubSpot: https://app.hubspot.com")


if __name__ == "__main__":
    main()

