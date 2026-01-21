#!/usr/bin/env python3
"""
Sync HubSpot Cohort Data to Attio CRM

Syncs all companies and contacts from HubSpot with their cohort assignments
and metadata to Attio CRM.

This script:
1. Pulls all companies from HubSpot with cohort data
2. Maps HubSpot properties to Attio fields
3. Creates/updates companies in Attio
4. Adds to appropriate Attio lists based on cohort

Usage:
    python sync_hubspot_to_attio.py                    # Full sync
    python sync_hubspot_to_attio.py --cohort 1        # Sync only Cohort 1
    python sync_hubspot_to_attio.py --cohort 2        # Sync only Cohort 2
    python sync_hubspot_to_attio.py --dry-run         # Preview without syncing
    python sync_hubspot_to_attio.py --limit 50        # Limit companies
    python sync_hubspot_to_attio.py --test            # Test connections
"""

import os
import json
import requests
import time
import argparse
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# Configuration
# =============================================================================

HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
HUBSPOT_BASE_URL = "https://api.hubapi.com"

ATTIO_API_KEY = os.getenv("ATTIO_API_KEY")
ATTIO_BASE_URL = "https://api.attio.com/v2"
ATTIO_WORKSPACE_SLUG = "chromadb"

# Attio List IDs for each cohort (created via API)
ATTIO_LISTS = {
    "cohort_1_current_customer": os.getenv("ATTIO_LIST_COHORT_1", "645fb022-ddfc-4328-87d6-9e94e3099d85"),
    "cohort_2_in_market": os.getenv("ATTIO_LIST_COHORT_2", "018c125b-fc34-47d5-a2e3-d71c9fec37e1"),
    "cohort_3_competitor": os.getenv("ATTIO_LIST_COHORT_3", "bafbc7af-8085-44ff-b61c-3d4813fb7fc8"),
    "cohort_4_si_partner": os.getenv("ATTIO_LIST_COHORT_4", "8658c141-132f-4fe8-87d5-f2ec765b9d1f"),
}

# HubSpot properties to fetch
HUBSPOT_COMPANY_PROPERTIES = [
    "name",
    "domain",
    "description",
    "industry",
    "numberofemployees",
    "annualrevenue",
    "city",
    "state",
    "country",
    "linkedin_company_page",
    # Custom cohort properties
    "customer_cohort",
    "chroma_customer_status",
    "chroma_cloud_mrr",
    "chroma_expansion_potential",
    "pipeline_stage",
    "in_market_signals",
    "ai_hiring_status",
    "ai_job_count",
    "company_type",
    "use_case_detected",
    "signal_strength",
    "signal_source",
    "current_vector_db",
    "competitor_source_channel",
    "competitor_relationship_status",
    "si_partner_status",
    "si_partner_tier",
    "lead_source",
    "q1_revenue_potential",
    "chroma_usage_tier",
]

# =============================================================================
# Property Mapping: HubSpot -> Attio
# =============================================================================

PROPERTY_MAPPING = {
    # Basic company info
    "name": "name",
    "domain": "domains",
    "description": "description",
    "industry": "industry",
    "numberofemployees": "employee_count",
    "annualrevenue": "annual_revenue",
    "linkedin_company_page": "company_linkedin_url",
    
    # Cohort & segmentation
    "customer_cohort": "customer_segment",  # Maps to customer_segment in Attio
    "company_type": "company_type",
    
    # Technographics
    "current_vector_db": "vector_db_competitor",
    "use_case_detected": "use_case_category",
    
    # Intent & engagement
    "signal_strength": "engagement_score",  # Will need transformation
    "ai_hiring_status": "intent_signals",
    "ai_job_count": "engagement_score",
    
    # GTM motion
    "lead_source": "lead_source",
    "pipeline_stage": "sales_stage",
    
    # Operations
    "q1_revenue_potential": "account_tier",
    "chroma_usage_tier": "account_tier",
}

# Value mappings for select fields
COHORT_TO_SEGMENT = {
    "cohort_1_current_customer": "Enterprise",  # Active customers
    "cohort_2_in_market": "Mid-Market",  # In-market prospects
    "cohort_3_competitor": "Strategic",  # Competitor customers
    "cohort_4_si_partner": "Strategic",  # SI Partners
}

SIGNAL_STRENGTH_TO_SCORE = {
    "high": 80,
    "medium": 50,
    "low": 20,
}

LEAD_SOURCE_MAPPING = {
    "product_signup": "Inbound - Website",
    "chroma_signal": "Outbound - LinkedIn",
    "competitor_intel": "Other",
    "si_program": "Partner Referral",
    "referral": "Partner Referral",
    "conference": "Event/Conference",
}

VECTOR_DB_MAPPING = {
    "pinecone": "Pinecone",
    "weaviate": "Weaviate",
    "qdrant": "Qdrant",
    "milvus": "Milvus",
    "elasticsearch": "Elasticsearch",
    "opensearch": "OpenSearch",
    "pgvector": "pgvector",
    "none": "None",
}


# =============================================================================
# HubSpot Client
# =============================================================================

class HubSpotClient:
    """Client for HubSpot API."""
    
    def __init__(self):
        self.api_key = HUBSPOT_API_KEY
        self.enabled = bool(self.api_key)
        if self.enabled:
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
            else:
                raise ValueError(f"Unknown method: {method}")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", 10))
                print(f"   ⏳ Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                return self._request(method, endpoint, json_data)
            else:
                print(f"   HubSpot API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   HubSpot request failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test HubSpot API connection."""
        response = self._request("GET", "/crm/v3/objects/companies?limit=1")
        return response is not None
    
    def get_all_companies(self, cohort_filter: str = None) -> List[dict]:
        """Get all companies from HubSpot with cohort data."""
        companies = []
        after = None
        properties = ",".join(HUBSPOT_COMPANY_PROPERTIES)
        
        while True:
            endpoint = f"/crm/v3/objects/companies?limit=100&properties={properties}"
            if after:
                endpoint += f"&after={after}"
            
            response = self._request("GET", endpoint)
            if not response:
                break
            
            for company in response.get("results", []):
                props = company.get("properties", {})
                company_cohort = props.get("customer_cohort", "")
                
                # Filter by cohort if specified
                if cohort_filter and company_cohort != cohort_filter:
                    continue
                
                companies.append({
                    "id": company.get("id"),
                    "properties": props
                })
            
            paging = response.get("paging", {})
            after = paging.get("next", {}).get("after")
            if not after:
                break
        
        return companies


# =============================================================================
# Attio Client
# =============================================================================

class AttioClient:
    """Client for Attio API."""
    
    def __init__(self):
        self.api_key = ATTIO_API_KEY
        self.enabled = bool(self.api_key)
        if self.enabled:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        self.company_cache = {}  # domain -> record_id
    
    def _request(self, method: str, endpoint: str, json_data: dict = None) -> Optional[dict]:
        """Make API request to Attio."""
        url = f"{ATTIO_BASE_URL}/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=json_data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=json_data)
            elif method == "PATCH":
                response = requests.patch(url, headers=self.headers, json=json_data)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 429:
                print("   ⏳ Rate limited, waiting 5s...")
                time.sleep(5)
                return self._request(method, endpoint, json_data)
            else:
                # Don't print every error, just return None
                return None
                
        except Exception as e:
            print(f"   Attio request failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test Attio API connection."""
        response = self._request("POST", "objects/companies/records/query", {"limit": 1})
        return response is not None
    
    def find_company_by_domain(self, domain: str) -> Optional[str]:
        """Find company by domain, return record_id."""
        if not domain:
            return None
        
        # Check cache first
        if domain in self.company_cache:
            return self.company_cache[domain]
        
        response = self._request(
            "POST",
            "objects/companies/records/query",
            {"filter": {"domains": {"$contains": domain}}}
        )
        
        if response and response.get("data"):
            record_id = response["data"][0].get("id", {}).get("record_id")
            self.company_cache[domain] = record_id
            return record_id
        
        return None
    
    def find_company_by_name(self, name: str) -> Optional[str]:
        """Find company by name, return record_id."""
        if not name:
            return None
        
        response = self._request(
            "POST",
            "objects/companies/records/query",
            {"filter": {"name": {"$contains": name}}}
        )
        
        if response and response.get("data"):
            return response["data"][0].get("id", {}).get("record_id")
        
        return None
    
    def create_company(self, values: dict) -> Optional[str]:
        """Create a new company in Attio."""
        response = self._request(
            "POST",
            "objects/companies/records",
            {"data": {"values": values}}
        )
        
        if response and response.get("data"):
            record_id = response["data"].get("id", {}).get("record_id")
            # Cache the domain if present
            if "domains" in values and values["domains"]:
                domain = values["domains"][0].get("domain", "")
                if domain:
                    self.company_cache[domain] = record_id
            return record_id
        
        return None
    
    def update_company(self, record_id: str, values: dict) -> bool:
        """Update an existing company in Attio."""
        response = self._request(
            "PATCH",
            f"objects/companies/records/{record_id}",
            {"data": {"values": values}}
        )
        return response is not None
    
    def add_to_list(self, list_id: str, record_id: str, entry_values: dict = None) -> bool:
        """Add a company to an Attio list."""
        if not list_id:
            return False
        
        response = self._request(
            "POST",
            f"lists/{list_id}/entries",
            {
                "data": {
                    "parent_object": "companies",
                    "parent_record_id": record_id,
                    "entry_values": entry_values or {}
                }
            }
        )
        return response is not None


# =============================================================================
# Sync Logic
# =============================================================================

def transform_hubspot_to_attio(hubspot_props: dict) -> dict:
    """Transform HubSpot properties to Attio values format."""
    attio_values = {}
    
    # Company name (required)
    name = hubspot_props.get("name", "")
    if name:
        attio_values["name"] = [{"value": name}]
    
    # Domain
    domain = hubspot_props.get("domain", "")
    if domain:
        # Clean domain
        domain = domain.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
        attio_values["domains"] = [{"domain": domain}]
    
    # Description
    description = hubspot_props.get("description", "")
    if description:
        attio_values["description"] = [{"value": description[:1000]}]
    
    # Employee count
    employees = hubspot_props.get("numberofemployees", "")
    if employees:
        try:
            attio_values["employee_count"] = [{"value": int(employees)}]
        except:
            pass
    
    # LinkedIn URL
    linkedin = hubspot_props.get("linkedin_company_page", "")
    if linkedin:
        attio_values["company_linkedin_url"] = [{"value": linkedin}]
    
    # Build a rich description with cohort info
    cohort = hubspot_props.get("customer_cohort", "")
    cohort_info = []
    
    if cohort:
        cohort_labels = {
            "cohort_1_current_customer": "🔴 Cohort 1: Current Customer",
            "cohort_2_in_market": "🟠 Cohort 2: In-Market",
            "cohort_3_competitor": "🟡 Cohort 3: Competitor Customer",
            "cohort_4_si_partner": "🟢 Cohort 4: SI Partner",
        }
        cohort_info.append(f"Cohort: {cohort_labels.get(cohort, cohort)}")
    
    # Add status info based on cohort
    if cohort == "cohort_1_current_customer":
        status = hubspot_props.get("chroma_customer_status", "")
        if status:
            cohort_info.append(f"Status: {status}")
        mrr = hubspot_props.get("chroma_cloud_mrr", "")
        if mrr:
            cohort_info.append(f"MRR: ${mrr}")
    
    elif cohort == "cohort_2_in_market":
        signals = hubspot_props.get("in_market_signals", "")
        if signals:
            cohort_info.append(f"Signals: {signals}")
        hiring = hubspot_props.get("ai_hiring_status", "")
        if hiring:
            cohort_info.append(f"Hiring: {hiring}")
        use_case = hubspot_props.get("use_case_detected", "")
        if use_case:
            cohort_info.append(f"Use Case: {use_case}")
    
    elif cohort == "cohort_3_competitor":
        vector_db = hubspot_props.get("current_vector_db", "")
        if vector_db:
            cohort_info.append(f"Current Vector DB: {vector_db}")
        rel_status = hubspot_props.get("competitor_relationship_status", "")
        if rel_status:
            cohort_info.append(f"Relationship: {rel_status}")
    
    elif cohort == "cohort_4_si_partner":
        partner_status = hubspot_props.get("si_partner_status", "")
        if partner_status:
            cohort_info.append(f"Partner Status: {partner_status}")
        partner_tier = hubspot_props.get("si_partner_tier", "")
        if partner_tier:
            cohort_info.append(f"Partner Tier: {partner_tier}")
    
    # Add lead source
    lead_source = hubspot_props.get("lead_source", "")
    if lead_source:
        cohort_info.append(f"Source: {lead_source}")
    
    # Add Q1 potential
    q1_potential = hubspot_props.get("q1_revenue_potential", "")
    if q1_potential:
        cohort_info.append(f"Q1 Potential: {q1_potential}")
    
    # Combine into notes
    if cohort_info:
        notes = "\n".join(cohort_info)
        if description:
            notes = f"{description}\n\n---\n{notes}"
        attio_values["description"] = [{"value": notes[:2000]}]
    
    return attio_values


def sync_company(hubspot: HubSpotClient, attio: AttioClient, 
                 company: dict, dry_run: bool = False) -> Tuple[bool, str]:
    """Sync a single company from HubSpot to Attio."""
    props = company.get("properties", {})
    name = props.get("name", "")
    domain = props.get("domain", "")
    cohort = props.get("customer_cohort", "")
    
    if not name:
        return False, "no_name"
    
    # Transform properties
    attio_values = transform_hubspot_to_attio(props)
    
    if dry_run:
        return True, "dry_run"
    
    # Try to find existing company
    record_id = None
    if domain:
        record_id = attio.find_company_by_domain(domain)
    if not record_id:
        record_id = attio.find_company_by_name(name)
    
    # Create or update
    if record_id:
        success = attio.update_company(record_id, attio_values)
        status = "updated" if success else "update_failed"
    else:
        record_id = attio.create_company(attio_values)
        status = "created" if record_id else "create_failed"
    
    # Add to cohort list if we have a list ID and record_id
    if record_id and cohort and ATTIO_LISTS.get(cohort):
        list_id = ATTIO_LISTS[cohort]
        attio.add_to_list(list_id, record_id)
    
    return record_id is not None, status


def sync_all(hubspot: HubSpotClient, attio: AttioClient,
             cohort_filter: str = None, dry_run: bool = False, 
             limit: int = None) -> dict:
    """Sync all companies from HubSpot to Attio."""
    
    print("\n📥 Fetching companies from HubSpot...")
    companies = hubspot.get_all_companies(cohort_filter)
    print(f"   Found {len(companies)} companies")
    
    if limit:
        companies = companies[:limit]
        print(f"   Limited to {len(companies)} companies")
    
    results = {
        "total": len(companies),
        "created": 0,
        "updated": 0,
        "failed": 0,
        "by_cohort": {
            "cohort_1_current_customer": 0,
            "cohort_2_in_market": 0,
            "cohort_3_competitor": 0,
            "cohort_4_si_partner": 0,
            "unassigned": 0,
        }
    }
    
    print(f"\n📤 Syncing to Attio{'  [DRY RUN]' if dry_run else ''}...")
    
    for i, company in enumerate(companies):
        props = company.get("properties", {})
        name = props.get("name", "Unknown")
        cohort = props.get("customer_cohort", "unassigned")
        
        if not cohort:
            cohort = "unassigned"
        
        success, status = sync_company(hubspot, attio, company, dry_run)
        
        # Update cohort count
        if cohort in results["by_cohort"]:
            results["by_cohort"][cohort] += 1
        else:
            results["by_cohort"]["unassigned"] += 1
        
        # Update status counts
        if success:
            if status == "created":
                results["created"] += 1
                if results["created"] <= 10:
                    print(f"   [{i+1}/{len(companies)}] ✅ {name} - created")
            elif status == "updated":
                results["updated"] += 1
                if results["updated"] <= 5:
                    print(f"   [{i+1}/{len(companies)}] 🔄 {name} - updated")
            elif status == "dry_run":
                if i < 10:
                    print(f"   [{i+1}/{len(companies)}] 🔍 {name} - would sync ({cohort})")
        else:
            results["failed"] += 1
            if results["failed"] <= 5:
                print(f"   [{i+1}/{len(companies)}] ❌ {name} - {status}")
        
        # Rate limiting
        if not dry_run:
            time.sleep(0.2)
    
    return results


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Sync HubSpot cohort data to Attio")
    parser.add_argument("--cohort", type=int, choices=[1, 2, 3, 4],
                        help="Sync only specific cohort (1-4)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without syncing")
    parser.add_argument("--limit", type=int,
                        help="Limit number of companies to sync")
    parser.add_argument("--test", action="store_true",
                        help="Test connections only")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🔄 HUBSPOT → ATTIO COHORT SYNC")
    print("=" * 70)
    print(f"   Started: {datetime.now().isoformat()}")
    
    # Initialize clients
    hubspot = HubSpotClient()
    attio = AttioClient()
    
    # Check configurations
    if not hubspot.enabled:
        print("❌ HUBSPOT_API_KEY not set in .env")
        return
    
    if not attio.enabled:
        print("❌ ATTIO_API_KEY not set in .env")
        return
    
    # Test connections
    print("\n🔗 Testing connections...")
    
    if not hubspot.test_connection():
        print("❌ HubSpot connection failed")
        return
    print("   ✅ HubSpot connected")
    
    if not attio.test_connection():
        print("❌ Attio connection failed")
        return
    print("   ✅ Attio connected")
    
    if args.test:
        print("\n✅ Connection tests passed!")
        return
    
    # Determine cohort filter
    cohort_filter = None
    if args.cohort:
        cohort_map = {
            1: "cohort_1_current_customer",
            2: "cohort_2_in_market",
            3: "cohort_3_competitor",
            4: "cohort_4_si_partner",
        }
        cohort_filter = cohort_map.get(args.cohort)
        print(f"\n🎯 Filtering to Cohort {args.cohort}: {cohort_filter}")
    
    # Run sync
    results = sync_all(
        hubspot, attio,
        cohort_filter=cohort_filter,
        dry_run=args.dry_run,
        limit=args.limit
    )
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SYNC SUMMARY")
    print("=" * 70)
    print(f"   Total processed: {results['total']}")
    print(f"   ✅ Created: {results['created']}")
    print(f"   🔄 Updated: {results['updated']}")
    print(f"   ❌ Failed: {results['failed']}")
    
    print("\n   By Cohort:")
    cohort_labels = {
        "cohort_1_current_customer": "🔴 Cohort 1: Current Customers",
        "cohort_2_in_market": "🟠 Cohort 2: In-Market",
        "cohort_3_competitor": "🟡 Cohort 3: Competitor Customers",
        "cohort_4_si_partner": "🟢 Cohort 4: SI Partners",
        "unassigned": "⚪ Unassigned",
    }
    for cohort_key, count in results["by_cohort"].items():
        if count > 0:
            label = cohort_labels.get(cohort_key, cohort_key)
            print(f"      {label}: {count}")
    
    print(f"\n   Completed: {datetime.now().isoformat()}")
    print(f"\n🔗 View in Attio: https://app.attio.com/{ATTIO_WORKSPACE_SLUG}/companies")


if __name__ == "__main__":
    main()

