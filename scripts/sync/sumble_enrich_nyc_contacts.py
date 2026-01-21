#!/usr/bin/env python3
"""
Sumble Enrichment for NYC Contacts

Uses Sumble API to:
1. Find decision-makers at companies without contacts
2. Enrich existing contacts with missing email/title

Usage:
    python scripts/sync/sumble_enrich_nyc_contacts.py
    python scripts/sync/sumble_enrich_nyc_contacts.py --dry-run
    python scripts/sync/sumble_enrich_nyc_contacts.py --limit 10
"""

import os
import csv
import json
import requests
import time
import argparse
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials/sumble_api_key.txt")
ENRICHMENT_QUEUE = os.path.join(BASE_DIR, "data/exports/sumble_enrichment_queue.csv")
CONTACTS_FILE = os.path.join(BASE_DIR, "data/exports/nyc_dinner_contacts.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "data/exports/nyc_dinner_contacts_enriched.csv")

SUMBLE_BASE_URL = "https://api.sumble.com/v3"
RATE_LIMIT_DELAY = 0.15  # 10 requests per second

# ICP titles to search for (prioritized)
ICP_TITLES = [
    "CTO", "Chief Technology Officer",
    "VP Engineering", "VP of Engineering", "Vice President Engineering",
    "Head of AI", "Head of ML", "Head of Data",
    "Chief AI Officer", "Chief Data Officer",
    "Director of Engineering", "Director of AI",
    "Principal Engineer", "Staff Engineer",
    "AI Lead", "ML Lead", "Engineering Manager"
]

# Job functions to filter
ICP_JOB_FUNCTIONS = ["Engineering", "Technology", "IT", "Data Science", "Research"]


class SumbleEnricher:
    """Enrich NYC contacts using Sumble API."""
    
    def __init__(self, api_key: str = None, dry_run: bool = False):
        self.api_key = api_key or self._load_api_key()
        self.dry_run = dry_run
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.last_request_time = 0
        self.credits_used = 0
        self.credits_remaining = None
    
    def _load_api_key(self) -> str:
        """Load API key from credentials file."""
        if os.path.exists(CREDENTIALS_PATH):
            with open(CREDENTIALS_PATH, 'r') as f:
                return f.read().strip()
        return os.getenv("SUMBLE_API_KEY", "")
    
    def _rate_limit(self):
        """Enforce rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()
    
    def find_people(self, domain: str) -> Optional[Dict]:
        """Find decision-makers at a company by domain."""
        if self.dry_run:
            print(f"   [DRY RUN] Would search for people at {domain}")
            return None
        
        self._rate_limit()
        
        try:
            response = requests.post(
                f"{SUMBLE_BASE_URL}/people/find",
                headers=self.headers,
                json={
                    "organization": {"domain": domain},
                    "filters": {}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.credits_used += data.get("credits_used", 0)
                self.credits_remaining = data.get("credits_remaining")
                return data
            elif response.status_code == 429:
                print(f"   ⚠️ Rate limited, waiting 5 seconds...")
                time.sleep(5)
                return self.find_people(domain)
            else:
                print(f"   ❌ Error {response.status_code}: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return None
    
    def filter_icp_contacts(self, people: List[Dict]) -> List[Dict]:
        """Filter people to ICP-relevant contacts."""
        icp_contacts = []
        
        for person in people:
            title = (person.get('job_title') or '').lower()
            job_function = person.get('job_function', '')
            
            # Check if title matches ICP
            is_icp = False
            
            # Check job function
            if job_function in ICP_JOB_FUNCTIONS:
                is_icp = True
            
            # Check title keywords
            title_keywords = ['cto', 'chief', 'vp', 'vice president', 'head of', 
                            'director', 'principal', 'staff', 'lead', 'manager',
                            'engineer', 'architect', 'scientist']
            if any(kw in title for kw in title_keywords):
                is_icp = True
            
            if is_icp:
                icp_contacts.append({
                    'name': person.get('name', ''),
                    'title': person.get('job_title', ''),
                    'email': person.get('email', ''),
                    'linkedin': person.get('linkedin_url', ''),
                    'job_function': job_function,
                })
        
        # Sort by title seniority
        def title_score(contact):
            title = contact.get('title', '').lower()
            if any(t in title for t in ['cto', 'chief']):
                return 0
            if any(t in title for t in ['vp', 'vice president']):
                return 1
            if any(t in title for t in ['head of', 'director']):
                return 2
            if any(t in title for t in ['principal', 'staff']):
                return 3
            return 4
        
        icp_contacts.sort(key=title_score)
        return icp_contacts[:5]  # Return top 5 contacts per company
    
    def enrich_companies_without_contacts(self, queue: List[Dict]) -> List[Dict]:
        """Find contacts for companies without any."""
        enriched = []
        
        # Filter to companies without contacts (have domain, no name)
        companies_to_enrich = [
            q for q in queue 
            if q.get('reason') == 'No contacts found' 
            and q.get('domain') 
            and q.get('domain') != 'NEEDS_DOMAIN'
        ]
        
        print(f"\n🔍 Enriching {len(companies_to_enrich)} companies without contacts...")
        
        for i, company in enumerate(companies_to_enrich):
            domain = company.get('domain')
            company_name = company.get('company')
            
            print(f"\n[{i+1}/{len(companies_to_enrich)}] {company_name} ({domain})")
            
            result = self.find_people(domain)
            
            if result and result.get('people'):
                people = result.get('people', [])
                print(f"   Found {len(people)} people total")
                
                # Filter to ICP
                icp_contacts = self.filter_icp_contacts(people)
                print(f"   Filtered to {len(icp_contacts)} ICP contacts")
                
                for contact in icp_contacts:
                    enriched.append({
                        'name': contact.get('name', ''),
                        'company': company_name,
                        'domain': domain,
                        'title': contact.get('title', ''),
                        'email': contact.get('email', ''),
                        'linkedin': contact.get('linkedin', ''),
                        'source': 'Sumble',
                        'category': company.get('category', ''),
                        'tier': company.get('tier', ''),
                        'priority': company.get('priority', ''),
                        'icp_score': self._calculate_icp_score(contact, company),
                    })
                    print(f"   ✅ {contact.get('name')}: {contact.get('title')}")
            else:
                print(f"   ⚠️ No people found")
            
            # Check credits
            if self.credits_remaining is not None and self.credits_remaining < 10:
                print(f"\n⚠️ Low credits ({self.credits_remaining}), stopping...")
                break
        
        return enriched
    
    def _calculate_icp_score(self, contact: Dict, company: Dict) -> int:
        """Calculate ICP score for enriched contact."""
        score = 5
        title = (contact.get('title') or '').lower()
        priority = (company.get('priority') or '').upper()
        
        if any(t in title for t in ['cto', 'chief']):
            score += 3
        elif any(t in title for t in ['vp', 'vice president', 'head of']):
            score += 2
        elif any(t in title for t in ['director', 'principal', 'staff']):
            score += 1
        
        if priority == 'CRITICAL':
            score += 2
        elif priority == 'HIGH':
            score += 1
        
        return min(10, score)


def load_enrichment_queue() -> List[Dict]:
    """Load the enrichment queue CSV."""
    queue = []
    with open(ENRICHMENT_QUEUE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            queue.append(row)
    return queue


def load_existing_contacts() -> List[Dict]:
    """Load existing contacts."""
    contacts = []
    with open(CONTACTS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacts.append(row)
    return contacts


def save_enriched_contacts(contacts: List[Dict]):
    """Save enriched contacts to CSV."""
    fields = [
        'name', 'company', 'domain', 'title', 'email', 'linkedin',
        'source', 'category', 'tier', 'priority', 'icp_score', 'talk_title'
    ]
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(contacts)


def main():
    parser = argparse.ArgumentParser(description="Enrich NYC contacts using Sumble API")
    parser.add_argument('--dry-run', action='store_true', help="Preview without API calls")
    parser.add_argument('--limit', type=int, default=None, help="Limit number of companies to enrich")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔍 SUMBLE ENRICHMENT FOR NYC CONTACTS")
    print("=" * 60)
    
    # Load data
    print("\n📂 Loading enrichment queue...")
    queue = load_enrichment_queue()
    print(f"   {len(queue)} items in queue")
    
    print("\n📂 Loading existing contacts...")
    existing_contacts = load_existing_contacts()
    print(f"   {len(existing_contacts)} existing contacts")
    
    # Apply limit if specified
    if args.limit:
        queue = queue[:args.limit]
        print(f"\n⚠️ Limited to {args.limit} items")
    
    # Initialize enricher
    enricher = SumbleEnricher(dry_run=args.dry_run)
    
    if not enricher.api_key:
        print("\n❌ No Sumble API key found!")
        print("   Set SUMBLE_API_KEY in .env or credentials/sumble_api_key.txt")
        return
    
    # Enrich companies without contacts
    new_contacts = enricher.enrich_companies_without_contacts(queue)
    
    # Combine with existing
    all_contacts = existing_contacts + new_contacts
    
    # Deduplicate by email
    seen_emails = set()
    unique_contacts = []
    for contact in all_contacts:
        email = (contact.get('email') or '').lower()
        if email and email in seen_emails:
            continue
        if email:
            seen_emails.add(email)
        unique_contacts.append(contact)
    
    # Save
    print(f"\n💾 Saving {len(unique_contacts)} contacts to {OUTPUT_FILE}...")
    save_enriched_contacts(unique_contacts)
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 ENRICHMENT SUMMARY")
    print("=" * 60)
    print(f"New contacts found: {len(new_contacts)}")
    print(f"Total contacts: {len(unique_contacts)}")
    print(f"Credits used: {enricher.credits_used}")
    if enricher.credits_remaining is not None:
        print(f"Credits remaining: {enricher.credits_remaining}")
    
    print(f"\n✅ Enriched contacts saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

