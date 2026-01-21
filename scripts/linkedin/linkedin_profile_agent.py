#!/usr/bin/env python3
"""
AI Agent: LinkedIn Profile Finder & Enrichment
===============================================

Uses Parallel AI FindAll API to find and enrich LinkedIn profiles 
for AI Engineer speakers, then exports to Duxsoup-compatible format.

Usage:
    python linkedin_profile_agent.py

Author: AI Agent for Chroma GTM
"""

import os
import json
import csv
import time
import requests
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

# Parallel AI API Configuration
PARALLEL_API_KEY = "VaIzyXZ3KJdjd0MWKca7nA-Zv0vvUp30tjXUg2sW"
BASE_URL = "https://api.parallel.ai/v1beta/findall"
BETA_HEADER = "findall-2025-09-15"

# File paths
INPUT_FILE = "ai_engineer_speakers.json"
OUTPUT_CSV = "ai_engineer_speakers_linkedin.csv"
DUXSOUP_CSV = "duxsoup_ai_engineers.csv"
PROGRESS_FILE = "linkedin_enrichment_progress.json"
ENRICHED_JSON = "ai_engineer_speakers_enriched.json"

# Rate limiting
DELAY_BETWEEN_SEARCHES = 3  # seconds between individual searches
BATCH_DELAY = 5  # seconds between batches
MAX_SPEAKERS_TO_PROCESS = 200  # Safety limit


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Speaker:
    name: str
    company: str
    role: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter: Optional[str] = None
    video: Optional[str] = None
    email: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    search_status: str = "pending"
    
    @property
    def has_valid_linkedin(self) -> bool:
        return bool(self.linkedin_url and "linkedin.com/in" in self.linkedin_url.lower())
    
    @property
    def needs_search(self) -> bool:
        if self.has_valid_linkedin:
            return False
        return True
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "company": self.company,
            "role": self.role,
            "linkedin_url": self.linkedin_url,
            "twitter": self.twitter,
            "video": self.video,
            "email": self.email,
            "headline": self.headline,
            "location": self.location,
            "search_status": self.search_status
        }


# ============================================================================
# LOAD & SAVE FUNCTIONS
# ============================================================================

def load_speakers() -> List[Speaker]:
    """Load speakers from JSON and parse into Speaker objects."""
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)
    
    speakers = []
    for item in data:
        company = item.get("company", "")
        role = None
        
        # Parse role from company field
        if "," in company:
            parts = company.split(",", 1)
            company = parts[0].strip()
            role = parts[1].strip()
        elif any(title in company for title in [" CEO", " CTO", " CPO", " COO", " CRO"]):
            parts = company.rsplit(" ", 1)
            if len(parts) == 2:
                company = parts[0].strip()
                role = parts[1].strip()
        
        linkedin_url = item.get("linkedin")
        twitter = None
        
        # Check if linkedin field contains Twitter URL
        if linkedin_url and "twitter.com" in linkedin_url.lower():
            twitter = linkedin_url
            linkedin_url = None
        # Check for other non-LinkedIn URLs
        elif linkedin_url and "linkedin.com" not in linkedin_url.lower():
            twitter = linkedin_url  # Store as twitter/other
            linkedin_url = None
        
        speaker = Speaker(
            name=item.get("name", ""),
            company=company,
            role=role,
            linkedin_url=linkedin_url,
            twitter=twitter,
            video=item.get("video"),
            search_status="found" if linkedin_url and "linkedin.com" in (linkedin_url or "").lower() else "pending"
        )
        speakers.append(speaker)
    
    return speakers


def load_progress() -> Dict:
    """Load search progress from file."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"searched": {}, "last_updated": None, "stats": {"found": 0, "not_found": 0, "errors": 0}}


def save_progress(progress: Dict):
    """Save search progress to file."""
    progress["last_updated"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


def save_enriched_json(speakers: List[Speaker]):
    """Save enriched speaker data to JSON."""
    data = [s.to_dict() for s in speakers]
    with open(ENRICHED_JSON, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✓ Saved enriched data to {ENRICHED_JSON}")


# ============================================================================
# PARALLEL AI CLIENT
# ============================================================================

class ParallelAIClient:
    """Client for Parallel AI FindAll API."""
    
    def __init__(self, api_key: str = PARALLEL_API_KEY):
        self.api_key = api_key
        self.headers = {
            "x-api-key": api_key,
            "parallel-beta": BETA_HEADER,
            "Content-Type": "application/json"
        }
        self.base_url = BASE_URL
    
    def search_person(self, name: str, company: str, role: str = "") -> Dict[str, Any]:
        """
        Search for a person's LinkedIn profile using Parallel AI.
        
        Returns dict with:
            - linkedin_url: Found LinkedIn URL or None
            - headline: Professional headline
            - location: Location if found
            - status: 'found', 'not_found', or 'error'
            - error: Error message if any
        """
        role_str = f" who is {role}" if role else ""
        query = f"Find the LinkedIn profile for {name}{role_str} at {company}"
        
        try:
            # Step 1: Ingest query to get structured schema
            response = requests.post(
                f"{self.base_url}/ingest",
                headers=self.headers,
                json={"objective": query},
                timeout=30
            )
            response.raise_for_status()
            schema = response.json()
            
            # Step 2: Create search run with enrichments
            payload = {
                "objective": schema["objective"],
                "entity_type": "people",
                "match_conditions": [
                    {"name": "name_match", "description": f"Person's name is {name} or very similar"},
                    {"name": "company_match", "description": f"Person currently works at or recently worked at {company}"}
                ],
                "generator": "base",  # Fast mode for individual searches
                "match_limit": 1,
                "enrichments": [
                    {"name": "linkedin_url", "description": "LinkedIn profile URL in format linkedin.com/in/username"},
                    {"name": "headline", "description": "Professional headline or job title"},
                    {"name": "location", "description": "Geographic location (city, state/country)"}
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/runs",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            findall_id = response.json()["findall_id"]
            
            # Step 3: Poll for completion (max 90 seconds)
            for _ in range(18):
                time.sleep(5)
                response = requests.get(
                    f"{self.base_url}/runs/{findall_id}",
                    headers=self.headers,
                    timeout=30
                )
                response.raise_for_status()
                status = response.json()
                
                if not status["status"]["is_active"]:
                    break
            
            # Step 4: Get results
            response = requests.get(
                f"{self.base_url}/runs/{findall_id}/result",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            results = response.json()
            
            # Parse results
            candidates = results.get("candidates", [])
            if candidates:
                best = candidates[0]
                output = best.get("output", {})
                linkedin_url = output.get("linkedin_url", "")
                
                # Validate LinkedIn URL
                if linkedin_url and "linkedin.com/in" in linkedin_url.lower():
                    return {
                        "linkedin_url": linkedin_url,
                        "headline": output.get("headline", ""),
                        "location": output.get("location", ""),
                        "found_name": best.get("name", ""),
                        "status": "found"
                    }
            
            return {"linkedin_url": None, "status": "not_found"}
            
        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_msg = e.response.json().get('message', str(e))
                except:
                    error_msg = e.response.text[:200]
            return {"linkedin_url": None, "status": "error", "error": error_msg}
        except requests.exceptions.Timeout:
            return {"linkedin_url": None, "status": "error", "error": "Request timeout"}
        except Exception as e:
            return {"linkedin_url": None, "status": "error", "error": str(e)}
    
    def batch_search(self, speakers: List[Speaker], limit: int = 20) -> List[Dict]:
        """
        Search for multiple speakers in a batch query.
        More efficient but less precise than individual searches.
        """
        names_list = ", ".join([
            f"{s.name} ({s.company})" 
            for s in speakers[:limit]
        ])
        
        query = f"""FindAll people who are AI/ML engineers, founders, or technical leaders.
        Specifically looking for these individuals: {names_list}.
        These are speakers at AI Engineer conferences and summits."""
        
        try:
            # Ingest
            response = requests.post(
                f"{self.base_url}/ingest",
                headers=self.headers,
                json={"objective": query},
                timeout=30
            )
            response.raise_for_status()
            schema = response.json()
            
            # Create run
            payload = {
                "objective": schema["objective"],
                "entity_type": "people",
                "match_conditions": schema.get("match_conditions", []),
                "generator": "core",  # Better quality for batch
                "match_limit": limit,
                "enrichments": [
                    {"name": "linkedin_url", "description": "LinkedIn profile URL"},
                    {"name": "current_company", "description": "Current company name"},
                    {"name": "current_title", "description": "Current job title"},
                    {"name": "location", "description": "Geographic location"}
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/runs",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            findall_id = response.json()["findall_id"]
            
            print(f"    Batch search started (ID: {findall_id})")
            
            # Wait for completion (up to 5 minutes for batch)
            for attempt in range(60):
                time.sleep(5)
                response = requests.get(
                    f"{self.base_url}/runs/{findall_id}",
                    headers=self.headers,
                    timeout=30
                )
                response.raise_for_status()
                status = response.json()
                
                metrics = status.get("status", {}).get("metrics", {})
                if attempt % 6 == 0:  # Print every 30 seconds
                    print(f"    Progress: Generated {metrics.get('generated_candidates_count', 0)}, Matched {metrics.get('matched_candidates_count', 0)}")
                
                if not status["status"]["is_active"]:
                    break
            
            # Get results
            response = requests.get(
                f"{self.base_url}/runs/{findall_id}/result",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            results = response.json()
            
            return results.get("candidates", [])
            
        except Exception as e:
            print(f"    Batch search error: {e}")
            return []


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_to_csv(speakers: List[Speaker], filename: str):
    """Export all speakers to CSV with all enriched data."""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'Name', 'Company', 'Role', 'LinkedIn URL', 'Twitter', 
            'Headline', 'Location', 'Video', 'Search Status'
        ])
        writer.writeheader()
        
        for s in speakers:
            writer.writerow({
                'Name': s.name,
                'Company': s.company,
                'Role': s.role or '',
                'LinkedIn URL': s.linkedin_url or '',
                'Twitter': s.twitter or '',
                'Headline': s.headline or '',
                'Location': s.location or '',
                'Video': s.video or '',
                'Search Status': s.search_status
            })
    
    print(f"✓ Exported {len(speakers)} speakers to {filename}")


def export_for_duxsoup(speakers: List[Speaker], filename: str):
    """Export speakers with LinkedIn URLs to Duxsoup-compatible CSV."""
    linkedin_speakers = [s for s in speakers if s.has_valid_linkedin]
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'LinkedIn URL', 'First Name', 'Last Name', 'Company', 
            'Title', 'Notes', 'Tags'
        ])
        writer.writeheader()
        
        for s in linkedin_speakers:
            name_parts = s.name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            notes = f"AI Engineer Summit speaker"
            if s.video:
                notes += f" | Talk: {s.video}"
            if s.headline:
                notes += f" | {s.headline}"
            
            writer.writerow({
                'LinkedIn URL': s.linkedin_url,
                'First Name': first_name,
                'Last Name': last_name,
                'Company': s.company,
                'Title': s.role or s.headline or '',
                'Notes': notes[:500],  # Duxsoup has character limits
                'Tags': 'ai_engineer_speaker,high_priority,conference_speaker'
            })
    
    print(f"✓ Exported {len(linkedin_speakers)} speakers with LinkedIn to {filename}")
    return len(linkedin_speakers)


# ============================================================================
# MAIN AGENT
# ============================================================================

def main():
    print("=" * 70)
    print("🤖 LinkedIn Profile Enrichment Agent")
    print("   Powered by Parallel AI FindAll API")
    print("=" * 70)
    
    # Step 1: Load speakers
    print("\n📂 Loading speakers from JSON...")
    speakers = load_speakers()
    print(f"   Total speakers loaded: {len(speakers)}")
    
    # Categorize speakers
    has_linkedin = [s for s in speakers if s.has_valid_linkedin]
    needs_search = [s for s in speakers if s.needs_search]
    has_twitter = [s for s in speakers if s.twitter]
    
    print(f"\n📊 Current Status:")
    print(f"   ✅ Already have LinkedIn: {len(has_linkedin)}")
    print(f"   🔍 Need to search: {len(needs_search)}")
    print(f"   🐦 Have Twitter/other URL: {len(has_twitter)}")
    
    # Step 2: Load previous progress
    progress = load_progress()
    already_searched = set(progress.get("searched", {}).keys())
    
    # Apply previously found results
    for speaker in speakers:
        if speaker.name in progress.get("searched", {}):
            result = progress["searched"][speaker.name].get("result", {})
            if result.get("linkedin_url") and not speaker.has_valid_linkedin:
                speaker.linkedin_url = result["linkedin_url"]
                speaker.headline = result.get("headline", "")
                speaker.location = result.get("location", "")
                speaker.search_status = "found"
    
    # Recalculate after applying progress
    has_linkedin = [s for s in speakers if s.has_valid_linkedin]
    needs_search = [s for s in speakers if s.needs_search and s.name not in already_searched]
    
    print(f"\n📈 After applying previous progress:")
    print(f"   ✅ Have LinkedIn: {len(has_linkedin)}")
    print(f"   🔍 Still need to search: {len(needs_search)}")
    print(f"   📝 Previously searched: {len(already_searched)}")
    
    # Step 3: Initialize Parallel AI client
    print(f"\n🔑 Initializing Parallel AI client...")
    client = ParallelAIClient()
    
    # Step 4: Search for missing LinkedIn profiles
    if needs_search:
        print(f"\n🔍 Starting LinkedIn profile search...")
        print(f"   Speakers to search: {len(needs_search)}")
        print(f"   Estimated time: {len(needs_search) * 30 // 60} - {len(needs_search) * 60 // 60} minutes")
        print("-" * 70)
        
        found_count = 0
        error_count = 0
        
        # Process speakers one by one for accuracy
        for i, speaker in enumerate(needs_search[:MAX_SPEAKERS_TO_PROCESS], 1):
            print(f"\n[{i}/{min(len(needs_search), MAX_SPEAKERS_TO_PROCESS)}] 🔎 {speaker.name} ({speaker.company})")
            
            result = client.search_person(
                speaker.name,
                speaker.company,
                speaker.role or ""
            )
            
            if result.get("linkedin_url"):
                speaker.linkedin_url = result["linkedin_url"]
                speaker.headline = result.get("headline", "")
                speaker.location = result.get("location", "")
                speaker.search_status = "found"
                found_count += 1
                print(f"   ✅ Found: {result['linkedin_url']}")
                if result.get("headline"):
                    print(f"      Headline: {result['headline']}")
            elif result.get("status") == "error":
                speaker.search_status = "error"
                error_count += 1
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
            else:
                speaker.search_status = "not_found"
                print(f"   ⚠️ Not found")
            
            # Save progress after each search
            progress["searched"][speaker.name] = {
                "company": speaker.company,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            progress["stats"]["found"] = found_count
            progress["stats"]["not_found"] = i - found_count - error_count
            progress["stats"]["errors"] = error_count
            save_progress(progress)
            
            # Rate limiting
            if i < len(needs_search):
                time.sleep(DELAY_BETWEEN_SEARCHES)
        
        print(f"\n{'=' * 70}")
        print(f"🎉 Search Complete!")
        print(f"   Found: {found_count}")
        print(f"   Not found: {len(needs_search[:MAX_SPEAKERS_TO_PROCESS]) - found_count - error_count}")
        print(f"   Errors: {error_count}")
    else:
        print("\n✓ All speakers have been searched!")
    
    # Step 5: Export results
    print(f"\n📁 Exporting results...")
    
    # Export full CSV
    export_to_csv(speakers, OUTPUT_CSV)
    
    # Export Duxsoup-ready CSV
    duxsoup_count = export_for_duxsoup(speakers, DUXSOUP_CSV)
    
    # Export enriched JSON
    save_enriched_json(speakers)
    
    # Final summary
    final_linkedin = [s for s in speakers if s.has_valid_linkedin]
    
    print(f"\n{'=' * 70}")
    print(f"📊 FINAL SUMMARY")
    print(f"{'=' * 70}")
    print(f"   Total speakers: {len(speakers)}")
    print(f"   With LinkedIn URLs: {len(final_linkedin)}")
    print(f"   Ready for Duxsoup: {duxsoup_count}")
    print(f"\n📁 Files created:")
    print(f"   • {OUTPUT_CSV} - All speakers with enrichment data")
    print(f"   • {DUXSOUP_CSV} - Duxsoup-ready format ({duxsoup_count} profiles)")
    print(f"   • {ENRICHED_JSON} - Full enriched JSON data")
    print(f"   • {PROGRESS_FILE} - Search progress (can resume)")
    print(f"\n🚀 Next steps:")
    print(f"   1. Import {DUXSOUP_CSV} into Duxsoup")
    print(f"   2. Create warm-up campaign (profile visits)")
    print(f"   3. Create connection request campaign")
    print(f"   4. Set up nurture sequence")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()

