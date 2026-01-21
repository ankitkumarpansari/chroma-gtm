#!/usr/bin/env python3
"""
LinkedIn Contact Scraper with Browser Automation
=================================================
Automatically finds and extracts contacts from LinkedIn using Playwright.
Works with LinkedIn Sales Navigator or regular LinkedIn.

Features:
- Automated search for target personas
- Extracts contact details
- Filters by relevance
- Exports to CSV for Attio import

Usage:
    python scripts/browser/linkedin_contact_scraper.py setup      # Install browser
    python scripts/browser/linkedin_contact_scraper.py search     # Run automated search
    python scripts/browser/linkedin_contact_scraper.py manual     # Manual browser with helper
"""

import os
import json
import csv
import time
import argparse
from datetime import datetime
from typing import Dict, List, Optional
from playwright.sync_api import sync_playwright, Page

class LinkedInContactScraper:
    """Automated LinkedIn contact discovery."""

    def __init__(self):
        self.target_companies = [
            {"name": "Vectara", "priority": 1, "employees": "50-200"},
            {"name": "Perplexity AI", "priority": 2, "employees": "50-200"},
            {"name": "Hebbia", "priority": 2, "employees": "50-200"},
            {"name": "Glean", "priority": 2, "employees": "200-500"},
            {"name": "AlphaSense", "priority": 2, "employees": "500-1000"},
            {"name": "Clay", "priority": 2, "employees": "50-200"},
            {"name": "Gong", "priority": 2, "employees": "1000-5000"}
        ]

        self.target_keywords = [
            "ML Engineer",
            "Machine Learning",
            "AI Engineer",
            "Staff Engineer AI",
            "Principal Engineer ML",
            "Head of AI",
            "Head of Machine Learning",
            "Director AI",
            "Director ML",
            "VP Engineering",
            "CTO",
            "Infrastructure Engineer",
            "Platform Engineer ML"
        ]

        self.contacts = []

    def setup_browser(self):
        """Install Playwright browsers."""
        os.system("playwright install chromium")
        print("✅ Browser setup complete")

    def create_search_url(self, company: str, keyword: str) -> str:
        """Generate LinkedIn search URL."""
        # Regular LinkedIn search (works without Sales Navigator)
        base_url = "https://www.linkedin.com/search/results/people/?"
        params = f'keywords={company}%20{keyword.replace(" ", "%20")}'
        return base_url + params

    def extract_contact_from_element(self, page: Page, element) -> Optional[Dict]:
        """Extract contact information from LinkedIn element."""
        try:
            contact = {}

            # Extract name
            name_elem = element.query_selector(".entity-result__title-text a span[aria-hidden='true']")
            if name_elem:
                contact['name'] = name_elem.inner_text().strip()

            # Extract title and company
            primary_subtitle = element.query_selector(".entity-result__primary-subtitle")
            if primary_subtitle:
                contact['title'] = primary_subtitle.inner_text().strip()

            # Extract location
            secondary_subtitle = element.query_selector(".entity-result__secondary-subtitle")
            if secondary_subtitle:
                contact['location'] = secondary_subtitle.inner_text().strip()

            # Extract profile URL
            link_elem = element.query_selector(".entity-result__title-text a")
            if link_elem:
                contact['linkedin_url'] = link_elem.get_attribute('href').split('?')[0]

            # Extract connection degree
            badge = element.query_selector(".entity-result__badge-text")
            if badge:
                contact['connection'] = badge.inner_text().strip()

            return contact if contact.get('name') else None

        except Exception as e:
            print(f"Error extracting contact: {e}")
            return None

    def is_relevant_contact(self, contact: Dict) -> bool:
        """Check if contact matches our target criteria."""
        if not contact.get('title'):
            return False

        title_lower = contact['title'].lower()

        # Check for relevant keywords
        relevant_keywords = [
            'ml', 'machine learning', 'ai', 'artificial intelligence',
            'staff', 'principal', 'head', 'director', 'vp', 'cto',
            'infrastructure', 'platform', 'backend', 'data'
        ]

        return any(keyword in title_lower for keyword in relevant_keywords)

    def score_contact(self, contact: Dict, company_priority: int) -> int:
        """Score contact relevance (0-100)."""
        score = 50
        title_lower = contact.get('title', '').lower()

        # Title scoring
        if 'ml' in title_lower or 'machine learning' in title_lower:
            score += 30
        elif 'ai' in title_lower:
            score += 25
        elif 'cto' in title_lower or 'vp' in title_lower:
            score += 20
        elif 'head' in title_lower or 'director' in title_lower:
            score += 15
        elif 'staff' in title_lower or 'principal' in title_lower:
            score += 15
        elif 'senior' in title_lower:
            score += 10

        # Connection scoring
        connection = contact.get('connection', '')
        if '1st' in connection:
            score += 10
        elif '2nd' in connection:
            score += 5

        # Company priority
        if company_priority == 1:
            score += 10

        return min(score, 100)

    def automated_search(self, headless: bool = False):
        """Run automated LinkedIn search."""
        print("\n🤖 Starting automated LinkedIn search...")
        print("=" * 60)

        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()

            # First, user needs to log in
            print("\n📝 Please log in to LinkedIn:")
            print("1. Browser will open LinkedIn")
            print("2. Log in with your credentials")
            print("3. Press Enter here when logged in")

            page.goto("https://www.linkedin.com/login")

            if not headless:
                input("\nPress Enter after logging in to LinkedIn...")

            # Search for each company and keyword combination
            for company in self.target_companies[:3]:  # Start with top 3 companies
                print(f"\n🔍 Searching {company['name']}...")

                for keyword in self.target_keywords[:5]:  # Top 5 keywords
                    search_url = self.create_search_url(company['name'], keyword)
                    page.goto(search_url)
                    time.sleep(3)  # Wait for results

                    # Extract contacts from search results
                    results = page.query_selector_all(".entity-result__item")

                    for result in results[:3]:  # Top 3 results per search
                        contact = self.extract_contact_from_element(page, result)

                        if contact and self.is_relevant_contact(contact):
                            contact['company'] = company['name']
                            contact['company_priority'] = company['priority']
                            contact['search_keyword'] = keyword
                            contact['relevance_score'] = self.score_contact(contact, company['priority'])
                            contact['discovered_at'] = datetime.now().isoformat()

                            self.contacts.append(contact)
                            print(f"  ✅ Found: {contact['name']} - {contact['title']}")

                    time.sleep(2)  # Rate limiting

            browser.close()

        # Export results
        self.export_results()

    def manual_browser_helper(self):
        """Launch browser with helper script for manual searching."""
        print("\n🌐 Launching browser with LinkedIn helper...")
        print("=" * 60)

        helper_script = """
// LinkedIn Contact Extractor Helper
// This script will help you extract contacts from LinkedIn

function extractContacts() {
    const contacts = [];
    const results = document.querySelectorAll('.entity-result__item');

    results.forEach(result => {
        const contact = {};

        // Extract name
        const nameElem = result.querySelector('.entity-result__title-text a span[aria-hidden="true"]');
        if (nameElem) contact.name = nameElem.innerText.trim();

        // Extract title
        const titleElem = result.querySelector('.entity-result__primary-subtitle');
        if (titleElem) contact.title = titleElem.innerText.trim();

        // Extract LinkedIn URL
        const linkElem = result.querySelector('.entity-result__title-text a');
        if (linkElem) contact.linkedin = linkElem.href.split('?')[0];

        // Extract connection degree
        const badgeElem = result.querySelector('.entity-result__badge-text');
        if (badgeElem) contact.connection = badgeElem.innerText.trim();

        if (contact.name) contacts.push(contact);
    });

    return contacts;
}

// Copy results to clipboard
function copyContacts() {
    const contacts = extractContacts();
    const csv = contacts.map(c =>
        `${c.name},${c.title},${c.linkedin},${c.connection}`
    ).join('\\n');

    navigator.clipboard.writeText(csv);
    console.log(`✅ Copied ${contacts.length} contacts to clipboard!`);
    console.table(contacts);
}

console.log('LinkedIn Helper Loaded! Use these commands:');
console.log('extractContacts() - Extract contacts from current page');
console.log('copyContacts() - Copy contacts to clipboard as CSV');
        """

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()

            # Inject helper script
            page.add_init_script(helper_script)

            # Navigate to LinkedIn
            page.goto("https://www.linkedin.com/login")

            print("\n📋 Instructions:")
            print("-" * 40)
            print("1. Log in to LinkedIn")
            print("2. Search for each company + title combination")
            print("3. Open browser console (F12)")
            print("4. Run: copyContacts()")
            print("5. Paste results into the CSV file")
            print("\n🔍 Suggested searches:")

            for company in self.target_companies:
                print(f"\n{company['name']}:")
                print(f'  • "{company["name"]}" AND "ML Engineer"')
                print(f'  • "{company["name"]}" AND "AI Engineer"')
                print(f'  • "{company["name"]}" AND "CTO"')

            print("\nPress Ctrl+C to exit when done...")

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                browser.close()

    def export_results(self):
        """Export discovered contacts to CSV."""
        if not self.contacts:
            print("❌ No contacts found")
            return

        output_file = f"data/companies/linkedin_contacts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        # Sort by relevance score
        self.contacts.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['company', 'name', 'title', 'linkedin_url', 'location',
                         'connection', 'relevance_score', 'search_keyword']
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')

            writer.writeheader()
            writer.writerows(self.contacts)

        print(f"\n✅ Exported {len(self.contacts)} contacts to: {output_file}")
        print(f"\nTop 5 contacts by relevance:")
        for contact in self.contacts[:5]:
            print(f"  • {contact['name']} ({contact['title']}) - Score: {contact['relevance_score']}")


def main():
    parser = argparse.ArgumentParser(description="LinkedIn contact scraper")
    parser.add_argument("command",
                       choices=["setup", "search", "manual"],
                       help="setup: Install browser | search: Auto search | manual: Manual helper")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")

    args = parser.parse_args()
    scraper = LinkedInContactScraper()

    if args.command == "setup":
        scraper.setup_browser()

    elif args.command == "search":
        scraper.automated_search(headless=args.headless)

    elif args.command == "manual":
        scraper.manual_browser_helper()


if __name__ == "__main__":
    main()