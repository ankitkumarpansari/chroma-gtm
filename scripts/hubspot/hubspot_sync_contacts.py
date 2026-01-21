#!/usr/bin/env python3
"""
HubSpot Contact Sync

Syncs contacts from all data sources with proper metadata:
- Tier CSV files (product signups)
- AI Engineer speakers
- Dormant business users
- SI Partner contacts

Contact Metadata includes:
- Email, Name, Company
- Job Title, LinkedIn URL, GitHub URL, Twitter URL
- Developer Persona, Lead Score
- VIP Status, Interaction History
- Location, Cohort Role

Usage:
    python3 hubspot_sync_contacts.py                    # Sync all contacts
    python3 hubspot_sync_contacts.py --source tier     # Sync tier contacts only
    python3 hubspot_sync_contacts.py --source speakers # Sync speakers only
    python3 hubspot_sync_contacts.py --source dormant  # Sync dormant users only
    python3 hubspot_sync_contacts.py --dry-run         # Preview without syncing
    python3 hubspot_sync_contacts.py --limit 50        # Limit contacts
"""

import os
import json
import csv
import requests
import time
import argparse
from datetime import datetime
from typing import Optional, Dict, List, Set
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
HUBSPOT_BASE_URL = "https://api.hubapi.com"
PROJECT_ROOT = Path(__file__).parent

# =============================================================================
# Data Sources
# =============================================================================

DATA_SOURCES = {
    "tier": {
        "tier1": PROJECT_ROOT / "tier1_enterprise_tech.csv",
        "tier2": PROJECT_ROOT / "tier2_ai_ml_startups.csv",
        "tier3": PROJECT_ROOT / "tier3_tech_agencies.csv",
        "tier4": PROJECT_ROOT / "tier4_other_business.csv",
    },
    "speakers": PROJECT_ROOT / "ai_engineer_speakers_enriched.json",
    "dormant": PROJECT_ROOT / "dormant_business_users_identified.json",
}

# =============================================================================
# Developer Persona Mapping
# =============================================================================

def map_job_title_to_persona(job_title: str) -> str:
    """Map job title to developer persona."""
    if not job_title:
        return ""
    
    title_lower = job_title.lower()
    
    if any(x in title_lower for x in ["cto", "vp eng", "vp of eng", "chief technology"]):
        return "cto_vp"
    elif any(x in title_lower for x in ["engineering manager", "eng manager", "director of eng"]):
        return "eng_manager"
    elif any(x in title_lower for x in ["ai engineer", "ml engineer", "machine learning", "ai/ml"]):
        return "ai_ml_engineer"
    elif any(x in title_lower for x in ["applied ai", "ai research"]):
        return "applied_ai"
    elif any(x in title_lower for x in ["data engineer", "data platform"]):
        return "data_engineer"
    elif any(x in title_lower for x in ["devops", "sre", "platform", "infrastructure"]):
        return "platform"
    elif any(x in title_lower for x in ["backend", "server", "api"]):
        return "backend"
    elif any(x in title_lower for x in ["full stack", "fullstack", "software engineer"]):
        return "fullstack"
    elif any(x in title_lower for x in ["product", "pm", "product manager"]):
        return "product"
    elif any(x in title_lower for x in ["founder", "ceo", "co-founder"]):
        return "cto_vp"  # Founders often make technical decisions
    else:
        return ""

def map_cohort_role(job_title: str, is_vip: bool) -> str:
    """Map to cohort role based on job title and VIP status."""
    if not job_title:
        if is_vip:
            return "champion"
        return ""
    
    title_lower = job_title.lower()
    
    if any(x in title_lower for x in ["cto", "vp", "chief", "director", "head of"]):
        return "decision_maker"
    elif any(x in title_lower for x in ["founder", "ceo", "co-founder"]):
        return "decision_maker"
    elif any(x in title_lower for x in ["manager", "lead", "principal", "staff"]):
        return "influencer"
    elif any(x in title_lower for x in ["engineer", "developer", "scientist"]):
        return "technical_evaluator"
    elif is_vip:
        return "champion"
    else:
        return "end_user"


# =============================================================================
# HubSpot Client
# =============================================================================

class HubSpotContactClient:
    """HubSpot API client for contacts."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or HUBSPOT_API_KEY
        self.enabled = bool(self.api_key)
        self.existing_contacts: Dict[str, str] = {}  # email -> id
        self.company_cache: Dict[str, str] = {}  # company name -> id
        
        if not self.enabled:
            print("❌ HUBSPOT_API_KEY not set in .env")
        else:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
    
    def _request(self, method: str, endpoint: str, json_data: dict = None,
                 retries: int = 3) -> Optional[dict]:
        """Make API request with retry logic."""
        if not self.enabled:
            return None
            
        url = f"{HUBSPOT_BASE_URL}{endpoint}"
        
        for attempt in range(retries):
            try:
                if method == "GET":
                    response = requests.get(url, headers=self.headers)
                elif method == "POST":
                    response = requests.post(url, headers=self.headers, json=json_data)
                elif method == "PATCH":
                    response = requests.patch(url, headers=self.headers, json=json_data)
                elif method == "PUT":
                    response = requests.put(url, headers=self.headers, json=json_data)
                else:
                    raise ValueError(f"Unknown method: {method}")
                
                if response.status_code in [200, 201, 204]:
                    if response.status_code == 204:
                        return {"success": True}
                    return response.json()
                elif response.status_code == 409:
                    return {"conflict": True, "response": response.json()}
                elif response.status_code == 429:
                    wait_time = int(response.headers.get("Retry-After", 10))
                    print(f"   ⏳ Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    # Return error on any non-success status
                    return {"error": response.status_code, "message": response.text[:500]}
                    
            except Exception as e:
                if attempt == retries - 1:
                    return {"error": str(e)}
                time.sleep(1)  # Wait before retry
        
        return None
    
    def test_connection(self) -> bool:
        """Test HubSpot API connection."""
        response = self._request("GET", "/crm/v3/objects/contacts?limit=1")
        return response is not None and "error" not in response
    
    def load_existing_contacts(self) -> None:
        """Load all existing contacts for deduplication."""
        print("   Loading existing contacts from HubSpot...")
        after = None
        
        while True:
            endpoint = "/crm/v3/objects/contacts?limit=100&properties=email"
            if after:
                endpoint += f"&after={after}"
            
            response = self._request("GET", endpoint)
            if not response or "error" in response:
                break
            
            for contact in response.get("results", []):
                props = contact.get("properties", {})
                email = (props.get("email") or "").lower().strip()
                contact_id = contact.get("id")
                
                if email:
                    self.existing_contacts[email] = contact_id
            
            paging = response.get("paging", {})
            after = paging.get("next", {}).get("after")
            if not after:
                break
        
        print(f"   Found {len(self.existing_contacts)} existing contacts")
    
    def load_company_cache(self) -> None:
        """Load companies for association."""
        print("   Loading companies for association...")
        after = None
        
        while True:
            endpoint = "/crm/v3/objects/companies?limit=100&properties=name"
            if after:
                endpoint += f"&after={after}"
            
            response = self._request("GET", endpoint)
            if not response or "error" in response:
                break
            
            for company in response.get("results", []):
                props = company.get("properties", {})
                name = (props.get("name") or "").lower().strip()
                company_id = company.get("id")
                
                if name:
                    self.company_cache[name] = company_id
            
            paging = response.get("paging", {})
            after = paging.get("next", {}).get("after")
            if not after:
                break
        
        print(f"   Loaded {len(self.company_cache)} companies for association")
    
    def find_company_id(self, company_name: str) -> Optional[str]:
        """Find company ID by name."""
        if not company_name:
            return None
        return self.company_cache.get(company_name.lower().strip())
    
    def create_or_update_contact(self, properties: dict) -> tuple:
        """Create or update a contact.
        
        Returns: (success, status, contact_id)
        """
        email = (properties.get("email") or "").lower().strip()
        
        if not email:
            return False, "no_email", None
        
        # Check if exists
        existing_id = self.existing_contacts.get(email)
        
        if existing_id:
            # Update existing
            response = self._request(
                "PATCH",
                f"/crm/v3/objects/contacts/{existing_id}",
                {"properties": properties}
            )
            if response and "error" not in response:
                return True, "updated", existing_id
            return False, "update_failed", existing_id
        else:
            # Create new
            response = self._request(
                "POST",
                "/crm/v3/objects/contacts",
                {"properties": properties}
            )
            if response and "error" not in response:
                contact_id = response.get("id")
                self.existing_contacts[email] = contact_id
                return True, "created", contact_id
            # Log the error for debugging
            error_msg = response.get("message", "Unknown error") if response else "No response"
            return False, f"create_failed: {error_msg}", None
    
    def associate_contact_to_company(self, contact_id: str, company_id: str) -> bool:
        """Associate a contact to a company."""
        response = self._request(
            "PUT",
            f"/crm/v3/objects/contacts/{contact_id}/associations/companies/{company_id}/contact_to_company",
            {}
        )
        return response is not None and "error" not in response


# =============================================================================
# Data Loaders
# =============================================================================

def clean_url(url: str) -> str:
    """Clean and normalize URL."""
    if not url:
        return ""
    url = url.strip()
    if not url.startswith("http"):
        url = "https://" + url
    return url


def load_tier_contacts() -> List[dict]:
    """Load contacts from tier CSV files."""
    contacts = []
    seen_emails: Set[str] = set()
    
    tier_mapping = {
        "tier1": "enterprise",
        "tier2": "growth",
        "tier3": "starter",
        "tier4": "free",
    }
    
    for tier_key, usage_tier in tier_mapping.items():
        file_path = DATA_SOURCES["tier"].get(tier_key)
        if not file_path or not file_path.exists():
            print(f"   ⚠️ File not found: {file_path}")
            continue
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                count = 0
                
                for row in reader:
                    email = (row.get("email") or "").lower().strip()
                    
                    # Skip invalid emails
                    if not email or "@" not in email:
                        continue
                    
                    # Skip internal Chroma emails
                    if "chroma" in email or "staffjoy" in email:
                        continue
                    
                    # Deduplicate
                    if email in seen_emails:
                        continue
                    seen_emails.add(email)
                    
                    # Parse name
                    name = row.get("name", "")
                    first_name = ""
                    last_name = ""
                    if name:
                        parts = name.split(" ", 1)
                        first_name = parts[0] if parts else ""
                        last_name = parts[1] if len(parts) > 1 else ""
                    
                    # Map job title to persona
                    job_title = row.get("enriched_job_title", "")
                    developer_persona = map_job_title_to_persona(job_title)
                    
                    # Map cohort role
                    is_vip = row.get("is_vip", "").upper() == "TRUE"
                    cohort_role = map_cohort_role(job_title, is_vip)
                    
                    # Build contact data
                    contact = {
                        "email": email,
                        "firstname": first_name,
                        "lastname": last_name,
                        "company": row.get("enriched_company", ""),
                        "jobtitle": job_title,
                        "city": row.get("enriched_location", "").split(",")[0] if row.get("enriched_location") else "",
                        "lifecyclestage": "lead",
                    }
                    
                    # Add LinkedIn URL (use HubSpot's built-in property)
                    linkedin = row.get("enriched_linkedin_url", "")
                    if linkedin:
                        contact["hs_linkedin_url"] = clean_url(linkedin)
                    
                    # Add GitHub URL (custom property)
                    github = row.get("enriched_github_url", "")
                    if github:
                        contact["github_url"] = clean_url(github)
                    
                    # Add Twitter URL
                    twitter = row.get("twitter_url", "")
                    if twitter:
                        contact["twitter_url"] = clean_url(twitter)
                    
                    # Add custom properties
                    if developer_persona:
                        contact["developer_persona"] = developer_persona
                    
                    if cohort_role:
                        contact["contact_cohort_role"] = cohort_role
                    
                    # Add lead score (custom property)
                    lead_score = row.get("lead_score", "")
                    if lead_score:
                        try:
                            contact["lead_score_custom"] = int(lead_score)
                        except:
                            pass
                    
                    # Add VIP status
                    if is_vip:
                        contact["is_vip"] = "true"
                    
                    # Add interaction history
                    contact["chroma_interaction_history"] = "cloud_signup"
                    
                    # Store company name for association
                    contact["_company_name"] = row.get("enriched_company", "")
                    contact["_source"] = f"tier_{tier_key}"
                    
                    contacts.append(contact)
                    count += 1
            
            print(f"   Loaded {tier_key}: {count} contacts")
            
        except Exception as e:
            print(f"   ❌ Error loading {file_path}: {e}")
    
    return contacts


def load_speaker_contacts() -> List[dict]:
    """Load contacts from AI engineer speakers."""
    contacts = []
    
    file_path = DATA_SOURCES["speakers"]
    if not file_path.exists():
        print(f"   ⚠️ File not found: {file_path}")
        return contacts
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        
        seen_emails: Set[str] = set()
        
        for speaker in data:
            email = (speaker.get("email") or "").lower().strip()
            name = speaker.get("name", "")
            
            # Skip if no email or name
            if not name:
                continue
            
            # Parse name
            parts = name.split(" ", 1)
            first_name = parts[0] if parts else ""
            last_name = parts[1] if len(parts) > 1 else ""
            
            # Create contact even without email (use name as key)
            if email and email in seen_emails:
                continue
            if email:
                seen_emails.add(email)
            
            contact = {
                "firstname": first_name,
                "lastname": last_name,
                "company": speaker.get("company", ""),
                "lifecyclestage": "lead",
            }
            
            if email:
                contact["email"] = email
            
            # Add LinkedIn
            linkedin = speaker.get("linkedin_url", "")
            if linkedin:
                contact["hs_linkedin_url"] = clean_url(linkedin)
            
            # Add Twitter
            twitter = speaker.get("twitter", "")
            if twitter:
                contact["twitter_url"] = clean_url(twitter)
            
            # Add headline as job title
            headline = speaker.get("headline", "")
            if headline:
                contact["jobtitle"] = headline[:255]
                contact["developer_persona"] = map_job_title_to_persona(headline)
            
            # Add location
            location = speaker.get("location", "")
            if location:
                contact["city"] = location.split(",")[0]
            
            # Set as influencer (speakers are thought leaders)
            contact["contact_cohort_role"] = "influencer"
            
            # Add interaction history
            contact["chroma_interaction_history"] = "conference"
            
            # Store metadata
            contact["_company_name"] = speaker.get("company", "")
            contact["_source"] = "ai_speaker"
            contact["_video"] = speaker.get("video", "")
            
            contacts.append(contact)
        
        print(f"   Loaded {len(contacts)} AI speaker contacts")
        
    except Exception as e:
        print(f"   ❌ Error loading speakers: {e}")
    
    return contacts


def load_dormant_contacts() -> List[dict]:
    """Load contacts from dormant business users."""
    contacts = []
    
    file_path = DATA_SOURCES["dormant"]
    if not file_path.exists():
        print(f"   ⚠️ File not found: {file_path}")
        return contacts
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        
        seen_emails: Set[str] = set()
        
        for user in data.get("users", []):
            email = (user.get("email") or "").lower().strip()
            
            if not email or "@" not in email:
                continue
            
            if email in seen_emails:
                continue
            seen_emails.add(email)
            
            # Parse name
            name = user.get("name", "")
            first_name = ""
            last_name = ""
            if name:
                parts = name.split(" ", 1)
                first_name = parts[0] if parts else ""
                last_name = parts[1] if len(parts) > 1 else ""
            
            # Map priority to lead score
            priority = user.get("priority", "").upper()
            if priority == "VERY HIGH":
                lead_score = 10
            elif priority == "HIGH":
                lead_score = 8
            elif priority == "MEDIUM":
                lead_score = 5
            else:
                lead_score = 3
            
            contact = {
                "email": email,
                "firstname": first_name,
                "lastname": last_name,
                "company": user.get("company", ""),
                "lifecyclestage": "lead",
                "lead_score_custom": lead_score,
            }
            
            # Add country as city (rough approximation)
            country = user.get("country", "")
            if country:
                contact["country"] = country
            
            # Add VIP status
            if user.get("is_vip"):
                contact["is_vip"] = "true"
                contact["contact_cohort_role"] = "champion"
            
            # Add interaction history
            contact["chroma_interaction_history"] = "cloud_signup"
            
            # Store metadata
            contact["_company_name"] = user.get("company", "")
            contact["_source"] = "dormant_user"
            contact["_tier"] = user.get("tier", "")
            
            contacts.append(contact)
        
        print(f"   Loaded {len(contacts)} dormant user contacts")
        
    except Exception as e:
        print(f"   ❌ Error loading dormant users: {e}")
    
    return contacts


# =============================================================================
# Sync Functions
# =============================================================================

def sync_contacts(client: HubSpotContactClient, contacts: List[dict],
                  source_name: str, dry_run: bool = False, limit: int = None) -> dict:
    """Sync contacts to HubSpot."""
    results = {
        "source": source_name,
        "total": len(contacts),
        "created": 0,
        "updated": 0,
        "failed": 0,
        "associated": 0,
    }
    
    if limit:
        contacts = contacts[:limit]
        results["total"] = len(contacts)
    
    if not contacts:
        print(f"   No contacts to sync from {source_name}")
        return results
    
    print(f"\n📤 Syncing {len(contacts)} contacts from {source_name}...")
    
    if dry_run:
        print("   [DRY RUN] Would sync:")
        for c in contacts[:10]:
            email = c.get("email", "no email")
            name = f"{c.get('firstname', '')} {c.get('lastname', '')}".strip() or "Unknown"
            company = c.get("company", "")
            print(f"      • {name} ({email}) - {company}")
        if len(contacts) > 10:
            print(f"      ... and {len(contacts) - 10} more")
        return results
    
    for i, contact in enumerate(contacts):
        email = contact.get("email", "")
        name = f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip() or "Unknown"
        
        # Extract metadata (not sent to HubSpot)
        company_name = contact.pop("_company_name", "")
        source = contact.pop("_source", "")
        contact.pop("_video", None)
        contact.pop("_tier", None)
        
        # Skip contacts without email
        if not email:
            results["failed"] += 1
            continue
        
        success, status, contact_id = client.create_or_update_contact(contact)
        
        if status == "created":
            results["created"] += 1
            if results["created"] <= 10:
                print(f"   [{i+1}/{len(contacts)}] ✅ {name} - created")
        elif status == "updated":
            results["updated"] += 1
            if results["updated"] <= 5:
                print(f"   [{i+1}/{len(contacts)}] 🔄 {name} - updated")
        else:
            results["failed"] += 1
            if results["failed"] <= 5:
                print(f"   [{i+1}/{len(contacts)}] ❌ {name} - {status}")
        
        # Associate to company if found
        if contact_id and company_name:
            company_id = client.find_company_id(company_name)
            if company_id:
                if client.associate_contact_to_company(contact_id, company_id):
                    results["associated"] += 1
        
        # Rate limiting
        time.sleep(0.1)
    
    return results


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Sync contacts to HubSpot")
    parser.add_argument("--source", type=str, choices=["tier", "speakers", "dormant", "all"],
                        default="all", help="Contact source to sync")
    parser.add_argument("--dry-run", action="store_true", help="Preview without syncing")
    parser.add_argument("--limit", type=int, help="Limit contacts per source")
    args = parser.parse_args()
    
    print("=" * 70)
    print("👤 HUBSPOT CONTACT SYNC")
    print("=" * 70)
    print(f"   Started: {datetime.now().isoformat()}")
    
    # Initialize client
    client = HubSpotContactClient()
    if not client.enabled:
        return
    
    print(f"   API Key: {client.api_key[:20]}...")
    
    # Test connection
    print("\n🔗 Testing HubSpot connection...")
    if not client.test_connection():
        print("❌ HubSpot connection failed")
        return
    print("✅ HubSpot connection successful!")
    
    # Load existing data
    if not args.dry_run:
        client.load_existing_contacts()
        client.load_company_cache()
    
    all_results = []
    
    # Determine sources to sync
    sources = [args.source] if args.source != "all" else ["tier", "speakers", "dormant"]
    
    for source in sources:
        print(f"\n{'=' * 70}")
        
        if source == "tier":
            print("📋 TIER CONTACTS (Product Signups)")
            print("=" * 70)
            contacts = load_tier_contacts()
            results = sync_contacts(client, contacts, "Tier Contacts",
                                   args.dry_run, args.limit)
            
        elif source == "speakers":
            print("🎤 AI ENGINEER SPEAKERS")
            print("=" * 70)
            contacts = load_speaker_contacts()
            # Filter to only contacts with emails
            contacts = [c for c in contacts if c.get("email")]
            results = sync_contacts(client, contacts, "AI Speakers",
                                   args.dry_run, args.limit)
            
        elif source == "dormant":
            print("😴 DORMANT BUSINESS USERS")
            print("=" * 70)
            contacts = load_dormant_contacts()
            results = sync_contacts(client, contacts, "Dormant Users",
                                   args.dry_run, args.limit)
        
        all_results.append(results)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SYNC SUMMARY")
    print("=" * 70)
    
    total_created = sum(r["created"] for r in all_results)
    total_updated = sum(r["updated"] for r in all_results)
    total_failed = sum(r["failed"] for r in all_results)
    total_associated = sum(r["associated"] for r in all_results)
    
    for r in all_results:
        print(f"\n   {r['source']}:")
        print(f"      Total: {r['total']}")
        print(f"      ✅ Created: {r['created']}")
        print(f"      🔄 Updated: {r['updated']}")
        print(f"      ❌ Failed: {r['failed']}")
        print(f"      🔗 Associated to Company: {r['associated']}")
    
    print(f"\n   GRAND TOTAL:")
    print(f"      ✅ Created: {total_created}")
    print(f"      🔄 Updated: {total_updated}")
    print(f"      ❌ Failed: {total_failed}")
    print(f"      🔗 Associated: {total_associated}")
    
    print(f"\n   Completed: {datetime.now().isoformat()}")
    print("\n🔗 View contacts in HubSpot: https://app.hubspot.com")


if __name__ == "__main__":
    main()

