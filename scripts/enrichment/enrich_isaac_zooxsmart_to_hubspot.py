#!/usr/bin/env python3
"""
Enrich Isaac Sebastian (Data Scientist at Zoox Smart) into HubSpot.

This script creates/updates:
1. Company record for Zoox Smart
2. Contact record for Isaac Sebastian (Data Scientist I)
3. Associates the contact with the company
4. Creates a note about the email outreach

Usage:
    python enrich_isaac_zooxsmart_to_hubspot.py
    python enrich_isaac_zooxsmart_to_hubspot.py --test  # Test connection only
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
# ENRICHED DATA: Zoox Smart & Isaac Sebastian
# ============================================

COMPANY_DATA = {
    "name": "Zoox Smart Data",
    "domain": "zooxsmart.com",
    "description": """AI-datatech company providing data and AI platform solutions.

Key Facts:
- Company: Zoox Smart Data (Zoox AI-datatech)
- Website: https://www.zooxsmart.com
- Industry: Data & AI Platform, Business Intelligence
- Customers: 1,700+ customers across 27+ countries
- Focus: Transforming data into actionable insights with AI

Products & Services:
1. AI Labs - Custom AI solutions and data intelligence
   - Strategic diagnosis with data analysis
   - Rapid prototyping with agile development
   - Scalable solutions with AI Agents
   - Real-time actionable insights

2. Data Core - Data management and analytics platform
   - Conversational interface for exploring data
   - Automate up to 90% of ETL process
   - AI-powered exploratory analytics
   - Dynamic charts for data scientists

3. Sales Platform - Intelligent lead segmentation and prospecting
4. Risk Management Platform - Automated due diligence with AI
5. Marketing Platform - Advanced segmentation and multichannel engagement
6. Wi-Fi Analytics - Visitor data capture and flow mapping

Technology Focus:
- AI Agents and intelligent dashboards
- Semantic search and retrieval systems
- Data analytics and business intelligence
- Predictive modeling and customer segmentation

Use Cases for Chroma:
- Semantic search over knowledge bases
- Intelligent content retrieval for AI agents
- Vector search for data analytics
- RAG for AI Labs solutions

Source: Deep Research Pipeline - Chroma GTM (Jan 2026)""",
    "industry": "COMPUTER_SOFTWARE",
    "website": "https://www.zooxsmart.com",
    "linkedin_company_page": "https://linkedin.com/company/zoox-smart-data",
    # Note: numberofemployees must be a number, not a range string
}

CONTACT_DATA = {
    "firstname": "Isaac",
    "lastname": "Sebastian",
    "email": "isaac.sebastian@zooxsmart.com",
    "jobtitle": "Data Scientist I",
    "company": "Zoox Smart Data",
    "linkedin_url": "https://br.linkedin.com/in/isaac-sebastian-a60329191",
    
    # Notes with enriched intelligence
    "notes": """Data Scientist I at Zoox Smart Data.

LINKEDIN: https://br.linkedin.com/in/isaac-sebastian-a60329191

BACKGROUND:
- Role: Data Scientist I (entry-level data science position)
- Company: Zoox Smart Data (AI-datatech platform)
- Location: João Pessoa, Brazil (based on LinkedIn)
- Education: Universidade Federal da Paraíba

COMPANY CONTEXT:
Zoox Smart is a data and AI platform company with:
- 1,700+ customers across 27+ countries
- Focus on AI Labs, Data Core, and intelligent analytics
- Building AI agents and retrieval systems
- Strong in semantic search and data intelligence

CHROMA ENGAGEMENT:
- Signed up for Chroma Cloud (Jan 2026)
- Likely exploring vector search for:
  * AI Labs solutions (custom AI agents)
  * Data Core platform (data analytics)
  * Semantic search over knowledge bases
  * Intelligent content retrieval

OUTREACH DETAILS:
- Email sent: Jan 2026
- Subject: Chroma Cloud + Zoox
- Credit gesture: $500
- CC'd: Jeff Huber (founder)
- Focus: Semantic search and retrieval for AI agents and intelligent dashboards
- Resource shared: Search API docs (https://docs.trychroma.com/cloud/search-api/overview)

NEXT STEPS:
- Follow up on use case exploration
- Offer technical support via Slack channel
- Share relevant case studies for AI Labs/Data Core use cases

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
                     "linkedin_company_page"]:
            if company_data.get(prop):
                properties[prop] = company_data[prop]
        
        # Handle numberofemployees separately (must be numeric)
        if company_data.get("numberofemployees"):
            try:
                # If it's a range string, use midpoint or remove
                emp_str = str(company_data["numberofemployees"])
                if "-" in emp_str:
                    # For ranges like "201-500", use midpoint
                    parts = emp_str.split("-")
                    if len(parts) == 2:
                        properties["numberofemployees"] = int((int(parts[0]) + int(parts[1])) / 2)
                else:
                    properties["numberofemployees"] = int(emp_str)
            except (ValueError, AttributeError):
                pass  # Skip if not numeric
        
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
    
    def find_contact_by_email(self, email: str) -> Optional[dict]:
        """Search for existing contact by email."""
        response = self._request(
            "POST",
            "/crm/v3/objects/contacts/search",
            {
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "email",
                        "operator": "EQ",
                        "value": email
                    }]
                }],
                "limit": 1
            }
        )
        
        if response and response.get("results"):
            return response["results"][0]
        return None
    
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
        # Check if contact exists by email first
        existing = None
        if contact_data.get("email"):
            existing = self.find_contact_by_email(contact_data["email"])
        
        if not existing:
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
        # Note: LinkedIn URL is included in the notes field since custom properties may not exist
        
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
    
    parser = argparse.ArgumentParser(description="Enrich Isaac Sebastian & Zoox Smart data into HubSpot")
    parser.add_argument("--test", action="store_true", help="Test connection only")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎯 ENRICHING ISAAC SEBASTIAN & ZOOX SMART INTO HUBSPOT")
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
    print(f"   Email: {CONTACT_DATA['email']}")
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
        print(f"   ✅ Contact associated with company")
    else:
        print(f"   ⚠️ Failed to associate contact (may already be associated)")
    
    # Step 4: Create Note about Email Outreach
    print("\n" + "-" * 60)
    print("📝 STEP 4: Creating Note about Email Outreach")
    print("-" * 60)
    
    note_body = """Email Outreach - Chroma Cloud + Zoox (Jan 2026)

OUTREACH DETAILS:
- Email sent to Isaac Sebastian (Data Scientist I at Zoox Smart)
- Subject: Chroma Cloud + Zoox
- Date: January 2026
- CC'd: Jeff Huber (founder of Chroma)

EMAIL CONTENT:
- Welcomed Isaac to Chroma Cloud
- Highlighted Zoox's AI Labs and Data Core platform
- Offered semantic search and retrieval capabilities for AI agents
- Shared Search API documentation
- Offered call or Slack channel for support
- Credit gesture: $500

COMPANY CONTEXT:
Zoox Smart is building:
- AI Labs: Custom AI solutions with AI Agents
- Data Core: Data management and analytics platform
- Focus on semantic search and intelligent dashboards

NEXT STEPS:
- Follow up on use case exploration
- Offer technical support via Slack channel
- Share relevant case studies for AI Labs/Data Core use cases
- Monitor product usage and engagement

Source: Chroma GTM Outreach (Jan 2026)"""
    
    note_id = hs.create_note_for_contact(contact_id, note_body)
    
    if note_id:
        print(f"   ✅ Note created (ID: {note_id})")
    else:
        print(f"   ⚠️ Failed to create note")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ ENRICHMENT COMPLETE")
    print("=" * 60)
    print(f"   Company: {COMPANY_DATA['name']} (ID: {company_id})")
    print(f"   Contact: {CONTACT_DATA['firstname']} {CONTACT_DATA['lastname']} (ID: {contact_id})")
    print(f"   View in HubSpot: https://app.hubspot.com/contacts/YOUR_PORTAL_ID/contact/{contact_id}")


if __name__ == "__main__":
    main()

