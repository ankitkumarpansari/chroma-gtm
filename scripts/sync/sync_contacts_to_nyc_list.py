#!/usr/bin/env python3
"""
Sync Contacts to Existing NYC Dinner List in Attio

Adds contacts from nyc_dinner_contacts_enriched.csv to the existing
"NYC Companies - Dinner Targets" list by:
1. Finding/creating People records
2. Linking them to existing Company records
3. Adding entries to the NYC list

Usage:
    python scripts/sync/sync_contacts_to_nyc_list.py
    python scripts/sync/sync_contacts_to_nyc_list.py --dry-run
    python scripts/sync/sync_contacts_to_nyc_list.py --limit 20
"""

import os
import csv
import requests
import time
import argparse
from typing import Optional, Dict, List, Tuple
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Configuration
ATTIO_API_KEY = os.getenv("ATTIO_API_KEY")
ATTIO_BASE_URL = "https://api.attio.com/v2"
ATTIO_WORKSPACE_SLUG = "chromadb"

# Existing NYC list ID
NYC_LIST_ID = "830b2e34-a75c-45b9-9070-651c2714c0f6"

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONTACTS_CSV = os.path.join(BASE_DIR, "data/exports/nyc_dinner_contacts_enriched.csv")
FALLBACK_CSV = os.path.join(BASE_DIR, "data/exports/nyc_dinner_contacts.csv")

RATE_LIMIT_DELAY = 0.25


class AttioContactSync:
    """Sync contacts to existing NYC Attio list."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or ATTIO_API_KEY
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        
        self.last_request_time = 0
        self.company_cache: Dict[str, str] = {}  # company_name -> record_id
        self.stats = {
            "people_created": 0,
            "people_updated": 0,
            "people_linked": 0,
            "companies_found": 0,
            "companies_not_found": 0,
            "failed": 0,
        }
    
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
                return {"conflict": True}
            elif response.status_code == 429:
                print("   ⚠️ Rate limited, waiting 5s...")
                time.sleep(5)
                return self._request(method, endpoint, json_data)
            else:
                # Don't print error for common cases
                if response.status_code != 404:
                    print(f"   ⚠️ API {response.status_code}: {response.text[:100]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test Attio connection and verify NYC list exists."""
        print("🔗 Testing Attio connection...")
        
        if not self.api_key:
            print("   ❌ ATTIO_API_KEY not set")
            return False
        
        # Test connection
        response = self._request("GET", f"/lists/{NYC_LIST_ID}")
        if response and "conflict" not in response:
            list_name = response.get("data", {}).get("name", "Unknown")
            print(f"   ✅ Connected! Found list: {list_name}")
            return True
        
        print("   ❌ Could not find NYC list")
        return False
    
    def load_contacts(self) -> List[Dict]:
        """Load contacts from CSV."""
        csv_path = CONTACTS_CSV if os.path.exists(CONTACTS_CSV) else FALLBACK_CSV
        
        if not os.path.exists(csv_path):
            print(f"   ❌ Contacts file not found")
            return []
        
        contacts = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('name') and row.get('company'):
                    contacts.append(row)
        
        return contacts
    
    def find_company_in_attio(self, company_name: str) -> Optional[str]:
        """Find company record ID in Attio."""
        # Check cache
        cache_key = company_name.lower().strip()
        if cache_key in self.company_cache:
            return self.company_cache[cache_key]
        
        # Search Attio
        response = self._request(
            "POST", "/objects/companies/records/query",
            {
                "filter": {"name": {"$contains": company_name}},
                "limit": 5
            }
        )
        
        if response and response.get("data"):
            for record in response["data"]:
                values = record.get("values", {})
                name_list = values.get("name", [])
                if name_list:
                    record_name = name_list[0].get("value", "").lower().strip()
                    if record_name == cache_key or cache_key in record_name:
                        record_id = record.get("id", {})
                        if isinstance(record_id, dict):
                            record_id = record_id.get("record_id")
                        self.company_cache[cache_key] = record_id
                        return record_id
        
        return None
    
    def find_person_in_attio(self, email: str = None, name: str = None) -> Optional[Tuple[str, dict]]:
        """Find existing person in Attio."""
        # Try email first
        if email and '@' in email:
            response = self._request(
                "POST", "/objects/people/records/query",
                {
                    "filter": {"email_addresses": {"$contains": email}},
                    "limit": 1
                }
            )
            if response and response.get("data"):
                record = response["data"][0]
                record_id = record.get("id", {})
                if isinstance(record_id, dict):
                    record_id = record_id.get("record_id")
                return record_id, record
        
        # Try name
        if name:
            response = self._request(
                "POST", "/objects/people/records/query",
                {
                    "filter": {"name": {"$contains": name}},
                    "limit": 3
                }
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
    
    def parse_name(self, full_name: str) -> Tuple[str, str]:
        """Parse full name into first and last name."""
        parts = full_name.strip().split()
        if len(parts) == 0:
            return "", ""
        elif len(parts) == 1:
            return parts[0], ""
        else:
            return parts[0], " ".join(parts[1:])
    
    def create_person(self, contact: Dict, company_record_id: str = None) -> Optional[str]:
        """Create a new person record."""
        name = contact.get('name', '') or ''
        email = contact.get('email', '') or ''  # Ensure not None
        title = contact.get('title', '') or ''
        linkedin = contact.get('linkedin', '') or ''
        company = contact.get('company', '') or ''
        source = contact.get('source', '') or ''
        icp_score = contact.get('icp_score', '') or ''
        
        # Parse name into first/last
        first_name, last_name = self.parse_name(name)
        
        # Build values - name requires first_name, last_name, full_name
        values = {
            "name": [{
                "first_name": first_name,
                "last_name": last_name,
                "full_name": name
            }]
        }
        
        # Add email
        if email and '@' in email:
            values["email_addresses"] = [{"email_address": email}]
        
        # Add job title
        if title:
            values["job_title"] = [{"value": title}]
        
        # Add LinkedIn
        if linkedin and 'linkedin.com' in linkedin:
            values["linkedin"] = [{"value": linkedin}]
        
        # Link to company - requires target_object
        if company_record_id:
            values["company"] = [{
                "target_object": "companies",
                "target_record_id": company_record_id
            }]
        
        # Build description
        desc_parts = [
            f"🗽 NYC Dinner Contact",
            f"📥 Source: {source}" if source else "",
            f"💯 ICP Score: {icp_score}/10" if icp_score else "",
            f"🏢 Company: {company}",
            f"📅 Added: {datetime.now().strftime('%Y-%m-%d')}"
        ]
        values["description"] = [{"value": "\n".join([p for p in desc_parts if p])}]
        
        # Create record
        response = self._request(
            "POST", "/objects/people/records",
            {"data": {"values": values}}
        )
        
        if response and "conflict" not in response:
            record_id = response.get("data", {}).get("id", {})
            if isinstance(record_id, dict):
                record_id = record_id.get("record_id")
            return record_id
        
        return None
    
    def update_person(self, person_id: str, contact: Dict, company_record_id: str = None) -> bool:
        """Update existing person record."""
        title = contact.get('title', '')
        company = contact.get('company', '')
        source = contact.get('source', '')
        icp_score = contact.get('icp_score', '')
        
        values = {}
        
        # Update job title if we have one
        if title:
            values["job_title"] = [{"value": title}]
        
        # Link to company if not already linked - requires target_object
        if company_record_id:
            values["company"] = [{
                "target_object": "companies",
                "target_record_id": company_record_id
            }]
        
        # Update description
        desc_parts = [
            f"🗽 NYC Dinner Contact",
            f"📥 Source: {source}" if source else "",
            f"💯 ICP Score: {icp_score}/10" if icp_score else "",
            f"🏢 Company: {company}",
            f"📅 Updated: {datetime.now().strftime('%Y-%m-%d')}"
        ]
        values["description"] = [{"value": "\n".join([p for p in desc_parts if p])}]
        
        if not values:
            return True
        
        response = self._request(
            "PATCH", f"/objects/people/records/{person_id}",
            {"data": {"values": values}}
        )
        
        return response is not None
    
    def add_person_to_nyc_list(self, person_id: str) -> bool:
        """
        Note: The NYC list is a Companies list, not a People list.
        People are linked to companies via the 'company' field.
        This method is kept for compatibility but doesn't add to the list directly.
        """
        # The NYC list is a Companies list, so we can't add people directly.
        # Instead, people are linked to companies via the company relationship.
        return True
    
    def sync_contact(self, contact: Dict, dry_run: bool = False) -> bool:
        """Sync a single contact."""
        name = contact.get('name', '')
        company = contact.get('company', '')
        email = contact.get('email', '') or ''  # Ensure not None
        title = contact.get('title', '')
        
        if dry_run:
            return True
        
        # Find company in Attio
        company_record_id = self.find_company_in_attio(company)
        if company_record_id:
            self.stats["companies_found"] += 1
        else:
            self.stats["companies_not_found"] += 1
        
        # Check if person exists
        existing_id, existing_record = self.find_person_in_attio(email, name)
        
        if existing_id:
            # Update existing person
            if self.update_person(existing_id, contact, company_record_id):
                self.stats["people_updated"] += 1
                if company_record_id:
                    self.stats["people_linked"] += 1
                # Add to list (will be no-op if already there)
                self.add_person_to_nyc_list(existing_id)
                return True
        else:
            # Create new person
            person_id = self.create_person(contact, company_record_id)
            if person_id:
                self.stats["people_created"] += 1
                if company_record_id:
                    self.stats["people_linked"] += 1
                # Add to NYC list
                self.add_person_to_nyc_list(person_id)
                return True
        
        self.stats["failed"] += 1
        return False
    
    def sync_all(self, dry_run: bool = False, limit: int = None) -> Dict:
        """Sync all contacts."""
        print("\n" + "=" * 60)
        print("👥 SYNCING CONTACTS TO NYC DINNER LIST")
        print("=" * 60)
        
        contacts = self.load_contacts()
        print(f"\n📂 Loaded {len(contacts)} contacts")
        
        if limit:
            contacts = contacts[:limit]
            print(f"   Limited to {limit} contacts")
        
        print(f"\n{'🧪 DRY RUN' if dry_run else '📤 Syncing'}...\n")
        
        for i, contact in enumerate(contacts, 1):
            name = contact.get('name', 'Unknown')
            company = contact.get('company', '')
            title = contact.get('title', '')
            source = contact.get('source', '')
            
            if dry_run:
                print(f"   [{i:3d}/{len(contacts)}] 🧪 {name} @ {company[:30]}")
                continue
            
            success = self.sync_contact(contact)
            
            if success:
                # Determine icon based on what happened
                if self.stats["people_created"] > i - 1:
                    icon = "✅"  # Created
                else:
                    icon = "🔄"  # Updated
                
                link_icon = "🔗" if self.find_company_in_attio(company) else "⚠️"
                print(f"   [{i:3d}/{len(contacts)}] {icon}{link_icon} {name} @ {company[:25]}")
            else:
                print(f"   [{i:3d}/{len(contacts)}] ❌ {name} @ {company[:25]}")
        
        return self.stats
    
    def print_summary(self):
        """Print sync summary."""
        print("\n" + "=" * 60)
        print("📊 SYNC SUMMARY")
        print("=" * 60)
        print(f"   ✅ People created:     {self.stats['people_created']}")
        print(f"   🔄 People updated:     {self.stats['people_updated']}")
        print(f"   🔗 Linked to company:  {self.stats['people_linked']}")
        print(f"   🏢 Companies found:    {self.stats['companies_found']}")
        print(f"   ⚠️  Companies missing: {self.stats['companies_not_found']}")
        print(f"   ❌ Failed:             {self.stats['failed']}")
        
        print(f"\n🔗 View in Attio:")
        print(f"   https://app.attio.com/{ATTIO_WORKSPACE_SLUG}/lists/{NYC_LIST_ID}")


def main():
    parser = argparse.ArgumentParser(description="Sync contacts to NYC Attio list")
    parser.add_argument("--dry-run", action="store_true", help="Preview without changes")
    parser.add_argument("--limit", type=int, help="Limit number of contacts")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("🗽 NYC DINNER CONTACTS → ATTIO")
    print("=" * 60)
    print(f"   List ID: {NYC_LIST_ID}")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    sync = AttioContactSync()
    
    if not sync.test_connection():
        return
    
    sync.sync_all(dry_run=args.dry_run, limit=args.limit)
    
    if not args.dry_run:
        sync.print_summary()


if __name__ == "__main__":
    main()

