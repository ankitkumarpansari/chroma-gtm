"""
Parallel API LinkedIn Profile Search

Uses Parallel FindAll API to find LinkedIn profiles for AI Engineer speakers.
The API searches the web and extracts structured data including LinkedIn URLs.
"""

import os
import json
import csv
import time
import requests
from typing import Optional, Dict, Any, List
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
            # Skip if already has LinkedIn or Twitter
            if linkedin_url and ('linkedin.com' in linkedin_url.lower() or 'twitter.com' in linkedin_url.lower()):
                continue
                
            speakers.append({
                'name': row['Name'],
                'company': row['Company'],
                'role': row.get('Role', ''),
            })
    
    return speakers


def search_linkedin_batch(speakers: List[Dict], batch_size: int = 20) -> List[Dict]:
    """
    Search for LinkedIn profiles using Parallel FindAll API.
    
    The API can find people and their associated URLs including LinkedIn.
    """
    
    if not PARALLEL_API_KEY:
        print("❌ PARALLEL_API_KEY not found in .env")
        return []
    
    headers = {
        "x-api-key": PARALLEL_API_KEY,
        "parallel-beta": BETA_HEADER,
        "Content-Type": "application/json"
    }
    
    # Build a query to find multiple people at once
    # Format: "FindAll people who are speakers at AI Engineer conferences"
    
    # Create a focused query for AI Engineer speakers
    names_list = ", ".join([f"{s['name']} ({s['company']})" for s in speakers[:batch_size]])
    
    query = f"""FindAll people who spoke at AI Engineer conferences or AI Engineer World's Fair. 
    Looking specifically for: {names_list}. 
    These are AI/ML engineers, founders, and technical leaders."""
    
    print(f"Searching for {min(len(speakers), batch_size)} speakers...")
    
    try:
        # Step 1: Ingest the query
        print("  → Ingesting query...")
        response = requests.post(
            f"{BASE_URL}/ingest",
            headers=headers,
            json={"objective": query}
        )
        response.raise_for_status()
        schema = response.json()
        
        print(f"  → Entity type: {schema.get('entity_type', 'unknown')}")
        
        # Step 2: Create run with enrichments for LinkedIn
        payload = {
            "objective": schema["objective"],
            "entity_type": "people",
            "match_conditions": schema.get("match_conditions", [
                {"name": "ai_engineer_speaker", "description": "Person has spoken at AI Engineer conference or related AI events"}
            ]),
            "generator": "core",  # Use core for better quality
            "match_limit": batch_size,
            "enrichments": [
                {"name": "linkedin_url", "description": "The person's LinkedIn profile URL (linkedin.com/in/...)"},
                {"name": "twitter_handle", "description": "The person's Twitter/X handle"},
                {"name": "current_company", "description": "The person's current company"},
                {"name": "current_role", "description": "The person's current job title"}
            ]
        }
        
        print("  → Creating search run...")
        response = requests.post(
            f"{BASE_URL}/runs",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        findall_id = response.json()["findall_id"]
        print(f"  → Run ID: {findall_id}")
        
        # Step 3: Wait for completion
        print("  → Waiting for results (this may take 1-3 minutes)...")
        max_attempts = 60
        for attempt in range(max_attempts):
            time.sleep(5)
            
            response = requests.get(
                f"{BASE_URL}/runs/{findall_id}",
                headers=headers
            )
            response.raise_for_status()
            status = response.json()
            
            metrics = status.get("status", {}).get("metrics", {})
            generated = metrics.get("generated_candidates_count", 0)
            matched = metrics.get("matched_candidates_count", 0)
            
            print(f"    Status: {status['status']['status']} | Generated: {generated} | Matched: {matched}")
            
            if not status["status"]["is_active"]:
                break
        
        # Step 4: Get results
        print("  → Fetching results...")
        response = requests.get(
            f"{BASE_URL}/runs/{findall_id}/result",
            headers=headers
        )
        response.raise_for_status()
        results = response.json()
        
        # Parse results
        found_profiles = []
        for candidate in results.get("candidates", []):
            output = candidate.get("output", {})
            found_profiles.append({
                "name": candidate.get("name", ""),
                "url": candidate.get("url", ""),
                "description": candidate.get("description", ""),
                "linkedin_url": output.get("linkedin_url", ""),
                "twitter_handle": output.get("twitter_handle", ""),
                "current_company": output.get("current_company", ""),
                "current_role": output.get("current_role", ""),
            })
        
        return found_profiles
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error: {e}")
        if hasattr(e, 'response'):
            print(f"   Response: {e.response.text}")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def search_individual_speaker(name: str, company: str, role: str = "") -> Dict:
    """Search for a single speaker's LinkedIn profile."""
    
    if not PARALLEL_API_KEY:
        return {"name": name, "company": company, "linkedin_url": "", "error": "No API key"}
    
    headers = {
        "x-api-key": PARALLEL_API_KEY,
        "parallel-beta": BETA_HEADER,
        "Content-Type": "application/json"
    }
    
    # More specific query for individual person
    role_str = f", {role}" if role else ""
    query = f"FindAll people named {name} who work at {company}{role_str}"
    
    try:
        # Ingest
        response = requests.post(
            f"{BASE_URL}/ingest",
            headers=headers,
            json={"objective": query}
        )
        response.raise_for_status()
        schema = response.json()
        
        # Create run
        payload = {
            "objective": schema["objective"],
            "entity_type": "people",
            "match_conditions": [
                {"name": "name_match", "description": f"Person's name is {name} or very similar"},
                {"name": "company_match", "description": f"Person works at or has worked at {company}"}
            ],
            "generator": "base",
            "match_limit": 3,
            "enrichments": [
                {"name": "linkedin_url", "description": "LinkedIn profile URL"},
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/runs",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        findall_id = response.json()["findall_id"]
        
        # Wait for completion
        for _ in range(30):
            time.sleep(3)
            response = requests.get(
                f"{BASE_URL}/runs/{findall_id}",
                headers=headers
            )
            response.raise_for_status()
            status = response.json()
            if not status["status"]["is_active"]:
                break
        
        # Get results
        response = requests.get(
            f"{BASE_URL}/runs/{findall_id}/result",
            headers=headers
        )
        response.raise_for_status()
        results = response.json()
        
        candidates = results.get("candidates", [])
        if candidates:
            best = candidates[0]
            return {
                "name": name,
                "company": company,
                "linkedin_url": best.get("output", {}).get("linkedin_url", ""),
                "found_name": best.get("name", ""),
                "found_url": best.get("url", ""),
            }
        
        return {"name": name, "company": company, "linkedin_url": "", "status": "not_found"}
        
    except Exception as e:
        return {"name": name, "company": company, "linkedin_url": "", "error": str(e)}


def main():
    """Main function."""
    print("=" * 70)
    print("Parallel API - LinkedIn Profile Search for AI Engineer Speakers")
    print("=" * 70)
    
    # Load speakers
    speakers = load_speakers_without_linkedin()
    print(f"\n📋 Found {len(speakers)} speakers without LinkedIn profiles\n")
    
    if not speakers:
        print("✓ All speakers already have LinkedIn profiles!")
        return
    
    # Show first few speakers
    print("First 10 speakers to search:")
    for i, s in enumerate(speakers[:10], 1):
        print(f"  {i}. {s['name']} ({s['company']})")
    
    print("\n" + "-" * 70)
    
    # Option 1: Batch search (faster, less precise)
    print("\n🔍 Running batch search...")
    batch_results = search_linkedin_batch(speakers, batch_size=20)
    
    if batch_results:
        print(f"\n✓ Found {len(batch_results)} profiles in batch search")
        
        # Save batch results
        with open("parallel_linkedin_batch_results.json", 'w') as f:
            json.dump(batch_results, f, indent=2)
        print("  Saved to parallel_linkedin_batch_results.json")
        
        # Show results
        print("\nBatch Results:")
        for r in batch_results[:10]:
            linkedin = r.get('linkedin_url', 'Not found')
            print(f"  • {r['name']}: {linkedin if linkedin else 'Not found'}")
    
    # Option 2: Individual search (slower, more precise)
    # Uncomment to run individual searches
    """
    print("\n🔍 Running individual searches...")
    individual_results = []
    
    for i, speaker in enumerate(speakers[:5], 1):  # Limit for testing
        print(f"\n[{i}/5] Searching for {speaker['name']}...")
        result = search_individual_speaker(
            speaker['name'],
            speaker['company'],
            speaker.get('role', '')
        )
        individual_results.append(result)
        
        if result.get('linkedin_url'):
            print(f"  ✓ Found: {result['linkedin_url']}")
        else:
            print(f"  ✗ Not found")
        
        time.sleep(2)  # Rate limiting
    
    # Save individual results
    with open("parallel_linkedin_individual_results.json", 'w') as f:
        json.dump(individual_results, f, indent=2)
    """
    
    print("\n" + "=" * 70)
    print("Done!")


if __name__ == "__main__":
    main()

