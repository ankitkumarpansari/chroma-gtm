"""
Parallel API - Individual LinkedIn Profile Search

Searches for each speaker individually to find their LinkedIn profile.
More precise than batch search.
"""

import os
import json
import csv
import time
import requests
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

PARALLEL_API_KEY = os.getenv("PARALLEL_API_KEY")
BASE_URL = "https://api.parallel.ai/v1beta/findall"
BETA_HEADER = "findall-2025-09-15"


def load_speakers_without_linkedin(csv_file: str = 'ai_engineer_speakers_linkedin.csv') -> List[Dict]:
    """Load speakers from CSV who don't have LinkedIn profiles."""
    speakers = []
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            linkedin_url = row.get('LinkedIn URL', '').strip()
            if linkedin_url and ('linkedin.com' in linkedin_url.lower() or 'twitter.com' in linkedin_url.lower()):
                continue
            speakers.append({
                'name': row['Name'],
                'company': row['Company'],
                'role': row.get('Role', ''),
            })
    
    return speakers


def search_person_linkedin(name: str, company: str, role: str = "") -> Dict:
    """
    Search for a single person's LinkedIn profile.
    Uses a very specific query to find the exact person.
    """
    
    headers = {
        "x-api-key": PARALLEL_API_KEY,
        "parallel-beta": BETA_HEADER,
        "Content-Type": "application/json"
    }
    
    # Very specific query for finding a person's LinkedIn
    role_part = f" ({role})" if role else ""
    query = f"Find the LinkedIn profile for {name}{role_part} at {company}"
    
    try:
        # Step 1: Create a direct run with specific match conditions
        payload = {
            "objective": query,
            "entity_type": "people",
            "match_conditions": [
                {
                    "name": "correct_person", 
                    "description": f"This is {name} who works or worked at {company}"
                }
            ],
            "generator": "base",  # Fast search
            "match_limit": 5,  # Minimum required by API
            "enrichments": [
                {"name": "linkedin_url", "description": "The person's LinkedIn profile URL (format: linkedin.com/in/username)"},
                {"name": "twitter_url", "description": "The person's Twitter/X profile URL"},
                {"name": "company", "description": "Current company"},
                {"name": "title", "description": "Current job title"}
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/runs",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        findall_id = response.json()["findall_id"]
        
        # Step 2: Wait for completion (with shorter timeout for individual searches)
        for _ in range(24):  # 2 min max
            time.sleep(5)
            response = requests.get(
                f"{BASE_URL}/runs/{findall_id}",
                headers=headers
            )
            response.raise_for_status()
            status = response.json()
            
            if not status["status"]["is_active"]:
                break
        
        # Step 3: Get results
        response = requests.get(
            f"{BASE_URL}/runs/{findall_id}/result",
            headers=headers
        )
        response.raise_for_status()
        results = response.json()
        
        candidates = results.get("candidates", [])
        if candidates:
            best = candidates[0]
            output = best.get("output", {})
            
            linkedin = output.get("linkedin_url", "")
            twitter = output.get("twitter_url", "")
            
            return {
                "name": name,
                "company": company,
                "search_name": best.get("name", ""),
                "linkedin_url": linkedin,
                "twitter_url": twitter,
                "found_company": output.get("company", ""),
                "found_title": output.get("title", ""),
                "status": "found" if linkedin or twitter else "partial"
            }
        
        return {
            "name": name,
            "company": company,
            "linkedin_url": "",
            "twitter_url": "",
            "status": "not_found"
        }
        
    except requests.exceptions.HTTPError as e:
        error_msg = str(e)
        if hasattr(e, 'response'):
            error_msg = e.response.text
        return {
            "name": name,
            "company": company,
            "linkedin_url": "",
            "status": "error",
            "error": error_msg
        }
    except Exception as e:
        return {
            "name": name,
            "company": company,
            "linkedin_url": "",
            "status": "error",
            "error": str(e)
        }


def main():
    """Search for LinkedIn profiles for all speakers."""
    
    print("=" * 70)
    print("Parallel API - Individual LinkedIn Profile Search")
    print("=" * 70)
    
    speakers = load_speakers_without_linkedin()
    print(f"\n📋 Found {len(speakers)} speakers without LinkedIn profiles\n")
    
    # Limit for this run (API costs money)
    max_searches = min(len(speakers), 50)  # Search up to 50
    
    print(f"Will search for {max_searches} speakers...")
    print("-" * 70)
    
    results = []
    found_count = 0
    
    for i, speaker in enumerate(speakers[:max_searches], 1):
        name = speaker['name']
        company = speaker['company']
        role = speaker.get('role', '')
        
        print(f"\n[{i}/{max_searches}] Searching: {name} ({company})")
        
        result = search_person_linkedin(name, company, role)
        results.append(result)
        
        if result.get('linkedin_url'):
            print(f"  ✓ LinkedIn: {result['linkedin_url']}")
            found_count += 1
        elif result.get('twitter_url'):
            print(f"  ~ Twitter: {result['twitter_url']}")
        elif result.get('status') == 'error':
            print(f"  ✗ Error: {result.get('error', 'Unknown')[:50]}")
        else:
            print(f"  ✗ Not found")
        
        # Small delay between requests
        time.sleep(1)
    
    # Save results
    output_file = "parallel_linkedin_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 70)
    print(f"Results saved to {output_file}")
    print(f"Found LinkedIn profiles: {found_count}/{max_searches}")
    
    # Also update the CSV with found profiles
    update_csv_with_results(results)
    
    return results


def update_csv_with_results(results: List[Dict]):
    """Update the CSV file with newly found LinkedIn profiles."""
    
    # Create lookup dict
    found_profiles = {}
    for r in results:
        if r.get('linkedin_url'):
            found_profiles[r['name']] = r['linkedin_url']
        elif r.get('twitter_url') and not r.get('linkedin_url'):
            found_profiles[r['name']] = r['twitter_url']
    
    if not found_profiles:
        print("No new profiles to update in CSV")
        return
    
    # Read existing CSV
    rows = []
    with open('ai_engineer_speakers_linkedin.csv', 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row['Name'] in found_profiles and not row.get('LinkedIn URL'):
                row['LinkedIn URL'] = found_profiles[row['Name']]
            rows.append(row)
    
    # Write updated CSV
    with open('ai_engineer_speakers_linkedin.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Updated CSV with {len(found_profiles)} new profiles")


if __name__ == "__main__":
    main()

