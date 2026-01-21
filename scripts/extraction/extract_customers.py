#!/usr/bin/env python3
"""
Extract Pinecone customers from YouTube video descriptions and titles.
Processes all videos and identifies companies mentioned as customers.
"""

import json
import subprocess
import re
from typing import List, Dict, Set
from pathlib import Path
import time

def get_video_metadata(video_url: str) -> Dict:
    """Get video metadata using yt-dlp."""
    try:
        cmd = [
            'yt-dlp',
            '--skip-download',
            '--print', '%(title)s|||%(description)s|||%(id)s',
            video_url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout:
            parts = result.stdout.strip().split('|||')
            if len(parts) >= 3:
                return {
                    'video_id': parts[2],
                    'title': parts[0],
                    'description': parts[1],
                    'url': video_url
                }
    except Exception as e:
        print(f"Error getting metadata for {video_url}: {e}")
    
    return None

def extract_companies_from_text(text: str) -> List[str]:
    """
    Extract company names from text using pattern matching.
    Looks for common patterns indicating customers/companies.
    """
    companies = set()
    text_lower = text.lower()
    
    # Common patterns for customer mentions
    patterns = [
        r'(?:customer|client|partner|using|with|from|at)\s+([A-Z][a-zA-Z0-9\s&]+(?:Inc|LLC|Ltd|Corp|Corporation|Technologies|AI|Systems|Software|Solutions)?)',
        r'([A-Z][a-zA-Z0-9\s&]+(?:Inc|LLC|Ltd|Corp|Corporation|Technologies|AI|Systems|Software|Solutions)?)\s+(?:is|are|uses|using|built|developed)',
        r'@([a-zA-Z0-9_-]+)',  # @mentions (like @withdelphi)
        r'from\s+([A-Z][a-zA-Z0-9\s&]+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0] if match else ''
            match = match.strip()
            # Filter out common false positives
            if (len(match) > 2 and 
                match.lower() not in ['pinecone', 'youtube', 'the', 'this', 'that', 'with', 'from', 'and', 'or'] and
                not match.lower().startswith('http')):
                companies.add(match)
    
    return list(companies)

def identify_customers_with_llm(text: str, video_title: str) -> List[str]:
    """
    Use LLM to identify Pinecone customers mentioned in the text.
    This is a placeholder - you can integrate with OpenAI, Anthropic, or local LLM.
    """
    # For now, return pattern-based extraction
    # TODO: Replace with actual LLM API call
    prompt = f"""
    Analyze the following YouTube video title and description to identify companies that are mentioned as Pinecone customers, partners, or users.
    
    Title: {video_title}
    Description: {text[:2000]}  # Limit to first 2000 chars
    
    Return a JSON list of company names that are clearly mentioned as using Pinecone, being customers of Pinecone, or partners with Pinecone.
    Only include companies explicitly mentioned in the context.
    Format: ["Company1", "Company2", ...]
    """
    
    # Pattern-based extraction as fallback
    companies = extract_companies_from_text(text + " " + video_title)
    
    # Filter and clean
    cleaned = []
    for company in companies:
        company = company.strip()
        # Remove common prefixes/suffixes
        company = re.sub(r'^(the|a|an)\s+', '', company, flags=re.IGNORECASE)
        if len(company) > 2 and company not in cleaned:
            cleaned.append(company)
    
    return cleaned[:10]  # Limit to top 10

def process_videos(video_urls: List[str], batch_size: int = 10) -> Dict:
    """Process all videos and extract customer information."""
    results = {
        'total_videos': len(video_urls),
        'processed': 0,
        'customers': {},  # company -> [video_ids]
        'videos': []  # video_id -> {metadata, customers}
    }
    
    print(f"Processing {len(video_urls)} videos...")
    
    for i, url in enumerate(video_urls, 1):
        print(f"[{i}/{len(video_urls)}] Processing {url}...")
        
        metadata = get_video_metadata(url)
        if not metadata:
            print(f"  ⚠️  Failed to get metadata")
            continue
        
        # Extract customers
        full_text = f"{metadata['title']}\n{metadata['description']}"
        customers = identify_customers_with_llm(metadata['description'], metadata['title'])
        
        # Store results
        video_result = {
            'video_id': metadata['video_id'],
            'url': url,
            'title': metadata['title'],
            'customers_mentioned': customers
        }
        results['videos'].append(video_result)
        
        # Track customers across videos
        for customer in customers:
            if customer not in results['customers']:
                results['customers'][customer] = []
            results['customers'][customer].append(metadata['video_id'])
        
        results['processed'] += 1
        
        # Rate limiting
        if i % batch_size == 0:
            print(f"  ⏸️  Pausing... ({i} videos processed)")
            time.sleep(2)
    
    return results

def main():
    # Load video URLs
    urls_file = Path('pinecone_ALL_video_urls_MASTER.txt')
    if not urls_file.exists():
        print(f"Error: {urls_file} not found!")
        return
    
    with open(urls_file, 'r') as f:
        video_urls = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(video_urls)} video URLs")
    
    # Process videos
    results = process_videos(video_urls, batch_size=10)
    
    # Save results
    output_file = Path('pinecone_customers_extracted.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Create summary
    summary = {
        'total_videos_processed': results['processed'],
        'total_unique_customers': len(results['customers']),
        'customers': {k: len(v) for k, v in results['customers'].items()},
        'top_customers': sorted(
            results['customers'].items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:20]
    }
    
    summary_file = Path('pinecone_customers_summary.json')
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("EXTRACTION COMPLETE")
    print("="*60)
    print(f"Videos processed: {results['processed']}/{len(video_urls)}")
    print(f"Unique customers found: {len(results['customers'])}")
    print(f"\nTop customers (by mention count):")
    for customer, video_ids in summary['top_customers']:
        print(f"  - {customer}: mentioned in {len(video_ids)} video(s)")
    print(f"\n📁 Results saved to:")
    print(f"   - {output_file}")
    print(f"   - {summary_file}")

if __name__ == '__main__':
    main()
