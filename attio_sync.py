#!/usr/bin/env python3
"""
Attio CRM Integration

Syncs leads from Chroma to Attio CRM.
Creates company records and adds them to the "Companies with RAG Jobs" list.

Setup:
1. Get API key from Attio → Settings → Developers → API Keys
2. Set ATTIO_API_KEY in .env
"""

import os
import requests
import time
from datetime import datetime
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

# Attio Configuration
ATTIO_API_KEY = os.getenv("ATTIO_API_KEY")
ATTIO_BASE_URL = "https://api.attio.com/v2"

# Your "Companies with RAG Jobs" list
ATTIO_LIST_ID = "bfd069d4-31e7-4733-9c0a-a54ea32df817"
ATTIO_WORKSPACE_SLUG = "chromadb"  # Your workspace slug for URLs

# Attribute API slugs for the list
LIST_ATTRIBUTES = {
    "lead_source": "lead_source",
    "industry": "industry",
    "funding": "funding",
    "notes": "notes",
    "stage": "stage",
    "priority": "priority",
}

# Large enterprise companies to IGNORE (unlikely to buy from startups)
IGNORE_LARGE_ENTERPRISES = {
    # Big Tech
    "amazon", "amazon.com", "aws", "amazon web services",
    "microsoft", "microsoft corporation", "azure",
    "google", "google llc", "alphabet", "deepmind",
    "meta", "meta platforms", "facebook",
    "apple", "apple inc",
    "oracle", "oracle corporation",
    "ibm", "international business machines",
    "salesforce", "salesforce inc",
    "adobe", "adobe inc",
    "nvidia", "nvidia corporation",
    "intel", "intel corporation",
    # Data/Cloud Giants
    "databricks", "databricks inc",
    "snowflake", "snowflake inc",
    "palantir", "palantir technologies",
    # Consulting Giants
    "accenture", "accenture plc",
    "deloitte",
    "mckinsey", "mckinsey & company",
    "bcg", "boston consulting",
    "pwc", "pricewaterhousecoopers",
    "ey", "ernst & young", "ernst young",
    "kpmg",
    "tcs", "tata consultancy", "tata consultancy services",
    "infosys", "infosys ltd",
    "wipro",
    "cognizant",
    "capgemini",
    "ntt data",
    "booz allen", "booz allen hamilton",
    # Large Retailers/Consumer
    "walmart", "walmart inc",
    "target",
    "costco",
    "home depot", "the home depot",
    "kroger",
    # Large Finance
    "jpmorgan", "jp morgan", "chase",
    "goldman sachs",
    "morgan stanley",
    "bank of america",
    "wells fargo",
    "capital one",
    "citi", "citibank", "citigroup",
    "geico",
    # Large Healthcare/Pharma
    "johnson & johnson", "j&j",
    "pfizer",
    "merck",
    "eli lilly",
    "bristol-myers", "bristol myers",
    "abbvie",
    "amgen",
    "cvs", "cvs health",
    # Other Large Enterprises
    "disney", "walt disney",
    "comcast",
    "at&t", "att",
    "verizon",
    "general motors", "gm",
    "ford",
    "boeing",
    "3m",
    "ge", "general electric",
    "honeywell",
    "lockheed martin",
    "raytheon",
    "northrop grumman",
    "bosch",
    "siemens",
    "bytedance",
    "openai",
}


def should_ignore_large_enterprise(company_name: str) -> bool:
    """Check if company is a large enterprise we should ignore."""
    company_lower = company_name.lower().strip()
    return any(enterprise in company_lower for enterprise in IGNORE_LARGE_ENTERPRISES)


class AttioSync:
    """Sync leads to Attio CRM."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or ATTIO_API_KEY
        if not self.api_key:
            print("⚠️  ATTIO_API_KEY not set - Attio sync disabled")
            self.enabled = False
        else:
            self.enabled = True
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
    
    def _make_request(self, method: str, endpoint: str, json_data: dict = None) -> dict:
        """Make API request to Attio."""
        url = f"{ATTIO_BASE_URL}{endpoint}"
        
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
            else:
                print(f"   Attio API error: {response.status_code} - {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"   Attio request failed: {e}")
            return None
    
    def find_company_by_name(self, company_name: str) -> Optional[dict]:
        """Search for existing company in Attio."""
        # Use the filter endpoint to search by name
        response = self._make_request(
            "POST",
            "/objects/companies/records/query",
            {
                "filter": {
                    "name": {"$contains": company_name}
                }
            }
        )
        
        if response and response.get("data"):
            return response["data"][0]  # Return first match
        return None
    
    def create_company(self, lead: dict) -> Optional[dict]:
        """
        Create a new company record in Attio.
        
        Args:
            lead: Dictionary with lead info from Chroma
            
        Returns:
            Created company record or None
        """
        if not self.enabled:
            return None
        
        company_name = lead.get("company_name", "")
        if not company_name:
            return None
        
        # Build the values for Attio
        # Note: Attio expects values as arrays of objects
        values = {
            "name": [{"value": company_name}],
        }
        
        # Add website/domain if available - skip job board domains
        website = lead.get("website", "")
        job_board_domains = ["indeed.com", "linkedin.com", "ziprecruiter.com", "glassdoor.com", "dice.com"]
        
        if website:
            domain = website.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
            # Only add domain if it's not a job board
            if not any(jb in domain.lower() for jb in job_board_domains):
                values["domains"] = [{"domain": domain}]
        
        # Add description
        description = lead.get("description", "")
        if description:
            values["description"] = [{"value": description[:1000]}]
        
        # Create the company record
        response = self._make_request(
            "POST",
            "/objects/companies/records",
            {"data": {"values": values}}
        )
        
        return response
    
    def add_to_list(self, company_record_id: str, lead: dict) -> Optional[dict]:
        """
        Add a company to the 'Companies with RAG Jobs' list with attributes.
        
        Args:
            company_record_id: The Attio record ID of the company
            lead: Lead dictionary with metadata
            
        Returns:
            Created list entry or None
        """
        if not self.enabled:
            return None
        
        # Build entry values for the list
        entry_values = {}
        
        # Job Posting URL - separate field (clickable!)
        if lead.get("job_posting_urls"):
            # Get the first URL if there are multiple
            first_url = lead["job_posting_urls"].split(";")[0].strip()
            entry_values["job_posting_url"] = [{"value": first_url}]
        
        # Notes - other metadata
        notes_parts = []
        if lead.get("vector_db_mentioned"):
            notes_parts.append(f"🗄️ Vector DB Tech: {lead['vector_db_mentioned']}")
        if lead.get("job_titles"):
            notes_parts.append(f"💼 Hiring: {lead['job_titles']}")
        if lead.get("headquarters"):
            notes_parts.append(f"📍 Location: {lead['headquarters']}")
        if lead.get("industry"):
            notes_parts.append(f"🏢 Industry: {lead['industry']}")
        if lead.get("description"):
            notes_parts.append(f"\n{lead['description'][:300]}")
        
        if notes_parts:
            entry_values["notes"] = [{"value": "\n".join(notes_parts)}]
        
        # Create list entry with parent_object
        response = self._make_request(
            "POST",
            f"/lists/{ATTIO_LIST_ID}/entries",
            {
                "data": {
                    "parent_object": "companies",
                    "parent_record_id": company_record_id,
                    "entry_values": entry_values
                }
            }
        )
        
        return response
    
    def find_company_record_id(self, company_name: str) -> Optional[str]:
        """Find company and return its record ID."""
        company = self.find_company_by_name(company_name)
        if company:
            return company.get("id", {}).get("record_id")
        return None
    
    def check_if_in_list(self, company_name: str) -> bool:
        """Check if company is already in the list."""
        response = self._make_request(
            "POST",
            f"/lists/{ATTIO_LIST_ID}/entries/query",
            {"limit": 500}
        )
        
        if response and response.get("data"):
            for entry in response["data"]:
                # Get the parent record (company) name
                parent = entry.get("parent_record", {})
                values = parent.get("values", {})
                name_list = values.get("name", [])
                if name_list:
                    existing_name = name_list[0].get("value", "").lower()
                    if company_name.lower() in existing_name or existing_name in company_name.lower():
                        return True
        return False
    
    def sync_lead(self, lead: dict) -> tuple[bool, str, Optional[str]]:
        """
        Sync a single lead to Attio and add to the RAG Jobs list.
        
        Returns:
            (success, message, record_id)
            - record_id can be used to build Attio URL
        """
        if not self.enabled:
            return False, "Attio not configured", None
        
        company_name = lead.get("company_name", "")
        if not company_name:
            return False, "No company name", None
        
        # Check if already in our list
        if self.check_if_in_list(company_name):
            # Still get the record_id for existing companies
            record_id = self.find_company_record_id(company_name)
            return True, "Already in list", record_id
        
        # Check if company exists in Attio
        record_id = self.find_company_record_id(company_name)
        
        if not record_id:
            # Create new company first
            result = self.create_company(lead)
            if result:
                record_id = result.get("data", {}).get("id", {}).get("record_id")
            else:
                return False, "Failed to create company", None
        
        if not record_id:
            return False, "No record ID", None
        
        # Add to the list with notes
        list_entry = self.add_to_list(record_id, lead)
        if list_entry:
            return True, "Added to list", record_id
        else:
            return False, "Failed to create", record_id
    
    @staticmethod
    def get_attio_url(record_id: str) -> str:
        """
        Build the Attio URL for a company record.
        
        Args:
            record_id: The Attio record ID
            
        Returns:
            Full Attio URL to view the company
        """
        if not record_id:
            return ""
        # Attio company URL format: https://app.attio.com/{workspace_slug}/companies/{record_id}
        return f"https://app.attio.com/{ATTIO_WORKSPACE_SLUG}/companies/{record_id}"
    
    def sync_leads_batch(self, leads: List[dict], delay: float = 0.5) -> dict:
        """
        Sync multiple leads to Attio.
        
        Args:
            leads: List of lead dictionaries
            delay: Delay between requests to avoid rate limiting
            
        Returns:
            Summary dict with counts and record_ids
        """
        if not self.enabled:
            print("⚠️  Attio not configured")
            return {"error": "Not configured"}
        
        results = {
            "total": len(leads),
            "created": 0,
            "existing": 0,
            "failed": 0,
            "companies": [],
            "record_ids": {}  # company_name -> record_id mapping
        }
        
        print(f"📤 Syncing {len(leads)} leads to Attio...")
        
        for i, lead in enumerate(leads, 1):
            company_name = lead.get("company_name", "Unknown")
            
            success, message, record_id = self.sync_lead(lead)
            
            # Store record_id for all successful syncs
            if record_id:
                results["record_ids"][company_name] = record_id
            
            if success:
                if "exists" in message.lower() or "already" in message.lower():
                    results["existing"] += 1
                    print(f"   [{i}/{len(leads)}] ⏭️  {company_name} - {message}")
                else:
                    results["created"] += 1
                    results["companies"].append(company_name)
                    print(f"   [{i}/{len(leads)}] ✅ {company_name} - {message}")
            else:
                results["failed"] += 1
                print(f"   [{i}/{len(leads)}] ❌ {company_name} - {message}")
            
            time.sleep(delay)  # Rate limiting
        
        return results


def sync_all_from_chroma():
    """Sync all leads from Chroma hiring_leads collection to Attio 'Companies with RAG Jobs' list."""
    import chromadb
    
    print("=" * 60)
    print("SYNC LEADS TO ATTIO 'Companies with RAG Jobs' LIST")
    print("=" * 60)
    print(f"List ID: {ATTIO_LIST_ID}")
    
    # Connect to Chroma
    print("\n🔗 Connecting to Chroma...")
    client = chromadb.CloudClient(
        api_key='ck-2i6neFLSKhd5pEqLP3jZKUkG6tX3yo4RVUZEeRxs4fHm',
        tenant='aa8f571e-03dc-4cd8-b888-723bd00b83f0',
        database='customer'
    )
    collection = client.get_collection('hiring_leads')
    
    # Get all leads
    results = collection.get()
    leads = results.get('metadatas', [])
    print(f"✅ Found {len(leads)} leads in Chroma")
    
    # Filter out vector DB companies AND large enterprises
    from slack_lead_notifier import should_ignore_company
    
    filtered_leads = []
    ignored_competitors = 0
    ignored_enterprises = 0
    
    for lead in leads:
        company = lead.get('company_name', '')
        if should_ignore_company(company):
            ignored_competitors += 1
        elif should_ignore_large_enterprise(company):
            ignored_enterprises += 1
        else:
            filtered_leads.append(lead)
    
    print(f"🚫 Filtered out {ignored_competitors} vector DB competitors")
    print(f"🏢 Filtered out {ignored_enterprises} large enterprises")
    print(f"📋 {len(filtered_leads)} qualified leads remaining")
    
    # Sync to Attio
    print()
    attio = AttioSync()
    results = attio.sync_leads_batch(filtered_leads, delay=0.3)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SYNC COMPLETE")
    print("=" * 60)
    print(f"   Total processed: {results['total']}")
    print(f"   ✅ Created: {results['created']}")
    print(f"   ⏭️  Already existed: {results['existing']}")
    print(f"   ❌ Failed: {results['failed']}")
    
    if results['companies']:
        print(f"\n   New companies in Attio:")
        for company in results['companies'][:20]:
            print(f"      • {company}")
        if len(results['companies']) > 20:
            print(f"      ... and {len(results['companies']) - 20} more")
    
    return results


def test_attio_connection():
    """Test Attio API connection."""
    print("Testing Attio connection...")
    
    if not ATTIO_API_KEY:
        print("❌ ATTIO_API_KEY not set in .env")
        return False
    
    print(f"✓ API key found: {ATTIO_API_KEY[:20]}...")
    
    attio = AttioSync()
    
    # Try to list companies (basic API test)
    response = attio._make_request("POST", "/objects/companies/records/query", {"limit": 1})
    
    if response is not None:
        print("✅ Attio connection successful!")
        return True
    else:
        print("❌ Attio connection failed")
        return False


if __name__ == "__main__":
    if test_attio_connection():
        print()
        sync_all_from_chroma()

