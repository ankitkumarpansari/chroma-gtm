"""
Parallel API - Full LinkedIn Profile Search for AI Engineer Speakers

Searches for LinkedIn profiles in batches using the Parallel FindAll API.
"""

import os
import json
import csv
import time
import requests
from dotenv import load_dotenv

load_dotenv()

PARALLEL_API_KEY = os.getenv('PARALLEL_API_KEY')
BASE_URL = 'https://api.parallel.ai/v1beta/findall'
BETA_HEADER = 'findall-2025-09-15'

headers = {
    'x-api-key': PARALLEL_API_KEY,
    'parallel-beta': BETA_HEADER,
    'Content-Type': 'application/json'
}


def load_speakers_without_linkedin():
    """Load speakers without LinkedIn profiles."""
    speakers = []
    with open('ai_engineer_speakers_linkedin.csv', 'r') as f:
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


def search_batch(speakers_batch, batch_num):
    """Search for a batch of speakers."""
    
    # Build speaker list string
    speaker_list = ", ".join([f"{s['name']} from {s['company']}" for s in speakers_batch])
    
    payload = {
        'objective': f'Find LinkedIn profiles of these AI/tech professionals: {speaker_list}',
        'entity_type': 'linkedin_profiles',
        'match_conditions': [
            {'name': 'tech_professional', 'description': 'Person works in AI, ML, software engineering, or related tech fields'},
        ],
        'generator': 'core',
        'match_limit': len(speakers_batch) + 5,  # Allow some extra
        'enrichments': [
            {'name': 'full_name', 'description': 'Full name of the person'},
            {'name': 'company', 'description': 'Current company'},
            {'name': 'title', 'description': 'Job title'}
        ]
    }
    
    try:
        print(f"\n{'='*60}")
        print(f"Batch {batch_num}: Searching for {len(speakers_batch)} speakers")
        print(f"{'='*60}")
        
        r = requests.post(f'{BASE_URL}/runs', headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        findall_id = r.json()['findall_id']
        print(f"Run ID: {findall_id}")
        
        # Wait for completion
        for i in range(40):  # Max ~3.5 minutes
            time.sleep(5)
            r = requests.get(f'{BASE_URL}/runs/{findall_id}', headers=headers, timeout=30)
            status = r.json()
            metrics = status.get('status', {}).get('metrics', {})
            gen = metrics.get('generated_candidates_count', 0)
            matched = metrics.get('matched_candidates_count', 0)
            state = status['status']['status']
            print(f"  [{i*5:3d}s] {state} | Generated: {gen} | Matched: {matched}")
            
            if not status['status']['is_active']:
                break
        
        # Get results
        r = requests.get(f'{BASE_URL}/runs/{findall_id}/result', headers=headers, timeout=30)
        result = r.json()
        
        candidates = result.get('candidates', [])
        print(f"\nFound {len(candidates)} profiles:")
        
        found_profiles = []
        for c in candidates:
            name = c.get('name', 'Unknown')
            url = c.get('url', '')
            
            # Check if URL is a LinkedIn profile
            if 'linkedin.com/in/' in url:
                found_profiles.append({
                    'name': name,
                    'linkedin_url': url,
                    'company': c.get('output', {}).get('company', ''),
                    'title': c.get('output', {}).get('title', '')
                })
                print(f"  ✓ {name}: {url}")
            else:
                print(f"  - {name}: {url} (not LinkedIn)")
        
        return found_profiles
        
    except Exception as e:
        print(f"Error in batch {batch_num}: {e}")
        return []


def update_csv_with_profiles(all_profiles):
    """Update CSV with found LinkedIn profiles."""
    
    # Create lookup by name (lowercase for matching)
    profile_lookup = {}
    for p in all_profiles:
        name_lower = p['name'].lower().strip()
        profile_lookup[name_lower] = p['linkedin_url']
    
    # Read and update CSV
    rows = []
    updated_count = 0
    
    with open('ai_engineer_speakers_linkedin.csv', 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        for row in reader:
            name_lower = row['Name'].lower().strip()
            current_linkedin = row.get('LinkedIn URL', '').strip()
            
            # Update if we found a profile and current is empty
            if name_lower in profile_lookup and not current_linkedin:
                row['LinkedIn URL'] = profile_lookup[name_lower]
                updated_count += 1
            
            rows.append(row)
    
    # Write updated CSV
    with open('ai_engineer_speakers_linkedin.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n✓ Updated {updated_count} profiles in CSV")


def main():
    print("=" * 70)
    print("Parallel API - Full LinkedIn Profile Search")
    print("=" * 70)
    
    # Load speakers
    speakers = load_speakers_without_linkedin()
    print(f"\nFound {len(speakers)} speakers without LinkedIn profiles")
    
    # Process in batches of 10 (API works better with smaller batches)
    batch_size = 10
    all_found_profiles = []
    
    for i in range(0, len(speakers), batch_size):
        batch = speakers[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(speakers) + batch_size - 1) // batch_size
        
        print(f"\n\n{'#'*70}")
        print(f"# BATCH {batch_num}/{total_batches}")
        print(f"{'#'*70}")
        
        profiles = search_batch(batch, batch_num)
        all_found_profiles.extend(profiles)
        
        # Save intermediate results
        with open('parallel_linkedin_progress.json', 'w') as f:
            json.dump(all_found_profiles, f, indent=2)
        
        # Delay between batches
        if i + batch_size < len(speakers):
            print("\nWaiting 5 seconds before next batch...")
            time.sleep(5)
    
    # Final results
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"Total profiles found: {len(all_found_profiles)}")
    
    # Save final results
    with open('parallel_linkedin_final.json', 'w') as f:
        json.dump(all_found_profiles, f, indent=2)
    print("Saved to parallel_linkedin_final.json")
    
    # Update CSV
    if all_found_profiles:
        update_csv_with_profiles(all_found_profiles)
    
    # Print summary
    print("\nFound LinkedIn profiles:")
    for p in all_found_profiles:
        print(f"  {p['name']}: {p['linkedin_url']}")


if __name__ == "__main__":
    main()

