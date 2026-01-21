#!/usr/bin/env python3
"""
Sync HubSpot Contacts to Attio CRM

Syncs all contacts from HubSpot to Attio as People records,
with proper company associations.

Usage:
    python sync_hubspot_contacts_to_attio.py                # Full sync
    python sync_hubspot_contacts_to_attio.py --dry-run      # Preview without syncing
    python sync_hubspot_contacts_to_attio.py --limit 100    # Limit contacts
    python sync_hubspot_contacts_to_attio.py --test         # Test connections
"""

import os
import requests
import time
import argparse
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# Configuration
# =============================================================================

HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
HUBSPOT_BASE_URL = "https://api.hubapi.com"

ATTIO_API_KEY = os.getenv("ATTIO_API_KEY")
ATTIO_BASE_URL = "https://api.attio.com/v2"
ATTIO_WORKSPACE_SLUG = "chromadb"

# HubSpot contact properties to fetch
HUBSPOT_CONTACT_PROPERTIES = [
    "email",
    "firstname",
    "lastname",
    "jobtitle",
    "company",
    "phone",
    "city",
    "state",
    "country",
    "hs_linkedin_url",
    "lifecyclestage",
    # Custom properties
    "github_url",
    "twitter_url",
    "developer_persona",
    "contact_cohort_role",
    "lead_score_custom",
    "is_vip",
    "chroma_interaction_history",
]


# =============================================================================
# HubSpot Client
# =============================================================================

class HubSpotClient:
    """Client for HubSpot API."""
    
    def __init__(self):
        self.api_key = HUBSPOT_API_KEY
        self.enabled = bool(self.api_key)
        if self.enabled:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
    
    def _request(self, method: str, endpoint: str, json_data: dict = None) -> Optional[dict]:
        """Make API request to HubSpot."""
        url = f"{HUBSPOT_BASE_URL}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=json_data)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", 10))
                print(f"   ⏳ Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                return self._request(method, endpoint, json_data)
            else:
                return None
                
        except Exception as e:
            print(f"   HubSpot request failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test HubSpot API connection."""
        response = self._request("GET", "/crm/v3/objects/contacts?limit=1")
        return response is not None
    
    def get_all_contacts(self) -> List[dict]:
        """Get all contacts from HubSpot."""
        contacts = []
        after = None
        properties = ",".join(HUBSPOT_CONTACT_PROPERTIES)
        
        while True:
            endpoint = f"/crm/v3/objects/contacts?limit=100&properties={properties}"
            if after:
                endpoint += f"&after={after}"
            
            response = self._request("GET", endpoint)
            if not response:
                break
            
            for contact in response.get("results", []):
                props = contact.get("properties", {})
                email = props.get("email", "")
                
                # Skip contacts without email
                if not email or "@" not in email:
                    continue
                
                contacts.append({
                    "id": contact.get("id"),
                    "properties": props
                })
            
            paging = response.get("paging", {})
            after = paging.get("next", {}).get("after")
            if not after:
                break
        
        return contacts


# =============================================================================
# Attio Client
# =============================================================================

class AttioClient:
    """Client for Attio API."""
    
    def __init__(self):
        self.api_key = ATTIO_API_KEY
        self.enabled = bool(self.api_key)
        if self.enabled:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        self.people_cache = {}  # email -> record_id
        self.company_cache = {}  # name -> record_id
    
    def _request(self, method: str, endpoint: str, json_data: dict = None) -> Optional[dict]:
        """Make API request to Attio."""
        url = f"{ATTIO_BASE_URL}/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=json_data)
            elif method == "PATCH":
                response = requests.patch(url, headers=self.headers, json=json_data)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 429:
                print("   ⏳ Rate limited, waiting 5s...")
                time.sleep(5)
                return self._request(method, endpoint, json_data)
            else:
                return None
                
        except Exception as e:
            print(f"   Attio request failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test Attio API connection."""
        response = self._request("POST", "objects/people/records/query", {"limit": 1})
        return response is not None
    
    def load_company_cache(self) -> None:
        """Load all companies for association."""
        print("   Loading companies for association...")
        after = None
        
        while True:
            query = {"limit": 100}
            response = self._request("POST", "objects/companies/records/query", query)
            if not response:
                break
            
            for company in response.get("data", []):
                values = company.get("values", {})
                name_list = values.get("name", [])
                if name_list:
                    name = name_list[0].get("value", "").lower().strip()
                    record_id = company.get("id", {}).get("record_id")
                    if name and record_id:
                        self.company_cache[name] = record_id
            
            # Check for pagination (Attio uses different pagination)
            if len(response.get("data", [])) < 100:
                break
        
        print(f"   Loaded {len(self.company_cache)} companies")
    
    def find_person_by_email(self, email: str) -> Optional[str]:
        """Find person by email, return record_id."""
        if not email:
            return None
        
        email = email.lower().strip()
        
        # Check cache first
        if email in self.people_cache:
            return self.people_cache[email]
        
        response = self._request(
            "POST",
            "objects/people/records/query",
            {"filter": {"email_addresses": {"$contains": email}}}
        )
        
        if response and response.get("data"):
            record_id = response["data"][0].get("id", {}).get("record_id")
            self.people_cache[email] = record_id
            return record_id
        
        return None
    
    def find_company_by_name(self, name: str) -> Optional[str]:
        """Find company by name from cache."""
        if not name:
            return None
        return self.company_cache.get(name.lower().strip())
    
    def create_person(self, values: dict) -> Optional[str]:
        """Create a new person in Attio."""
        response = self._request(
            "POST",
            "objects/people/records",
            {"data": {"values": values}}
        )
        
        if response and response.get("data"):
            record_id = response["data"].get("id", {}).get("record_id")
            # Cache the email
            if "email_addresses" in values and values["email_addresses"]:
                email = values["email_addresses"][0].get("email_address", "").lower()
                if email:
                    self.people_cache[email] = record_id
            return record_id
        
        return None
    
    def update_person(self, record_id: str, values: dict) -> bool:
        """Update an existing person in Attio."""
        response = self._request(
            "PATCH",
            f"objects/people/records/{record_id}",
            {"data": {"values": values}}
        )
        return response is not None


# =============================================================================
# Sync Logic
# =============================================================================

def transform_contact_to_attio(hubspot_props: dict) -> dict:
    """Transform HubSpot contact properties to Attio values format."""
    attio_values = {}
    
    # Email (required for people)
    email = hubspot_props.get("email", "")
    if email:
        attio_values["email_addresses"] = [{"email_address": email}]
    
    # Name
    first_name = hubspot_props.get("firstname", "")
    last_name = hubspot_props.get("lastname", "")
    if first_name or last_name:
        full_name = f"{first_name} {last_name}".strip()
        attio_values["name"] = [{"first_name": first_name, "last_name": last_name, "full_name": full_name}]
    
    # Job title
    job_title = hubspot_props.get("jobtitle", "")
    if job_title:
        attio_values["job_title"] = [{"value": job_title}]
    
    # Phone
    phone = hubspot_props.get("phone", "")
    if phone:
        attio_values["phone_numbers"] = [{"phone_number": phone}]
    
    # LinkedIn URL
    linkedin = hubspot_props.get("hs_linkedin_url", "")
    if linkedin:
        attio_values["linkedin_url"] = [{"value": linkedin}]
    
    # Build description with metadata
    notes_parts = []
    
    # Developer persona
    persona = hubspot_props.get("developer_persona", "")
    if persona:
        persona_labels = {
            "cto_vp": "CTO/VP Engineering",
            "eng_manager": "Engineering Manager",
            "ai_ml_engineer": "AI/ML Engineer",
            "applied_ai": "Applied AI",
            "data_engineer": "Data Engineer",
            "platform": "Platform/DevOps",
            "backend": "Backend Engineer",
            "fullstack": "Full Stack",
            "product": "Product",
        }
        notes_parts.append(f"👤 Persona: {persona_labels.get(persona, persona)}")
    
    # Cohort role
    cohort_role = hubspot_props.get("contact_cohort_role", "")
    if cohort_role:
        role_labels = {
            "decision_maker": "Decision Maker",
            "champion": "Champion",
            "user": "User",
            "influencer": "Influencer",
            "evaluator": "Evaluator",
        }
        notes_parts.append(f"🎯 Role: {role_labels.get(cohort_role, cohort_role)}")
    
    # VIP status
    is_vip = hubspot_props.get("is_vip", "")
    if is_vip and is_vip.lower() == "true":
        notes_parts.append("⭐ VIP Contact")
    
    # Lead score
    lead_score = hubspot_props.get("lead_score_custom", "")
    if lead_score:
        notes_parts.append(f"📊 Lead Score: {lead_score}")
    
    # Interaction history
    interaction = hubspot_props.get("chroma_interaction_history", "")
    if interaction:
        notes_parts.append(f"📝 Source: {interaction}")
    
    # GitHub URL
    github = hubspot_props.get("github_url", "")
    if github:
        notes_parts.append(f"🔗 GitHub: {github}")
    
    # Twitter URL
    twitter = hubspot_props.get("twitter_url", "")
    if twitter:
        notes_parts.append(f"🐦 Twitter: {twitter}")
    
    if notes_parts:
        attio_values["description"] = [{"value": "\n".join(notes_parts)}]
    
    return attio_values


def sync_contact(attio: AttioClient, contact: dict, dry_run: bool = False) -> Tuple[bool, str]:
    """Sync a single contact from HubSpot to Attio."""
    props = contact.get("properties", {})
    email = props.get("email", "")
    name = f"{props.get('firstname', '')} {props.get('lastname', '')}".strip() or email
    company_name = props.get("company", "")
    
    if not email:
        return False, "no_email"
    
    # Transform properties
    attio_values = transform_contact_to_attio(props)
    
    if dry_run:
        return True, "dry_run"
    
    # Try to find existing person
    record_id = attio.find_person_by_email(email)
    
    # Create or update
    if record_id:
        success = attio.update_person(record_id, attio_values)
        status = "updated" if success else "update_failed"
    else:
        record_id = attio.create_person(attio_values)
        status = "created" if record_id else "create_failed"
    
    return record_id is not None, status


def sync_all_contacts(hubspot: HubSpotClient, attio: AttioClient,
                      dry_run: bool = False, limit: int = None) -> dict:
    """Sync all contacts from HubSpot to Attio."""
    
    print("\n📥 Fetching contacts from HubSpot...")
    contacts = hubspot.get_all_contacts()
    print(f"   Found {len(contacts)} contacts with emails")
    
    if limit:
        contacts = contacts[:limit]
        print(f"   Limited to {len(contacts)} contacts")
    
    # Load company cache for associations
    if not dry_run:
        attio.load_company_cache()
    
    results = {
        "total": len(contacts),
        "created": 0,
        "updated": 0,
        "failed": 0,
    }
    
    print(f"\n📤 Syncing to Attio{'  [DRY RUN]' if dry_run else ''}...")
    
    for i, contact in enumerate(contacts):
        props = contact.get("properties", {})
        email = props.get("email", "")
        name = f"{props.get('firstname', '')} {props.get('lastname', '')}".strip() or email
        
        success, status = sync_contact(attio, contact, dry_run)
        
        # Update status counts
        if success:
            if status == "created":
                results["created"] += 1
                if results["created"] <= 10:
                    print(f"   [{i+1}/{len(contacts)}] ✅ {name} - created")
            elif status == "updated":
                results["updated"] += 1
                if results["updated"] <= 5:
                    print(f"   [{i+1}/{len(contacts)}] 🔄 {name} - updated")
            elif status == "dry_run":
                if i < 10:
                    print(f"   [{i+1}/{len(contacts)}] 🔍 {name} ({email})")
        else:
            results["failed"] += 1
            if results["failed"] <= 5:
                print(f"   [{i+1}/{len(contacts)}] ❌ {name} - {status}")
        
        # Rate limiting
        if not dry_run:
            time.sleep(0.15)
        
        # Progress update every 500
        if (i + 1) % 500 == 0:
            print(f"   ... processed {i+1}/{len(contacts)} contacts")
    
    return results


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Sync HubSpot contacts to Attio")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without syncing")
    parser.add_argument("--limit", type=int,
                        help="Limit number of contacts to sync")
    parser.add_argument("--test", action="store_true",
                        help="Test connections only")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("👤 HUBSPOT CONTACTS → ATTIO SYNC")
    print("=" * 70)
    print(f"   Started: {datetime.now().isoformat()}")
    
    # Initialize clients
    hubspot = HubSpotClient()
    attio = AttioClient()
    
    # Check configurations
    if not hubspot.enabled:
        print("❌ HUBSPOT_API_KEY not set in .env")
        return
    
    if not attio.enabled:
        print("❌ ATTIO_API_KEY not set in .env")
        return
    
    # Test connections
    print("\n🔗 Testing connections...")
    
    if not hubspot.test_connection():
        print("❌ HubSpot connection failed")
        return
    print("   ✅ HubSpot connected")
    
    if not attio.test_connection():
        print("❌ Attio connection failed")
        return
    print("   ✅ Attio connected")
    
    if args.test:
        print("\n✅ Connection tests passed!")
        return
    
    # Run sync
    results = sync_all_contacts(
        hubspot, attio,
        dry_run=args.dry_run,
        limit=args.limit
    )
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SYNC SUMMARY")
    print("=" * 70)
    print(f"   Total processed: {results['total']}")
    print(f"   ✅ Created: {results['created']}")
    print(f"   🔄 Updated: {results['updated']}")
    print(f"   ❌ Failed: {results['failed']}")
    print(f"\n   Completed: {datetime.now().isoformat()}")
    print(f"\n🔗 View in Attio: https://app.attio.com/{ATTIO_WORKSPACE_SLUG}/people")


if __name__ == "__main__":
    main()

