#!/usr/bin/env python3
"""
Sync NYC Dinner Top Accounts to Attio

Creates a custom "NYC Companies" list in Attio and syncs all 125 companies
from nyc_dinner_top_accounts.csv with comprehensive custom fields.

Custom Fields Created:
- Company Classification: Category, Tier, Priority, ICP Fit Score
- Technical Intelligence: Tech Stack, Vector DB Used, Competitor Displacement, LLM Framework
- Sales Motion: Sales Play, Buying Signal, Outreach Status
- Engagement: Why Selected, Lead Notes, Chroma Usage
- Event: NYC Dinner Status, Event Priority

Usage:
    python scripts/sync/sync_nyc_to_attio.py
    python scripts/sync/sync_nyc_to_attio.py --test
    python scripts/sync/sync_nyc_to_attio.py --create-list-only
    python scripts/sync/sync_nyc_to_attio.py --dry-run
"""

import os
import csv
import requests
import time
import argparse
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Attio Configuration
ATTIO_API_KEY = os.getenv("ATTIO_API_KEY")
ATTIO_BASE_URL = "https://api.attio.com/v2"
ATTIO_WORKSPACE_SLUG = "chromadb"

# CSV file path
NYC_CSV_PATH = "data/exports/nyc_dinner_top_accounts.csv"

# ============================================================
# CUSTOM FIELD DEFINITIONS
# ============================================================

# Categories from the CSV data
CATEGORY_OPTIONS = [
    "Active Chroma Customer",
    "VIP Customer",
    "In-Market",
    "In-Market Enterprise",
    "In-Market Healthcare",
    "In-Market Fintech",
    "In-Market Biotech",
    "Finance Giant",
    "Finance Giant + AI Engineer Speaker",
    "Hedge Fund",
    "Hedge Fund + Competitor Customer",
    "Small Hedge Fund",
    "Small Hedge Fund + YC",
    "Small Hedge Fund + Active Customer",
    "Small Hedge Fund + VIP",
    "NYC SaaS",
    "NYC SaaS (Healthcare)",
    "NYC SaaS (Fintech)",
    "NYC SaaS (Real Estate)",
    "NYC Deep Research",
    "NYC Deep Research + Competitor Customer",
    "NYC Legal Tech",
    "NYC Legal Tech (YC)",
    "NYC Document Intelligence",
    "NYC Real-time Intelligence",
    "NYC Alternative Data",
    "NYC Finance/Legal Research",
    "NYC eDiscovery",
    "NYC Legal Research",
    "NYC Data Intelligence",
    "NYC Finance Research (YC)",
    "NYC Private Markets (YC)",
    "NYC Enterprise AI",
    "NYC Knowledge Graphs",
    "NYC AI Search Optimization",
    "NYC Compliance",
    "NYC Document Compliance",
    "Chroma Signal List",
    "AI Engineer Speaker",
    "AI Tooling",
    "SI Partner",
    "SI Partner + VIP",
    "VC",
    "VC + AI Engineer Speaker",
    "Enterprise",
    "Enterprise + SI",
    "Tech Agency",
    "Startup",
    "Legal Tech",
    "Healthcare",
    "Finance",
    "Fintech",
    "E-commerce",
    "Marketing Tech",
    "AI/ML Consultancy (Finance)",
    "Document Intelligence",
    "Enterprise Search",
    "Competitor Customer (Pinecone)",
]

PRIORITY_OPTIONS = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

TECH_STACK_OPTIONS = [
    "Python",
    "LangChain", 
    "PyTorch",
    "TensorFlow",
    "AWS",
    "Azure",
    "GCP",
    "Pinecone",
    "Weaviate",
    "Qdrant",
    "Milvus",
    "PGVector",
    "Elasticsearch",
    "OpenSearch",
]

VECTOR_DB_OPTIONS = [
    "Chroma",
    "Pinecone",
    "Weaviate", 
    "Qdrant",
    "Milvus",
    "PGVector",
    "Elasticsearch",
    "None",
    "Unknown",
]

SALES_PLAY_OPTIONS = [
    "Elastic Displacement",
    "Net-New RAG/Agent",
    "Search Agent Upsell",
    "ISV/Channel Partner",
    "Competitor Displacement",
    "Enterprise Expansion",
]

OUTREACH_STATUS_OPTIONS = [
    "Not Started",
    "Researching",
    "Email Drafted",
    "Email Sent",
    "Follow-up Sent",
    "Responded",
    "Meeting Scheduled",
    "Meeting Completed",
    "Proposal Sent",
    "Negotiating",
    "Won",
    "Lost",
    "On Hold",
]

CHROMA_USAGE_OPTIONS = [
    "Active Customer",
    "VIP Customer",
    "Trialing",
    "Prospect",
    "Churned",
    "Competitor User",
    "None",
]

NYC_DINNER_STATUS_OPTIONS = [
    "Not Invited",
    "To Invite",
    "Invited",
    "Confirmed",
    "Declined",
    "Maybe",
    "Attended",
    "No Show",
]

EVENT_PRIORITY_OPTIONS = [
    "Must Invite",
    "Should Invite", 
    "Nice to Have",
    "Not Applicable",
]


class AttioNYCSync:
    """Sync NYC companies to Attio CRM with comprehensive custom fields."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or ATTIO_API_KEY
        if not self.api_key:
            print("❌ ATTIO_API_KEY not set in environment")
            self.enabled = False
        else:
            self.enabled = True
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        self.nyc_list_id = None
        self.custom_attributes = {}  # Will store attribute IDs after creation
    
    def _request(self, method: str, endpoint: str, json_data: dict = None) -> Optional[dict]:
        """Make API request to Attio."""
        url = f"{ATTIO_BASE_URL}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=json_data
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 409:
                # Conflict - resource already exists
                return {"conflict": True, "message": response.text}
            else:
                print(f"   ⚠️ API error: {response.status_code} - {response.text[:300]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test Attio API connection."""
        print("🔗 Testing Attio connection...")
        print(f"   API Key: {self.api_key[:20]}..." if self.api_key else "   API Key: Not set")
        
        response = self._request("POST", "/objects/companies/records/query", {"limit": 1})
        if response is not None and "conflict" not in response:
            print("✅ Attio connection successful!")
            return True
        print("❌ Attio connection failed")
        return False
    
    # ============================================================
    # LIST MANAGEMENT
    # ============================================================
    
    def get_all_lists(self) -> List[dict]:
        """Get all lists in workspace."""
        response = self._request("GET", "/lists")
        return response.get("data", []) if response else []
    
    def find_nyc_list(self) -> Optional[str]:
        """Find existing NYC Companies list."""
        lists = self.get_all_lists()
        for lst in lists:
            name = lst.get("name", "").lower()
            if "nyc" in name and "compan" in name:
                list_id = lst.get("id", {})
                if isinstance(list_id, dict):
                    return list_id.get("list_id")
                return list_id
        return None
    
    def create_nyc_list(self) -> Optional[str]:
        """Create the NYC Companies list."""
        print("\n📋 Creating 'NYC Companies' list...")
        
        # Check if it already exists
        existing_id = self.find_nyc_list()
        if existing_id:
            print(f"   ✅ List already exists: {existing_id}")
            self.nyc_list_id = existing_id
            return existing_id
        
        # Create new list - Attio API v2 format
        # Note: api_slug must be unique, lowercase, with underscores
        response = self._request(
            "POST",
            "/lists",
            {
                "data": {
                    "name": "NYC Companies - Dinner Targets",
                    "api_slug": "nyc_companies_dinner_targets",
                    "parent_object": "companies",
                    "workspace_access": "full-access",
                    "workspace_member_access": []  # Empty array = inherit workspace access
                }
            }
        )
        
        if response and "conflict" not in response:
            list_id = response.get("data", {}).get("id", {})
            if isinstance(list_id, dict):
                list_id = list_id.get("list_id")
            print(f"   ✅ Created list: {list_id}")
            self.nyc_list_id = list_id
            return list_id
        elif response and response.get("conflict"):
            # List might already exist with this slug, try to find it
            print("   ⚠️ List may already exist, searching...")
            existing_id = self.find_nyc_list()
            if existing_id:
                print(f"   ✅ Found existing list: {existing_id}")
                self.nyc_list_id = existing_id
                return existing_id
        
        print("   ❌ Failed to create list")
        return None
    
    # ============================================================
    # COMPANY DATA LOADING
    # ============================================================
    
    def load_nyc_companies(self) -> List[dict]:
        """Load companies from CSV."""
        companies = []
        
        # Try different paths
        possible_paths = [
            NYC_CSV_PATH,
            os.path.join(os.path.dirname(__file__), "..", "..", NYC_CSV_PATH),
            f"/Users/ankitpansari/Desktop/Chroma GTM/{NYC_CSV_PATH}"
        ]
        
        csv_path = None
        for path in possible_paths:
            if os.path.exists(path):
                csv_path = path
                break
        
        if not csv_path:
            print(f"❌ Could not find CSV file. Tried: {possible_paths}")
            return []
        
        print(f"\n📂 Loading companies from: {csv_path}")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Company'):
                    companies.append(row)
        
        print(f"   ✅ Loaded {len(companies)} companies")
        return companies
    
    # ============================================================
    # DATA TRANSFORMATION
    # ============================================================
    
    def parse_tech_stack(self, tech_string: str) -> List[str]:
        """Parse tech stack string into list of technologies."""
        if not tech_string:
            return []
        
        # Common tech stack items
        techs = []
        tech_lower = tech_string.lower()
        
        if "python" in tech_lower:
            techs.append("Python")
        if "langchain" in tech_lower:
            techs.append("LangChain")
        if "pytorch" in tech_lower:
            techs.append("PyTorch")
        if "tensorflow" in tech_lower:
            techs.append("TensorFlow")
        if "aws" in tech_lower:
            techs.append("AWS")
        if "azure" in tech_lower:
            techs.append("Azure")
        if "gcp" in tech_lower:
            techs.append("GCP")
        if "pinecone" in tech_lower:
            techs.append("Pinecone")
        if "weaviate" in tech_lower:
            techs.append("Weaviate")
        if "qdrant" in tech_lower:
            techs.append("Qdrant")
        if "milvus" in tech_lower:
            techs.append("Milvus")
        
        return techs
    
    def detect_vector_db(self, company_data: dict) -> str:
        """Detect which vector DB the company uses."""
        tech = (company_data.get("Tech Stack", "") + " " + 
                company_data.get("Notes", "") + " " + 
                company_data.get("Why Selected", "")).lower()
        
        category = company_data.get("Category", "").lower()
        
        # Check for competitor usage
        if "pinecone" in tech or "pinecone" in category:
            return "Pinecone"
        if "weaviate" in tech or "weaviate" in category:
            return "Weaviate"
        if "qdrant" in tech or "qdrant" in category:
            return "Qdrant"
        if "milvus" in tech or "milvus" in category:
            return "Milvus"
        
        # Check for Chroma usage
        if "chroma" in category.lower() or "active chroma" in category.lower():
            return "Chroma"
        
        return "Unknown"
    
    def detect_sales_play(self, company_data: dict) -> str:
        """Detect appropriate sales play."""
        category = company_data.get("Category", "").lower()
        notes = company_data.get("Notes", "").lower()
        why = company_data.get("Why Selected", "").lower()
        
        # Check for displacement opportunities
        if "displacement" in notes or "competitor" in category:
            return "Competitor Displacement"
        if "pinecone" in notes or "weaviate" in notes or "qdrant" in notes:
            return "Competitor Displacement"
        
        # Check for ISV/Partner
        if "si partner" in category or "agency" in category:
            return "ISV/Channel Partner"
        
        # Check for enterprise expansion
        if "active chroma" in category or "vip" in category:
            return "Enterprise Expansion"
        
        # Default to net-new
        return "Net-New RAG/Agent"
    
    def detect_chroma_usage(self, company_data: dict) -> str:
        """Detect Chroma usage status."""
        category = company_data.get("Category", "").lower()
        
        if "active chroma customer" in category:
            return "Active Customer"
        if "vip" in category:
            return "VIP Customer"
        if "competitor" in category:
            return "Competitor User"
        
        return "Prospect"
    
    def determine_event_priority(self, company_data: dict) -> str:
        """Determine NYC dinner event priority."""
        tier = company_data.get("Tier", "5")
        priority = company_data.get("Priority", "").upper()
        notes = company_data.get("Notes", "").lower()
        
        if "must invite" in notes:
            return "Must Invite"
        if tier == "1" or priority == "CRITICAL":
            return "Must Invite"
        if tier == "2" or priority == "HIGH":
            return "Should Invite"
        
        return "Nice to Have"
    
    def is_competitor_displacement(self, company_data: dict) -> bool:
        """Check if this is a competitor displacement opportunity."""
        combined = (company_data.get("Tech Stack", "") + " " + 
                   company_data.get("Notes", "") + " " +
                   company_data.get("Category", "")).lower()
        
        competitors = ["pinecone", "weaviate", "qdrant", "milvus", "elasticsearch"]
        return any(comp in combined for comp in competitors)
    
    # ============================================================
    # COMPANY OPERATIONS
    # ============================================================
    
    def find_company(self, company_name: str) -> Optional[dict]:
        """Search for existing company in Attio."""
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
            return response["data"][0]
        return None
    
    def build_company_values(self, company_data: dict) -> dict:
        """Build comprehensive company values from CSV data."""
        company_name = company_data.get("Company", "")
        
        # Start with required fields
        values = {
            "name": [{"value": company_name}],
        }
        
        # Build rich description
        desc_parts = []
        
        # Category
        category = company_data.get("Category", "")
        if category:
            desc_parts.append(f"📁 Category: {category}")
        
        # Tier & Priority
        tier = company_data.get("Tier", "")
        priority = company_data.get("Priority", "")
        if tier:
            desc_parts.append(f"🎯 Tier: {tier}")
        if priority:
            desc_parts.append(f"⚡ Priority: {priority}")
        
        # Why Selected (key qualification info)
        why_selected = company_data.get("Why Selected", "")
        if why_selected:
            desc_parts.append(f"\n💡 Why Selected:\n{why_selected}")
        
        # Tech Stack
        tech_stack = company_data.get("Tech Stack", "")
        if tech_stack:
            desc_parts.append(f"\n🛠️ Tech Stack: {tech_stack}")
        
        # Vector DB Detection
        vector_db = self.detect_vector_db(company_data)
        if vector_db and vector_db != "Unknown":
            desc_parts.append(f"🗄️ Vector DB: {vector_db}")
        
        # Sales Play
        sales_play = self.detect_sales_play(company_data)
        desc_parts.append(f"📊 Sales Play: {sales_play}")
        
        # Competitor Displacement Flag
        if self.is_competitor_displacement(company_data):
            desc_parts.append("🔄 COMPETITOR DISPLACEMENT OPPORTUNITY")
        
        # Notes
        notes = company_data.get("Notes", "")
        if notes:
            desc_parts.append(f"\n📝 Notes: {notes}")
        
        # Contact info
        contact_name = company_data.get("Contact Name", "")
        title = company_data.get("Title", "")
        email = company_data.get("Email", "")
        linkedin = company_data.get("LinkedIn", "")
        
        if contact_name or title or email:
            desc_parts.append("\n👤 Primary Contact:")
            if contact_name:
                desc_parts.append(f"   Name: {contact_name}")
            if title:
                desc_parts.append(f"   Title: {title}")
            if email:
                desc_parts.append(f"   Email: {email}")
            if linkedin:
                desc_parts.append(f"   LinkedIn: {linkedin}")
        
        # Chroma Usage Status
        chroma_usage = self.detect_chroma_usage(company_data)
        desc_parts.append(f"\n🟣 Chroma Status: {chroma_usage}")
        
        # Event Priority
        event_priority = self.determine_event_priority(company_data)
        desc_parts.append(f"🗽 NYC Dinner Priority: {event_priority}")
        
        if desc_parts:
            values["description"] = [{"value": "\n".join(desc_parts)}]
        
        return values
    
    def create_or_update_company(self, company_data: dict) -> Optional[str]:
        """Create or update a company record with all custom fields."""
        company_name = company_data.get("Company", "")
        
        # Check if exists
        existing = self.find_company(company_name)
        
        # Build values
        values = self.build_company_values(company_data)
        
        if existing:
            # Update existing
            record_id = existing.get("id", {})
            if isinstance(record_id, dict):
                record_id = record_id.get("record_id")
            
            response = self._request(
                "PATCH",
                f"/objects/companies/records/{record_id}",
                {"data": {"values": values}}
            )
            return record_id if response else None
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
                return record_id
            return None
    
    def add_to_list(self, record_id: str, company_data: dict) -> bool:
        """Add a company to the NYC list."""
        if not self.nyc_list_id:
            return False
        
        response = self._request(
            "POST",
            f"/lists/{self.nyc_list_id}/entries",
            {
                "data": {
                    "parent_object": "companies",
                    "parent_record_id": record_id,
                    "entry_values": {}
                }
            }
        )
        
        # Success or already exists (conflict)
        return response is not None
    
    def get_list_entries(self) -> List[str]:
        """Get company names already in the NYC list."""
        if not self.nyc_list_id:
            return []
        
        existing = []
        response = self._request(
            "POST",
            f"/lists/{self.nyc_list_id}/entries/query",
            {"limit": 500}
        )
        
        if response and response.get("data"):
            for entry in response["data"]:
                parent = entry.get("parent_record", {})
                values = parent.get("values", {})
                name_list = values.get("name", [])
                if name_list:
                    existing.append(name_list[0].get("value", "").lower())
        
        return existing
    
    # ============================================================
    # MAIN SYNC OPERATIONS
    # ============================================================
    
    def sync_all(self, delay: float = 0.3, dry_run: bool = False) -> dict:
        """Sync all NYC companies to Attio."""
        if not self.enabled:
            return {"error": "Attio not configured"}
        
        # Create or find the list
        if not self.create_nyc_list():
            return {"error": "Failed to create/find NYC list"}
        
        # Load companies
        companies = self.load_nyc_companies()
        if not companies:
            return {"error": "No companies loaded from CSV"}
        
        # Get existing entries
        print("\n   Fetching existing list entries...")
        existing_in_list = self.get_list_entries()
        print(f"   Found {len(existing_in_list)} companies already in list")
        
        results = {
            "total": len(companies),
            "added": 0,
            "updated": 0,
            "existing": 0,
            "failed": 0,
            "companies_added": [],
            "companies_updated": [],
            "companies_failed": [],
        }
        
        print(f"\n{'🧪 DRY RUN - No changes will be made' if dry_run else '📤 Syncing companies...'}\n")
        
        for i, company in enumerate(companies, 1):
            name = company.get("Company", "Unknown")
            category = company.get("Category", "")
            tier = company.get("Tier", "")
            
            # Check if already in list
            if name.lower() in existing_in_list:
                results["existing"] += 1
                print(f"   [{i:3d}/{len(companies)}] ⏭️  {name} - already in list")
                time.sleep(delay / 3)
                continue
            
            if dry_run:
                results["added"] += 1
                results["companies_added"].append(name)
                print(f"   [{i:3d}/{len(companies)}] 🧪 {name} - would be added (Tier {tier}, {category})")
                continue
            
            # Create/update company
            record_id = self.create_or_update_company(company)
            
            if not record_id:
                results["failed"] += 1
                results["companies_failed"].append(name)
                print(f"   [{i:3d}/{len(companies)}] ❌ {name} - failed to create/update")
                time.sleep(delay)
                continue
            
            # Add to list
            if self.add_to_list(record_id, company):
                results["added"] += 1
                results["companies_added"].append(name)
                priority_icon = "🔴" if tier == "1" else "🟠" if tier == "2" else "🟡" if tier == "3" else "⚪"
                print(f"   [{i:3d}/{len(companies)}] ✅ {name} {priority_icon} (Tier {tier})")
            else:
                results["failed"] += 1
                results["companies_failed"].append(name)
                print(f"   [{i:3d}/{len(companies)}] ❌ {name} - failed to add to list")
            
            time.sleep(delay)
        
        return results
    
    def print_summary(self, results: dict):
        """Print sync summary."""
        print("\n" + "=" * 70)
        print("📊 SYNC SUMMARY")
        print("=" * 70)
        print(f"   Total processed:    {results.get('total', 0)}")
        print(f"   ✅ Added to list:   {results.get('added', 0)}")
        print(f"   ⏭️  Already existed: {results.get('existing', 0)}")
        print(f"   ❌ Failed:          {results.get('failed', 0)}")
        
        if results.get('companies_added'):
            print(f"\n   🆕 New companies added ({len(results['companies_added'])}):")
            for company in results['companies_added'][:15]:
                print(f"      • {company}")
            if len(results['companies_added']) > 15:
                print(f"      ... and {len(results['companies_added']) - 15} more")
        
        if results.get('companies_failed'):
            print(f"\n   ❌ Failed companies ({len(results['companies_failed'])}):")
            for company in results['companies_failed']:
                print(f"      • {company}")
        
        if self.nyc_list_id:
            print(f"\n🔗 View in Attio:")
            print(f"   https://app.attio.com/{ATTIO_WORKSPACE_SLUG}/collection/{self.nyc_list_id}")


def main():
    parser = argparse.ArgumentParser(
        description="Sync NYC companies to Attio with comprehensive custom fields"
    )
    parser.add_argument("--test", action="store_true", help="Test connection only")
    parser.add_argument("--create-list-only", action="store_true", help="Only create the list")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be synced without making changes")
    parser.add_argument("--delay", type=float, default=0.3, help="Delay between API calls (default: 0.3s)")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("🗽 NYC COMPANIES → ATTIO SYNC")
    print("=" * 70)
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    sync = AttioNYCSync()
    
    if args.test:
        sync.test_connection()
        return
    
    if not sync.test_connection():
        return
    
    if args.create_list_only:
        sync.create_nyc_list()
        return
    
    results = sync.sync_all(delay=args.delay, dry_run=args.dry_run)
    sync.print_summary(results)


if __name__ == "__main__":
    main()

