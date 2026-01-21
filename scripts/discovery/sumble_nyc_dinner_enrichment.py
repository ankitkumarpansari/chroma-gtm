"""
Sumble API Integration for NYC Dinner Company Enrichment
=========================================================

This script enriches the 58 NYC companies identified for the Chroma dinner
using the Sumble API to find the right ICPs (decision-makers).

Usage:
    python scripts/discovery/sumble_nyc_dinner_enrichment.py

API Documentation: https://docs.sumble.com/api
"""

import requests
import json
import csv
import time
import os
from typing import List, Dict, Optional
from datetime import datetime

# Configuration
CREDENTIALS_PATH = "credentials/sumble_api_key.txt"
BASE_URL = "https://api.sumble.com/v3"
RATE_LIMIT_DELAY = 0.15  # 10 requests per second = 100ms between requests, adding buffer
OUTPUT_DIR = "data/exports"
OUTPUT_FILE = f"{OUTPUT_DIR}/nyc_dinner_enriched_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
OUTPUT_JSON = f"{OUTPUT_DIR}/nyc_dinner_enriched_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

# ICP Titles to search for (prioritized)
ICP_TITLES = [
    # C-Level
    "CTO", "Chief Technology Officer", "Chief AI Officer", "Chief Data Officer",
    # VP Level
    "VP Engineering", "VP of Engineering", "Vice President Engineering",
    "VP AI", "VP Machine Learning", "VP Data", "VP Platform",
    # Head/Director Level
    "Head of AI", "Head of ML", "Head of Data", "Head of Engineering",
    "Head of Platform", "Director of Engineering", "Engineering Director",
    "Director of AI", "Director of ML", "Director of Data",
    # Staff/Principal Level
    "Staff Engineer", "Principal Engineer", "Staff ML Engineer", 
    "Staff AI Engineer", "Principal ML Engineer", "Staff Software Engineer",
    # Lead Level
    "AI Engineer", "ML Engineer", "Machine Learning Engineer",
    "Platform Lead", "Tech Lead", "Engineering Manager"
]

# 58 NYC Companies for the dinner (from our comprehensive analysis)
NYC_COMPANIES = [
    # TIER 1: HIGHEST PRIORITY (Finance Giants + Active Customers)
    {"name": "BlackRock", "domain": "blackrock.com", "tier": 1, "category": "Finance Giant", "priority": "CRITICAL"},
    {"name": "JP Morgan", "domain": "jpmorgan.com", "tier": 1, "category": "Finance Giant", "priority": "CRITICAL"},
    {"name": "Morgan Stanley", "domain": "morganstanley.com", "tier": 1, "category": "Finance Giant", "priority": "CRITICAL"},
    {"name": "Bloomberg", "domain": "bloomberg.com", "tier": 1, "category": "Finance Giant", "priority": "CRITICAL"},
    {"name": "Jane Street", "domain": "janestreet.com", "tier": 1, "category": "Finance Giant", "priority": "CRITICAL"},
    {"name": "HoneyHive", "domain": "honeyhive.ai", "tier": 1, "category": "Active Customer", "priority": "CRITICAL"},
    {"name": "Monk.io", "domain": "monk.io", "tier": 1, "category": "Active Customer", "priority": "CRITICAL"},
    {"name": "Datafold", "domain": "datafold.com", "tier": 1, "category": "Active Customer", "priority": "CRITICAL"},
    {"name": "Shaped", "domain": "shaped.ai", "tier": 1, "category": "Active Customer", "priority": "HIGH"},
    {"name": "General Intelligence Co.", "domain": "generalintelligencecompany.com", "tier": 1, "category": "Active Customer", "priority": "HIGH"},
    
    # TIER 2: HIGH PRIORITY (Signal List + In-Market)
    {"name": "Rogo", "domain": "rogodata.com", "tier": 2, "category": "Signal List", "priority": "HIGH"},
    {"name": "Koyfin", "domain": "koyfin.com", "tier": 2, "category": "Signal List", "priority": "HIGH"},
    {"name": "Spotnana", "domain": "spotnana.com", "tier": 2, "category": "Signal List", "priority": "HIGH"},
    {"name": "Gushwork", "domain": "gushwork.ai", "tier": 2, "category": "Active Customer", "priority": "HIGH"},
    {"name": "Sandbar", "domain": "sandbar.inc", "tier": 2, "category": "Active Customer", "priority": "HIGH"},
    {"name": "Peloton Interactive", "domain": "onepeloton.com", "tier": 2, "category": "In-Market", "priority": "HIGH"},
    {"name": "Superblocks", "domain": "superblocks.com", "tier": 2, "category": "In-Market", "priority": "HIGH"},
    {"name": "Connatix (JWP)", "domain": "connatix.com", "tier": 2, "category": "Active Customer", "priority": "HIGH"},
    {"name": "Rightway", "domain": "rightwayhealthcare.com", "tier": 2, "category": "In-Market", "priority": "HIGH"},
    {"name": "TermSheet", "domain": "termsheet.com", "tier": 2, "category": "In-Market", "priority": "HIGH"},
    
    # TIER 3: MEDIUM-HIGH PRIORITY (Enterprise + In-Market)
    {"name": "Novo", "domain": "novo.co", "tier": 3, "category": "In-Market", "priority": "MEDIUM"},
    {"name": "1upHealth", "domain": "1up.health", "tier": 3, "category": "In-Market", "priority": "MEDIUM"},
    {"name": "Able", "domain": "able.co", "tier": 3, "category": "In-Market", "priority": "MEDIUM"},
    {"name": "Opentrons Labworks", "domain": "opentrons.com", "tier": 3, "category": "In-Market", "priority": "MEDIUM"},
    {"name": "IBM", "domain": "ibm.com", "tier": 3, "category": "Enterprise", "priority": "MEDIUM"},
    {"name": "The Browser Company", "domain": "thebrowser.company", "tier": 3, "category": "AI Engineer Speaker", "priority": "HIGH"},
    {"name": "Ramp", "domain": "ramp.com", "tier": 3, "category": "AI Engineer Speaker", "priority": "HIGH"},
    {"name": "Complex Media", "domain": "complex.com", "tier": 3, "category": "VIP Customer", "priority": "HIGH"},
    {"name": "Medidata Solutions", "domain": "mdsol.com", "tier": 3, "category": "VIP Customer", "priority": "HIGH"},
    {"name": "FarmEvo", "domain": "farmevo.io", "tier": 3, "category": "In-Market", "priority": "MEDIUM"},
    
    # TIER 4: SI PARTNERS + AGENCIES (NYC)
    {"name": "SJ Innovation", "domain": "sjinnovation.com", "tier": 4, "category": "SI Partner", "priority": "MEDIUM"},
    {"name": "Halo Media", "domain": "halomedia.com", "tier": 4, "category": "SI Partner", "priority": "MEDIUM"},
    {"name": "PYYNE Digital", "domain": "pyyne.com", "tier": 4, "category": "SI Partner", "priority": "MEDIUM"},
    {"name": "Small Planet", "domain": "smallplanet.com", "tier": 4, "category": "SI Partner", "priority": "MEDIUM"},
    {"name": "Brownstone Investment Group", "domain": "brownstoneig.com", "tier": 4, "category": "Finance", "priority": "MEDIUM"},
    {"name": "RAB Lighting", "domain": "rablighting.com", "tier": 4, "category": "Enterprise", "priority": "LOW"},
    {"name": "Accenture", "domain": "accenture.com", "tier": 4, "category": "SI Partner", "priority": "MEDIUM"},
    {"name": "Deloitte", "domain": "deloitte.com", "tier": 4, "category": "SI Partner", "priority": "MEDIUM"},
    
    # TIER 5: ADDITIONAL NYC TARGETS
    {"name": "Sutra", "domain": "sutra.co", "tier": 5, "category": "In-Market", "priority": "LOW"},
    {"name": "Storytime", "domain": "storytime.co", "tier": 5, "category": "In-Market", "priority": "LOW"},
    {"name": "Pelago Health", "domain": "pelagohealth.com", "tier": 5, "category": "Healthcare", "priority": "MEDIUM"},
    {"name": "GoStork", "domain": "gostork.com", "tier": 5, "category": "Healthcare", "priority": "LOW"},
    {"name": "SportsRecruits", "domain": "sportsrecruits.com", "tier": 5, "category": "In-Market", "priority": "LOW"},
    {"name": "StubHub", "domain": "stubhub.com", "tier": 5, "category": "Enterprise", "priority": "MEDIUM"},
    {"name": "Berkadia", "domain": "berkadia.com", "tier": 5, "category": "Finance", "priority": "MEDIUM"},
    {"name": "Compound VC", "domain": "compound.vc", "tier": 5, "category": "VC", "priority": "MEDIUM"},
    {"name": "Lux Capital", "domain": "luxcapital.com", "tier": 5, "category": "VC", "priority": "MEDIUM"},
    {"name": "Every (AI & I)", "domain": "every.to", "tier": 5, "category": "AI Media", "priority": "MEDIUM"},
    {"name": "Triple Whale", "domain": "triplewhale.com", "tier": 5, "category": "VIP Customer", "priority": "HIGH"},
    {"name": "xAI", "domain": "x.ai", "tier": 5, "category": "VIP Customer", "priority": "CRITICAL"},
    
    # BONUS: HIGH-VALUE TARGETS
    {"name": "DigitalOcean", "domain": "digitalocean.com", "tier": 5, "category": "Competitor Customer", "priority": "HIGH"},
    {"name": "Mintlify", "domain": "mintlify.com", "tier": 5, "category": "VIP Customer", "priority": "HIGH"},
    {"name": "Warp", "domain": "warp.dev", "tier": 5, "category": "VIP Customer", "priority": "HIGH"},
    {"name": "Clay", "domain": "clay.com", "tier": 5, "category": "Signal List", "priority": "HIGH"},
    {"name": "Harvey AI", "domain": "harvey.ai", "tier": 5, "category": "Signal List", "priority": "HIGH"},
    {"name": "Travelers Insurance", "domain": "travelers.com", "tier": 5, "category": "VIP Customer", "priority": "MEDIUM"},
    {"name": "Salesforce", "domain": "salesforce.com", "tier": 5, "category": "VIP Customer", "priority": "MEDIUM"},
    {"name": "Optum", "domain": "optum.com", "tier": 5, "category": "VIP Customer", "priority": "MEDIUM"},
]


def load_api_key() -> str:
    """Load Sumble API key from credentials file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    key_path = os.path.join(project_root, CREDENTIALS_PATH)
    
    if not os.path.exists(key_path):
        raise FileNotFoundError(f"API key file not found at {key_path}")
    
    with open(key_path, 'r') as f:
        return f.read().strip()


class SumbleClient:
    """Client for interacting with Sumble API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.last_request_time = 0
        self.request_count = 0
        self.error_count = 0
    
    def _rate_limit(self):
        """Ensure we don't exceed 10 requests/second"""
        elapsed = time.time() - self.last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()
        self.request_count += 1
    
    def enrich_organization(self, domain: str) -> Optional[Dict]:
        """
        Enrich organization with firmographic data
        
        API: POST /organizations/enrich
        Returns: Company info including technologies used
        """
        self._rate_limit()
        
        try:
            response = requests.post(
                f"{BASE_URL}/organizations/enrich",
                headers=self.headers,
                json={
                    "organization": {"domain": domain},
                    "filters": {
                        "technologies": [
                            "python", "langchain", "openai", "huggingface",
                            "pinecone", "weaviate", "milvus", "qdrant",
                            "pytorch", "tensorflow", "aws", "gcp", "azure"
                        ]
                    }
                },
                timeout=30
            )
            
            if response.status_code == 429:
                print(f"  ⚠️ Rate limited, waiting 2 seconds...")
                time.sleep(2)
                return self.enrich_organization(domain)
            
            if response.status_code == 200:
                data = response.json()
                # Extract technology names from the technologies array
                tech_names = [t.get("name", "") for t in data.get("technologies", [])]
                data["technology_names"] = tech_names
                return data
            else:
                print(f"  ⚠️ Organization enrich failed: {response.status_code}")
                self.error_count += 1
                return None
                
        except Exception as e:
            print(f"  ❌ Error enriching organization: {e}")
            self.error_count += 1
            return None
    
    def discover_people(self, domain: str, titles: List[str] = None) -> Optional[Dict]:
        """
        Find decision-makers at a company
        
        API: POST /people/find
        Returns: List of people at the organization
        """
        self._rate_limit()
        
        try:
            response = requests.post(
                f"{BASE_URL}/people/find",
                headers=self.headers,
                json={
                    "organization": {"domain": domain},
                    "filters": {}  # Get all people, filter client-side
                },
                timeout=30
            )
            
            if response.status_code == 429:
                print(f"  ⚠️ Rate limited, waiting 2 seconds...")
                time.sleep(2)
                return self.discover_people(domain, titles)
            
            if response.status_code == 200:
                data = response.json()
                # Filter for engineering/tech roles client-side
                if "people" in data:
                    tech_functions = ["engineering", "technology", "it", "data", "product", "executive"]
                    tech_titles = ["cto", "vp", "head", "director", "staff", "principal", "lead", "engineer", "architect"]
                    
                    filtered_people = []
                    for person in data.get("people", []):
                        job_function = (person.get("job_function") or "").lower()
                        job_title = (person.get("job_title") or "").lower()
                        
                        # Include if job function is tech-related OR title matches
                        is_tech_function = any(func in job_function for func in tech_functions)
                        is_tech_title = any(title in job_title for title in tech_titles)
                        
                        if is_tech_function or is_tech_title:
                            filtered_people.append(person)
                    
                    data["people"] = filtered_people
                    data["filtered_count"] = len(filtered_people)
                return data
            else:
                print(f"  ⚠️ People discovery failed: {response.status_code}")
                self.error_count += 1
                return None
                
        except Exception as e:
            print(f"  ❌ Error discovering people: {e}")
            self.error_count += 1
            return None


def calculate_icp_score(person: Dict, org: Dict, company: Dict) -> int:
    """
    Score a contact based on ICP fit for Chroma
    
    Scoring:
    - Title: CTO/VP = 10, Director = 8, Staff = 6, Lead = 4
    - Job Function: Engineering/Technology = +3
    - Tech Stack: AI/ML tech = +5, Competitor tech = +3
    - Company Priority: CRITICAL = +5, HIGH = +3, MEDIUM = +1
    """
    score = 0
    title = person.get("job_title", "").lower()
    job_function = person.get("job_function", "").lower()
    
    # Title scoring
    if any(t in title for t in ["cto", "chief technology", "chief ai", "chief data"]):
        score += 10
    elif any(t in title for t in ["vp", "vice president"]):
        score += 9
    elif any(t in title for t in ["head of", "director"]):
        score += 8
    elif any(t in title for t in ["staff", "principal"]):
        score += 6
    elif any(t in title for t in ["lead", "manager", "senior"]):
        score += 4
    elif any(t in title for t in ["engineer", "architect"]):
        score += 3
    
    # Job function scoring
    if any(f in job_function for f in ["engineering", "technology", "it", "data"]):
        score += 3
    elif "executive" in job_function:
        score += 2
    
    # Tech stack scoring (if using AI/ML tech)
    tech_stack = org.get("technologies", []) if org else []
    ai_tech = ["python", "langchain", "openai", "huggingface", "pytorch", "tensorflow"]
    if any(tech.lower() in [t.lower() for t in tech_stack] for tech in ai_tech):
        score += 5
    
    # Competitor tech (displacement opportunity!)
    competitor_tech = ["pinecone", "weaviate", "milvus", "qdrant", "elasticsearch"]
    if any(tech.lower() in [t.lower() for t in tech_stack] for tech in competitor_tech):
        score += 3
    
    # Company priority scoring
    priority = company.get("priority", "MEDIUM")
    if priority == "CRITICAL":
        score += 5
    elif priority == "HIGH":
        score += 3
    elif priority == "MEDIUM":
        score += 1
    
    # Tier scoring (lower tier = higher priority)
    tier = company.get("tier", 5)
    score += max(0, 6 - tier)
    
    return score


def main():
    """Main execution function"""
    print("=" * 60)
    print("🚀 Sumble NYC Dinner Company Enrichment")
    print("=" * 60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏢 Companies to process: {len(NYC_COMPANIES)}")
    print()
    
    # Load API key
    try:
        api_key = load_api_key()
        print("✅ API key loaded successfully")
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return
    
    # Initialize client
    client = SumbleClient(api_key)
    
    # Results storage
    all_results = []
    company_summaries = []
    
    print()
    print("🔍 Starting enrichment process...")
    print("-" * 60)
    
    for i, company in enumerate(NYC_COMPANIES, 1):
        print(f"\n[{i}/{len(NYC_COMPANIES)}] Processing: {company['name']} ({company['domain']})")
        print(f"  Tier: {company['tier']} | Category: {company['category']} | Priority: {company['priority']}")
        
        # Step 1: Enrich organization
        print("  📊 Enriching organization data...")
        org_data = client.enrich_organization(company["domain"])
        
        if org_data:
            tech_names = org_data.get("technology_names", [])
            print(f"  ✅ Organization data retrieved - Technologies: {', '.join(tech_names) if tech_names else 'None found'}")
            org_info = org_data.get("organization", {})
            org_info["technologies"] = tech_names
            org_info["technologies_count"] = org_data.get("technologies_count", 0)
        else:
            print(f"  ⚠️ No organization data found")
            org_info = {}
            tech_names = []
        
        # Step 2: Discover ICPs
        print("  👥 Discovering decision-makers...")
        people_data = client.discover_people(company["domain"])
        
        people_found = 0
        total_people = 0
        if people_data and "people" in people_data:
            total_people = people_data.get("people_count", 0)
            people_found = people_data.get("filtered_count", len(people_data.get("people", [])))
            print(f"  ✅ Found {people_found} tech/engineering contacts (from {total_people} total)")
            
            # Score and collect each person
            for person in people_data.get("people", []):
                score = calculate_icp_score(person, org_info, company)
                
                result = {
                    "company": company["name"],
                    "domain": company["domain"],
                    "tier": company["tier"],
                    "category": company["category"],
                    "priority": company["priority"],
                    "name": person.get("name", ""),
                    "title": person.get("job_title", ""),
                    "job_function": person.get("job_function", ""),
                    "linkedin_url": person.get("linkedin_url", ""),
                    "sumble_url": person.get("url", ""),
                    "icp_score": score,
                    "tech_stack": ", ".join(org_info.get("technologies", [])[:5]),
                }
                all_results.append(result)
        else:
            print(f"  ⚠️ No contacts found")
        
        # Company summary
        company_summaries.append({
            "company": company["name"],
            "domain": company["domain"],
            "tier": company["tier"],
            "category": company["category"],
            "priority": company["priority"],
            "contacts_found": people_found,
            "total_employees": total_people,
            "technologies": ", ".join(org_info.get("technologies", [])),
            "has_ai_tech": any(
                tech.lower() in ["python", "langchain", "openai", "pytorch", "tensorflow", "huggingface"] 
                for tech in org_info.get("technologies", [])
            ),
            "has_competitor_tech": any(
                tech.lower() in ["pinecone", "weaviate", "milvus", "qdrant"]
                for tech in org_info.get("technologies", [])
            )
        })
    
    print()
    print("=" * 60)
    print("📊 ENRICHMENT COMPLETE")
    print("=" * 60)
    print(f"Total API requests: {client.request_count}")
    print(f"Errors encountered: {client.error_count}")
    print(f"Total contacts found: {len(all_results)}")
    print()
    
    # Sort results by ICP score
    all_results.sort(key=lambda x: x["icp_score"], reverse=True)
    
    # Ensure output directory exists
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    output_dir = os.path.join(project_root, OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    
    # Export to CSV
    csv_path = os.path.join(project_root, OUTPUT_FILE)
    if all_results:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
            writer.writeheader()
            writer.writerows(all_results)
        print(f"✅ CSV exported: {csv_path}")
    
    # Export to JSON (full data)
    json_path = os.path.join(project_root, OUTPUT_JSON)
    export_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_companies": len(NYC_COMPANIES),
            "total_contacts": len(all_results),
            "api_requests": client.request_count,
            "errors": client.error_count
        },
        "company_summaries": company_summaries,
        "contacts": all_results
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON exported: {json_path}")
    
    # Print top 20 ICPs
    print()
    print("=" * 60)
    print("🎯 TOP 20 ICPs FOR NYC DINNER")
    print("=" * 60)
    for i, r in enumerate(all_results[:20], 1):
        print(f"{i:2}. {r['name'][:25]:<25} | {r['title'][:30]:<30} | {r['company']:<20} | Score: {r['icp_score']}")
    
    # Print company summary
    print()
    print("=" * 60)
    print("📋 COMPANY SUMMARY")
    print("=" * 60)
    for summary in sorted(company_summaries, key=lambda x: x["tier"]):
        ai_badge = "🤖" if summary["has_ai_tech"] else ""
        comp_badge = "⚔️" if summary["has_competitor_tech"] else ""
        tech_preview = summary.get("technologies", "")[:30] + "..." if len(summary.get("technologies", "")) > 30 else summary.get("technologies", "")
        print(f"T{summary['tier']} | {summary['company']:<25} | {summary['contacts_found']:2} contacts | {tech_preview:<35} | {ai_badge}{comp_badge}")
    
    print()
    print("🎉 Done! Check the exports folder for full results.")


if __name__ == "__main__":
    main()

