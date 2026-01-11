#!/usr/bin/env python3
"""
Enrich Ping Identity contact (Arun Goel - VP Engineering) into HubSpot.

This script creates/updates:
1. Company record for Ping Identity
2. Contact record for Arun Goel (VP of Engineering)
3. Associates the contact with the company

Usage:
    python enrich_ping_identity_to_hubspot.py
    python enrich_ping_identity_to_hubspot.py --test  # Test connection only
"""

import os
import requests
import time
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

# HubSpot Configuration
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
HUBSPOT_BASE_URL = "https://api.hubapi.com"

# ============================================
# ENRICHED DATA: Ping Identity & Arun Goel
# ============================================

COMPANY_DATA = {
    "name": "Ping Identity",
    "domain": "pingidentity.com",
    "description": """Identity security company providing enterprise identity solutions.

Key Facts:
- Founded: 2002 by Andre Durand
- HQ: Denver, Colorado
- Employees: 1,001-5,000
- Industry: Identity & Access Management (IAM)
- Recognition: Leader in 2024 Gartner Magic Quadrant for Access Management

Recent AI Initiatives:
- Nov 2025: Launched "Identity for AI" solution for securing AI agents
- Sept 2025: Released AI-Driven Trust Framework for enterprise security
- Focus on AI agent identity management and intelligent access control

Technology Focus:
- Identity Security Platform
- AI-powered identity verification
- Zero Trust architecture
- Customer & workforce identity solutions

Source: Deep Research Pipeline - Chroma GTM""",
    "industry": "COMPUTER_SOFTWARE",
    "city": "Denver",
    "state": "Colorado",
    "country": "United States",
    "website": "https://www.pingidentity.com",
    "linkedin_company_page": "https://linkedin.com/company/ping-identity",
    "numberofemployees": "2000",
}

CONTACT_DATA = {
    "firstname": "Arun",
    "lastname": "Goel",
    "email": "",  # We don't have verified email - HubSpot will need this filled
    "jobtitle": "VP of Engineering",
    "company": "Ping Identity",
    "city": "San Francisco",
    "state": "California",
    "linkedin_url": "https://www.linkedin.com/in/akgoel",
    
    # Notes with enriched intelligence
    "notes": """VP of Engineering at Ping Identity since June 2023.

BACKGROUND:
- Previous: Senior Director at VMware (2018-2023) - Led Tanzu Mission Control & VMware Marketplace
- Earlier roles: Oracle, Cisco Systems, Brocade, Aerohive Networks
- Education: MBA from Columbia Business School & UC Berkeley; Engineering degrees from UT Austin and IIT-BHU

TEAM (Direct Reports):
- Sudhir Prakash - Sr. Director, Global Quality & Performance Engineering
- Wesley Dunnington - VP Architecture, Chief Architect
- Sandeep Goyal - Sr. Director of Engineering
- 10+ additional engineering directors and staff engineers

KEY TALKING POINTS:
1. Ping Identity is heavily investing in AI - launched "Identity for AI" solution (Nov 2025)
2. They're building AI agent security and intelligent access control
3. Vector database could support: semantic identity matching, AI agent behavior analysis, fraud detection patterns, RAG for identity platform

OUTREACH STRATEGY:
- Primary Target: Arun Goel (owns technical infrastructure decisions)
- Champion: Wesley Dunnington (VP Architecture) - technical influencer
- Executive Sponsor: Rakesh Thaker (Chief Development Officer) for larger deals

Source: Deep Research - Chroma GTM (Jan 2026)"""
}


class HubSpotEnrich:
    """Enrich company and contact data into HubSpot."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or HUBSPOT_API_KEY
        if not self.api_key:
            print("❌ HUBSPOT_API_KEY not set in .env")
            print("   Get your private app access token from:")
            print("   https://app.hubspot.com/private-apps/YOUR_PORTAL_ID")
            self.enabled = False
        else:
            self.enabled = True
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
            elif method == "PATCH":
                response = requests.patch(url, headers=self.headers, json=json_data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=json_data)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 409:
                return {"conflict": True, "response": response.json()}
            elif response.status_code == 429:
                print("   ⏳ Rate limited, waiting 10 seconds...")
                time.sleep(10)
                return self._request(method, endpoint, json_data)
            else:
                print(f"   ⚠️ API error: {response.status_code} - {response.text[:500]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test HubSpot API connection."""
        response = self._request("GET", "/crm/v3/objects/companies?limit=1")
        return response is not None
    
    # ========== COMPANY METHODS ==========
    
    def find_company_by_domain(self, domain: str) -> Optional[dict]:
        """Search for existing company by domain."""
        response = self._request(
            "POST",
            "/crm/v3/objects/companies/search",
            {
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "domain",
                        "operator": "EQ",
                        "value": domain
                    }]
                }],
                "limit": 1
            }
        )
        
        if response and response.get("results"):
            return response["results"][0]
        return None
    
    def find_company_by_name(self, name: str) -> Optional[dict]:
        """Search for existing company by name."""
        response = self._request(
            "POST",
            "/crm/v3/objects/companies/search",
            {
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "name",
                        "operator": "EQ",
                        "value": name
                    }]
                }],
                "limit": 1
            }
        )
        
        if response and response.get("results"):
            return response["results"][0]
        return None
    
    def create_or_update_company(self, company_data: dict) -> Optional[str]:
        """Create or update a company record."""
        # Check if company exists by domain first
        existing = self.find_company_by_domain(company_data.get("domain", ""))
        if not existing:
            existing = self.find_company_by_name(company_data.get("name", ""))
        
        properties = {
            "name": company_data["name"],
            "domain": company_data.get("domain", ""),
            "description": company_data.get("description", ""),
            "lifecyclestage": "lead",
            "hs_lead_status": "NEW",
        }
        
        # Add optional properties
        for prop in ["industry", "city", "state", "country", "website", 
                     "linkedin_company_page", "numberofemployees"]:
            if company_data.get(prop):
                properties[prop] = company_data[prop]
        
        if existing:
            # Update existing company
            company_id = existing.get("id")
            print(f"   📝 Company exists (ID: {company_id}), updating...")
            response = self._request(
                "PATCH",
                f"/crm/v3/objects/companies/{company_id}",
                {"properties": properties}
            )
            if response:
                return company_id
        else:
            # Create new company
            print(f"   ➕ Creating new company...")
            response = self._request(
                "POST",
                "/crm/v3/objects/companies",
                {"properties": properties}
            )
            if response:
                return response.get("id")
        
        return None
    
    # ========== CONTACT METHODS ==========
    
    def find_contact_by_name_and_company(self, firstname: str, lastname: str, company: str) -> Optional[dict]:
        """Search for existing contact by name and company."""
        response = self._request(
            "POST",
            "/crm/v3/objects/contacts/search",
            {
                "filterGroups": [{
                    "filters": [
                        {"propertyName": "firstname", "operator": "EQ", "value": firstname},
                        {"propertyName": "lastname", "operator": "EQ", "value": lastname},
                        {"propertyName": "company", "operator": "EQ", "value": company}
                    ]
                }],
                "limit": 1
            }
        )
        
        if response and response.get("results"):
            return response["results"][0]
        return None
    
    def find_contact_by_linkedin(self, linkedin_url: str) -> Optional[dict]:
        """Search for existing contact by LinkedIn URL."""
        # Try with hs_linkedin_url property (standard HubSpot property)
        for prop_name in ["hs_linkedinbio", "linkedin_url"]:
            response = self._request(
                "POST",
                "/crm/v3/objects/contacts/search",
                {
                    "filterGroups": [{
                        "filters": [{
                            "propertyName": prop_name,
                            "operator": "CONTAINS_TOKEN",
                            "value": linkedin_url.split("/in/")[-1].rstrip("/")
                        }]
                    }],
                    "limit": 1
                }
            )
            
            if response and response.get("results"):
                return response["results"][0]
        
        return None
    
    def create_or_update_contact(self, contact_data: dict) -> Optional[str]:
        """Create or update a contact record."""
        # Check if contact exists
        existing = self.find_contact_by_name_and_company(
            contact_data.get("firstname", ""),
            contact_data.get("lastname", ""),
            contact_data.get("company", "")
        )
        
        if not existing and contact_data.get("linkedin_url"):
            existing = self.find_contact_by_linkedin(contact_data["linkedin_url"])
        
        properties = {
            "firstname": contact_data["firstname"],
            "lastname": contact_data["lastname"],
            "jobtitle": contact_data.get("jobtitle", ""),
            "company": contact_data.get("company", ""),
            "lifecyclestage": "lead",
            "hs_lead_status": "NEW",
        }
        
        # Add optional properties
        if contact_data.get("email"):
            properties["email"] = contact_data["email"]
        if contact_data.get("city"):
            properties["city"] = contact_data["city"]
        if contact_data.get("state"):
            properties["state"] = contact_data["state"]
        
        # Add notes to the description/message field
        if contact_data.get("notes"):
            properties["message"] = contact_data["notes"][:65535]  # HubSpot limit
        
        if existing:
            # Update existing contact
            contact_id = existing.get("id")
            print(f"   📝 Contact exists (ID: {contact_id}), updating...")
            response = self._request(
                "PATCH",
                f"/crm/v3/objects/contacts/{contact_id}",
                {"properties": properties}
            )
            if response:
                return contact_id
        else:
            # Create new contact
            print(f"   ➕ Creating new contact...")
            response = self._request(
                "POST",
                "/crm/v3/objects/contacts",
                {"properties": properties}
            )
            if response:
                return response.get("id")
        
        return None
    
    # ========== ASSOCIATION METHODS ==========
    
    def associate_contact_to_company(self, contact_id: str, company_id: str) -> bool:
        """Associate a contact with a company."""
        response = self._request(
            "PUT",
            f"/crm/v3/objects/contacts/{contact_id}/associations/companies/{company_id}/contact_to_company",
            {}
        )
        return response is not None
    
    def create_note_for_contact(self, contact_id: str, note_body: str) -> Optional[str]:
        """Create a note associated with a contact."""
        response = self._request(
            "POST",
            "/crm/v3/objects/notes",
            {
                "properties": {
                    "hs_note_body": note_body,
                    "hs_timestamp": str(int(time.time() * 1000))
                },
                "associations": [{
                    "to": {"id": contact_id},
                    "types": [{
                        "associationCategory": "HUBSPOT_DEFINED",
                        "associationTypeId": 202  # Note to Contact
                    }]
                }]
            }
        )
        if response:
            return response.get("id")
        return None


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Enrich Ping Identity data into HubSpot")
    parser.add_argument("--test", action="store_true", help="Test connection only")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎯 ENRICHING PING IDENTITY INTO HUBSPOT")
    print("=" * 60)
    
    # Initialize HubSpot client
    hs = HubSpotEnrich()
    
    if not hs.enabled:
        return
    
    print(f"\n🔗 Testing HubSpot connection...")
    print(f"   API key: {hs.api_key[:20]}...")
    
    if not hs.test_connection():
        print("❌ HubSpot connection failed")
        return
    
    print("✅ HubSpot connection successful!")
    
    if args.test:
        return
    
    # Step 1: Create/Update Company
    print("\n" + "-" * 60)
    print("📦 STEP 1: Creating/Updating Company Record")
    print("-" * 60)
    print(f"   Company: {COMPANY_DATA['name']}")
    print(f"   Domain: {COMPANY_DATA['domain']}")
    
    company_id = hs.create_or_update_company(COMPANY_DATA)
    
    if company_id:
        print(f"   ✅ Company ID: {company_id}")
    else:
        print("   ❌ Failed to create/update company")
        return
    
    # Step 2: Create/Update Contact
    print("\n" + "-" * 60)
    print("👤 STEP 2: Creating/Updating Contact Record")
    print("-" * 60)
    print(f"   Contact: {CONTACT_DATA['firstname']} {CONTACT_DATA['lastname']}")
    print(f"   Title: {CONTACT_DATA['jobtitle']}")
    print(f"   LinkedIn: {CONTACT_DATA['linkedin_url']}")
    
    contact_id = hs.create_or_update_contact(CONTACT_DATA)
    
    if contact_id:
        print(f"   ✅ Contact ID: {contact_id}")
    else:
        print("   ❌ Failed to create/update contact")
        return
    
    # Step 3: Associate Contact to Company
    print("\n" + "-" * 60)
    print("🔗 STEP 3: Associating Contact to Company")
    print("-" * 60)
    
    if hs.associate_contact_to_company(contact_id, company_id):
        print(f"   ✅ Associated {CONTACT_DATA['firstname']} {CONTACT_DATA['lastname']} → {COMPANY_DATA['name']}")
    else:
        print("   ⚠️ Association may have failed (contact might already be associated)")
    
    # Step 4: Create enrichment note
    print("\n" + "-" * 60)
    print("📝 STEP 4: Adding Research Note")
    print("-" * 60)
    
    note_body = f"""🎯 SALES INTELLIGENCE: {CONTACT_DATA['firstname']} {CONTACT_DATA['lastname']} - {COMPANY_DATA['name']}

{CONTACT_DATA['notes']}

---
Enriched via Chroma GTM Research Agent
Date: January 2026"""
    
    note_id = hs.create_note_for_contact(contact_id, note_body)
    if note_id:
        print(f"   ✅ Note created (ID: {note_id})")
    else:
        print("   ⚠️ Note creation may have failed")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ ENRICHMENT COMPLETE")
    print("=" * 60)
    print(f"""
   Company: {COMPANY_DATA['name']}
   Company ID: {company_id}
   
   Contact: {CONTACT_DATA['firstname']} {CONTACT_DATA['lastname']}
   Contact ID: {contact_id}
   Title: {CONTACT_DATA['jobtitle']}
   LinkedIn: {CONTACT_DATA['linkedin_url']}
   
🔗 View in HubSpot:
   Company: https://app.hubspot.com/contacts/YOUR_PORTAL_ID/company/{company_id}
   Contact: https://app.hubspot.com/contacts/YOUR_PORTAL_ID/contact/{contact_id}
""")


if __name__ == "__main__":
    main()

