#!/usr/bin/env python3
"""
Sync AI Engineer Speakers to Attio

Creates an "AI Engineer Speakers" list in Attio and syncs all LinkedIn profiles.
Attio will auto-enrich profiles with names, titles, companies from LinkedIn URLs.

Usage:
    python scripts/sync/sync_ai_speakers_to_attio.py
    python scripts/sync/sync_ai_speakers_to_attio.py --test
    python scripts/sync/sync_ai_speakers_to_attio.py --dry-run
"""

import os
import csv
import requests
import time
import argparse
from typing import Optional, Dict, List
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Attio Configuration
ATTIO_API_KEY = os.getenv("ATTIO_API_KEY")
ATTIO_BASE_URL = "https://api.attio.com/v2"
ATTIO_WORKSPACE_SLUG = "chromadb"

# CSV file path
SPEAKERS_CSV_PATH = "data/linkedin/ai_engineer_speakers_linkedin.csv"


class AttioSpeakersSync:
    """Sync AI Engineer speakers to Attio CRM."""
    
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
        self.list_id = None
    
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
        
        response = self._request("POST", "/objects/people/records/query", {"limit": 1})
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
    
    def find_speakers_list(self) -> Optional[str]:
        """Find existing AI Engineer Speakers list."""
        lists = self.get_all_lists()
        for lst in lists:
            name = lst.get("name", "").lower()
            if "speaker" in name or "ai engineer" in name:
                list_id = lst.get("id", {})
                if isinstance(list_id, dict):
                    return list_id.get("list_id")
                return list_id
        return None
    
    def create_speakers_list(self) -> Optional[str]:
        """Create the AI Engineer Speakers list."""
        print("\n📋 Creating 'AI Engineer Speakers' list...")
        
        # Check if it already exists
        existing_id = self.find_speakers_list()
        if existing_id:
            print(f"   ✅ List already exists: {existing_id}")
            self.list_id = existing_id
            return existing_id
        
        # Create new list for People
        response = self._request(
            "POST",
            "/lists",
            {
                "data": {
                    "name": "AI Engineer Speakers",
                    "api_slug": "ai_engineer_speakers",
                    "parent_object": "people",  # This is a People list, not Companies
                    "workspace_access": "full-access",
                    "workspace_member_access": []
                }
            }
        )
        
        if response and "conflict" not in response:
            list_id = response.get("data", {}).get("id", {})
            if isinstance(list_id, dict):
                list_id = list_id.get("list_id")
            print(f"   ✅ Created list: {list_id}")
            self.list_id = list_id
            return list_id
        elif response and response.get("conflict"):
            print("   ⚠️ List may already exist, searching...")
            existing_id = self.find_speakers_list()
            if existing_id:
                print(f"   ✅ Found existing list: {existing_id}")
                self.list_id = existing_id
                return existing_id
        
        print("   ❌ Failed to create list")
        return None
    
    # ============================================================
    # DATA LOADING
    # ============================================================
    
    def load_speakers(self) -> List[dict]:
        """Load speakers from CSV."""
        speakers = []
        
        possible_paths = [
            SPEAKERS_CSV_PATH,
            os.path.join(os.path.dirname(__file__), "..", "..", SPEAKERS_CSV_PATH),
            f"/Users/ankitpansari/Desktop/Chroma GTM/{SPEAKERS_CSV_PATH}"
        ]
        
        csv_path = None
        for path in possible_paths:
            if os.path.exists(path):
                csv_path = path
                break
        
        if not csv_path:
            print(f"❌ Could not find CSV file")
            return []
        
        print(f"\n📂 Loading speakers from: {csv_path}")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                linkedin_url = row.get('linkedin_url', '').strip()
                if linkedin_url and linkedin_url.startswith('http'):
                    speakers.append({'linkedin_url': linkedin_url})
        
        print(f"   ✅ Loaded {len(speakers)} speakers")
        return speakers
    
    # ============================================================
    # PERSON OPERATIONS
    # ============================================================
    
    def normalize_linkedin_url(self, url: str) -> str:
        """Normalize LinkedIn URL for consistent matching."""
        url = url.strip().rstrip('/')
        # Ensure https
        if url.startswith('linkedin.com'):
            url = 'https://www.' + url
        elif url.startswith('www.linkedin.com'):
            url = 'https://' + url
        elif not url.startswith('https://'):
            url = url.replace('http://', 'https://')
        return url
    
    def find_person_by_linkedin(self, linkedin_url: str) -> Optional[dict]:
        """Search for existing person in Attio by LinkedIn URL."""
        # Skip search - just create new records
        # Attio doesn't have a reliable way to search by LinkedIn URL
        return None
    
    def create_person(self, linkedin_url: str) -> Optional[str]:
        """Create a new person record with LinkedIn URL.
        
        Attio will auto-enrich the profile with:
        - Full name
        - Current job title
        - Current company
        - Profile photo
        - Location
        """
        import re
        
        normalized_url = self.normalize_linkedin_url(linkedin_url)
        
        # Extract username from URL for initial name
        username = normalized_url.split('/in/')[-1].rstrip('/').replace('-', ' ').title()
        # Clean up any trailing numbers that are LinkedIn IDs
        username = re.sub(r'\s+[a-f0-9]{6,}$', '', username, flags=re.IGNORECASE)
        
        # Split into first/last name - Attio requires both
        name_parts = username.split() if username else ["Unknown"]
        first_name = name_parts[0] if name_parts else "Unknown"
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else "Speaker"
        
        values = {
            # Use 'linkedin' which is the standard Attio attribute for People
            "linkedin": [{"value": normalized_url}],
            "name": [{"first_name": first_name, "last_name": last_name, "full_name": f"{first_name} {last_name}"}],
        }
        
        response = self._request(
            "POST",
            "/objects/people/records",
            {"data": {"values": values}}
        )
        
        if response and "conflict" not in response:
            record_id = response.get("data", {}).get("id", {})
            if isinstance(record_id, dict):
                record_id = record_id.get("record_id")
            return record_id
        return None
    
    def add_to_list(self, record_id: str) -> bool:
        """Add a person to the AI Engineer Speakers list."""
        if not self.list_id:
            return False
        
        response = self._request(
            "POST",
            f"/lists/{self.list_id}/entries",
            {
                "data": {
                    "parent_object": "people",
                    "parent_record_id": record_id,
                    "entry_values": {}
                }
            }
        )
        
        return response is not None
    
    def get_list_entries(self) -> List[str]:
        """Get LinkedIn URLs already in the list."""
        if not self.list_id:
            return []
        
        existing = []
        response = self._request(
            "POST",
            f"/lists/{self.list_id}/entries/query",
            {"limit": 500}
        )
        
        if response and response.get("data"):
            for entry in response["data"]:
                parent = entry.get("parent_record", {})
                values = parent.get("values", {})
                linkedin_list = values.get("linkedin_url", [])
                if linkedin_list:
                    url = linkedin_list[0].get("value", "")
                    if url:
                        # Normalize for comparison
                        existing.append(url.lower().rstrip('/'))
        
        return existing
    
    # ============================================================
    # MAIN SYNC
    # ============================================================
    
    def sync_all(self, delay: float = 0.5, dry_run: bool = False) -> dict:
        """Sync all AI Engineer speakers to Attio."""
        if not self.enabled:
            return {"error": "Attio not configured"}
        
        # Create or find the list
        if not self.create_speakers_list():
            return {"error": "Failed to create/find speakers list"}
        
        # Load speakers
        speakers = self.load_speakers()
        if not speakers:
            return {"error": "No speakers loaded from CSV"}
        
        # Get existing entries
        print("\n   Fetching existing list entries...")
        existing_in_list = self.get_list_entries()
        print(f"   Found {len(existing_in_list)} people already in list")
        
        results = {
            "total": len(speakers),
            "added": 0,
            "existing": 0,
            "failed": 0,
            "speakers_added": [],
            "speakers_failed": [],
        }
        
        print(f"\n{'🧪 DRY RUN - No changes will be made' if dry_run else '📤 Syncing speakers...'}\n")
        
        for i, speaker in enumerate(speakers, 1):
            linkedin_url = speaker.get("linkedin_url", "")
            normalized = self.normalize_linkedin_url(linkedin_url).lower().rstrip('/')
            
            # Extract display name from URL
            display_name = linkedin_url.split('/in/')[-1].rstrip('/').replace('-', ' ').title()[:30]
            
            # Check if already in list
            if normalized in existing_in_list or any(normalized in e for e in existing_in_list):
                results["existing"] += 1
                print(f"   [{i:2d}/{len(speakers)}] ⏭️  {display_name} - already in list")
                time.sleep(delay / 3)
                continue
            
            if dry_run:
                results["added"] += 1
                results["speakers_added"].append(display_name)
                print(f"   [{i:2d}/{len(speakers)}] 🧪 {display_name} - would be added")
                continue
            
            # Find or create person
            existing = self.find_person_by_linkedin(linkedin_url)
            
            if existing:
                record_id = existing.get("id", {})
                if isinstance(record_id, dict):
                    record_id = record_id.get("record_id")
            else:
                record_id = self.create_person(linkedin_url)
            
            if not record_id:
                results["failed"] += 1
                results["speakers_failed"].append(display_name)
                print(f"   [{i:2d}/{len(speakers)}] ❌ {display_name} - failed to create")
                time.sleep(delay)
                continue
            
            # Add to list
            if self.add_to_list(record_id):
                results["added"] += 1
                results["speakers_added"].append(display_name)
                print(f"   [{i:2d}/{len(speakers)}] ✅ {display_name}")
            else:
                results["failed"] += 1
                results["speakers_failed"].append(display_name)
                print(f"   [{i:2d}/{len(speakers)}] ❌ {display_name} - failed to add to list")
            
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
        
        if results.get('speakers_added'):
            print(f"\n   🆕 New speakers added ({len(results['speakers_added'])}):")
            for speaker in results['speakers_added'][:15]:
                print(f"      • {speaker}")
            if len(results['speakers_added']) > 15:
                print(f"      ... and {len(results['speakers_added']) - 15} more")
        
        if results.get('speakers_failed'):
            print(f"\n   ❌ Failed speakers ({len(results['speakers_failed'])}):")
            for speaker in results['speakers_failed']:
                print(f"      • {speaker}")
        
        if self.list_id:
            print(f"\n🔗 View in Attio:")
            print(f"   https://app.attio.com/{ATTIO_WORKSPACE_SLUG}/collection/{self.list_id}")
        
        print("\n💡 Note: Attio will auto-enrich profiles with names, titles, and companies")
        print("   from LinkedIn URLs. Check back in a few minutes for enriched data.")


def main():
    parser = argparse.ArgumentParser(
        description="Sync AI Engineer Speakers to Attio"
    )
    parser.add_argument("--test", action="store_true", help="Test connection only")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be synced")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between API calls")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("🎤 AI ENGINEER SPEAKERS → ATTIO SYNC")
    print("=" * 70)
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    sync = AttioSpeakersSync()
    
    if args.test:
        sync.test_connection()
        return
    
    if not sync.test_connection():
        return
    
    results = sync.sync_all(delay=args.delay, dry_run=args.dry_run)
    sync.print_summary(results)


if __name__ == "__main__":
    main()
