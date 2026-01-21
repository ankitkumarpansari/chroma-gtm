#!/usr/bin/env python3
"""
Import Deep Research Companies to Attio
========================================
Imports the 120+ companies with deep research functions into Attio
with all relevant metadata and field mappings.

Usage:
    python scripts/sync/attio_import_research_companies.py import    # Import all companies
    python scripts/sync/attio_import_research_companies.py test      # Test with first 5 companies
    python scripts/sync/attio_import_research_companies.py stats     # Show statistics
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

class AttioCompanyImporter:
    """Import deep research companies to Attio."""

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

        # Load companies data
        self.companies_file = "data/companies/deep_research_companies.json"
        self.companies_data = self.load_companies()

        # Track import results
        self.created = []
        self.updated = []
        self.failed = []
        self.skipped = []

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
            if e.response:
                try:
                    error_detail = e.response.json()
                    print(f"❌ API Error: {error_detail.get('message', str(e))}")
                    if 'validation_errors' in error_detail:
                        for err in error_detail['validation_errors']:
                            print(f"   - {err.get('path', [])}: {err.get('message', '')}")
                except:
                    print(f"❌ API Error: {e}")
                    print(f"Response: {e.response.text}")
            else:
                print(f"❌ API Error: {e}")
            return {}
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return {}

    def check_existing_company(self, name: str) -> Optional[str]:
        """Check if company already exists in Attio."""
        # For now, return None to force creation
        # This is because the search seems unreliable
        return None

    def map_company_to_attio_fields(self, company: Dict, category: str) -> Dict:
        """Map company data to Attio field structure."""

        # Build Attio field values - start with minimal fields that work
        values = {}

        # REQUIRED: Company name
        values["name"] = [{"value": company.get("name", "")}]

        # Standard fields that Attio accepts
        if company.get("description"):
            values["description"] = [{"value": company.get("description", "")[:500]}]  # Limit length

        # Add custom fields one by one - text fields first (they work)
        research_feature = company.get("research_feature", "")
        if research_feature:
            values["ai_use_cases"] = [{"value": research_feature[:500]}]

        values["intent_signals"] = [{"value": "Has deep research functionality requiring vector DB"}]
        values["chroma_advantages"] = [{"value": f"Perfect fit for {research_feature or 'research capabilities'}"}]
        values["next_steps"] = [{"value": "Initial outreach and qualification"}]

        # Number fields
        values["technical_fit_score"] = [{"value": 70}]
        values["engagement_score"] = [{"value": 0}]

        # Add funding info if available
        valuation = company.get("valuation", "")
        if valuation and valuation not in ["Private", "Unknown"]:
            # Extract number from valuation string
            if "$" in valuation:
                try:
                    # Convert $100M+ to 100000000
                    val_str = valuation.replace("$", "").replace("+", "").replace(",", "")
                    if "B" in val_str.upper():
                        multiplier = 1000000000
                        val_str = val_str.upper().replace("B", "")
                    elif "M" in val_str.upper():
                        multiplier = 1000000
                        val_str = val_str.upper().replace("M", "")
                    else:
                        multiplier = 1

                    val_num = float(val_str) * multiplier
                    values["funding_raised_usd"] = [{"value": val_num}]
                except:
                    pass

        # Remove any None values
        values = {k: v for k, v in values.items() if v[0]["value"] is not None}

        return values

    def create_or_update_company(self, company: Dict, category: str) -> bool:
        """Create or update a company in Attio."""
        name = company.get("name", "")

        if not name:
            print(f"  ⚠️ Skipping company with no name")
            self.skipped.append(company)
            return False

        # Check if exists
        existing_id = self.check_existing_company(name)

        # Map fields
        values = self.map_company_to_attio_fields(company, category)

        if existing_id:
            # Update existing
            endpoint = f"objects/companies/records/{existing_id}"
            data = {"data": {"values": values}}

            result = self._request("PATCH", endpoint, data)

            if result:
                print(f"  ✅ Updated: {name}")
                self.updated.append(name)
                return True
            else:
                print(f"  ❌ Failed to update: {name}")
                self.failed.append(name)
                return False
        else:
            # Create new - ensure name is included
            endpoint = "objects/companies/records"

            # Make sure we have a name field
            if "name" not in values:
                values["name"] = [{"value": name}]

            data = {"data": {"values": values}}

            result = self._request("POST", endpoint, data)

            if result:
                print(f"  ✅ Created: {name}")
                self.created.append(name)
                return True
            else:
                print(f"  ❌ Failed to create: {name}")
                self.failed.append(name)
                return False

    def import_companies(self, test_mode: bool = False):
        """Import all companies to Attio."""
        print("\n🚀 IMPORTING DEEP RESEARCH COMPANIES TO ATTIO")
        print("=" * 60)

        if not self.companies_data:
            print("❌ No companies data loaded")
            return

        categories = self.companies_data.get("categories", {})
        total_companies = 0

        for category, category_data in categories.items():
            companies = category_data.get("companies", [])

            if test_mode and total_companies >= 5:
                break

            print(f"\n📁 {category.upper().replace('_', ' ')}")
            print("-" * 40)

            for company in companies:
                if test_mode and total_companies >= 5:
                    break

                self.create_or_update_company(company, category)
                total_companies += 1

                # Rate limiting
                time.sleep(0.5)

        # Print summary
        print("\n" + "=" * 60)
        print("📊 IMPORT SUMMARY")
        print("=" * 60)
        print(f"  ✅ Created: {len(self.created)} companies")
        print(f"  🔄 Updated: {len(self.updated)} companies")
        print(f"  ❌ Failed: {len(self.failed)} companies")
        print(f"  ⏭️  Skipped: {len(self.skipped)} companies")
        print(f"  📋 Total processed: {total_companies}")

        if self.failed:
            print(f"\n❌ Failed companies: {', '.join(self.failed[:10])}")

    def show_stats(self):
        """Show statistics about companies to import."""
        if not self.companies_data:
            print("❌ No companies data loaded")
            return

        print("\n📊 DEEP RESEARCH COMPANIES STATISTICS")
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

        print("\n📋 Key Insights:")
        insights = self.companies_data.get("key_insights", {})
        if insights:
            print(f"  • Total addressable market: {insights.get('total_addressable_market', 'N/A')}")

            segments = insights.get("highest_value_segments", [])
            if segments:
                print("\n  Highest value segments:")
                for segment in segments:
                    print(f"    - {segment}")

            features = insights.get("common_research_features", [])
            if features:
                print("\n  Common research features:")
                for feature in features[:5]:
                    print(f"    - {feature}")

    def create_list(self, name: str, description: str) -> Optional[str]:
        """Create a list in Attio."""
        endpoint = "lists"
        data = {
            "data": {
                "parent_object": "companies",
                "name": name,
                "api_slug": name.lower().replace(" ", "_").replace("-", "_")
            }
        }

        result = self._request("POST", endpoint, data)

        if result and 'data' in result:
            return result['data']['id']['list_id']
        return None

    def add_companies_to_list(self, list_id: str, company_ids: List[str]):
        """Add companies to a list."""
        endpoint = f"lists/{list_id}/entries"

        for company_id in company_ids:
            data = {
                "entries": [{"record_id": company_id}]
            }
            self._request("POST", endpoint, data)
            time.sleep(0.2)  # Rate limiting


def main():
    parser = argparse.ArgumentParser(description="Import deep research companies to Attio")
    parser.add_argument("command",
                       choices=["import", "test", "stats"],
                       help="import: Import all | test: Test with 5 | stats: Show statistics")

    args = parser.parse_args()
    importer = AttioCompanyImporter()

    if args.command == "stats":
        importer.show_stats()

    elif args.command == "test":
        print("\n🧪 TEST MODE - Importing first 5 companies only")
        importer.import_companies(test_mode=True)

    elif args.command == "import":
        importer.show_stats()
        print("\n⚠️  This will import all companies to Attio.")
        response = input("Continue? (yes/no): ")

        if response.lower() == 'yes':
            importer.import_companies(test_mode=False)

            print("\n💡 Next steps:")
            print("  1. Go to Attio and review imported companies")
            print("  2. Create smart lists using the filter criteria")
            print("  3. Set up pipeline views by Buying Stage")
            print("  4. Create dashboards for tracking")
        else:
            print("❌ Import cancelled")


if __name__ == "__main__":
    main()