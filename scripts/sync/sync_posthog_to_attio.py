#!/usr/bin/env python3
"""
Sync PostHog Persons to Attio

Exports all persons from PostHog and syncs them to Attio CRM.
This handles historical/batch sync that the real-time destination doesn't cover.

Usage:
    python scripts/sync/sync_posthog_to_attio.py
    python scripts/sync/sync_posthog_to_attio.py --dry-run
    python scripts/sync/sync_posthog_to_attio.py --limit 100
    python scripts/sync/sync_posthog_to_attio.py --from-csv posthog_export.csv
"""

import os
import csv
import json
import requests
import time
import argparse
from typing import Optional, Dict, List
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Configuration
POSTHOG_API_KEY = os.getenv("POSTHOG_PERSONAL_API_KEY") or os.getenv("POSTHOG_API_KEY")
POSTHOG_PROJECT_ID = os.getenv("POSTHOG_PROJECT_ID")
POSTHOG_HOST = os.getenv("POSTHOG_HOST", "https://app.posthog.com")

ATTIO_API_KEY = os.getenv("ATTIO_API_KEY")
ATTIO_BASE_URL = "https://api.attio.com/v2"

RATE_LIMIT_DELAY = 0.25  # seconds between requests


class PostHogToAttioSync:
    """Sync PostHog persons to Attio."""
    
    def __init__(self):
        self.posthog_headers = {
            "Authorization": f"Bearer {POSTHOG_API_KEY}",
            "Content-Type": "application/json"
        }
        self.attio_headers = {
            "Authorization": f"Bearer {ATTIO_API_KEY}",
            "Content-Type": "application/json"
        }
        self.last_request_time = 0
        self.stats = {
            "total_persons": 0,
            "synced": 0,
            "skipped_no_email": 0,
            "created": 0,
            "updated": 0,
            "failed": 0,
        }
    
    def _rate_limit(self):
        """Enforce rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()
    
    def test_connections(self) -> bool:
        """Test both PostHog and Attio connections."""
        print("🔗 Testing connections...")
        
        # Test PostHog
        if not POSTHOG_API_KEY:
            print("   ❌ POSTHOG_PERSONAL_API_KEY not set")
            return False
        
        if not POSTHOG_PROJECT_ID:
            print("   ❌ POSTHOG_PROJECT_ID not set")
            return False
            
        try:
            resp = requests.get(
                f"{POSTHOG_HOST}/api/projects/{POSTHOG_PROJECT_ID}/",
                headers=self.posthog_headers,
                timeout=10
            )
            if resp.status_code == 200:
                project_name = resp.json().get("name", "Unknown")
                print(f"   ✅ PostHog connected: {project_name}")
            else:
                print(f"   ❌ PostHog error: {resp.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ PostHog connection failed: {e}")
            return False
        
        # Test Attio
        if not ATTIO_API_KEY:
            print("   ❌ ATTIO_API_KEY not set")
            return False
        
        try:
            resp = requests.get(
                f"{ATTIO_BASE_URL}/objects/people",
                headers=self.attio_headers,
                timeout=10
            )
            if resp.status_code == 200:
                print("   ✅ Attio connected")
            else:
                print(f"   ❌ Attio error: {resp.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Attio connection failed: {e}")
            return False
        
        return True
    
    def fetch_posthog_persons(self, limit: int = None) -> List[Dict]:
        """Fetch all persons from PostHog."""
        print("\n📥 Fetching persons from PostHog...")
        
        persons = []
        url = f"{POSTHOG_HOST}/api/projects/{POSTHOG_PROJECT_ID}/persons/"
        params = {"limit": 100}  # PostHog pagination limit
        
        while url:
            self._rate_limit()
            try:
                resp = requests.get(url, headers=self.posthog_headers, params=params, timeout=30)
                if resp.status_code != 200:
                    print(f"   ⚠️ Error fetching persons: {resp.status_code}")
                    break
                
                data = resp.json()
                batch = data.get("results", [])
                persons.extend(batch)
                
                print(f"   Fetched {len(persons)} persons...", end="\r")
                
                # Check limit
                if limit and len(persons) >= limit:
                    persons = persons[:limit]
                    break
                
                # Next page
                url = data.get("next")
                params = {}  # URL already contains params
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                break
        
        print(f"   ✅ Fetched {len(persons)} persons total")
        return persons
    
    def load_from_csv(self, csv_path: str) -> List[Dict]:
        """Load persons from a CSV export."""
        print(f"\n📂 Loading persons from {csv_path}...")
        
        persons = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert CSV row to PostHog-like person format
                person = {
                    "properties": {
                        "email": row.get("email") or row.get("Email") or row.get("$email"),
                        "name": row.get("name") or row.get("Name") or row.get("$name"),
                        "$initial_browser": row.get("browser"),
                        "$initial_os": row.get("os"),
                    },
                    "created_at": row.get("created_at") or row.get("Created At"),
                }
                # Add any other columns as properties
                for key, value in row.items():
                    if key not in ["email", "Email", "$email", "name", "Name", "$name", "created_at", "Created At"]:
                        if value:
                            person["properties"][key] = value
                
                persons.append(person)
        
        print(f"   ✅ Loaded {len(persons)} persons")
        return persons
    
    def sync_person_to_attio(self, person: Dict, dry_run: bool = False) -> bool:
        """Sync a single person to Attio."""
        props = person.get("properties", {})
        
        # Get email - required for Attio matching
        email = props.get("email") or props.get("$email") or props.get("Email")
        if not email or "@" not in str(email):
            self.stats["skipped_no_email"] += 1
            return False
        
        # Get name
        name = props.get("name") or props.get("$name") or props.get("Name") or ""
        
        # Parse name into first/last
        name_parts = str(name).strip().split() if name else []
        first_name = name_parts[0] if name_parts else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        if dry_run:
            return True
        
        # Build Attio payload
        values = {
            "email_addresses": [{"email_address": email}]
        }
        
        # Add name if available
        if name:
            values["name"] = [{
                "first_name": first_name,
                "last_name": last_name,
                "full_name": name
            }]
        
        # Add other properties as description or custom fields
        extra_props = []
        for key, value in props.items():
            if key not in ["email", "$email", "Email", "name", "$name", "Name"] and value:
                # Skip internal PostHog properties
                if not str(key).startswith("$"):
                    extra_props.append(f"{key}: {value}")
        
        if extra_props:
            values["description"] = [{"value": f"PostHog sync: {datetime.now().strftime('%Y-%m-%d')}\n" + "\n".join(extra_props[:10])}]
        
        # Upsert to Attio using matching_attribute
        self._rate_limit()
        try:
            resp = requests.put(
                f"{ATTIO_BASE_URL}/objects/people/records?matching_attribute=email_addresses",
                headers=self.attio_headers,
                json={"data": {"values": values}},
                timeout=30
            )
            
            if resp.status_code in [200, 201]:
                # Check if created or updated
                if resp.status_code == 201:
                    self.stats["created"] += 1
                else:
                    self.stats["updated"] += 1
                self.stats["synced"] += 1
                return True
            else:
                self.stats["failed"] += 1
                if resp.status_code != 429:  # Don't spam rate limit errors
                    print(f"   ⚠️ Attio error for {email}: {resp.status_code} - {resp.text[:100]}")
                return False
                
        except Exception as e:
            self.stats["failed"] += 1
            print(f"   ❌ Error syncing {email}: {e}")
            return False
    
    def sync_all(self, persons: List[Dict], dry_run: bool = False):
        """Sync all persons to Attio."""
        self.stats["total_persons"] = len(persons)
        
        print(f"\n{'🧪 DRY RUN' if dry_run else '📤 Syncing'} {len(persons)} persons to Attio...\n")
        
        for i, person in enumerate(persons, 1):
            props = person.get("properties", {})
            email = props.get("email") or props.get("$email") or props.get("Email") or "no-email"
            name = props.get("name") or props.get("$name") or props.get("Name") or "Unknown"
            
            success = self.sync_person_to_attio(person, dry_run)
            
            if dry_run:
                if email and "@" in str(email):
                    print(f"   [{i:4d}/{len(persons)}] 🧪 {name[:25]:<25} ({email})")
            else:
                if success:
                    print(f"   [{i:4d}/{len(persons)}] ✅ {name[:25]:<25} ({email})")
                elif "no-email" not in email:
                    print(f"   [{i:4d}/{len(persons)}] ❌ {name[:25]:<25} ({email})")
            
            # Progress update every 50
            if i % 50 == 0 and not dry_run:
                print(f"\n   --- Progress: {i}/{len(persons)} ({self.stats['synced']} synced, {self.stats['skipped_no_email']} skipped) ---\n")
    
    def print_summary(self):
        """Print sync summary."""
        print("\n" + "=" * 60)
        print("📊 SYNC SUMMARY")
        print("=" * 60)
        print(f"   📥 Total persons:      {self.stats['total_persons']}")
        print(f"   ✅ Synced to Attio:    {self.stats['synced']}")
        print(f"   🆕 Created:            {self.stats['created']}")
        print(f"   🔄 Updated:            {self.stats['updated']}")
        print(f"   ⏭️  Skipped (no email): {self.stats['skipped_no_email']}")
        print(f"   ❌ Failed:             {self.stats['failed']}")


def main():
    parser = argparse.ArgumentParser(description="Sync PostHog persons to Attio")
    parser.add_argument("--dry-run", action="store_true", help="Preview without making changes")
    parser.add_argument("--limit", type=int, help="Limit number of persons to sync")
    parser.add_argument("--from-csv", type=str, help="Load persons from CSV instead of PostHog API")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("📊 POSTHOG → ATTIO HISTORICAL SYNC")
    print("=" * 60)
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    sync = PostHogToAttioSync()
    
    if not args.from_csv:
        if not sync.test_connections():
            print("\n❌ Connection test failed. Check your API keys.")
            return
        
        persons = sync.fetch_posthog_persons(limit=args.limit)
    else:
        # Still test Attio connection
        if not ATTIO_API_KEY:
            print("❌ ATTIO_API_KEY not set")
            return
        persons = sync.load_from_csv(args.from_csv)
        if args.limit:
            persons = persons[:args.limit]
    
    if not persons:
        print("\n⚠️ No persons to sync")
        return
    
    sync.sync_all(persons, dry_run=args.dry_run)
    
    if not args.dry_run:
        sync.print_summary()


if __name__ == "__main__":
    main()

