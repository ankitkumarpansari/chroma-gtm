#!/usr/bin/env python3
"""
HubSpot Custom Properties Setup

Creates all custom properties needed for Chroma GTM data in HubSpot.

Usage:
    python hubspot_setup_properties.py          # Create all properties
    python hubspot_setup_properties.py --test   # Test connection only
    python hubspot_setup_properties.py --list   # List existing properties
"""

import os
import requests
import argparse
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
HUBSPOT_BASE_URL = "https://api.hubapi.com"

# =============================================================================
# Custom Property Definitions
# =============================================================================

COMPANY_PROPERTIES = [
    {
        "name": "lead_source",
        "label": "Lead Source",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "companyinformation",
        "description": "How this company was discovered",
        "options": [
            {"label": "Chroma Signal", "value": "chroma_signal"},
            {"label": "Deep Research", "value": "deep_research"},
            {"label": "Competitor Customer", "value": "competitor_customer"},
            {"label": "Product Signup", "value": "product_signup"},
            {"label": "LinkedIn Sales Nav", "value": "linkedin_sales_nav"},
            {"label": "AI Speakers", "value": "ai_speakers"},
            {"label": "Dormant User", "value": "dormant_user"},
            {"label": "Inbound", "value": "inbound"},
            {"label": "Referral", "value": "referral"},
        ]
    },
    {
        "name": "signal_tier",
        "label": "Signal Tier",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "companyinformation",
        "description": "Priority tier based on signal strength",
        "options": [
            {"label": "Tier 1 - Highest Priority", "value": "tier_1"},
            {"label": "Tier 2 - High Priority", "value": "tier_2"},
            {"label": "Tier 3 - Medium Priority", "value": "tier_3"},
            {"label": "Tier 4 - Standard", "value": "tier_4"},
        ]
    },
    {
        "name": "signal_strength",
        "label": "Signal Strength",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "companyinformation",
        "description": "Strength of buying signal",
        "options": [
            {"label": "High", "value": "high"},
            {"label": "Medium", "value": "medium"},
            {"label": "Low", "value": "low"},
        ]
    },
    {
        "name": "current_vector_db",
        "label": "Current Vector DB",
        "type": "string",
        "fieldType": "text",
        "groupName": "companyinformation",
        "description": "Vector database currently in use (Pinecone, Weaviate, Qdrant, PGVector, etc.)"
    },
    {
        "name": "competitor_source",
        "label": "Competitor Source",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "companyinformation",
        "description": "Which competitor this company was using",
        "options": [
            {"label": "Pinecone", "value": "pinecone"},
            {"label": "Weaviate", "value": "weaviate"},
            {"label": "Qdrant", "value": "qdrant"},
            {"label": "Vespa", "value": "vespa"},
            {"label": "LangChain", "value": "langchain"},
            {"label": "LlamaIndex", "value": "llamaindex"},
            {"label": "MongoDB", "value": "mongodb"},
            {"label": "PGVector", "value": "pgvector"},
            {"label": "Elasticsearch", "value": "elasticsearch"},
            {"label": "OpenSearch", "value": "opensearch"},
        ]
    },
    {
        "name": "use_case",
        "label": "Use Case",
        "type": "string",
        "fieldType": "textarea",
        "groupName": "companyinformation",
        "description": "Primary use case (RAG, Agent, Search, etc.)"
    },
    {
        "name": "linkedin_company_url",
        "label": "LinkedIn Company URL",
        "type": "string",
        "fieldType": "text",
        "groupName": "companyinformation",
        "description": "Company LinkedIn page URL"
    },
    {
        "name": "funding_stage",
        "label": "Funding Stage",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "companyinformation",
        "description": "Current funding stage",
        "options": [
            {"label": "Pre-Seed", "value": "pre_seed"},
            {"label": "Seed", "value": "seed"},
            {"label": "Series A", "value": "series_a"},
            {"label": "Series B", "value": "series_b"},
            {"label": "Series C", "value": "series_c"},
            {"label": "Series D+", "value": "series_d_plus"},
            {"label": "Public", "value": "public"},
            {"label": "Bootstrapped", "value": "bootstrapped"},
            {"label": "Acquired", "value": "acquired"},
        ]
    },
    {
        "name": "chroma_signal_id",
        "label": "Chroma Signal ID",
        "type": "string",
        "fieldType": "text",
        "groupName": "companyinformation",
        "description": "Internal ID from Chroma Signal database"
    },
    {
        "name": "valuation_info",
        "label": "Valuation Info",
        "type": "string",
        "fieldType": "text",
        "groupName": "companyinformation",
        "description": "Known valuation or funding amount"
    },
    {
        "name": "source_channel",
        "label": "Source Channel",
        "type": "string",
        "fieldType": "text",
        "groupName": "companyinformation",
        "description": "Specific channel where company was found (e.g., LangChain YouTube)"
    },
]

CONTACT_PROPERTIES = [
    {
        "name": "github_url",
        "label": "GitHub URL",
        "type": "string",
        "fieldType": "text",
        "groupName": "contactinformation",
        "description": "GitHub profile URL"
    },
    {
        "name": "twitter_url",
        "label": "Twitter/X URL",
        "type": "string",
        "fieldType": "text",
        "groupName": "contactinformation",
        "description": "Twitter/X profile URL"
    },
    {
        "name": "lead_score_custom",
        "label": "Lead Score (Custom)",
        "type": "number",
        "fieldType": "number",
        "groupName": "contactinformation",
        "description": "Custom lead score from 1-10"
    },
    {
        "name": "is_vip",
        "label": "VIP Status",
        "type": "enumeration",
        "fieldType": "booleancheckbox",
        "groupName": "contactinformation",
        "description": "Is this contact a VIP?",
        "options": [
            {"label": "Yes", "value": "true"},
            {"label": "No", "value": "false"},
        ]
    },
    {
        "name": "enrichment_source",
        "label": "Enrichment Source",
        "type": "string",
        "fieldType": "text",
        "groupName": "contactinformation",
        "description": "How this contact was enriched"
    },
    {
        "name": "technical_role",
        "label": "Technical Role",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "contactinformation",
        "description": "Type of technical role",
        "options": [
            {"label": "Engineer", "value": "engineer"},
            {"label": "Engineering Manager", "value": "eng_manager"},
            {"label": "CTO/VP Eng", "value": "cto_vp"},
            {"label": "Data Scientist", "value": "data_scientist"},
            {"label": "ML Engineer", "value": "ml_engineer"},
            {"label": "DevOps/Platform", "value": "devops"},
            {"label": "Product", "value": "product"},
            {"label": "Other", "value": "other"},
        ]
    },
]


# =============================================================================
# HubSpot API Client
# =============================================================================

class HubSpotPropertyManager:
    """Manage HubSpot custom properties."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or HUBSPOT_API_KEY
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            print("❌ HUBSPOT_API_KEY not set in .env")
        else:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
    
    def _request(self, method: str, endpoint: str, json_data: dict = None) -> Optional[dict]:
        """Make API request."""
        if not self.enabled:
            return None
            
        url = f"{HUBSPOT_BASE_URL}{endpoint}"
        
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
            elif response.status_code == 409:
                return {"exists": True}
            else:
                return {"error": response.status_code, "message": response.text[:200]}
                
        except Exception as e:
            return {"error": str(e)}
    
    def test_connection(self) -> bool:
        """Test API connection."""
        response = self._request("GET", "/crm/v3/properties/companies")
        return response is not None and "error" not in response
    
    def list_properties(self, object_type: str = "companies") -> List[dict]:
        """List all properties for an object type."""
        response = self._request("GET", f"/crm/v3/properties/{object_type}")
        if response and "results" in response:
            return response["results"]
        return []
    
    def create_property(self, object_type: str, property_def: dict) -> tuple:
        """Create a custom property.
        
        Returns: (success, message)
        """
        endpoint = f"/crm/v3/properties/{object_type}"
        response = self._request("POST", endpoint, property_def)
        
        if response is None:
            return False, "Request failed"
        elif response.get("exists"):
            return True, "Already exists"
        elif "error" in response:
            return False, f"Error: {response.get('message', response.get('error'))}"
        else:
            return True, "Created"
    
    def setup_all_properties(self) -> dict:
        """Create all custom properties for companies and contacts."""
        results = {
            "companies": {"created": 0, "existed": 0, "failed": 0},
            "contacts": {"created": 0, "existed": 0, "failed": 0},
        }
        
        print("\n📝 Setting up Company properties...")
        for prop in COMPANY_PROPERTIES:
            success, message = self.create_property("companies", prop)
            if success:
                if "exists" in message.lower():
                    results["companies"]["existed"] += 1
                    print(f"   ⏭️  {prop['label']} - already exists")
                else:
                    results["companies"]["created"] += 1
                    print(f"   ✅ {prop['label']} - created")
            else:
                results["companies"]["failed"] += 1
                print(f"   ❌ {prop['label']} - {message}")
        
        print("\n📝 Setting up Contact properties...")
        for prop in CONTACT_PROPERTIES:
            success, message = self.create_property("contacts", prop)
            if success:
                if "exists" in message.lower():
                    results["contacts"]["existed"] += 1
                    print(f"   ⏭️  {prop['label']} - already exists")
                else:
                    results["contacts"]["created"] += 1
                    print(f"   ✅ {prop['label']} - created")
            else:
                results["contacts"]["failed"] += 1
                print(f"   ❌ {prop['label']} - {message}")
        
        return results


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Setup HubSpot custom properties")
    parser.add_argument("--test", action="store_true", help="Test connection only")
    parser.add_argument("--list", action="store_true", help="List existing properties")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🏷️  HUBSPOT PROPERTY SETUP")
    print("=" * 60)
    
    manager = HubSpotPropertyManager()
    
    if not manager.enabled:
        return
    
    print(f"   API Key: {manager.api_key[:20]}...")
    
    # Test connection
    print("\n🔗 Testing connection...")
    if not manager.test_connection():
        print("❌ Connection failed")
        return
    print("✅ Connection successful!")
    
    if args.test:
        return
    
    if args.list:
        print("\n📋 Existing Company Properties:")
        props = manager.list_properties("companies")
        custom_props = [p for p in props if not p.get("hubspotDefined", True)]
        for prop in custom_props[:30]:
            print(f"   • {prop['label']} ({prop['name']})")
        if len(custom_props) > 30:
            print(f"   ... and {len(custom_props) - 30} more")
        
        print(f"\n📋 Existing Contact Properties:")
        props = manager.list_properties("contacts")
        custom_props = [p for p in props if not p.get("hubspotDefined", True)]
        for prop in custom_props[:30]:
            print(f"   • {prop['label']} ({prop['name']})")
        return
    
    # Setup properties
    results = manager.setup_all_properties()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SETUP COMPLETE")
    print("=" * 60)
    print(f"\n   Company Properties:")
    print(f"      ✅ Created: {results['companies']['created']}")
    print(f"      ⏭️  Already existed: {results['companies']['existed']}")
    print(f"      ❌ Failed: {results['companies']['failed']}")
    print(f"\n   Contact Properties:")
    print(f"      ✅ Created: {results['contacts']['created']}")
    print(f"      ⏭️  Already existed: {results['contacts']['existed']}")
    print(f"      ❌ Failed: {results['contacts']['failed']}")


if __name__ == "__main__":
    main()

