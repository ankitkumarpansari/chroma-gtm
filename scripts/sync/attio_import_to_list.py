#!/usr/bin/env python3
"""
Import Deep Research Companies to Attio with List Management
=============================================================
Creates a dedicated list and imports all deep research companies into it.

Usage:
    python scripts/sync/attio_import_to_list.py create-list   # Create the list only
    python scripts/sync/attio_import_to_list.py import        # Import all companies to list
    python scripts/sync/attio_import_to_list.py quick         # Quick import (first 20)
"""

import os
import json
import requests
import argparse
import time
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class AttioListImporter:
    """Import deep research companies to a dedicated Attio list."""

    def __init__(self):
        self.api_key = os.getenv("ATTIO_API_KEY")
        if not self.api_key:
            print("❌ ATTIO_API_KEY not found in .env file")
            exit(1)

        self.base_url = "https://api.attio.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # List configuration
        self.list_name = "🔬 Deep Research Companies"
        self.list_id = None

        # Load companies data
        self.companies_file = "data/companies/deep_research_companies.json"
        self.companies_data = self.load_companies()

        # Track results
        self.created_companies = []
        self.failed_companies = []
        self.company_ids = []

    def load_companies(self) -> Dict:
        """Load deep research companies from JSON file."""
        filepath = os.path.join(os.path.dirname(__file__), '../../', self.companies_file)

        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            return {}

        with open(filepath, 'r') as f:
            return json.load(f)

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make API request to Attio."""
        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data
            )

            # Handle rate limiting
            if response.status_code == 429:
                print("⏳ Rate limited, waiting 5 seconds...")
                time.sleep(5)
                return self._request(method, endpoint, data)

            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.HTTPError as e:
            return {}  # Silently handle errors for bulk operations
        except Exception as e:
            return {}

    def create_list(self) -> str:
        """Create the Deep Research Companies list in Attio."""
        print(f"\n📋 Creating list: {self.list_name}")

        # First check if list already exists
        endpoint = "lists"
        existing = self._request("GET", endpoint)

        if existing and 'data' in existing:
            for list_item in existing['data']:
                if list_item.get('name') == self.list_name:
                    self.list_id = list_item['id']['list_id']
                    print(f"  ✓ List already exists (ID: {self.list_id})")
                    return self.list_id

        # Create new list with required fields
        data = {
            "data": {
                "parent_object": "companies",
                "name": self.list_name,
                "api_slug": "deep_research_companies",
                "workspace_access": "full-access",
                "workspace_member_access": []
            }
        }

        result = self._request("POST", endpoint, data)

        if result and 'data' in result:
            self.list_id = result['data']['id']['list_id']
            print(f"  ✅ Created list (ID: {self.list_id})")
            return self.list_id
        else:
            print(f"  ❌ Failed to create list")
            return None

    def clean_company_name(self, name: str) -> str:
        """Clean company name for Attio."""
        # Remove problematic characters
        name = name.replace(".ai", " AI")
        name = name.replace(".com", "")
        name = name.replace(".io", " io")
        return name.strip()

    def create_company(self, company: Dict, category: str) -> Optional[str]:
        """Create a company in Attio and return its ID."""
        original_name = company.get("name", "")
        clean_name = self.clean_company_name(original_name)

        if not clean_name:
            return None

        # Build company data
        values = {
            "name": [{"value": clean_name}]
        }

        # Add description if available
        if company.get("description"):
            values["description"] = [{"value": company.get("description", "")[:500]}]

        # Add custom fields with safe values
        research_feature = company.get("research_feature", "")
        if research_feature:
            values["ai_use_cases"] = [{"value": research_feature[:500]}]
            values["intent_signals"] = [{"value": f"Deep research: {research_feature[:200]}"}]

        # Add metadata fields
        values["chroma_advantages"] = [{"value": f"Perfect for {category.replace('_', ' ')}"}]
        values["next_steps"] = [{"value": "Qualify and reach out"}]
        values["technical_fit_score"] = [{"value": 70}]
        values["engagement_score"] = [{"value": 0}]

        # Create company
        endpoint = "objects/companies/records"
        data = {"data": {"values": values}}

        result = self._request("POST", endpoint, data)

        if result and 'data' in result:
            company_id = result['data']['id']['record_id']
            self.company_ids.append(company_id)
            self.created_companies.append(clean_name)
            return company_id
        else:
            self.failed_companies.append(original_name)
            return None

    def add_companies_to_list(self, company_ids: List[str]):
        """Add multiple companies to the list."""
        if not self.list_id:
            print("❌ No list ID available")
            return

        print(f"\n📌 Adding {len(company_ids)} companies to list...")

        endpoint = f"lists/{self.list_id}/entries"

        # Add in batches
        batch_size = 10
        for i in range(0, len(company_ids), batch_size):
            batch = company_ids[i:i+batch_size]

            data = {
                "entries": [{"record_id": cid} for cid in batch]
            }

            result = self._request("POST", endpoint, data)
            if result:
                print(f"  ✅ Added batch {i//batch_size + 1} ({len(batch)} companies)")
            else:
                print(f"  ❌ Failed to add batch {i//batch_size + 1}")

            time.sleep(0.5)  # Rate limiting

    def import_all_companies(self, quick_mode: bool = False):
        """Import all companies and add to list."""
        print("\n🚀 IMPORTING DEEP RESEARCH COMPANIES")
        print("=" * 60)

        # Create or get list
        self.create_list()
        if not self.list_id:
            print("❌ Cannot proceed without list")
            return

        # Import companies
        categories = self.companies_data.get("categories", {})
        total_processed = 0
        max_companies = 20 if quick_mode else 999999

        for category, category_data in categories.items():
            companies = category_data.get("companies", [])

            print(f"\n📁 {category.upper().replace('_', ' ')} ({len(companies)} companies)")
            print("-" * 40)

            for company in companies:
                if total_processed >= max_companies:
                    break

                # Create company
                company_id = self.create_company(company, category)
                if company_id:
                    print(f"  ✅ {self.clean_company_name(company.get('name', ''))}")
                else:
                    print(f"  ⚠️ Skipped: {company.get('name', '')}")

                total_processed += 1

                # Rate limiting
                time.sleep(0.3)

            if total_processed >= max_companies:
                break

        # Add all created companies to the list
        if self.company_ids:
            self.add_companies_to_list(self.company_ids)

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print import summary."""
        print("\n" + "=" * 60)
        print("📊 IMPORT SUMMARY")
        print("=" * 60)
        print(f"  ✅ Successfully created: {len(self.created_companies)} companies")
        print(f"  ❌ Failed/Skipped: {len(self.failed_companies)} companies")
        print(f"  📋 List: {self.list_name}")
        print(f"  🆔 List ID: {self.list_id}")

        if self.created_companies:
            print(f"\n  First 5 created:")
            for name in self.created_companies[:5]:
                print(f"    • {name}")

        if self.failed_companies:
            print(f"\n  Failed companies (first 5):")
            for name in self.failed_companies[:5]:
                print(f"    • {name}")

        print("\n💡 Next Steps:")
        print(f"  1. View list in Attio: https://app.attio.com/lists/{self.list_id}")
        print("  2. Add filters and sorting in Attio UI")
        print("  3. Create pipeline view from this list")
        print("  4. Start outreach to high-priority companies")

    def show_stats(self):
        """Show statistics about companies to import."""
        if not self.companies_data:
            print("❌ No companies data loaded")
            return

        print("\n📊 DEEP RESEARCH COMPANIES TO IMPORT")
        print("=" * 60)

        categories = self.companies_data.get("categories", {})
        total = 0

        for category, category_data in categories.items():
            companies = category_data.get("companies", [])
            count = len(companies)
            total += count
            print(f"  • {category:<30} {count:>3} companies")

        print("-" * 60)
        print(f"  TOTAL: {total} companies")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Import deep research companies to Attio list")
    parser.add_argument("command",
                       choices=["create-list", "import", "quick", "stats"],
                       help="create-list: Just create list | import: Full import | quick: Import 20 | stats: Show stats")

    args = parser.parse_args()
    importer = AttioListImporter()

    if args.command == "create-list":
        importer.create_list()

    elif args.command == "stats":
        importer.show_stats()

    elif args.command == "quick":
        print("\n🧪 QUICK MODE - Importing first 20 companies")
        importer.import_all_companies(quick_mode=True)

    elif args.command == "import":
        importer.show_stats()
        print("\n⚠️  This will import ALL deep research companies to Attio.")
        print(f"   List name: {importer.list_name}")
        response = input("\nContinue? (yes/no): ")

        if response.lower() == 'yes':
            importer.import_all_companies(quick_mode=False)
        else:
            print("❌ Import cancelled")


if __name__ == "__main__":
    main()