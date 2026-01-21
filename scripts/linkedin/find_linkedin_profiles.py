"""
Find LinkedIn Profiles for AI Engineer Speakers using Parallel FindAll API

This script uses the Parallel FindAll API to search for LinkedIn profiles
of speakers who don't have them in our database.
"""

import os
import json
import csv
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

# API Configuration
PARALLEL_API_KEY = os.getenv("PARALLEL_API_KEY")
BASE_URL = "https://api.parallel.ai/v1beta/findall"
BETA_HEADER = "findall-2025-09-15"


def load_speakers_without_linkedin():
    """Load speakers from CSV who don't have LinkedIn profiles."""
    speakers_needing_linkedin = []
    
    with open('ai_engineer_speakers_linkedin.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            linkedin_url = row.get('LinkedIn URL', '').strip()
            # Skip if already has a LinkedIn URL
            if linkedin_url and 'linkedin.com' in linkedin_url.lower():
                continue
            # Skip if has Twitter (we already have some contact info)
            if linkedin_url and 'twitter.com' in linkedin_url.lower():
                continue
                
            speakers_needing_linkedin.append({
                'name': row['Name'],
                'company': row['Company'],
                'role': row.get('Role', ''),
            })
    
    return speakers_needing_linkedin


class ParallelLinkedInFinder:
    """Find LinkedIn profiles using Parallel FindAll API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or PARALLEL_API_KEY
        if not self.api_key:
            raise ValueError("PARALLEL_API_KEY not found")
        
        self.headers = {
            "x-api-key": self.api_key,
            "parallel-beta": BETA_HEADER,
            "Content-Type": "application/json"
        }
    
    def find_person_linkedin(self, name: str, company: str, role: str = "") -> Dict[str, Any]:
        """
        Use Parallel FindAll to find a person's LinkedIn profile.
        
        Args:
            name: Person's full name
            company: Company they work at
            role: Their role/title (optional)
            
        Returns:
            Dict with linkedin_url and confidence
        """
        import requests
        
        # Construct the search query
        role_str = f" who is {role}" if role else ""
        query = f"FindAll people named {name}{role_str} at {company}"
        
        # Use ingest to get structured query
        try:
            # Step 1: Ingest
            response = requests.post(
                f"{BASE_URL}/ingest",
                headers=self.headers,
                json={"objective": query}
            )
            response.raise_for_status()
            schema = response.json()
            
            # Add enrichment for LinkedIn URL
            enrichments = [
                {
                    "name": "linkedin_url",
                    "description": "The person's LinkedIn profile URL"
                }
            ]
            
            # Step 2: Create run
            payload = {
                "objective": schema["objective"],
                "entity_type": "people",  # Override to search for people
                "match_conditions": schema["match_conditions"],
                "generator": "base",  # Use base for speed
                "match_limit": 1,  # We only need the best match
                "enrichments": enrichments
            }
            
            response = requests.post(
                f"{BASE_URL}/runs",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            findall_id = response.json()["findall_id"]
            
            # Step 3: Wait for completion
            for _ in range(60):  # Max 60 attempts (5 min timeout)
                time.sleep(5)
                response = requests.get(
                    f"{BASE_URL}/runs/{findall_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                status = response.json()
                
                if not status["status"]["is_active"]:
                    break
            
            # Step 4: Get results
            response = requests.get(
                f"{BASE_URL}/runs/{findall_id}/result",
                headers=self.headers
            )
            response.raise_for_status()
            results = response.json()
            
            # Extract LinkedIn URL from results
            candidates = results.get("candidates", [])
            if candidates:
                candidate = candidates[0]
                output = candidate.get("output", {})
                linkedin_url = output.get("linkedin_url", "")
                
                return {
                    "name": name,
                    "company": company,
                    "linkedin_url": linkedin_url,
                    "found_name": candidate.get("name", ""),
                    "confidence": "high" if linkedin_url else "not_found"
                }
            
            return {
                "name": name,
                "company": company,
                "linkedin_url": "",
                "confidence": "not_found"
            }
            
        except Exception as e:
            print(f"Error finding {name} at {company}: {e}")
            return {
                "name": name,
                "company": company,
                "linkedin_url": "",
                "confidence": "error",
                "error": str(e)
            }


def batch_search_linkedin_google(speakers: List[Dict], output_file: str = "linkedin_search_results.json"):
    """
    Alternative: Use Google search queries to generate LinkedIn URLs.
    This doesn't require API but gives search strings you can use.
    """
    search_queries = []
    
    for speaker in speakers:
        name = speaker['name']
        company = speaker['company']
        role = speaker.get('role', '')
        
        # Generate Google search query for LinkedIn
        search_query = f'site:linkedin.com/in "{name}" "{company}"'
        if role:
            search_query += f' "{role}"'
        
        search_queries.append({
            "name": name,
            "company": company,
            "role": role,
            "google_search": search_query,
            "google_url": f"https://www.google.com/search?q={search_query.replace(' ', '+').replace('\"', '%22')}"
        })
    
    # Save search queries
    with open(output_file, 'w') as f:
        json.dump(search_queries, f, indent=2)
    
    print(f"Generated {len(search_queries)} search queries")
    print(f"Saved to {output_file}")
    
    return search_queries


def main():
    """Main function to find LinkedIn profiles."""
    
    print("=" * 60)
    print("AI Engineer Speakers - LinkedIn Profile Finder")
    print("=" * 60)
    
    # Load speakers without LinkedIn
    speakers = load_speakers_without_linkedin()
    print(f"\nFound {len(speakers)} speakers without LinkedIn profiles")
    
    if not speakers:
        print("All speakers already have LinkedIn profiles!")
        return
    
    # Check if we have API key
    if not PARALLEL_API_KEY:
        print("\n⚠️  PARALLEL_API_KEY not found in .env")
        print("Generating Google search queries instead...")
        batch_search_linkedin_google(speakers)
        return
    
    print(f"\nUsing Parallel FindAll API to search for LinkedIn profiles...")
    print("This may take a while as each search takes ~30-60 seconds\n")
    
    # Initialize finder
    finder = ParallelLinkedInFinder()
    
    # Process speakers (limit for testing)
    results = []
    max_to_process = 10  # Start with 10 for testing
    
    for i, speaker in enumerate(speakers[:max_to_process], 1):
        print(f"[{i}/{min(len(speakers), max_to_process)}] Searching for {speaker['name']} at {speaker['company']}...")
        
        result = finder.find_person_linkedin(
            name=speaker['name'],
            company=speaker['company'],
            role=speaker.get('role', '')
        )
        
        results.append(result)
        
        if result.get('linkedin_url'):
            print(f"  ✓ Found: {result['linkedin_url']}")
        else:
            print(f"  ✗ Not found")
        
        # Rate limiting
        time.sleep(2)
    
    # Save results
    output_file = "linkedin_profiles_found.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'=' * 60}")
    print(f"Results saved to {output_file}")
    
    # Summary
    found = sum(1 for r in results if r.get('linkedin_url'))
    print(f"Found {found}/{len(results)} LinkedIn profiles")
    
    # Also generate search queries for remaining speakers
    remaining_speakers = speakers[max_to_process:]
    if remaining_speakers:
        print(f"\nGenerating search queries for remaining {len(remaining_speakers)} speakers...")
        batch_search_linkedin_google(remaining_speakers, "remaining_linkedin_searches.json")


def generate_all_search_queries():
    """Generate Google search queries for all speakers without LinkedIn."""
    speakers = load_speakers_without_linkedin()
    print(f"Found {len(speakers)} speakers without LinkedIn profiles")
    
    # Generate search queries
    queries = batch_search_linkedin_google(speakers, "all_linkedin_search_queries.json")
    
    # Also create a simple text file with queries
    with open("linkedin_search_queries.txt", 'w') as f:
        for q in queries:
            f.write(f"{q['name']} ({q['company']})\n")
            f.write(f"  Search: {q['google_search']}\n")
            f.write(f"  URL: {q['google_url']}\n\n")
    
    print(f"Also saved to linkedin_search_queries.txt")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--queries-only":
        generate_all_search_queries()
    else:
        main()

