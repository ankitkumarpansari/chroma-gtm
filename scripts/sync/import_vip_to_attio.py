#!/usr/bin/env python3
"""
Import VIP Users CSV to Attio
==============================
Imports the nyc_dinner_top_accounts.csv with all VIP targets to Attio.

Creates:
1. A dedicated "🌟 NYC VIP Targets" list
2. Company records with full metadata
3. People records linked to companies
4. Adds all to the VIP list for targeting

Usage:
    python scripts/sync/import_vip_to_attio.py              # Full import
    python scripts/sync/import_vip_to_attio.py --test       # Test with 5 records
    python scripts/sync/import_vip_to_attio.py --dry-run    # Preview only
    python scripts/sync/import_vip_to_attio.py --tier 1     # Import only Tier 1
    python scripts/sync/import_vip_to_attio.py --priority CRITICAL  # Critical only
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

# File path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VIP_CSV = os.path.join(BASE_DIR, "data/exports/nyc_dinner_top_accounts.csv")

# Rate limiting
RATE_LIMIT_DELAY = 0.3  # seconds between requests


class AttioVIPImporter:
    """Import VIP accounts to Attio with full metadata."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or ATTIO_API_KEY
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        
        self.last_request_time = 0
        self.vip_list_id = None
        self.company_cache: Dict[str, str] = {}  # company_name -> record_id
        
        self.stats = {
            "companies_created": 0,
            "companies_updated": 0,
            "people_created": 0,
            "people_updated": 0,
            "list_entries_added": 0,
            "skipped": 0,
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
                return {"conflict": True, "data": response.json().get("data", {})}
            elif response.status_code == 429:
                print("   ⏳ Rate limited, waiting 5s...")
                time.sleep(5)
                return self._request(method, endpoint, json_data)
            else:
                if response.status_code not in [404]:
                    print(f"   ⚠️ API {response.status_code}: {response.text[:150]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test Attio API connection."""
        print("🔗 Testing Attio connection...")
        
        if not self.api_key:
            print("   ❌ ATTIO_API_KEY not set in .env file")
            return False
        
        response = self._request("POST", "/objects/companies/records/query", {"limit": 1})
        if response:
            print("   ✅ Connected to Attio!")
            return True
        
        print("   ❌ Could not connect to Attio")
        return False
    
    def find_or_create_vip_list(self) -> Optional[str]:
        """Find or create the VIP targets list."""
        print("\n📋 Setting up VIP list...")
        
        # First, search for existing list
        response = self._request("GET", "/lists")
        if response and response.get("data"):
            for lst in response["data"]:
                if "VIP" in lst.get("name", "") or "vip" in lst.get("name", "").lower():
                    self.vip_list_id = lst.get("id")
                    print(f"   ✅ Found existing list: {lst.get('name')}")
                    return self.vip_list_id
        
        # Create new list
        list_data = {
            "data": {
                "name": "🌟 NYC VIP Targets",
                "parent_object": "companies"
            }
        }
        
        response = self._request("POST", "/lists", list_data)
        if response and response.get("data"):
            self.vip_list_id = response["data"].get("id")
            print(f"   ✅ Created new list: 🌟 NYC VIP Targets")
            return self.vip_list_id
        
        print("   ⚠️ Could not create list, will use existing NYC list")
        self.vip_list_id = "830b2e34-a75c-45b9-9070-651c2714c0f6"  # Fallback to NYC list
        return self.vip_list_id
    
    def load_vip_data(self, tier_filter: int = None, priority_filter: str = None) -> List[Dict]:
        """Load VIP data from CSV."""
        if not os.path.exists(VIP_CSV):
            print(f"   ❌ VIP CSV not found: {VIP_CSV}")
            return []
        
        records = []
        with open(VIP_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Apply filters
                if tier_filter and row.get('Tier'):
                    try:
                        if int(row['Tier']) != tier_filter:
                            continue
                    except ValueError:
                        pass
                
                if priority_filter and row.get('Priority', '').upper() != priority_filter.upper():
                    continue
                
                records.append(row)
        
        return records
    
    def parse_contacts(self, row: Dict) -> List[Dict]:
        """Parse contact information from a row (can have multiple contacts)."""
        contacts = []
        
        names = row.get('Contact Name', '')
        emails = row.get('Email', '')
        titles = row.get('Title', '')
        linkedin = row.get('LinkedIn', '')
        
        # Handle multiple contacts (comma-separated)
        name_list = [n.strip() for n in names.split(',') if n.strip()] if names else []
        email_list = [e.strip() for e in emails.split(',') if e.strip()] if emails else []
        title_list = [t.strip() for t in titles.split(',') if t.strip()] if titles else []
        linkedin_list = [l.strip() for l in linkedin.split(',') if l.strip()] if linkedin else []
        
        # Match up contacts
        max_contacts = max(len(name_list), len(email_list), 1)
        
        for i in range(max_contacts):
            contact = {
                'name': name_list[i] if i < len(name_list) else '',
                'email': email_list[i] if i < len(email_list) else '',
                'title': title_list[i] if i < len(title_list) else (title_list[0] if title_list else ''),
                'linkedin': linkedin_list[i] if i < len(linkedin_list) else (linkedin_list[0] if linkedin_list else ''),
            }
            
            # Only add if we have at least name or email
            if contact['name'] or contact['email']:
                contacts.append(contact)
        
        return contacts
    
    def find_company(self, company_name: str) -> Optional[str]:
        """Find company in Attio."""
        cache_key = company_name.lower().strip()
        if cache_key in self.company_cache:
            return self.company_cache[cache_key]
        
        response = self._request(
            "POST", "/objects/companies/records/query",
            {
                "filter": {"name": {"$contains": company_name[:50]}},
                "limit": 5
            }
        )
        
        if response and response.get("data"):
            for record in response["data"]:
                values = record.get("values", {})
                name_list = values.get("name", [])
                if name_list:
                    record_name = name_list[0].get("value", "").lower().strip()
                    if record_name == cache_key or cache_key in record_name or record_name in cache_key:
                        record_id = record.get("id", {})
                        if isinstance(record_id, dict):
                            record_id = record_id.get("record_id")
                        self.company_cache[cache_key] = record_id
                        return record_id
        
        return None
    
    def create_or_update_company(self, row: Dict) -> Optional[str]:
        """Create or update company in Attio."""
        company_name = row.get('Company', '').strip()
        if not company_name:
            return None
        
        # Check if exists
        existing_id = self.find_company(company_name)
        
        # Build company values
        values = {
            "name": [{"value": company_name}]
        }
        
        # Build rich description with all metadata
        desc_parts = [
            f"🌟 VIP Target - {row.get('Category', 'Unknown')}",
            f"",
            f"📊 Tier: {row.get('Tier', 'N/A')} | Priority: {row.get('Priority', 'N/A')}",
            f"",
            f"💡 Why Selected:",
            f"{row.get('Why Selected', 'N/A')}",
            f"",
            f"🛠️ Tech Stack: {row.get('Tech Stack', 'Unknown')}",
            f"",
            f"📝 Notes: {row.get('Notes', '')}",
            f"",
            f"📅 Imported: {datetime.now().strftime('%Y-%m-%d')}"
        ]
        values["description"] = [{"value": "\n".join(desc_parts)}]
        
        if existing_id:
            # Update existing
            response = self._request(
                "PATCH", f"/objects/companies/records/{existing_id}",
                {"data": {"values": values}}
            )
            if response:
                self.stats["companies_updated"] += 1
                self.company_cache[company_name.lower().strip()] = existing_id
                return existing_id
        else:
            # Create new
            response = self._request(
                "POST", "/objects/companies/records",
                {"data": {"values": values}}
            )
            if response and response.get("data"):
                record_id = response["data"].get("id", {})
                if isinstance(record_id, dict):
                    record_id = record_id.get("record_id")
                self.stats["companies_created"] += 1
                self.company_cache[company_name.lower().strip()] = record_id
                return record_id
            elif response and response.get("conflict"):
                # Handle conflict - try to get the existing record
                self.stats["companies_updated"] += 1
                return self.find_company(company_name)
        
        return None
    
    def parse_name(self, full_name: str) -> Tuple[str, str]:
        """Parse full name into first and last name."""
        parts = full_name.strip().split()
        if len(parts) == 0:
            return "", ""
        elif len(parts) == 1:
            return parts[0], ""
        else:
            return parts[0], " ".join(parts[1:])
    
    def find_person(self, email: str = None, name: str = None) -> Optional[str]:
        """Find person in Attio."""
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
                return record_id
        
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
                        record_name = name_list[0].get("full_name", "") or name_list[0].get("value", "")
                        if record_name.lower() == name.lower():
                            record_id = record.get("id", {})
                            if isinstance(record_id, dict):
                                record_id = record_id.get("record_id")
                            return record_id
        
        return None
    
    def create_or_update_person(self, contact: Dict, company_name: str, company_record_id: str, row: Dict) -> Optional[str]:
        """Create or update person in Attio."""
        name = contact.get('name', '')
        email = contact.get('email', '')
        title = contact.get('title', '')
        linkedin = contact.get('linkedin', '')
        
        if not name and not email:
            return None
        
        # Check if exists
        existing_id = self.find_person(email, name)
        
        # Parse name
        first_name, last_name = self.parse_name(name) if name else ("", "")
        
        # Build values
        values = {}
        
        if name:
            values["name"] = [{
                "first_name": first_name,
                "last_name": last_name,
                "full_name": name
            }]
        
        if email and '@' in email:
            values["email_addresses"] = [{"email_address": email}]
        
        if title:
            values["job_title"] = [{"value": title}]
        
        if linkedin and 'linkedin.com' in linkedin:
            values["linkedin"] = [{"value": linkedin}]
        
        # Link to company
        if company_record_id:
            values["company"] = [{
                "target_object": "companies",
                "target_record_id": company_record_id
            }]
        
        # Description
        desc_parts = [
            f"🌟 VIP Contact - {row.get('Category', '')}",
            f"🏢 Company: {company_name}",
            f"📊 Tier: {row.get('Tier', 'N/A')} | Priority: {row.get('Priority', 'N/A')}",
            f"📅 Imported: {datetime.now().strftime('%Y-%m-%d')}"
        ]
        values["description"] = [{"value": "\n".join(desc_parts)}]
        
        if existing_id:
            # Update
            response = self._request(
                "PATCH", f"/objects/people/records/{existing_id}",
                {"data": {"values": values}}
            )
            if response:
                self.stats["people_updated"] += 1
                return existing_id
        else:
            # Create
            response = self._request(
                "POST", "/objects/people/records",
                {"data": {"values": values}}
            )
            if response and response.get("data"):
                record_id = response["data"].get("id", {})
                if isinstance(record_id, dict):
                    record_id = record_id.get("record_id")
                self.stats["people_created"] += 1
                return record_id
            elif response and response.get("conflict"):
                self.stats["people_updated"] += 1
                return self.find_person(email, name)
        
        return None
    
    def add_company_to_list(self, company_record_id: str) -> bool:
        """Add company to VIP list."""
        if not self.vip_list_id or not company_record_id:
            return False
        
        response = self._request(
            "POST", f"/lists/{self.vip_list_id}/entries",
            {
                "data": {
                    "parent_record_id": company_record_id
                }
            }
        )
        
        if response:
            self.stats["list_entries_added"] += 1
            return True
        
        return False
    
    def import_record(self, row: Dict, dry_run: bool = False) -> bool:
        """Import a single VIP record (company + contacts)."""
        company_name = row.get('Company', '').strip()
        
        if not company_name:
            self.stats["skipped"] += 1
            return False
        
        if dry_run:
            contacts = self.parse_contacts(row)
            contact_names = [c['name'] for c in contacts if c['name']]
            print(f"   🧪 {company_name} | Tier {row.get('Tier')} | {row.get('Priority')} | Contacts: {', '.join(contact_names) or 'None'}")
            return True
        
        # Create/update company
        company_id = self.create_or_update_company(row)
        
        if not company_id:
            self.stats["failed"] += 1
            return False
        
        # Add to list
        self.add_company_to_list(company_id)
        
        # Create/update contacts
        contacts = self.parse_contacts(row)
        for contact in contacts:
            self.create_or_update_person(contact, company_name, company_id, row)
        
        return True
    
    def run_import(self, dry_run: bool = False, limit: int = None, tier: int = None, priority: str = None):
        """Run the full import."""
        print("\n" + "=" * 70)
        print("🌟 VIP TARGETS → ATTIO IMPORT")
        print("=" * 70)
        print(f"   📁 Source: {VIP_CSV}")
        print(f"   ⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if tier:
            print(f"   🎯 Filter: Tier {tier} only")
        if priority:
            print(f"   🎯 Filter: {priority} priority only")
        
        # Test connection
        if not self.test_connection():
            return
        
        # Setup list
        if not dry_run:
            self.find_or_create_vip_list()
        
        # Load data
        records = self.load_vip_data(tier_filter=tier, priority_filter=priority)
        print(f"\n📂 Loaded {len(records)} VIP records")
        
        if limit:
            records = records[:limit]
            print(f"   Limited to {limit} records")
        
        print(f"\n{'🧪 DRY RUN - Preview Only' if dry_run else '📤 Importing...'}\n")
        
        # Import records
        for i, row in enumerate(records, 1):
            company = row.get('Company', 'Unknown')
            tier_val = row.get('Tier', '?')
            priority_val = row.get('Priority', '?')
            category = row.get('Category', '')[:30]
            
            success = self.import_record(row, dry_run=dry_run)
            
            if not dry_run:
                if success:
                    icon = "✅" if self.stats["companies_created"] == i else "🔄"
                    print(f"   [{i:3d}/{len(records)}] {icon} {company[:35]} | T{tier_val} | {priority_val}")
                else:
                    print(f"   [{i:3d}/{len(records)}] ❌ {company[:35]}")
        
        # Print summary
        if not dry_run:
            self.print_summary()
    
    def print_summary(self):
        """Print import summary."""
        print("\n" + "=" * 70)
        print("📊 IMPORT SUMMARY")
        print("=" * 70)
        print(f"   🏢 Companies created:    {self.stats['companies_created']}")
        print(f"   🔄 Companies updated:    {self.stats['companies_updated']}")
        print(f"   👤 People created:       {self.stats['people_created']}")
        print(f"   🔄 People updated:       {self.stats['people_updated']}")
        print(f"   📋 List entries added:   {self.stats['list_entries_added']}")
        print(f"   ⏭️  Skipped:              {self.stats['skipped']}")
        print(f"   ❌ Failed:               {self.stats['failed']}")
        
        total = self.stats['companies_created'] + self.stats['companies_updated']
        print(f"\n   📈 Total companies: {total}")
        print(f"   📈 Total people: {self.stats['people_created'] + self.stats['people_updated']}")
        
        if self.vip_list_id:
            print(f"\n🔗 View VIP List in Attio:")
            print(f"   https://app.attio.com/{ATTIO_WORKSPACE_SLUG}/lists/{self.vip_list_id}")


def main():
    parser = argparse.ArgumentParser(description="Import VIP targets to Attio")
    parser.add_argument("--dry-run", action="store_true", help="Preview without making changes")
    parser.add_argument("--test", action="store_true", help="Test with first 5 records")
    parser.add_argument("--limit", type=int, help="Limit number of records to import")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3, 4, 5], help="Filter by tier (1-5)")
    parser.add_argument("--priority", type=str, choices=["CRITICAL", "HIGH", "MEDIUM", "LOW"], 
                       help="Filter by priority")
    
    args = parser.parse_args()
    
    limit = 5 if args.test else args.limit
    
    importer = AttioVIPImporter()
    importer.run_import(
        dry_run=args.dry_run,
        limit=limit,
        tier=args.tier,
        priority=args.priority
    )


if __name__ == "__main__":
    main()

