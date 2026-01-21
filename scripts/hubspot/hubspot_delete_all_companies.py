#!/usr/bin/env python3
"""
HubSpot Delete All Companies

⚠️  WARNING: This script will DELETE ALL companies from your HubSpot account!
    Use with caution. This action cannot be undone.

Usage:
    python3 hubspot_delete_all_companies.py --count    # Count companies only
    python3 hubspot_delete_all_companies.py --preview  # Preview what will be deleted
    python3 hubspot_delete_all_companies.py --delete   # Actually delete (requires confirmation)
"""

import os
import requests
import time
import argparse
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
HUBSPOT_BASE_URL = "https://api.hubapi.com"


class HubSpotDeleter:
    """Delete companies from HubSpot."""
    
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
                elif method == "DELETE":
                    response = requests.delete(url, headers=self.headers)
                else:
                    raise ValueError(f"Unknown method: {method}")
                
                if response.status_code in [200, 201, 204]:
                    if response.status_code == 204:
                        return {"success": True}
                    return response.json()
                elif response.status_code == 429:
                    wait_time = int(response.headers.get("Retry-After", 10))
                    print(f"   ⏳ Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    if attempt == retries - 1:
                        return {"error": response.status_code, "message": response.text[:200]}
                    return None
                    
            except Exception as e:
                if attempt == retries - 1:
                    return {"error": str(e)}
                return None
        
        return None
    
    def test_connection(self) -> bool:
        """Test HubSpot API connection."""
        response = self._request("GET", "/crm/v3/objects/companies?limit=1")
        return response is not None and "error" not in response
    
    def get_all_company_ids(self) -> List[dict]:
        """Get all company IDs and names."""
        companies = []
        after = None
        
        print("   Fetching all companies...")
        
        while True:
            endpoint = "/crm/v3/objects/companies?limit=100&properties=name,domain"
            if after:
                endpoint += f"&after={after}"
            
            response = self._request("GET", endpoint)
            if not response or "error" in response:
                break
            
            for company in response.get("results", []):
                companies.append({
                    "id": company.get("id"),
                    "name": company.get("properties", {}).get("name", "Unknown"),
                    "domain": company.get("properties", {}).get("domain", ""),
                })
            
            paging = response.get("paging", {})
            after = paging.get("next", {}).get("after")
            
            if not after:
                break
            
            # Progress indicator
            if len(companies) % 500 == 0:
                print(f"   ... found {len(companies)} companies so far")
        
        return companies
    
    def delete_company(self, company_id: str) -> bool:
        """Delete a single company."""
        response = self._request("DELETE", f"/crm/v3/objects/companies/{company_id}")
        return response is not None and response.get("success", False)
    
    def delete_companies_batch(self, company_ids: List[str]) -> dict:
        """Delete companies in batch (up to 100 at a time)."""
        # HubSpot batch delete endpoint
        response = self._request(
            "POST",
            "/crm/v3/objects/companies/batch/archive",
            {"inputs": [{"id": cid} for cid in company_ids]}
        )
        return response


def main():
    parser = argparse.ArgumentParser(description="Delete all companies from HubSpot")
    parser.add_argument("--count", action="store_true", help="Just count companies")
    parser.add_argument("--preview", action="store_true", help="Preview companies to delete")
    parser.add_argument("--delete", action="store_true", help="Actually delete companies")
    args = parser.parse_args()
    
    if not any([args.count, args.preview, args.delete]):
        print("⚠️  Please specify an action: --count, --preview, or --delete")
        print("   Run with --help for more information")
        return
    
    print("=" * 70)
    print("🗑️  HUBSPOT COMPANY DELETION TOOL")
    print("=" * 70)
    
    deleter = HubSpotDeleter()
    
    if not deleter.enabled:
        return
    
    print(f"   API Key: {deleter.api_key[:20]}...")
    
    # Test connection
    print("\n🔗 Testing HubSpot connection...")
    if not deleter.test_connection():
        print("❌ HubSpot connection failed")
        return
    print("✅ HubSpot connection successful!")
    
    # Get all companies
    print("\n📊 Fetching companies...")
    companies = deleter.get_all_company_ids()
    print(f"\n   Found {len(companies)} companies in HubSpot")
    
    if args.count:
        print("\n✅ Count complete. Use --preview to see company names or --delete to remove them.")
        return
    
    if args.preview:
        print("\n📋 Companies that would be deleted:")
        for i, company in enumerate(companies[:50]):
            print(f"   {i+1}. {company['name']} ({company['domain'] or 'no domain'})")
        if len(companies) > 50:
            print(f"   ... and {len(companies) - 50} more")
        print("\n⚠️  Use --delete to actually remove these companies")
        return
    
    if args.delete:
        if len(companies) == 0:
            print("\n✅ No companies to delete. HubSpot is already empty!")
            return
        
        print("\n" + "=" * 70)
        print("⚠️  WARNING: YOU ARE ABOUT TO DELETE ALL COMPANIES!")
        print("=" * 70)
        print(f"\n   This will permanently delete {len(companies)} companies.")
        print("   This action CANNOT be undone!")
        print("\n   Type 'DELETE ALL' to confirm: ", end="")
        
        confirmation = input().strip()
        
        if confirmation != "DELETE ALL":
            print("\n❌ Deletion cancelled. You typed: '{}'".format(confirmation))
            return
        
        print("\n🗑️  Deleting companies...")
        
        deleted = 0
        failed = 0
        
        # Delete in batches of 100
        batch_size = 100
        for i in range(0, len(companies), batch_size):
            batch = companies[i:i+batch_size]
            batch_ids = [c["id"] for c in batch]
            
            response = deleter.delete_companies_batch(batch_ids)
            
            if response and "error" not in response:
                deleted += len(batch)
                print(f"   ✅ Deleted batch {i//batch_size + 1}: {len(batch)} companies ({deleted}/{len(companies)} total)")
            else:
                # Try individual deletion as fallback
                for company in batch:
                    if deleter.delete_company(company["id"]):
                        deleted += 1
                    else:
                        failed += 1
                        print(f"   ❌ Failed to delete: {company['name']}")
            
            # Rate limiting
            time.sleep(0.5)
        
        print("\n" + "=" * 70)
        print("📊 DELETION COMPLETE")
        print("=" * 70)
        print(f"   ✅ Deleted: {deleted}")
        print(f"   ❌ Failed: {failed}")
        print("\n   Your HubSpot is now clean and ready for fresh data!")


if __name__ == "__main__":
    main()

