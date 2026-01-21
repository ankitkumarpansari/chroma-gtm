#!/usr/bin/env python3
"""
Attio Field Checker - Identify Existing vs Custom Fields Needed
================================================================
This script checks what fields already exist in Attio (default + custom)
and identifies which new fields we actually need to create.

Usage:
    python scripts/sync/attio_check_existing_fields.py check    # List all existing fields
    python scripts/sync/attio_check_existing_fields.py analyze  # Show what's missing
"""

import os
import json
import requests
import argparse
from typing import Dict, List, Set
from dotenv import load_dotenv

load_dotenv()

class AttioFieldChecker:
    """Check existing Attio fields to avoid duplication."""

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

        # Attio's default fields (these come out-of-the-box)
        self.attio_default_fields = {
            # Company Basics (Attio provides these automatically)
            "name": "Company Name",
            "domains": "Website Domain(s)",
            "description": "Company Description",
            "logo": "Company Logo",
            "primary_location": "Headquarters Location",
            "founded": "Year Founded",
            "company_size": "Employee Count Range",
            "linkedin_url": "LinkedIn Profile",
            "twitter_url": "Twitter/X Profile",
            "facebook_url": "Facebook Profile",

            # Firmographics (Auto-enriched by Attio)
            "estimated_arr": "Estimated Annual Revenue",
            "total_raised": "Total Funding Raised",
            "last_funding_round_date": "Last Funding Date",
            "last_funding_type": "Last Funding Type",
            "investors": "Investor List",
            "market_cap": "Market Capitalization",
            "ticker": "Stock Ticker",
            "industries": "Industry Categories",
            "keywords": "Business Keywords",

            # People & Relationships
            "team_members": "Associated People",
            "interactions": "Interaction History",
            "tasks": "Tasks & Reminders",
            "notes": "Notes",

            # System Fields
            "created_at": "Created Date",
            "updated_at": "Last Updated",
            "owner": "Record Owner",
            "followers": "Following Users",
            "tags": "Tags",
            "lists": "List Memberships",
            "rating": "Star Rating",
            "categories": "Categories"
        }

        # Fields we ACTUALLY need to create (Chroma-specific)
        self.required_custom_fields = {
            # Vector DB & AI Specific
            "vector_db_status": {
                "title": "Vector DB Status",
                "type": "select",
                "description": "Current vector database usage status",
                "options": ["Active Chroma User", "Evaluating Chroma", "Using Competitor",
                           "Building In-House", "No Vector DB", "Needs Vector DB"]
            },
            "vector_db_competitor": {
                "title": "Current Vector DB",
                "type": "select",
                "description": "Which vector database they currently use",
                "options": ["Pinecone", "Weaviate", "Qdrant", "Milvus", "Vespa",
                           "Elasticsearch", "pgvector", "MongoDB Atlas", "None"]
            },
            "ai_use_cases": {
                "title": "AI Use Cases",
                "type": "text",
                "description": "Specific AI/ML use cases (RAG, search, etc.)"
            },
            "use_case_category": {
                "title": "Primary Use Case",
                "type": "select",
                "description": "Main vector DB use case",
                "options": ["Semantic Search", "RAG", "Recommendations", "Knowledge Management",
                           "Similarity Matching", "Personalization", "Q&A", "Document Processing"]
            },
            "data_volume_estimate": {
                "title": "Vector Data Volume",
                "type": "select",
                "description": "Estimated vectors to store",
                "options": ["<100K", "100K-1M", "1M-10M", "10M-100M", "100M-1B", ">1B"]
            },
            "embedding_model": {
                "title": "Embedding Model",
                "type": "text",
                "description": "Which embedding model they use/plan to use"
            },

            # GTM & Sales Specific
            "customer_cohort": {
                "title": "Customer Cohort",
                "type": "select",
                "description": "GTM segmentation",
                "options": ["Cohort 1 - Current Customer", "Cohort 2 - In Market",
                           "Cohort 3 - Competitor Customer", "Cohort 4 - SI Partner"]
            },
            "buying_stage": {
                "title": "Buying Stage",
                "type": "select",
                "description": "Stage in buying journey",
                "options": ["Awareness", "Interest", "Consideration", "Evaluation",
                           "Decision", "Customer", "Churned"]
            },
            "technical_fit_score": {
                "title": "Technical Fit Score",
                "type": "number",
                "description": "Technical fit with Chroma (0-100)"
            },
            "engagement_score": {
                "title": "Engagement Score",
                "type": "number",
                "description": "Level of engagement (0-100)"
            },
            "champion_identified": {
                "title": "Champion Identified",
                "type": "checkbox",
                "description": "Internal champion exists"
            },
            "champion_name": {
                "title": "Champion Name",
                "type": "text",
                "description": "Name of internal champion"
            },
            "competitive_position": {
                "title": "Competitive Position",
                "type": "select",
                "description": "Our position vs competitors",
                "options": ["Leading", "Strong", "Equal", "Behind", "Unknown"]
            },

            # Commercial
            "deal_size": {
                "title": "Expected Deal Size",
                "type": "currency",
                "description": "Potential contract value"
            },
            "budget_confirmed": {
                "title": "Budget Confirmed",
                "type": "checkbox",
                "description": "Budget has been verified"
            },

            # Intent Signals
            "intent_signals": {
                "title": "Intent Signals",
                "type": "text",
                "description": "Buying signals observed (hiring AI engineers, raised funding, etc.)"
            },
            "github_activity": {
                "title": "GitHub AI Activity",
                "type": "text",
                "description": "AI/ML related GitHub activity"
            },

            # Tracking
            "lead_source": {
                "title": "Lead Source",
                "type": "select",
                "description": "How we found this company",
                "options": ["LinkedIn Outbound", "Inbound", "Partner Referral", "Conference",
                           "Open Source", "Content Marketing", "Competitor Analysis"]
            },
            "last_outreach_date": {
                "title": "Last Outreach Date",
                "type": "date",
                "description": "Date of last sales outreach"
            },
            "next_steps": {
                "title": "Next Steps",
                "type": "text",
                "description": "Immediate action items for this account"
            },
            "account_tier": {
                "title": "Account Tier",
                "type": "select",
                "description": "Account prioritization",
                "options": ["Tier 1 - Strategic", "Tier 2 - Growth", "Tier 3 - Standard", "Tier 4 - Long-tail"]
            },
            "chroma_advantages": {
                "title": "Why Chroma Wins",
                "type": "text",
                "description": "Specific advantages Chroma has for this account"
            },
            "blocker_notes": {
                "title": "Blockers",
                "type": "text",
                "description": "Current obstacles or concerns"
            }
        }

    def _request(self, method: str, endpoint: str, data=None):
        """Make API request."""
        url = f"{self.base_url}/{endpoint}"
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json() if response.text else {}

    def get_existing_fields(self):
        """Fetch all existing fields from Attio."""
        print("\n🔍 Fetching existing fields from Attio...")

        endpoint = "objects/companies/attributes"
        result = self._request("GET", endpoint)

        existing_fields = {}
        if result and 'data' in result:
            for field in result['data']:
                api_slug = field.get('api_slug', '')
                existing_fields[api_slug] = {
                    'title': field.get('title', ''),
                    'type': field.get('type', ''),
                    'is_system': field.get('is_system', False),
                    'is_writable': field.get('is_writable_by_api', True),
                    'description': field.get('description', '')
                }

        return existing_fields

    def analyze_fields(self):
        """Analyze which fields exist vs need to be created."""
        existing = self.get_existing_fields()

        print("\n" + "="*70)
        print("📊 ATTIO FIELD ANALYSIS")
        print("="*70)

        # 1. System/Default Fields
        print("\n✅ EXISTING SYSTEM FIELDS (Attio Default):")
        print("-"*50)
        system_fields = [f for f, details in existing.items() if details.get('is_system')]
        for field in sorted(system_fields):
            print(f"  • {field:<25} [{existing[field]['type']}]")

        # 2. Existing Custom Fields
        print(f"\n✅ EXISTING CUSTOM FIELDS ({len([f for f, d in existing.items() if not d.get('is_system')])} fields):")
        print("-"*50)
        custom_fields = [f for f, details in existing.items() if not details.get('is_system')]
        for field in sorted(custom_fields):
            print(f"  • {field:<25} [{existing[field]['type']}] - {existing[field]['title']}")

        # 3. Fields We Need to Create
        print(f"\n🆕 FIELDS TO CREATE ({len(self.required_custom_fields)} Chroma-specific):")
        print("-"*50)

        fields_to_create = []
        fields_already_exist = []

        for field_slug, field_config in self.required_custom_fields.items():
            if field_slug not in existing:
                fields_to_create.append((field_slug, field_config))
                print(f"  • {field_config['title']:<25} [{field_config['type']}]")
                if field_config.get('description'):
                    print(f"    └─ {field_config['description']}")
            else:
                fields_already_exist.append(field_slug)

        # 4. Summary
        print("\n" + "="*70)
        print("📈 SUMMARY:")
        print(f"  • Total existing fields: {len(existing)}")
        print(f"  • System fields: {len(system_fields)}")
        print(f"  • Custom fields existing: {len(custom_fields)}")
        print(f"  • New fields needed: {len(fields_to_create)}")
        print(f"  • Already have: {len(fields_already_exist)} of our required fields")

        if fields_already_exist:
            print(f"\n  ✓ These required fields already exist: {', '.join(fields_already_exist)}")

        print("\n💡 RECOMMENDATION:")
        if fields_to_create:
            print(f"  Create {len(fields_to_create)} new Chroma-specific fields")
            print("  Run: python scripts/sync/attio_create_minimal_fields.py")
        else:
            print("  All required fields already exist!")

        return fields_to_create

    def create_minimal_fields(self):
        """Create only the fields that don't exist yet."""
        fields_to_create = self.analyze_fields()

        if not fields_to_create:
            print("\n✅ All required fields already exist!")
            return

        print("\n" + "="*70)
        print(f"🚀 CREATING {len(fields_to_create)} NEW FIELDS")
        print("="*70)

        endpoint = "objects/companies/attributes"
        created = 0
        failed = 0

        for field_slug, field_config in fields_to_create:
            print(f"\nCreating: {field_config['title']}...", end=" ")

            # Build request in Attio's format with required fields
            request_data = {
                "data": {
                    "api_slug": field_slug,
                    "title": field_config["title"],
                    "type": field_config["type"],
                    "description": field_config.get("description", ""),
                    "is_required": False,
                    "is_unique": False,
                    "is_multiselect": field_config["type"] == "select",
                    "config": {}
                }
            }

            # Add options for select fields
            if field_config["type"] == "select" and "options" in field_config:
                request_data["data"]["config"] = {
                    "options": [{"title": opt} for opt in field_config["options"]]
                }

            try:
                result = self._request("POST", endpoint, request_data)
                if result:
                    print("✅ Created")
                    created += 1
            except Exception as e:
                print(f"❌ Failed: {str(e)}")
                # Try to get more details about the error
                if hasattr(e, 'response') and e.response:
                    try:
                        error_detail = e.response.json()
                        print(f"    Error details: {error_detail}")
                    except:
                        pass
                failed += 1

        print("\n" + "="*70)
        print(f"✅ Successfully created: {created} fields")
        if failed:
            print(f"❌ Failed to create: {failed} fields")
        print("="*70)


def main():
    parser = argparse.ArgumentParser(description="Check and manage Attio fields")
    parser.add_argument("command", choices=["check", "analyze", "create"],
                       help="check: list all fields | analyze: show what's needed | create: add missing fields")

    args = parser.parse_args()
    checker = AttioFieldChecker()

    if args.command == "check":
        existing = checker.get_existing_fields()
        print(f"\n📋 Found {len(existing)} total fields in Attio")
        for slug, details in sorted(existing.items()):
            print(f"  • {slug:<30} [{details['type']:<10}] - {details['title']}")

    elif args.command == "analyze":
        checker.analyze_fields()

    elif args.command == "create":
        response = input("\n⚠️  This will create new fields in Attio. Continue? (yes/no): ")
        if response.lower() == 'yes':
            checker.create_minimal_fields()
        else:
            print("❌ Cancelled")


if __name__ == "__main__":
    main()