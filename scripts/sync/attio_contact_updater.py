#!/usr/bin/env python3
"""
Attio Contact Discovery & Update System
========================================
Continuously find and update contacts for target companies in Attio.

Features:
- Add new contacts to companies
- Update contact information
- Track discovery source
- Score contact relevance
- Add engagement notes

Usage:
    python scripts/sync/attio_contact_updater.py add-contact    # Add single contact
    python scripts/sync/attio_contact_updater.py bulk-import    # Import from CSV
    python scripts/sync/attio_contact_updater.py search-guide   # Show search instructions
"""

import os
import json
import csv
import requests
import argparse
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class AttioContactUpdater:
    """Manage contacts in Attio CRM."""

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

        # Target companies with their Attio IDs (we'll fetch these)
        self.target_companies = {
            "Vectara": {"priority": 1, "focus": "RAG platform"},
            "Perplexity AI": {"priority": 2, "focus": "AI search"},
            "Hebbia": {"priority": 2, "focus": "Enterprise RAG"},
            "Glean": {"priority": 2, "focus": "Enterprise search"},
            "AlphaSense": {"priority": 2, "focus": "Financial research"},
            "Clay": {"priority": 2, "focus": "Sales intelligence"},
            "Gong": {"priority": 2, "focus": "Revenue intelligence"}
        }

        # High-value titles to look for
        self.target_titles = {
            "technical_champion": [
                "ML Engineer", "Machine Learning Engineer",
                "AI Engineer", "AI Platform Engineer",
                "Staff Engineer", "Principal Engineer",
                "Senior ML Engineer", "Head of AI",
                "Head of Machine Learning", "Director of AI"
            ],
            "decision_maker": [
                "CTO", "Chief Technology Officer",
                "VP Engineering", "VP of Engineering",
                "Director of Engineering", "Engineering Manager"
            ],
            "influencer": [
                "Product Manager", "Head of Product",
                "Data Scientist", "Research Scientist"
            ]
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
        except Exception as e:
            print(f"❌ API Error: {e}")
            return {}

    def find_company_id(self, company_name: str) -> Optional[str]:
        """Find company ID in Attio."""
        endpoint = "objects/companies/records/query"
        data = {
            "filter": {
                "name": {"$contains": company_name.replace(" AI", "").replace(".com", "")}
            },
            "limit": 5
        }

        result = self._request("POST", endpoint, data)

        if result and 'data' in result and result['data']:
            # Try to find exact match first
            for company in result['data']:
                values = company.get('values', {})
                name = values.get('name', [{}])[0].get('value', '')
                if company_name.lower() in name.lower() or name.lower() in company_name.lower():
                    return company['id']['record_id']
            # Return first match if no exact match
            return result['data'][0]['id']['record_id']

        return None

    def categorize_contact(self, title: str) -> str:
        """Categorize contact based on title."""
        title_lower = title.lower()

        for category, titles in self.target_titles.items():
            for target_title in titles:
                if target_title.lower() in title_lower:
                    return category

        # Default categorization
        if any(word in title_lower for word in ["engineer", "developer", "architect"]):
            return "technical_champion"
        elif any(word in title_lower for word in ["director", "vp", "head", "chief"]):
            return "decision_maker"
        else:
            return "influencer"

    def score_contact_relevance(self, title: str, company_priority: int) -> int:
        """Score contact relevance (1-100)."""
        score = 50  # Base score

        title_lower = title.lower()

        # Title scoring
        if "ml" in title_lower or "machine learning" in title_lower:
            score += 30
        elif "ai" in title_lower:
            score += 25
        elif "cto" in title_lower or "vp eng" in title_lower:
            score += 25
        elif "head" in title_lower or "director" in title_lower:
            score += 20
        elif "staff" in title_lower or "principal" in title_lower:
            score += 15
        elif "senior" in title_lower:
            score += 10

        # Company priority bonus
        if company_priority == 1:
            score += 10
        elif company_priority == 2:
            score += 5

        return min(score, 100)

    def add_contact(self, contact_data: Dict) -> bool:
        """Add a contact to Attio."""
        endpoint = "objects/people/records"

        # Prepare contact data
        values = {
            "name": [{
                "first_name": contact_data.get("first_name", ""),
                "last_name": contact_data.get("last_name", "")
            }]
        }

        # Add email if provided
        if contact_data.get("email"):
            values["email_addresses"] = [{"email_address": contact_data["email"]}]

        # Add job title
        if contact_data.get("title"):
            values["job_title"] = [{"value": contact_data["title"]}]

        # Link to company
        if contact_data.get("company_id"):
            values["company"] = [{"target_record_id": contact_data["company_id"]}]

        # Add custom fields
        if contact_data.get("linkedin_url"):
            values["linkedin"] = [{"value": contact_data["linkedin_url"]}]

        # Add notes with metadata
        notes = f"""
Contact Category: {contact_data.get('category', 'Unknown')}
Relevance Score: {contact_data.get('relevance_score', 0)}
Discovery Source: {contact_data.get('source', 'Manual')}
Discovery Date: {datetime.now().strftime('%Y-%m-%d')}
Focus Area: {contact_data.get('company_focus', '')}
Notes: {contact_data.get('notes', '')}
        """.strip()

        data = {"data": {"values": values}}

        result = self._request("POST", endpoint, data)

        if result and 'data' in result:
            contact_id = result['data']['id']['record_id']
            print(f"✅ Added contact: {contact_data.get('first_name')} {contact_data.get('last_name')} at {contact_data.get('company_name')}")

            # Add note to contact
            self.add_note_to_contact(contact_id, notes)
            return True
        else:
            print(f"❌ Failed to add contact: {contact_data.get('first_name')} {contact_data.get('last_name')}")
            return False

    def add_note_to_contact(self, contact_id: str, note_content: str):
        """Add a note to a contact."""
        endpoint = "notes"
        data = {
            "data": {
                "title": "Contact Discovery Info",
                "content": note_content,
                "parent_object": "people",
                "parent_record_id": contact_id
            }
        }

        self._request("POST", endpoint, data)

    def bulk_import_from_csv(self, csv_path: str):
        """Import contacts from CSV file."""
        if not os.path.exists(csv_path):
            print(f"❌ File not found: {csv_path}")
            return

        print(f"\n📥 Importing contacts from: {csv_path}")
        print("=" * 60)

        success_count = 0
        fail_count = 0

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Skip empty rows
                if not row.get('Contact Name') or not row.get('Company'):
                    continue

                # Parse name
                name_parts = row['Contact Name'].strip().split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ""

                # Get company info
                company_name = row['Company']
                company_info = self.target_companies.get(company_name, {})

                # Find company ID
                company_id = self.find_company_id(company_name)
                if not company_id:
                    print(f"⚠️ Company not found in Attio: {company_name}")
                    continue

                # Prepare contact data
                contact_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": row.get('Email', ''),
                    "title": row.get('Title', ''),
                    "company_name": company_name,
                    "company_id": company_id,
                    "linkedin_url": row.get('LinkedIn URL', ''),
                    "category": self.categorize_contact(row.get('Title', '')),
                    "relevance_score": self.score_contact_relevance(
                        row.get('Title', ''),
                        company_info.get('priority', 3)
                    ),
                    "source": row.get('Source', 'LinkedIn'),
                    "company_focus": company_info.get('focus', ''),
                    "notes": row.get('Notes', '')
                }

                # Add contact
                if self.add_contact(contact_data):
                    success_count += 1
                else:
                    fail_count += 1

        print("\n" + "=" * 60)
        print(f"✅ Successfully imported: {success_count} contacts")
        print(f"❌ Failed to import: {fail_count} contacts")

    def create_search_instructions(self):
        """Print search instructions for finding contacts."""
        print("\n" + "=" * 60)
        print("🔍 CONTACT DISCOVERY WORKFLOW")
        print("=" * 60)

        print("\n📋 STEP 1: Find Contacts on LinkedIn")
        print("-" * 40)

        for company_name, info in self.target_companies.items():
            print(f"\n🏢 {company_name} (Priority {info['priority']})")
            print(f"   Focus: {info['focus']}")
            print(f'   Search: company:"{company_name}" AND (title:"ML Engineer" OR title:"AI Engineer" OR title:"CTO")')

        print("\n📋 STEP 2: Collect Contact Information")
        print("-" * 40)
        print("""
For each contact, collect:
  ✓ Full Name
  ✓ Current Title
  ✓ LinkedIn URL
  ✓ Email (use Apollo.io or Hunter.io)
  ✓ Recent activity/posts (for personalization)
  ✓ Any mutual connections
        """)

        print("\n📋 STEP 3: Add to CSV Template")
        print("-" * 40)
        print("""
CSV Format:
  Company, Contact Name, Title, Email, LinkedIn URL, Source, Notes

Example:
  Vectara, John Smith, ML Engineer, john@vectara.com, linkedin.com/in/johnsmith, LinkedIn, Posted about RAG recently
        """)

        print("\n📋 STEP 4: Import to Attio")
        print("-" * 40)
        print("""
Run: python scripts/sync/attio_contact_updater.py bulk-import --file your_contacts.csv
        """)

        print("\n🎯 HIGH-VALUE TITLES TO PRIORITIZE:")
        print("-" * 40)
        for category, titles in self.target_titles.items():
            print(f"\n{category.upper().replace('_', ' ')}:")
            for title in titles[:5]:
                print(f"  • {title}")

    def interactive_add_contact(self):
        """Interactively add a single contact."""
        print("\n📝 ADD CONTACT TO ATTIO")
        print("=" * 60)

        # Get company
        print("\nSelect company:")
        companies = list(self.target_companies.keys())
        for i, company in enumerate(companies, 1):
            print(f"  {i}. {company}")

        company_choice = int(input("\nCompany number: ")) - 1
        company_name = companies[company_choice]

        # Get contact details
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()
        title = input("Job title: ").strip()
        email = input("Email (optional): ").strip()
        linkedin = input("LinkedIn URL (optional): ").strip()
        notes = input("Notes (optional): ").strip()

        # Find company ID
        company_id = self.find_company_id(company_name)
        if not company_id:
            print(f"❌ Company '{company_name}' not found in Attio")
            return

        # Prepare contact data
        contact_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "title": title,
            "company_name": company_name,
            "company_id": company_id,
            "linkedin_url": linkedin,
            "category": self.categorize_contact(title),
            "relevance_score": self.score_contact_relevance(
                title,
                self.target_companies[company_name]['priority']
            ),
            "source": "Manual Entry",
            "company_focus": self.target_companies[company_name]['focus'],
            "notes": notes
        }

        # Add contact
        self.add_contact(contact_data)


def main():
    parser = argparse.ArgumentParser(description="Manage contacts in Attio")
    parser.add_argument("command",
                       choices=["add-contact", "bulk-import", "search-guide"],
                       help="Command to execute")
    parser.add_argument("--file", help="CSV file path for bulk import")

    args = parser.parse_args()
    updater = AttioContactUpdater()

    if args.command == "add-contact":
        updater.interactive_add_contact()

    elif args.command == "bulk-import":
        if not args.file:
            print("❌ Please provide CSV file path with --file")
            return
        updater.bulk_import_from_csv(args.file)

    elif args.command == "search-guide":
        updater.create_search_instructions()


if __name__ == "__main__":
    main()