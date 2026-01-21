#!/usr/bin/env python3
"""
Attio CRM Integration for Claude Code
======================================
Enhanced Attio integration optimized for use within Claude Code.

Features:
- Quick company/contact search
- Bulk operations support
- Rich field mapping
- Pipeline management
- Note/activity tracking
- Custom attribute support

Usage:
    python scripts/sync/attio_claude_integration.py search "company name"
    python scripts/sync/attio_claude_integration.py create-company "Name" --domain "example.com"
    python scripts/sync/attio_claude_integration.py list-companies --limit 10
    python scripts/sync/attio_claude_integration.py update-company "id" --field "stage" --value "qualified"
"""

import os
import json
import requests
import argparse
from datetime import datetime
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv
import sys

load_dotenv()

class AttioClient:
    """Enhanced Attio CRM client for Claude Code operations."""

    def __init__(self):
        self.api_key = os.getenv("ATTIO_API_KEY")
        if not self.api_key:
            print("❌ ATTIO_API_KEY not found in .env file")
            sys.exit(1)

        self.base_url = "https://api.attio.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

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
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.HTTPError as e:
            print(f"❌ API Error: {e}")
            print(f"Response: {e.response.text}")
            return {}
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return {}

    # ========== SEARCH OPERATIONS ==========

    def search_companies(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for companies by name or domain."""
        endpoint = "objects/companies/records/query"
        data = {
            "filter": {
                "or": [
                    {"attribute": "name", "relation": "contains", "value": query},
                    {"attribute": "domains", "relation": "contains", "value": query}
                ]
            },
            "limit": limit
        }
        result = self._request("POST", endpoint, data)
        return result.get("data", [])

    def search_people(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for people by name or email."""
        endpoint = "objects/people/records/query"
        data = {
            "filter": {
                "or": [
                    {"attribute": "name", "relation": "contains", "value": query},
                    {"attribute": "email_addresses", "relation": "contains", "value": query}
                ]
            },
            "limit": limit
        }
        result = self._request("POST", endpoint, data)
        return result.get("data", [])

    # ========== COMPANY OPERATIONS ==========

    def create_company(self, name: str, **kwargs) -> Dict:
        """Create a new company with optional attributes."""
        endpoint = "objects/companies/records"

        data = {
            "data": {
                "values": {
                    "name": [{"value": name}]
                }
            }
        }

        # Add optional fields
        if kwargs.get("domain"):
            data["data"]["values"]["domains"] = [{"domain": kwargs["domain"]}]
        if kwargs.get("description"):
            data["data"]["values"]["description"] = [{"value": kwargs["description"]}]
        if kwargs.get("industry"):
            data["data"]["values"]["industry"] = [{"value": kwargs["industry"]}]
        if kwargs.get("employee_count"):
            data["data"]["values"]["employee_count"] = [{"value": kwargs["employee_count"]}]

        result = self._request("POST", endpoint, data)
        return result.get("data", {})

    def update_company(self, company_id: str, updates: Dict[str, Any]) -> Dict:
        """Update company attributes."""
        endpoint = f"objects/companies/records/{company_id}"

        values = {}
        for field, value in updates.items():
            values[field] = [{"value": value}]

        data = {"data": {"values": values}}
        result = self._request("PATCH", endpoint, data)
        return result.get("data", {})

    def get_company(self, company_id: str) -> Dict:
        """Get company details by ID."""
        endpoint = f"objects/companies/records/{company_id}"
        result = self._request("GET", endpoint)
        return result.get("data", {})

    def list_companies(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """List all companies with pagination."""
        endpoint = "objects/companies/records/query"
        data = {
            "sorts": [{"attribute": "created_at", "direction": "desc"}],
            "limit": limit,
            "offset": offset
        }
        result = self._request("POST", endpoint, data)
        return result.get("data", [])

    # ========== PEOPLE OPERATIONS ==========

    def create_person(self, name: str, email: str, **kwargs) -> Dict:
        """Create a new person/contact."""
        endpoint = "objects/people/records"

        data = {
            "data": {
                "values": {
                    "name": [{"first_name": name.split()[0], "last_name": " ".join(name.split()[1:])}],
                    "email_addresses": [{"email_address": email}]
                }
            }
        }

        # Add optional fields
        if kwargs.get("company_id"):
            data["data"]["values"]["company"] = [{"target_record_id": kwargs["company_id"]}]
        if kwargs.get("title"):
            data["data"]["values"]["job_title"] = [{"value": kwargs["title"]}]
        if kwargs.get("phone"):
            data["data"]["values"]["phone_numbers"] = [{"phone_number": kwargs["phone"]}]

        result = self._request("POST", endpoint, data)
        return result.get("data", {})

    # ========== NOTE OPERATIONS ==========

    def add_note(self, parent_object: str, parent_id: str, title: str, content: str) -> Dict:
        """Add a note to a company or person."""
        endpoint = "notes"

        data = {
            "data": {
                "title": title,
                "content": content,
                "parent_object": parent_object,  # "companies" or "people"
                "parent_record_id": parent_id
            }
        }

        result = self._request("POST", endpoint, data)
        return result.get("data", {})

    # ========== LIST OPERATIONS ==========

    def add_to_list(self, list_id: str, record_ids: List[str]) -> Dict:
        """Add records to a list."""
        endpoint = f"lists/{list_id}/entries"

        data = {
            "entries": [{"record_id": rid} for rid in record_ids]
        }

        result = self._request("POST", endpoint, data)
        return result.get("data", {})

    def get_list_entries(self, list_id: str, limit: int = 50) -> List[Dict]:
        """Get entries in a list."""
        endpoint = f"lists/{list_id}/entries"
        params = f"?limit={limit}"
        result = self._request("GET", endpoint + params)
        return result.get("data", [])

    # ========== UTILITY FUNCTIONS ==========

    def test_connection(self) -> bool:
        """Test API connection."""
        # Test by fetching workspace info
        endpoint = "objects/companies/records/query"
        data = {"limit": 1}
        result = self._request("POST", endpoint, data)
        if result:
            print(f"✅ Connected to Attio successfully!")
            print(f"   Test query returned: {len(result.get('data', []))} companies")
            return True
        return False

    def get_workspace_info(self) -> Dict:
        """Get workspace information."""
        result = self._request("GET", "workspace")
        return result.get("data", {})


def main():
    """CLI interface for Attio operations."""
    parser = argparse.ArgumentParser(description="Attio CRM Integration for Claude Code")
    parser.add_argument("command", help="Command to execute",
                       choices=["test", "search", "create-company", "create-person",
                               "list-companies", "add-note", "update-company"])
    parser.add_argument("query", nargs="?", help="Search query or name")
    parser.add_argument("--domain", help="Company domain")
    parser.add_argument("--email", help="Person email")
    parser.add_argument("--title", help="Job title")
    parser.add_argument("--company-id", help="Company ID for association")
    parser.add_argument("--field", help="Field to update")
    parser.add_argument("--value", help="Value to set")
    parser.add_argument("--limit", type=int, default=10, help="Result limit")
    parser.add_argument("--note-title", help="Note title")
    parser.add_argument("--note-content", help="Note content")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    client = AttioClient()

    if args.command == "test":
        client.test_connection()

    elif args.command == "search":
        if not args.query:
            print("❌ Please provide a search query")
            return

        print(f"\n🔍 Searching for '{args.query}'...\n")

        companies = client.search_companies(args.query, args.limit)
        if companies:
            print("📊 COMPANIES:")
            for i, company in enumerate(companies, 1):
                values = company.get("values", {})
                name = values.get("name", [{}])[0].get("value", "Unknown")
                domains = values.get("domains", [])
                domain = domains[0].get("domain") if domains else "No domain"
                print(f"{i}. {name} ({domain})")
                print(f"   ID: {company.get('id', 'N/A')}")

        people = client.search_people(args.query, args.limit)
        if people:
            print("\n👥 PEOPLE:")
            for i, person in enumerate(people, 1):
                values = person.get("values", {})
                name_obj = values.get("name", [{}])[0]
                name = f"{name_obj.get('first_name', '')} {name_obj.get('last_name', '')}".strip()
                emails = values.get("email_addresses", [])
                email = emails[0].get("email_address") if emails else "No email"
                print(f"{i}. {name} ({email})")
                print(f"   ID: {person.get('id', 'N/A')}")

    elif args.command == "create-company":
        if not args.query:
            print("❌ Please provide a company name")
            return

        company = client.create_company(
            name=args.query,
            domain=args.domain
        )

        if company:
            print(f"✅ Created company: {args.query}")
            print(f"   ID: {company.get('id', 'N/A')}")
            if args.json:
                print(json.dumps(company, indent=2))

    elif args.command == "create-person":
        if not args.query or not args.email:
            print("❌ Please provide both name and email")
            return

        person = client.create_person(
            name=args.query,
            email=args.email,
            title=args.title,
            company_id=args.company_id
        )

        if person:
            print(f"✅ Created person: {args.query}")
            print(f"   ID: {person.get('id', 'N/A')}")

    elif args.command == "list-companies":
        companies = client.list_companies(limit=args.limit)

        print(f"\n📊 Recent Companies ({len(companies)} results):\n")
        for i, company in enumerate(companies, 1):
            values = company.get("values", {})
            name = values.get("name", [{}])[0].get("value", "Unknown")
            domains = values.get("domains", [])
            domain = domains[0].get("domain") if domains else "No domain"
            print(f"{i}. {name}")
            print(f"   Domain: {domain}")
            print(f"   ID: {company.get('id', 'N/A')}")
            print()

    elif args.command == "add-note":
        if not args.query or not args.note_title or not args.note_content:
            print("❌ Please provide record ID, note title, and content")
            return

        # Determine if it's a company or person ID
        object_type = "companies"  # Default, could be enhanced with detection

        note = client.add_note(
            parent_object=object_type,
            parent_id=args.query,
            title=args.note_title,
            content=args.note_content
        )

        if note:
            print(f"✅ Added note to {object_type[:-1]}")

    elif args.command == "update-company":
        if not args.query or not args.field or not args.value:
            print("❌ Please provide company ID, field, and value")
            return

        updates = {args.field: args.value}
        company = client.update_company(args.query, updates)

        if company:
            print(f"✅ Updated company {args.query}")
            print(f"   {args.field} = {args.value}")


if __name__ == "__main__":
    main()