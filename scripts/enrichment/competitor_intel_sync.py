#!/usr/bin/env python3
"""
Competitor Intelligence Sync

Syncs competitor customer data from Chroma to:
1. Attio CRM (Competitor Accounts collection)
2. Slack (#competitor-intel channel)

Run manually or as a cron job to track new competitor customers.

Setup:
1. Set ATTIO_API_KEY in .env
2. Set SLACK_WEBHOOK_URL in .env (for #competitor-intel)
3. Run: python competitor_intel_sync.py

Cron example (run every 6 hours):
0 */6 * * * cd "/Users/ankitpansari/Desktop/Chroma GTM" && /usr/bin/python3 competitor_intel_sync.py >> /tmp/competitor_intel.log 2>&1
"""

import os
import json
import requests
import time
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

# Attio Configuration
ATTIO_API_KEY = os.getenv("ATTIO_API_KEY")
ATTIO_BASE_URL = "https://api.attio.com/v2"
ATTIO_WORKSPACE_SLUG = "chromadb"  # Your Attio workspace slug

# Competitor Accounts collection
ATTIO_COLLECTION_ID = "ddab7523-f25a-4639-8596-a7d27d33432a"

# Slack Configuration - Use #gtm-signal channel
SLACK_WEBHOOK_URL = os.getenv("SLACK_GTM_SIGNAL_WEBHOOK") or os.getenv("SLACK_COMPETITOR_INTEL_WEBHOOK") or os.getenv("SLACK_WEBHOOK_URL")
SLACK_CHANNEL = "#gtm-signal"

# Chroma Configuration
CHROMA_API_KEY = "ck-2i6neFLSKhd5pEqLP3jZKUkG6tX3yo4RVUZEeRxs4fHm"
CHROMA_TENANT = "aa8f571e-03dc-4cd8-b888-723bd00b83f0"
CHROMA_DATABASE = "customer"
CHROMA_COLLECTION = "customers"

# Current Vendor mapping (vector_db_used -> Attio option ID)
VENDOR_OPTION_MAP = {
    "weaviate": "bbc41186-1ab9-4fb1-b4ea-0d0158482c08",
    "qdrant": "d6b48635-9d33-4e66-ba31-404cbbec7558",
    "mongodb atlas": "43c4b4a8-c009-4c3c-ae7d-7905de2a321f",
    "mongodb atlas vector search": "43c4b4a8-c009-4c3c-ae7d-7905de2a321f",
    "mongodb": "43c4b4a8-c009-4c3c-ae7d-7905de2a321f",
    "milvus/zilliz": "2c2f7a32-953c-453b-880e-e3561b1bd8fa",
    "milvus": "2c2f7a32-953c-453b-880e-e3561b1bd8fa",
    "zilliz": "2c2f7a32-953c-453b-880e-e3561b1bd8fa",
    "zilliz cloud": "2c2f7a32-953c-453b-880e-e3561b1bd8fa",
    "pinecone": "ca333bfd-ccf5-4d62-947a-029395ba4380",
    "langchain/langgraph": "b452dee0-537c-46aa-90e6-115e3dc8ee06",
    "langchain": "6aa3ee6c-4ed1-41dd-95c9-11872f35ba38",
    "langgraph": "b452dee0-537c-46aa-90e6-115e3dc8ee06",
    "turbopuffer": "fb01bf07-93b5-47b1-92d3-bce4467c8322",
    "llamaindex": "b89aef07-81e6-4ce4-8194-40adda71beb6",
    "llamaindex/llamacloud": "b89aef07-81e6-4ce4-8194-40adda71beb6",
    "llamacloud": "b89aef07-81e6-4ce4-8194-40adda71beb6",
    "aws opensearch": "661b5a99-9a19-4b08-8bc2-e927828f47e9",
    "opensearch": "661b5a99-9a19-4b08-8bc2-e927828f47e9",
    "amazon opensearch serverless": "661b5a99-9a19-4b08-8bc2-e927828f47e9",
    "aws bedrock": "2372fa17-742c-4266-adf5-e3b2562bf295",
    "bedrock": "2372fa17-742c-4266-adf5-e3b2562bf295",
    "haystack (deepset)": "d479fe4f-6a11-4b7f-abfb-6b64dda60717",
    "haystack": "d479fe4f-6a11-4b7f-abfb-6b64dda60717",
    "deepset": "d479fe4f-6a11-4b7f-abfb-6b64dda60717",
    "lancedb": "167beb53-cd67-48b1-81ea-0e7beacd6f39",
    "marqo": "817f205f-5635-41d5-a038-f29bb0a53b11",
    "cohere": "3bcb5ff9-442c-489a-b5cf-c83df3162323",
}

# Industry mapping
INDUSTRY_OPTIONS = {
    "ai/ml": "AI/ML",
    "ai / ml": "AI/ML",
    "artificial intelligence": "AI/ML",
    "machine learning": "AI/ML",
    "fintech": "FinTech",
    "financial services": "FinTech",
    "finance": "FinTech",
    "healthcare": "Healthcare",
    "health": "Healthcare",
    "medical": "Healthcare",
    "saas": "SaaS",
    "software": "SaaS",
    "enterprise": "Enterprise",
    "e-commerce": "E-commerce",
    "ecommerce": "E-commerce",
    "retail": "E-commerce",
    "media": "Media/Entertainment",
    "entertainment": "Media/Entertainment",
    "publishing": "Media/Entertainment",
}

# Lead source option ID for this sync
LEAD_SOURCE_OPTION_ID = "76342f6b-4dbf-4fde-a132-38d2d4f9e10c"  # YouTube Research


# =============================================================================
# LOGGING
# =============================================================================

def log(message: str, level: str = "INFO"):
    """Log with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


# =============================================================================
# ATTIO API
# =============================================================================

class AttioAPI:
    """Attio CRM API client."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or ATTIO_API_KEY
        self.enabled = bool(self.api_key)
        if self.enabled:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        else:
            log("ATTIO_API_KEY not set - Attio sync disabled", "WARNING")
    
    def _request(self, method: str, endpoint: str, json_data: dict = None) -> Optional[dict]:
        """Make API request to Attio."""
        if not self.enabled:
            return None
            
        url = f"{ATTIO_BASE_URL}{endpoint}"
        
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
            else:
                log(f"Attio API error: {response.status_code} - {response.text[:200]}", "ERROR")
                return None
                
        except Exception as e:
            log(f"Attio request failed: {e}", "ERROR")
            return None
    
    def find_company(self, company_name: str) -> Optional[dict]:
        """Search for existing company in Attio."""
        response = self._request(
            "POST",
            "/objects/companies/records/query",
            {"filter": {"name": {"$contains": company_name}}}
        )
        if response and response.get("data"):
            return response["data"][0]
        return None
    
    def create_company(self, company_name: str, description: str = "") -> Optional[str]:
        """Create company record, return record_id.
        
        NOTE: We intentionally do NOT set the domain here because we don't have
        the actual company website - only the source URL (which is the vector DB's site).
        The domain should be enriched later or manually added.
        """
        values = {"name": [{"value": company_name}]}
        
        if description:
            values["description"] = [{"value": description[:1000]}]
        
        # Do NOT set domain - we don't have the company's actual website
        # The source_url is the vector DB's website, not the customer's website
        
        response = self._request(
            "POST",
            "/objects/companies/records",
            {"data": {"values": values}}
        )
        
        if response:
            return response.get("data", {}).get("id", {}).get("record_id")
        return None
    
    def get_collection_entries(self) -> List[str]:
        """Get all company names currently in the collection."""
        companies = []
        
        response = self._request(
            "POST",
            f"/lists/{ATTIO_COLLECTION_ID}/entries/query",
            {"limit": 500}
        )
        
        if response and response.get("data"):
            for entry in response["data"]:
                parent = entry.get("parent_record", {})
                values = parent.get("values", {})
                name_list = values.get("name", [])
                if name_list:
                    companies.append(name_list[0].get("value", "").lower())
        
        return companies
    
    def add_to_collection(self, record_id: str, lead: dict) -> bool:
        """Add company to Competitor Accounts collection with metadata."""
        entry_values = {}
        
        # Current Vendor (select field)
        vector_db = lead.get("vector_db_used", "").lower()
        vendor_option_id = VENDOR_OPTION_MAP.get(vector_db)
        if vendor_option_id:
            entry_values["current_vendor"] = vendor_option_id
        
        # Lead Source
        entry_values["lead_source"] = LEAD_SOURCE_OPTION_ID
        
        # Industry (select field)
        industry = lead.get("industry", "").lower()
        for key, value in INDUSTRY_OPTIONS.items():
            if key in industry:
                entry_values["industry"] = value
                break
        
        # Notes
        notes_parts = []
        if lead.get("use_case"):
            notes_parts.append(f"Use case: {lead['use_case']}")
        if lead.get("source"):
            notes_parts.append(f"Source: {lead['source']}")
        if lead.get("source_url"):
            notes_parts.append(f"URL: {lead['source_url']}")
        if lead.get("company_size"):
            notes_parts.append(f"Size: {lead['company_size']}")
        if lead.get("category"):
            notes_parts.append(f"Category: {lead['category']}")
        
        if notes_parts:
            entry_values["notes"] = [{"value": "\n".join(notes_parts)}]
        
        response = self._request(
            "POST",
            f"/lists/{ATTIO_COLLECTION_ID}/entries",
            {
                "data": {
                    "parent_object": "companies",
                    "parent_record_id": record_id,
                    "entry_values": entry_values
                }
            }
        )
        
        return response is not None
    
    def sync_lead(self, lead: dict, existing_companies: List[str]) -> Tuple[bool, str]:
        """Sync single lead to Attio. Returns (success, status)."""
        company_name = lead.get("company_name", "")
        if not company_name:
            return False, "no_name"
        
        # Check if already in collection
        if company_name.lower() in existing_companies:
            return True, "exists"
        
        # Find or create company
        company = self.find_company(company_name)
        if company:
            record_id = company.get("id", {}).get("record_id")
        else:
            # Create company WITHOUT domain (we don't have the actual company website)
            record_id = self.create_company(
                company_name,
                lead.get("use_case", "")
            )
        
        if not record_id:
            return False, "failed_create"
        
        # Add to collection
        if self.add_to_collection(record_id, lead):
            return True, "added"
        else:
            return False, "failed_add"


# =============================================================================
# SLACK NOTIFICATIONS
# =============================================================================

def send_single_company_notification(company: dict, attio_record_id: str = None):
    """Send individual Slack notification for a single new competitor customer."""
    if not SLACK_WEBHOOK_URL:
        return False
    
    company_name = company.get("company_name", "Unknown")
    vendor = company.get("vector_db_used", "Unknown")
    industry = company.get("industry", "N/A")
    use_case = company.get("use_case", "N/A")
    company_size = company.get("company_size", "N/A")
    source_url = company.get("source_url", "")
    category = company.get("category", "competitor_customer")
    
    # Emoji based on vendor
    vendor_emoji = {
        "pinecone": "🌲",
        "weaviate": "🔷",
        "qdrant": "🔶",
        "milvus": "🐬",
        "zilliz": "🐬",
        "mongodb": "🍃",
        "langchain": "🦜",
        "llamaindex": "🦙",
        "turbopuffer": "🐡",
        "cohere": "🧠",
        "haystack": "🔍",
        "aws": "☁️",
        "bedrock": "☁️",
        "opensearch": "🔎",
    }.get(vendor.lower().split("/")[0].split(" ")[0], "🎯")
    
    # Build Attio URL - link directly to the company record if we have the ID
    if attio_record_id:
        attio_url = f"https://app.attio.com/{ATTIO_WORKSPACE_SLUG}/companies/{attio_record_id}"
    else:
        attio_url = f"https://app.attio.com/{ATTIO_WORKSPACE_SLUG}"
    
    # Build message blocks
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{vendor_emoji} New Competitor Customer: {company_name}",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Company:*\n{company_name}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Current Vendor:*\n{vendor}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Industry:*\n{industry}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Company Size:*\n{company_size}"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Use Case:*\n{use_case[:500] if use_case else 'N/A'}"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"📍 Source: {source_url if source_url else 'Competitor research'} | Category: {category}"
                }
            ]
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "💡 *Action:* This company is using a competitor's vector DB. Potential Chroma customer!"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "View in Attio",
                    "emoji": True
                },
                "url": attio_url,
                "action_id": "view_attio"
            }
        }
    ]
    
    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json={"blocks": blocks},
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        log(f"Slack notification error for {company_name}: {e}", "ERROR")
        return False


def send_slack_notification(new_companies: List[dict], attio: 'AttioAPI' = None):
    """Send individual Slack notifications for each new competitor customer."""
    if not SLACK_WEBHOOK_URL:
        log("SLACK_WEBHOOK_URL not set - skipping notifications", "WARNING")
        return
    
    if not new_companies:
        return
    
    log(f"Sending {len(new_companies)} individual Slack notifications...")
    
    # Build a lookup of company names to Attio record IDs
    attio_records = {}
    if attio and attio.enabled:
        log("   Fetching Attio record IDs for direct links...")
        try:
            response = attio._request(
                "POST",
                f"/lists/{ATTIO_COLLECTION_ID}/entries/query",
                {"limit": 500}
            )
            if response and response.get("data"):
                for entry in response["data"]:
                    parent_record_id = entry.get("parent_record_id")
                    if parent_record_id:
                        # Get the company name for this record
                        company_resp = attio._request(
                            "GET",
                            f"/objects/companies/records/{parent_record_id}"
                        )
                        if company_resp:
                            name = company_resp.get("data", {}).get("values", {}).get("name", [{}])[0].get("value", "")
                            if name:
                                attio_records[name.lower()] = parent_record_id
        except Exception as e:
            log(f"   Warning: Could not fetch Attio records: {e}", "WARNING")
    
    success_count = 0
    for i, company in enumerate(new_companies, 1):
        company_name = company.get('company_name', '')
        
        # Look up the Attio record ID
        attio_record_id = attio_records.get(company_name.lower()) if attio_records else None
        
        if send_single_company_notification(company, attio_record_id):
            success_count += 1
            log(f"   [{i}/{len(new_companies)}] ✅ Notified: {company_name}")
        else:
            log(f"   [{i}/{len(new_companies)}] ❌ Failed: {company_name}")
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    log(f"Slack notifications complete: {success_count}/{len(new_companies)} sent")


# =============================================================================
# CHROMA DATA FETCH
# =============================================================================

def get_chroma_customers() -> List[dict]:
    """Fetch all customers from Chroma database."""
    import chromadb
    
    log("Connecting to Chroma Cloud...")
    client = chromadb.CloudClient(
        api_key=CHROMA_API_KEY,
        tenant=CHROMA_TENANT,
        database=CHROMA_DATABASE
    )
    
    collection = client.get_collection(CHROMA_COLLECTION)
    total_count = collection.count()
    log(f"Total records in Chroma: {total_count}")
    
    # Fetch in batches due to quota limits
    all_metadatas = []
    batch_size = 100
    offset = 0
    
    while offset < total_count:
        batch = collection.get(
            limit=batch_size,
            offset=offset,
            include=['metadatas']
        )
        all_metadatas.extend(batch['metadatas'])
        offset += batch_size
        if len(batch['ids']) < batch_size:
            break
    
    log(f"Retrieved {len(all_metadatas)} records from Chroma")
    return all_metadatas


# =============================================================================
# MAIN SYNC
# =============================================================================

def run_sync(dry_run: bool = False):
    """
    Main sync function.
    
    Args:
        dry_run: If True, don't actually sync, just show what would happen
    """
    log("=" * 60)
    log("COMPETITOR INTELLIGENCE SYNC")
    log("=" * 60)
    log(f"Attio Collection: {ATTIO_COLLECTION_ID}")
    log(f"Slack Channel: {SLACK_CHANNEL}")
    log(f"Dry Run: {dry_run}")
    
    # Initialize Attio
    attio = AttioAPI()
    if not attio.enabled:
        log("Attio not configured - exiting", "ERROR")
        return
    
    # Get existing companies in Attio collection
    log("\n📋 Fetching existing Attio collection entries...")
    existing_companies = attio.get_collection_entries()
    log(f"Found {len(existing_companies)} companies already in Attio")
    
    # Get all customers from Chroma
    log("\n📊 Fetching customers from Chroma...")
    chroma_customers = get_chroma_customers()
    
    # Filter to only competitor customers (not partners, etc.)
    competitor_categories = ['competitor_customer', 'ecosystem_customer', 'agent_framework_customer']
    filtered = [
        c for c in chroma_customers 
        if c.get('category') in competitor_categories
        and c.get('company_name')
    ]
    log(f"Filtered to {len(filtered)} competitor/ecosystem customers")
    
    # Sync each customer
    log("\n🔄 Syncing to Attio...")
    results = {
        "added": [],
        "exists": 0,
        "failed": 0
    }
    
    for i, lead in enumerate(filtered, 1):
        company_name = lead.get("company_name", "")
        
        if dry_run:
            if company_name.lower() in existing_companies:
                results["exists"] += 1
            else:
                results["added"].append(lead)
                log(f"[DRY RUN] Would add: {company_name} ({lead.get('vector_db_used')})")
        else:
            success, status = attio.sync_lead(lead, existing_companies)
            
            if status == "added":
                results["added"].append(lead)
                log(f"[{i}/{len(filtered)}] ✅ Added: {company_name}")
                # Add to existing list to prevent duplicates in same run
                existing_companies.append(company_name.lower())
            elif status == "exists":
                results["exists"] += 1
            else:
                results["failed"] += 1
                log(f"[{i}/{len(filtered)}] ❌ Failed: {company_name} ({status})")
            
            # Rate limiting
            time.sleep(0.3)
    
    # Summary
    log("\n" + "=" * 60)
    log("SYNC COMPLETE")
    log("=" * 60)
    log(f"✅ Added: {len(results['added'])}")
    log(f"⏭️  Already existed: {results['exists']}")
    log(f"❌ Failed: {results['failed']}")
    
    # Send Slack notification for new companies
    if results["added"] and not dry_run:
        log("\n📤 Sending Slack notifications...")
        send_slack_notification(results["added"], attio)
    
    # Show new companies by vendor
    if results["added"]:
        log("\n📊 New Companies by Vendor:")
        by_vendor = {}
        for c in results["added"]:
            vendor = c.get("vector_db_used", "Unknown")
            if vendor not in by_vendor:
                by_vendor[vendor] = []
            by_vendor[vendor].append(c["company_name"])
        
        for vendor, companies in sorted(by_vendor.items(), key=lambda x: -len(x[1])):
            log(f"\n  {vendor} ({len(companies)}):")
            for name in companies[:5]:
                log(f"    • {name}")
            if len(companies) > 5:
                log(f"    ... and {len(companies) - 5} more")
    
    return results


# =============================================================================
# CLI
# =============================================================================

def notify_all_existing():
    """Send Slack notifications for ALL companies currently in Chroma."""
    log("=" * 60)
    log("SENDING SLACK NOTIFICATIONS FOR ALL COMPANIES")
    log("=" * 60)
    
    if not SLACK_WEBHOOK_URL:
        log("❌ SLACK_COMPETITOR_INTEL_WEBHOOK not set in .env", "ERROR")
        log("Please add your webhook URL for #competitor-intel channel")
        return
    
    # Initialize Attio for record lookups
    attio = AttioAPI()
    
    # Get all customers from Chroma
    chroma_customers = get_chroma_customers()
    
    # Filter to competitor customers
    competitor_categories = ['competitor_customer', 'ecosystem_customer', 'agent_framework_customer']
    filtered = [
        c for c in chroma_customers 
        if c.get('category') in competitor_categories
        and c.get('company_name')
    ]
    
    log(f"Found {len(filtered)} competitor customers to notify")
    
    # Confirm before sending
    confirm = input(f"\n⚠️  This will send {len(filtered)} individual Slack messages. Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        log("Cancelled by user")
        return
    
    # Send notifications with Attio record lookups
    send_slack_notification(filtered, attio)
    
    log("\n✅ All notifications sent!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync competitor customers to Attio and Slack")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without syncing")
    parser.add_argument("--test", action="store_true", help="Test Attio connection only")
    parser.add_argument("--notify-all", action="store_true", help="Send Slack notifications for ALL existing companies")
    parser.add_argument("--test-slack", action="store_true", help="Send a test Slack notification")
    
    args = parser.parse_args()
    
    if args.test:
        log("Testing Attio connection...")
        attio = AttioAPI()
        if attio.enabled:
            entries = attio.get_collection_entries()
            log(f"✅ Connection successful! Found {len(entries)} existing entries")
        else:
            log("❌ Attio not configured", "ERROR")
    elif args.test_slack:
        log("Testing Slack notification...")
        if not SLACK_WEBHOOK_URL:
            log("❌ SLACK_COMPETITOR_INTEL_WEBHOOK not set in .env", "ERROR")
        else:
            test_company = {
                "company_name": "Test Company",
                "vector_db_used": "Pinecone",
                "industry": "AI/ML",
                "use_case": "This is a test notification to verify Slack integration works.",
                "company_size": "Startup",
                "source_url": "https://example.com",
                "category": "competitor_customer"
            }
            if send_single_company_notification(test_company):
                log("✅ Test Slack notification sent successfully!")
            else:
                log("❌ Test Slack notification failed", "ERROR")
    elif args.notify_all:
        notify_all_existing()
    else:
        run_sync(dry_run=args.dry_run)

