#!/usr/bin/env python3
"""
Find Target Contacts at High-Priority Companies
================================================
Discovers ML Engineers, AI Engineers, and CTOs at target companies
using multiple data sources.

Methods:
1. LinkedIn Sales Navigator search
2. GitHub contributor analysis
3. Company blog/team page scraping
4. Conference speaker databases
5. Patent/paper authors

Usage:
    python scripts/discovery/find_target_contacts.py search    # Search all companies
    python scripts/discovery/find_target_contacts.py export    # Export to CSV
"""

import os
import json
import csv
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import quote

class ContactFinder:
    """Find technical contacts at target companies."""

    def __init__(self):
        self.target_companies = [
            {
                "name": "Vectara",
                "linkedin_name": "vectara",
                "github_org": "vectara",
                "website": "vectara.com",
                "blog": "vectara.com/blog",
                "priority": "Tier 1",
                "score": 75,
                "focus": "RAG platform"
            },
            {
                "name": "Perplexity AI",
                "linkedin_name": "perplexity-ai",
                "github_org": "perplexity-ai",
                "website": "perplexity.ai",
                "blog": "blog.perplexity.ai",
                "priority": "Tier 2",
                "score": 65,
                "focus": "AI search"
            },
            {
                "name": "Hebbia",
                "linkedin_name": "hebbia",
                "github_org": "hebbia",
                "website": "hebbia.ai",
                "blog": "hebbia.ai/blog",
                "priority": "Tier 2",
                "score": 65,
                "focus": "Enterprise RAG"
            },
            {
                "name": "Glean",
                "linkedin_name": "glean-work",
                "github_org": "glean",
                "website": "glean.com",
                "blog": "glean.com/blog",
                "priority": "Tier 2",
                "score": 55,
                "focus": "Enterprise search"
            },
            {
                "name": "AlphaSense",
                "linkedin_name": "alphasense",
                "github_org": "alphasense",
                "website": "alpha-sense.com",
                "blog": "alpha-sense.com/blog",
                "priority": "Tier 2",
                "score": 50,
                "focus": "Financial research"
            },
            {
                "name": "Clay",
                "linkedin_name": "clay-run",
                "github_org": "clay-run",
                "website": "clay.com",
                "blog": "clay.com/blog",
                "priority": "Tier 2",
                "score": 50,
                "focus": "Sales intelligence"
            },
            {
                "name": "Gong",
                "linkedin_name": "gong-io",
                "github_org": "gong-io",
                "website": "gong.io",
                "blog": "gong.io/blog",
                "priority": "Tier 2",
                "score": 50,
                "focus": "Revenue intelligence"
            }
        ]

        self.target_titles = [
            # Technical Champions
            "ML Engineer",
            "Machine Learning Engineer",
            "AI Engineer",
            "AI Platform Engineer",
            "Staff Engineer",
            "Principal Engineer",
            "Senior ML Engineer",
            "Head of AI",
            "Head of Machine Learning",
            "Director of AI",
            "Director of ML",
            "VP of AI",

            # Decision Makers
            "CTO",
            "Chief Technology Officer",
            "VP Engineering",
            "VP of Engineering",
            "Director of Engineering",
            "Engineering Manager",

            # Infrastructure/Platform
            "Infrastructure Engineer",
            "Platform Engineer",
            "Data Engineer",
            "Backend Engineer"
        ]

        self.discovered_contacts = []

    def generate_linkedin_searches(self) -> List[Dict]:
        """Generate LinkedIn Sales Navigator search URLs."""
        searches = []

        for company in self.target_companies:
            # For each company, create multiple targeted searches

            # ML/AI Engineers
            ml_search = {
                "company": company["name"],
                "search_url": f'https://www.linkedin.com/sales/search/people?query=(filters:List((type:COMPANY,values:List((text:{quote(company["name"])},selectionType:INCLUDED))),(type:TITLE,values:List((text:"ML Engineer",selectionType:INCLUDED),(text:"Machine Learning",selectionType:INCLUDED),(text:"AI Engineer",selectionType:INCLUDED)))))',
                "search_type": "ML/AI Engineers",
                "manual_search": f'Company: "{company["name"]}" AND (title:"ML Engineer" OR title:"Machine Learning" OR title:"AI Engineer")'
            }
            searches.append(ml_search)

            # Leadership
            leadership_search = {
                "company": company["name"],
                "search_url": f'https://www.linkedin.com/sales/search/people?query=(filters:List((type:COMPANY,values:List((text:{quote(company["name"])},selectionType:INCLUDED))),(type:TITLE,values:List((text:"CTO",selectionType:INCLUDED),(text:"VP Engineering",selectionType:INCLUDED),(text:"Head of AI",selectionType:INCLUDED)))))',
                "search_type": "Leadership",
                "manual_search": f'Company: "{company["name"]}" AND (title:"CTO" OR title:"VP Engineering" OR title:"Head of AI")'
            }
            searches.append(leadership_search)

            # Recent Hires (often most responsive)
            recent_search = {
                "company": company["name"],
                "search_url": f'https://www.linkedin.com/sales/search/people?query=(filters:List((type:COMPANY,values:List((text:{quote(company["name"])},selectionType:INCLUDED))),(type:TITLE,values:List((text:"Engineer",selectionType:INCLUDED))),(type:WHEN_JOINED,values:List((text:PAST_90_DAYS,selectionType:INCLUDED)))))',
                "search_type": "Recent Engineering Hires",
                "manual_search": f'Company: "{company["name"]}" AND title:"Engineer" (joined in last 90 days)'
            }
            searches.append(recent_search)

        return searches

    def check_github_contributors(self) -> List[Dict]:
        """Find engineers via GitHub contributions."""
        github_contacts = []

        for company in self.target_companies:
            if not company.get("github_org"):
                continue

            contact = {
                "company": company["name"],
                "method": "GitHub",
                "search_url": f"https://github.com/orgs/{company['github_org']}/people",
                "repos_url": f"https://github.com/{company['github_org']}",
                "note": "Check recent contributors to AI/ML repos"
            }
            github_contacts.append(contact)

        return github_contacts

    def generate_google_searches(self) -> List[Dict]:
        """Generate Google searches for finding team pages and engineers."""
        google_searches = []

        for company in self.target_companies:
            # Team page search
            team_search = {
                "company": company["name"],
                "search": f'site:{company["website"]} "team" OR "about us" OR "our team"',
                "purpose": "Find team page"
            }
            google_searches.append(team_search)

            # Engineering blog authors
            blog_search = {
                "company": company["name"],
                "search": f'site:{company["blog"]} "machine learning" OR "ML" OR "AI" OR "embeddings" OR "vector"',
                "purpose": "Find engineers who blog"
            }
            google_searches.append(blog_search)

            # Conference speakers
            conf_search = {
                "company": company["name"],
                "search": f'"{company["name"]}" "NeurIPS" OR "ICML" OR "AI Summit" OR "MLOps" speaker',
                "purpose": "Find conference speakers"
            }
            google_searches.append(conf_search)

        return google_searches

    def create_contact_template(self) -> Dict:
        """Create a template for manual contact collection."""
        template = {
            "timestamp": datetime.now().isoformat(),
            "companies": {}
        }

        for company in self.target_companies:
            template["companies"][company["name"]] = {
                "priority": company["priority"],
                "score": company["score"],
                "focus": company["focus"],
                "contacts": {
                    "technical_champions": [
                        {
                            "name": "",
                            "title": "",
                            "linkedin": "",
                            "email": "",
                            "github": "",
                            "twitter": "",
                            "recent_activity": "",
                            "relevance": "High/Medium/Low"
                        }
                    ],
                    "decision_makers": [
                        {
                            "name": "",
                            "title": "",
                            "linkedin": "",
                            "email": "",
                            "relevance": "High/Medium/Low"
                        }
                    ],
                    "influencers": []
                },
                "signals": {
                    "recent_hires": [],
                    "recent_content": [],
                    "github_activity": [],
                    "job_postings": []
                }
            }

        return template

    def export_search_guide(self):
        """Export a comprehensive search guide."""
        guide_path = "data/companies/contact_search_guide.json"

        guide = {
            "generated_at": datetime.now().isoformat(),
            "target_companies": self.target_companies,
            "linkedin_searches": self.generate_linkedin_searches(),
            "github_searches": self.check_github_contributors(),
            "google_searches": self.generate_google_searches(),
            "contact_template": self.create_contact_template(),
            "enrichment_tools": {
                "email_finders": [
                    "Hunter.io - https://hunter.io",
                    "Apollo.io - https://apollo.io",
                    "RocketReach - https://rocketreach.com",
                    "Clearbit - https://clearbit.com",
                    "Lusha - https://lusha.com"
                ],
                "verification": [
                    "EmailListVerify - https://emaillistverify.com",
                    "NeverBounce - https://neverbounce.com"
                ]
            },
            "outreach_tips": {
                "subject_lines": [
                    "Quick question about {company}'s RAG implementation",
                    "Thoughts on {company}'s vector search scale challenges?",
                    "How {company} handles embedding storage at scale"
                ],
                "personalization_angles": {
                    "Vectara": "RAG accuracy and hybrid search",
                    "Perplexity": "Real-time semantic search at scale",
                    "Hebbia": "Enterprise RAG security and compliance",
                    "Glean": "Multi-modal enterprise search",
                    "AlphaSense": "Financial document embeddings",
                    "Clay": "Enrichment data vectorization",
                    "Gong": "Conversation analysis vectors"
                }
            }
        }

        os.makedirs(os.path.dirname(guide_path), exist_ok=True)
        with open(guide_path, 'w') as f:
            json.dump(guide, f, indent=2)

        print(f"✅ Search guide exported to: {guide_path}")
        return guide

    def create_csv_template(self):
        """Create CSV template for contact collection."""
        csv_path = "data/companies/target_contacts_template.csv"

        headers = [
            "Company", "Priority", "Contact Name", "Title", "Category",
            "LinkedIn URL", "Email", "Email Verified", "GitHub",
            "Twitter", "Recent Activity", "Relevance Score",
            "Personalization Angle", "Notes"
        ]

        rows = []
        for company in self.target_companies:
            # Create 5 blank rows per company for manual filling
            for i in range(5):
                rows.append([
                    company["name"],
                    company["priority"],
                    "",  # Contact Name
                    "",  # Title
                    "Technical Champion" if i < 3 else "Decision Maker",  # Category
                    "",  # LinkedIn URL
                    "",  # Email
                    "No",  # Email Verified
                    "",  # GitHub
                    "",  # Twitter
                    "",  # Recent Activity
                    "",  # Relevance Score
                    company["focus"],  # Personalization Angle
                    ""  # Notes
                ])

        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

        print(f"✅ CSV template created: {csv_path}")

    def print_search_instructions(self):
        """Print manual search instructions."""
        print("\n" + "="*60)
        print("🎯 CONTACT DISCOVERY GUIDE FOR TOP 7 COMPANIES")
        print("="*60)

        for company in self.target_companies:
            print(f"\n📊 {company['name']} ({company['priority']} - Score: {company['score']})")
            print("-"*40)
            print(f"Focus: {company['focus']}")
            print("\n🔍 LinkedIn Search:")
            print(f'  Company: "{company["name"]}"')
            print(f'  Titles: ML Engineer, AI Engineer, CTO, VP Engineering')
            print(f'  Recent hires: Check "Started in last 90 days"')

            print(f"\n💻 GitHub:")
            print(f"  https://github.com/{company.get('github_org', company['name'].lower())}")
            print(f"  Look for: Contributors to ML/AI repos")

            print(f"\n🌐 Website:")
            print(f"  Team page: {company['website']}/team")
            print(f"  Blog: {company['blog']}")
            print(f"  Careers: {company['website']}/careers")

        print("\n" + "="*60)
        print("💡 PRO TIPS FOR CONTACT DISCOVERY")
        print("="*60)
        print("""
1. LINKEDIN SALES NAVIGATOR:
   - Use Boolean search: (company:"Company Name") AND (title:"ML Engineer" OR title:"AI Engineer")
   - Filter by: Recently changed jobs, Posted on LinkedIn recently
   - Look for: Shared connections, Alumni from your school

2. GITHUB DISCOVERY:
   - Check recent commits to ML/AI repos
   - Look for engineers with vector DB experience
   - Check issues/PRs mentioning "embeddings", "vectors", "RAG"

3. TWITTER/X:
   - Search: from:company_handle "machine learning" OR "AI"
   - Find engineers tweeting about technical topics
   - Check who's following Chroma's Twitter

4. CONFERENCE SPEAKERS:
   - NeurIPS, ICML, AI Summit speakers from these companies
   - Podcast guests talking about AI/ML
   - Webinar presenters

5. TOOLS TO USE:
   - Apollo.io - Free tier gives 50 email credits
   - Hunter.io - Find email patterns
   - RocketReach - Good for senior executives
   - LinkedIn Sales Navigator - 30-day free trial
        """)


def main():
    finder = ContactFinder()

    print("🚀 CONTACT FINDER FOR HIGH-PRIORITY COMPANIES")
    print("="*60)

    # Generate all search materials
    finder.export_search_guide()
    finder.create_csv_template()
    finder.print_search_instructions()

    print("\n✅ DELIVERABLES CREATED:")
    print("-"*40)
    print("1. 📋 Search guide: data/companies/contact_search_guide.json")
    print("2. 📊 CSV template: data/companies/target_contacts_template.csv")
    print("3. 🔍 LinkedIn searches: See guide above")

    print("\n🎯 NEXT STEPS:")
    print("-"*40)
    print("1. Use LinkedIn Sales Navigator (30-day free trial)")
    print("2. Search for each company using provided queries")
    print("3. Fill in the CSV template with discovered contacts")
    print("4. Use Apollo.io or Hunter.io to find emails")
    print("5. Import contacts to Attio")


if __name__ == "__main__":
    main()