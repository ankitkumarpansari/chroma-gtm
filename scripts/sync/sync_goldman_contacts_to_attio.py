#!/usr/bin/env python3
"""
Sync Goldman Sachs Contacts to Attio

This script syncs Goldman Sachs contacts with all metadata to Attio CRM.
It creates/updates people records and associates them with Goldman Sachs company.

Usage:
    python sync_goldman_contacts_to_attio.py
    python sync_goldman_contacts_to_attio.py --test  # Test connection only
    python sync_goldman_contacts_to_attio.py --limit 5  # Sync first 5 only
"""

import os
import json
import requests
import time
import argparse
from datetime import datetime
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

# Attio Configuration
ATTIO_API_KEY = os.getenv("ATTIO_API_KEY")
ATTIO_BASE_URL = "https://api.attio.com/v2"
ATTIO_WORKSPACE_SLUG = "chromadb"

# Goldman Sachs contacts data
GOLDMAN_CONTACTS = [
    {
        "name": "Daniel Marcu",
        "title": "Partner & Global Head of AI Engineering and Science",
        "company": "Goldman Sachs",
        "location": "New York, NY",
        "tier": "Tier 1 - Executive Decision-Maker",
        "why_they_fit_icp": "Runs all AI engineering at GS. Direct decision-maker for AI infrastructure including vector DBs",
        "linkedin_search_url": "https://www.linkedin.com/search/results/people/?keywords=Daniel%20Marcu%20Goldman%20Sachs"
    },
    {
        "name": "Nishith Desai",
        "title": "Managing Director & CDO, Global Head of Investment Banking Engineering",
        "company": "Goldman Sachs",
        "location": "New York, NY",
        "tier": "Tier 1 - Executive Decision-Maker",
        "why_they_fit_icp": "CDO + Global Head of Engineering. Would own data infrastructure decisions",
        "linkedin_search_url": "https://www.linkedin.com/search/results/people/?keywords=Nishith%20Desai%20Goldman%20Sachs"
    },
    {
        "name": "Steven X. Chen CFA",
        "title": "Managing Director, Global Head of Core Quant Strategists",
        "company": "Goldman Sachs",
        "location": "New York, NY",
        "tier": "Tier 1 - Executive Decision-Maker",
        "why_they_fit_icp": "Former CTO Office at Bloomberg. Built AI products. Understands quant analytics infrastructure",
        "linkedin_search_url": "https://www.linkedin.com/search/results/people/?keywords=Steven%20Chen%20CFA%20Goldman%20Sachs"
    },
    {
        "name": "Ankur Khare",
        "title": "Head of Data & Analytics Engineering, Global Banking & Markets",
        "company": "Goldman Sachs",
        "location": "New York, NY",
        "tier": "Tier 1 - Executive Decision-Maker",
        "why_they_fit_icp": "Owns data infrastructure for Global Banking & Markets. Perfect buyer persona",
        "linkedin_search_url": "https://www.linkedin.com/search/results/people/?keywords=Ankur%20Khare%20Goldman%20Sachs"
    },
    {
        "name": "Raunak Sinha",
        "title": "GenAI Scientist, Applied AI Scientist - NLP",
        "company": "Goldman Sachs",
        "location": "New York, NY",
        "tier": "Tier 2 - Technical Leader",
        "why_they_fit_icp": "Ex-IBM Research, PayPal, UCLA NLP. Building GenAI products that need RAG/vector search",
        "linkedin_search_url": "https://www.linkedin.com/search/results/people/?keywords=Raunak%20Sinha%20Goldman%20Sachs"
    },
    {
        "name": "Riya Gupta",
        "title": "ML Research Scientist - Generative AI & LLM",
        "company": "Goldman Sachs",
        "location": "New York, NY",
        "tier": "Tier 2 - Technical Leader",
        "why_they_fit_icp": "Working on multimodal learning and Generative AI. Direct user of vector DBs for RAG",
        "linkedin_search_url": "https://www.linkedin.com/search/results/people/?keywords=Riya%20Gupta%20Goldman%20Sachs"
    },
    {
        "name": "Qian Zhao",
        "title": "Head of Applied AI US (ML Quant)",
        "company": "Goldman Sachs",
        "location": "New York, NY",
        "tier": "Tier 2 - Technical Leader",
        "why_they_fit_icp": "Leads Applied AI team. Time-series modeling + AI/ML engineering",
        "linkedin_search_url": "https://www.linkedin.com/search/results/people/?keywords=Qian%20Zhao%20Goldman%20Sachs"
    },
    {
        "name": "Suryakiran S.",
        "title": "Software Engineer - Search",
        "company": "Goldman Sachs",
        "location": "New York, NY",
        "tier": "Tier 2 - Technical Leader",
        "why_they_fit_icp": "Building search tools using Elasticsearch. Improved search speeds 3x. Direct competitor evaluation",
        "linkedin_search_url": "https://www.linkedin.com/search/results/people/?keywords=Suryakiran%20Goldman%20Sachs"
    },
    {
        "name": "Kunaal Ahuja",
        "title": "VP, Global Co-head Private Markets Quant & AI Strats",
        "company": "Goldman Sachs",
        "location": "New York, NY",
        "tier": "Tier 3 - VP Engineering",
        "why_they_fit_icp": "Leads 16-person AI Strats team globally. 3K followers",
        "linkedin_search_url": "https://www.linkedin.com/search/results/people/?keywords=Kunaal%20Ahuja%20Goldman%20Sachs"
    },
    {
        "name": "Simranjot Sandhu",
        "title": "VP, Compliance Engineering",
        "company": "Goldman Sachs",
        "location": "New York, NY",
        "tier": "Tier 3 - VP Engineering",
        "why_they_fit_icp": "ML background (ex-FactSet). Builds data platforms",
        "linkedin_search_url": "https://www.linkedin.com/search/results/people/?keywords=Simranjot%20Sandhu%20Goldman%20Sachs"
    },
    {
        "name": "Vaishnavi Rayapati",
        "title": "Senior AI/ML Engineer, Conversational AI Architect",
        "company": "Goldman Sachs",
        "location": "New York, NY",
        "tier": "Tier 3 - VP Engineering",
        "why_they_fit_icp": "Building conversational AI = needs semantic search",
        "linkedin_search_url": "https://www.linkedin.com/search/results/people/?keywords=Vaishnavi%20Rayapati%20Goldman%20Sachs"
    }
]


class AttioContactSync:
    """Sync contacts to Attio CRM."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or ATTIO_API_KEY
        if not self.api_key:
            print("❌ ATTIO_API_KEY not set in .env")
            self.enabled = False
        else:
            self.enabled = True
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

    def _request(self, method: str, endpoint: str, json_data: dict = None) -> Optional[dict]:
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
                print(f"   ⚠️ API error: {response.status_code} - {response.text[:500]}")
                return None

        except Exception as e:
            print(f"   ❌ Request failed: {e}")
            return None

    def find_or_create_company(self, company_name: str, domain: str = None) -> Optional[str]:
        """Find or create Goldman Sachs company record."""
        # First try to find by domain
        if domain:
            response = self._request(
                "POST",
                "/objects/companies/records/query",
                {
                    "filter": {
                        "domains": {"$contains": domain}
                    }
                }
            )
            if response and response.get("data"):
                return response["data"][0]["id"]["record_id"]

        # Try to find by name
        response = self._request(
            "POST",
            "/objects/companies/records/query",
            {
                "filter": {
                    "name": {"$contains": company_name}
                }
            }
        )

        if response and response.get("data"):
            return response["data"][0]["id"]["record_id"]

        # Create new company
        values = {
            "name": [{"value": company_name}]
        }

        if domain:
            values["domains"] = [{"domain": domain}]

        response = self._request(
            "POST",
            "/objects/companies/records",
            {"data": {"values": values}}
        )

        if response:
            return response.get("data", {}).get("id", {}).get("record_id")
        return None

    def find_person(self, name: str, email: str = None) -> Optional[dict]:
        """Search for existing person in Attio."""
        # Try to find by email first (most accurate)
        if email:
            response = self._request(
                "POST",
                "/objects/people/records/query",
                {
                    "filter": {
                        "email_addresses": {"$contains": email}
                    }
                }
            )
            if response and response.get("data"):
                return response["data"][0]

        # Fallback to name search
        response = self._request(
            "POST",
            "/objects/people/records/query",
            {
                "filter": {
                    "name": {"$contains": name}
                }
            }
        )

        if response and response.get("data"):
            # Be more careful with name matches - check if it's the same person
            for person in response["data"]:
                person_name = person.get("values", {}).get("name", [{}])[0].get("value", "")
                if person_name.lower() == name.lower():
                    return person
        return None

    def create_or_update_person(self, contact: dict, company_id: str) -> Optional[str]:
        """Create or update a person record in Attio with all metadata."""

        # Check if person already exists
        existing_person = self.find_person(contact["name"])

        # Parse the name into first and last
        name_parts = contact["name"].strip().split()
        if len(name_parts) >= 2:
            # Handle cases like "Steven X. Chen CFA"
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:])  # Everything after first name
        else:
            first_name = name_parts[0] if name_parts else contact["name"]
            last_name = ""

        # Prepare values - only use standard Attio fields
        values = {
            "name": [{
                "first_name": first_name,
                "last_name": last_name,
                "full_name": contact["name"]
            }],
            "job_title": [{"value": contact["title"]}]
        }

        # Add all metadata to description/notes field
        notes_content = f"""
Location: {contact['location']}

Tier: {contact['tier']}

Why They Fit ICP:
{contact['why_they_fit_icp']}

LinkedIn Search:
{contact['linkedin_search_url']}
"""
        values["description"] = [{"value": notes_content}]

        if existing_person:
            # Update existing person
            person_id = existing_person["id"]["record_id"]
            response = self._request(
                "PATCH",
                f"/objects/people/records/{person_id}",
                {"data": {"values": values}}
            )
        else:
            # Create new person
            response = self._request(
                "POST",
                "/objects/people/records",
                {"data": {"values": values}}
            )
            if response:
                person_id = response.get("data", {}).get("id", {}).get("record_id")
            else:
                return None

        # Associate person with company
        if person_id and company_id:
            self.associate_person_with_company(person_id, company_id)

        return person_id

    def associate_person_with_company(self, person_id: str, company_id: str) -> bool:
        """Associate a person with a company in Attio."""
        # Update person record with company association
        response = self._request(
            "PATCH",
            f"/objects/people/records/{person_id}",
            {
                "data": {
                    "values": {
                        "company": [{
                            "target_object": "companies",
                            "target_record_id": company_id
                        }]
                    }
                }
            }
        )
        return response is not None

    def sync_all_contacts(self, contacts: List[dict], delay: float = 0.5, limit: int = None) -> dict:
        """Sync all Goldman Sachs contacts to Attio."""
        if not self.enabled:
            return {"error": "Attio not configured"}

        if limit:
            contacts = contacts[:limit]

        print(f"\n📤 Syncing {len(contacts)} Goldman Sachs contacts to Attio...")
        print()

        # First, find or create Goldman Sachs company
        print("🏢 Finding/creating Goldman Sachs company...")
        goldman_company_id = self.find_or_create_company("Goldman Sachs", "goldmansachs.com")

        if not goldman_company_id:
            print("❌ Failed to find or create Goldman Sachs company")
            return {"error": "Could not create company"}

        print(f"✅ Goldman Sachs company ready (ID: {goldman_company_id})")
        print()

        results = {
            "total": len(contacts),
            "created": 0,
            "updated": 0,
            "failed": 0,
            "contacts_processed": []
        }

        for i, contact in enumerate(contacts, 1):
            name = contact["name"]
            print(f"[{i}/{len(contacts)}] Processing {name}...")

            person_id = self.create_or_update_person(contact, goldman_company_id)

            if person_id:
                results["created"] += 1
                results["contacts_processed"].append(name)
                print(f"   ✅ {name} - {contact['title']}")
            else:
                results["failed"] += 1
                print(f"   ❌ {name} - Failed to sync")

            time.sleep(delay)

        return results


def test_connection():
    """Test Attio API connection."""
    print("🔗 Testing Attio connection...")

    if not ATTIO_API_KEY:
        print("❌ ATTIO_API_KEY not set in .env")
        return False

    print(f"   API key: {ATTIO_API_KEY[:20]}...")

    sync = AttioContactSync()
    response = sync._request("GET", "/objects")

    if response is not None:
        print("✅ Attio connection successful!")
        print("   Available objects:", ", ".join([obj["api_slug"] for obj in response.get("data", [])[:5]]))
        return True
    else:
        print("❌ Attio connection failed")
        return False


def main():
    parser = argparse.ArgumentParser(description="Sync Goldman Sachs contacts to Attio")
    parser.add_argument("--test", action="store_true", help="Test connection only")
    parser.add_argument("--limit", type=int, help="Limit number of contacts to sync")

    args = parser.parse_args()

    if args.test:
        test_connection()
        return

    if not test_connection():
        return

    print(f"\n📊 Contacts to sync: {len(GOLDMAN_CONTACTS)}")

    # Sync contacts
    sync = AttioContactSync()
    results = sync.sync_all_contacts(GOLDMAN_CONTACTS, limit=args.limit)

    # Summary
    print("\n" + "=" * 60)
    print("📊 SYNC COMPLETE")
    print("=" * 60)
    print(f"   Total processed: {results.get('total', 0)}")
    print(f"   ✅ Created/Updated: {results.get('created', 0)}")
    print(f"   ❌ Failed: {results.get('failed', 0)}")

    if results.get('contacts_processed'):
        print(f"\n   Contacts synced:")
        for contact in results['contacts_processed']:
            print(f"      • {contact}")

    print(f"\n🔗 View in Attio: https://app.attio.com/{ATTIO_WORKSPACE_SLUG}")
    print("\nNote: Contacts are associated with Goldman Sachs company record")


if __name__ == "__main__":
    main()