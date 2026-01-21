#!/usr/bin/env python3
"""
Sync NYC Dinner Companies AND People to Attio (v2)

Enhanced sync that creates linked Company and People records:
1. Creates/updates Company records with all metadata
2. Creates/updates People records linked to companies
3. Adds both to the NYC Dinner list

Data Sources:
- nyc_dinner_companies_final.csv (companies)
- nyc_dinner_contacts_enriched.csv (people)

Usage:
    python scripts/sync/sync_nyc_to_attio_v2.py
    python scripts/sync/sync_nyc_to_attio_v2.py --test
    python scripts/sync/sync_nyc_to_attio_v2.py --dry-run
    python scripts/sync/sync_nyc_to_attio_v2.py --companies-only
    python scripts/sync/sync_nyc_to_attio_v2.py --people-only
"""

import os
import csv
import requests
import time
import argparse
from typing import Optional, Dict, List, Any, Tuple
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Configuration
ATTIO_API_KEY = os.getenv("ATTIO_API_KEY")
ATTIO_BASE_URL = "https://api.attio.com/v2"
ATTIO_WORKSPACE_SLUG = "chromadb"

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPANIES_CSV = os.path.join(BASE_DIR, "data/exports/nyc_dinner_companies_final.csv")
CONTACTS_CSV = os.path.join(BASE_DIR, "data/exports/nyc_dinner_contacts_enriched.csv")
FALLBACK_CONTACTS_CSV = os.path.join(BASE_DIR, "data/exports/nyc_dinner_contacts.csv")

# Rate limiting
RATE_LIMIT_DELAY = 0.25  # seconds between requests


class AttioNYCSyncV2:
    """Sync NYC companies AND people to Attio with proper linking."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or ATTIO_API_KEY
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        
        self.last_request_time = 0
        self.nyc_companies_list_id = None
        self.nyc_contacts_list_id = None
        
        # Cache for company record IDs (name -> record_id)
        self.company_cache: Dict[str, str] = {}
    
    def _rate_limit(self):
        """Enforce rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()
    
    def _request(self, method: str, endpoint: str, json_data: dict = None) -> Optional[dict]:
        """Make API request to Attio."""
        self._rate_limit()
        url = f"{ATTIO_BASE_URL}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=json_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 409:
                return {"conflict": True, "message": response.text}
            elif response.status_code == 429:
                print("   ⚠️ Rate limited, waiting 5s...")
                time.sleep(5)
                return self._request(method, endpoint, json_data)
            else:
                print(f"   ⚠️ API error: {response.status_code} - {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
            return None
    
    # ============================================================
    # CONNECTION & SETUP
    # ============================================================
    
    def test_connection(self) -> bool:
        """Test Attio API connection."""
        print("🔗 Testing Attio connection...")
        
        if not self.api_key:
            print("   ❌ ATTIO_API_KEY not set")
            return False
        
        print(f"   API Key: {self.api_key[:20]}...")
        
        response = self._request("POST", "/objects/companies/records/query", {"limit": 1})
        if response and "conflict" not in response:
            print("   ✅ Connection successful!")
            return True
        
        print("   ❌ Connection failed")
        return False
    
    def get_or_create_list(self, name: str, api_slug: str, parent_object: str) -> Optional[str]:
        """Get or create a list."""
        print(f"\n📋 Setting up '{name}' list...")
        
        # Search existing lists
        response = self._request("GET", "/lists")
        if response:
            for lst in response.get("data", []):
                if api_slug in str(lst.get("api_slug", "")).lower():
                    list_id = lst.get("id", {})
                    if isinstance(list_id, dict):
                        list_id = list_id.get("list_id")
                    print(f"   ✅ Found existing list: {list_id}")
                    return list_id
        
        # Create new list
        response = self._request(
            "POST", "/lists",
            {
                "data": {
                    "name": name,
                    "api_slug": api_slug,
                    "parent_object": parent_object,
                    "workspace_access": "full-access"
                }
            }
        )
        
        if response and "conflict" not in response:
            list_id = response.get("data", {}).get("id", {})
            if isinstance(list_id, dict):
                list_id = list_id.get("list_id")
            print(f"   ✅ Created new list: {list_id}")
            return list_id
        
        print(f"   ❌ Failed to create list")
        return None
    
    def setup_lists(self) -> bool:
        """Setup both companies and contacts lists."""
        self.nyc_companies_list_id = self.get_or_create_list(
            "NYC Dinner - Companies",
            "nyc_dinner_companies",
            "companies"
        )
        
        self.nyc_contacts_list_id = self.get_or_create_list(
            "NYC Dinner - Contacts", 
            "nyc_dinner_contacts",
            "people"
        )
        
        return bool(self.nyc_companies_list_id and self.nyc_contacts_list_id)
    
    # ============================================================
    # DATA LOADING
    # ============================================================
    
    def load_companies(self) -> List[Dict]:
        """Load companies from CSV."""
        companies = []
        
        if not os.path.exists(COMPANIES_CSV):
            print(f"   ⚠️ Companies file not found: {COMPANIES_CSV}")
            return companies
        
        with open(COMPANIES_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('company'):
                    companies.append(row)
        
        return companies
    
    def load_contacts(self) -> List[Dict]:
        """Load contacts from CSV."""
        contacts = []
        
        # Try enriched first, then fallback
        csv_path = CONTACTS_CSV if os.path.exists(CONTACTS_CSV) else FALLBACK_CONTACTS_CSV
        
        if not os.path.exists(csv_path):
            print(f"   ⚠️ Contacts file not found")
            return contacts
        
        print(f"   Loading from: {os.path.basename(csv_path)}")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('name') and row.get('company'):
                    contacts.append(row)
        
        return contacts
    
    # ============================================================
    # COMPANY OPERATIONS
    # ============================================================
    
    def find_company(self, company_name: str, domain: str = None) -> Optional[Tuple[str, dict]]:
        """Find existing company by name or domain."""
        # Try cache first
        cache_key = company_name.lower()
        if cache_key in self.company_cache:
            return self.company_cache[cache_key], {}
        
        # Search by name
        response = self._request(
            "POST", "/objects/companies/records/query",
            {"filter": {"name": {"$contains": company_name}}, "limit": 5}
        )
        
        if response and response.get("data"):
            for record in response["data"]:
                record_name = ""
                values = record.get("values", {})
                name_list = values.get("name", [])
                if name_list:
                    record_name = name_list[0].get("value", "")
                
                if record_name.lower() == company_name.lower():
                    record_id = record.get("id", {})
                    if isinstance(record_id, dict):
                        record_id = record_id.get("record_id")
                    self.company_cache[cache_key] = record_id
                    return record_id, record
        
        return None, None
    
    def build_company_description(self, company: Dict) -> str:
        """Build rich description for company."""
        parts = []
        
        category = company.get('category', '')
        tier = company.get('tier', '')
        priority = company.get('priority', '')
        why_selected = company.get('why_selected', '')
        tech_stack = company.get('tech_stack', '')
        notes = company.get('notes', '')
        
        if category:
            parts.append(f"📁 Category: {category}")
        if tier:
            parts.append(f"🎯 Tier: {tier}")
        if priority:
            parts.append(f"⚡ Priority: {priority}")
        if why_selected:
            parts.append(f"\n💡 Why Selected:\n{why_selected}")
        if tech_stack:
            parts.append(f"\n🛠️ Tech Stack: {tech_stack}")
        if notes:
            parts.append(f"\n📝 Notes: {notes}")
        
        # Detect vector DB
        combined = f"{tech_stack} {notes} {category}".lower()
        if "pinecone" in combined:
            parts.append("\n🔄 COMPETITOR: Using Pinecone")
        if "weaviate" in combined:
            parts.append("\n🔄 COMPETITOR: Using Weaviate")
        if "qdrant" in combined:
            parts.append("\n🔄 COMPETITOR: Using Qdrant")
        if "milvus" in combined:
            parts.append("\n🔄 COMPETITOR: Using Milvus")
        
        parts.append(f"\n🗽 NYC Dinner Target")
        parts.append(f"📅 Synced: {datetime.now().strftime('%Y-%m-%d')}")
        
        return "\n".join(parts)
    
    def create_or_update_company(self, company: Dict) -> Optional[str]:
        """Create or update company record."""
        company_name = company.get('company', '')
        domain = company.get('domain', '')
        
        # Build values
        values = {
            "name": [{"value": company_name}],
            "description": [{"value": self.build_company_description(company)}]
        }
        
        # Add domain if available
        if domain and domain != 'NEEDS_DOMAIN':
            values["domains"] = [{"domain": domain}]
        
        # Check if exists
        existing_id, existing_record = self.find_company(company_name, domain)
        
        if existing_id:
            # Update existing
            response = self._request(
                "PATCH",
                f"/objects/companies/records/{existing_id}",
                {"data": {"values": values}}
            )
            return existing_id if response else None
        else:
            # Create new
            response = self._request(
                "POST",
                "/objects/companies/records",
                {"data": {"values": values}}
            )
            if response and "conflict" not in response:
                record_id = response.get("data", {}).get("id", {})
                if isinstance(record_id, dict):
                    record_id = record_id.get("record_id")
                self.company_cache[company_name.lower()] = record_id
                return record_id
        
        return None
    
    def add_company_to_list(self, record_id: str) -> bool:
        """Add company to NYC list."""
        if not self.nyc_companies_list_id:
            return False
        
        response = self._request(
            "POST",
            f"/lists/{self.nyc_companies_list_id}/entries",
            {
                "data": {
                    "parent_object": "companies",
                    "parent_record_id": record_id,
                    "entry_values": {}
                }
            }
        )
        return response is not None
    
    # ============================================================
    # PEOPLE OPERATIONS
    # ============================================================
    
    def find_person(self, email: str = None, name: str = None, company: str = None) -> Optional[Tuple[str, dict]]:
        """Find existing person by email or name."""
        # Try email first (most reliable)
        if email and '@' in email:
            response = self._request(
                "POST", "/objects/people/records/query",
                {"filter": {"email_addresses": {"$contains": email}}, "limit": 1}
            )
            if response and response.get("data"):
                record = response["data"][0]
                record_id = record.get("id", {})
                if isinstance(record_id, dict):
                    record_id = record_id.get("record_id")
                return record_id, record
        
        # Try name search
        if name:
            response = self._request(
                "POST", "/objects/people/records/query",
                {"filter": {"name": {"$contains": name}}, "limit": 5}
            )
            if response and response.get("data"):
                for record in response["data"]:
                    values = record.get("values", {})
                    name_list = values.get("name", [])
                    if name_list:
                        record_name = name_list[0].get("value", "")
                        if record_name.lower() == name.lower():
                            record_id = record.get("id", {})
                            if isinstance(record_id, dict):
                                record_id = record_id.get("record_id")
                            return record_id, record
        
        return None, None
    
    def build_person_description(self, contact: Dict) -> str:
        """Build description for person."""
        parts = []
        
        source = contact.get('source', '')
        category = contact.get('category', '')
        tier = contact.get('tier', '')
        priority = contact.get('priority', '')
        icp_score = contact.get('icp_score', '')
        talk_title = contact.get('talk_title', '')
        
        if source:
            parts.append(f"📥 Source: {source}")
        if category:
            parts.append(f"📁 Category: {category}")
        if tier:
            parts.append(f"🎯 Tier: {tier}")
        if priority:
            parts.append(f"⚡ Priority: {priority}")
        if icp_score:
            parts.append(f"💯 ICP Score: {icp_score}/10")
        if talk_title:
            parts.append(f"\n🎤 Talk: {talk_title}")
        
        parts.append(f"\n🗽 NYC Dinner Contact")
        parts.append(f"📅 Synced: {datetime.now().strftime('%Y-%m-%d')}")
        
        return "\n".join(parts)
    
    def create_or_update_person(self, contact: Dict, company_record_id: str = None) -> Optional[str]:
        """Create or update person record."""
        name = contact.get('name', '')
        email = contact.get('email', '')
        title = contact.get('title', '')
        linkedin = contact.get('linkedin', '')
        company = contact.get('company', '')
        
        # Build values
        values = {
            "name": [{"value": name}],
            "description": [{"value": self.build_person_description(contact)}]
        }
        
        # Add email if available
        if email and '@' in email:
            values["email_addresses"] = [{"email_address": email}]
        
        # Add job title
        if title:
            values["job_title"] = [{"value": title}]
        
        # Link to company if we have the record ID
        if company_record_id:
            values["company"] = [{"target_record_id": company_record_id}]
        
        # Check if exists
        existing_id, existing_record = self.find_person(email, name, company)
        
        if existing_id:
            # Update existing
            response = self._request(
                "PATCH",
                f"/objects/people/records/{existing_id}",
                {"data": {"values": values}}
            )
            return existing_id if response else None
        else:
            # Create new
            response = self._request(
                "POST",
                "/objects/people/records",
                {"data": {"values": values}}
            )
            if response and "conflict" not in response:
                record_id = response.get("data", {}).get("id", {})
                if isinstance(record_id, dict):
                    record_id = record_id.get("record_id")
                return record_id
        
        return None
    
    def add_person_to_list(self, record_id: str) -> bool:
        """Add person to NYC contacts list."""
        if not self.nyc_contacts_list_id:
            return False
        
        response = self._request(
            "POST",
            f"/lists/{self.nyc_contacts_list_id}/entries",
            {
                "data": {
                    "parent_object": "people",
                    "parent_record_id": record_id,
                    "entry_values": {}
                }
            }
        )
        return response is not None
    
    # ============================================================
    # SYNC OPERATIONS
    # ============================================================
    
    def sync_companies(self, dry_run: bool = False) -> Dict:
        """Sync all companies."""
        print("\n" + "=" * 60)
        print("🏢 SYNCING COMPANIES")
        print("=" * 60)
        
        companies = self.load_companies()
        print(f"\n📂 Loaded {len(companies)} companies")
        
        results = {
            "total": len(companies),
            "created": 0,
            "updated": 0,
            "failed": 0,
            "details": []
        }
        
        for i, company in enumerate(companies, 1):
            name = company.get('company', 'Unknown')
            tier = company.get('tier', '?')
            priority = company.get('priority', '')
            
            if dry_run:
                results["created"] += 1
                print(f"   [{i:3d}/{len(companies)}] 🧪 {name} (Tier {tier})")
                continue
            
            # Check if exists
            existing_id, _ = self.find_company(name)
            
            # Create/update
            record_id = self.create_or_update_company(company)
            
            if record_id:
                # Add to list
                self.add_company_to_list(record_id)
                
                if existing_id:
                    results["updated"] += 1
                    icon = "🔄"
                else:
                    results["created"] += 1
                    icon = "✅"
                
                tier_icon = "🔴" if tier == "1" else "🟠" if tier == "2" else "🟡" if tier == "3" else "⚪"
                print(f"   [{i:3d}/{len(companies)}] {icon} {name} {tier_icon}")
                results["details"].append({"name": name, "id": record_id, "status": "success"})
            else:
                results["failed"] += 1
                print(f"   [{i:3d}/{len(companies)}] ❌ {name}")
                results["details"].append({"name": name, "status": "failed"})
        
        return results
    
    def sync_contacts(self, dry_run: bool = False) -> Dict:
        """Sync all contacts."""
        print("\n" + "=" * 60)
        print("👥 SYNCING CONTACTS")
        print("=" * 60)
        
        contacts = self.load_contacts()
        print(f"\n📂 Loaded {len(contacts)} contacts")
        
        results = {
            "total": len(contacts),
            "created": 0,
            "updated": 0,
            "linked": 0,
            "failed": 0,
            "details": []
        }
        
        for i, contact in enumerate(contacts, 1):
            name = contact.get('name', 'Unknown')
            company = contact.get('company', '')
            title = contact.get('title', '')
            source = contact.get('source', '')
            
            if dry_run:
                results["created"] += 1
                print(f"   [{i:3d}/{len(contacts)}] 🧪 {name} @ {company}")
                continue
            
            # Find company record ID for linking
            company_record_id = None
            if company:
                company_record_id, _ = self.find_company(company)
            
            # Check if person exists
            existing_id, _ = self.find_person(contact.get('email'), name, company)
            
            # Create/update person
            record_id = self.create_or_update_person(contact, company_record_id)
            
            if record_id:
                # Add to list
                self.add_person_to_list(record_id)
                
                if existing_id:
                    results["updated"] += 1
                    icon = "🔄"
                else:
                    results["created"] += 1
                    icon = "✅"
                
                if company_record_id:
                    results["linked"] += 1
                    link_icon = "🔗"
                else:
                    link_icon = "⚠️"
                
                print(f"   [{i:3d}/{len(contacts)}] {icon}{link_icon} {name} @ {company[:25]}")
                results["details"].append({"name": name, "company": company, "id": record_id, "status": "success"})
            else:
                results["failed"] += 1
                print(f"   [{i:3d}/{len(contacts)}] ❌ {name} @ {company}")
                results["details"].append({"name": name, "company": company, "status": "failed"})
        
        return results
    
    def sync_all(self, dry_run: bool = False, companies_only: bool = False, people_only: bool = False) -> Dict:
        """Sync everything."""
        if not self.enabled:
            return {"error": "Attio not configured"}
        
        # Setup lists
        if not dry_run:
            if not self.setup_lists():
                return {"error": "Failed to setup lists"}
        
        results = {
            "companies": {},
            "contacts": {}
        }
        
        if not people_only:
            results["companies"] = self.sync_companies(dry_run)
        
        if not companies_only:
            results["contacts"] = self.sync_contacts(dry_run)
        
        return results
    
    def print_summary(self, results: Dict):
        """Print sync summary."""
        print("\n" + "=" * 60)
        print("📊 SYNC SUMMARY")
        print("=" * 60)
        
        if "companies" in results and results["companies"]:
            cr = results["companies"]
            print(f"\n🏢 COMPANIES:")
            print(f"   Total: {cr.get('total', 0)}")
            print(f"   ✅ Created: {cr.get('created', 0)}")
            print(f"   🔄 Updated: {cr.get('updated', 0)}")
            print(f"   ❌ Failed: {cr.get('failed', 0)}")
        
        if "contacts" in results and results["contacts"]:
            pr = results["contacts"]
            print(f"\n👥 CONTACTS:")
            print(f"   Total: {pr.get('total', 0)}")
            print(f"   ✅ Created: {pr.get('created', 0)}")
            print(f"   🔄 Updated: {pr.get('updated', 0)}")
            print(f"   🔗 Linked to company: {pr.get('linked', 0)}")
            print(f"   ❌ Failed: {pr.get('failed', 0)}")
        
        print(f"\n🔗 View in Attio:")
        print(f"   Companies: https://app.attio.com/{ATTIO_WORKSPACE_SLUG}/lists/{self.nyc_companies_list_id}")
        print(f"   Contacts: https://app.attio.com/{ATTIO_WORKSPACE_SLUG}/lists/{self.nyc_contacts_list_id}")


def main():
    parser = argparse.ArgumentParser(description="Sync NYC companies and contacts to Attio")
    parser.add_argument("--test", action="store_true", help="Test connection only")
    parser.add_argument("--dry-run", action="store_true", help="Preview without making changes")
    parser.add_argument("--companies-only", action="store_true", help="Sync only companies")
    parser.add_argument("--people-only", action="store_true", help="Sync only people")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("🗽 NYC DINNER → ATTIO SYNC (v2)")
    print("   Companies + People with Linking")
    print("=" * 60)
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    sync = AttioNYCSyncV2()
    
    if args.test:
        sync.test_connection()
        return
    
    if not sync.test_connection():
        return
    
    results = sync.sync_all(
        dry_run=args.dry_run,
        companies_only=args.companies_only,
        people_only=args.people_only
    )
    
    if "error" not in results:
        sync.print_summary(results)


if __name__ == "__main__":
    main()

