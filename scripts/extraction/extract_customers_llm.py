#!/usr/bin/env python3
"""
Advanced version using LLM API to extract Pinecone customers.
Supports OpenAI, Anthropic, or local LLM.
"""

import json
import subprocess
import os
from typing import List, Dict, Optional
from pathlib import Path
import time

# Try to import LLM libraries
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

def get_video_metadata(video_url: str) -> Optional[Dict]:
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
                    'description': parts[1] or '',
                    'url': video_url
                }
    except Exception as e:
        print(f"Error getting metadata for {video_url}: {e}")
    
    return None

def extract_customers_openai(text: str, video_title: str, api_key: str) -> List[str]:
    """Extract customers using OpenAI API."""
    if not HAS_OPENAI:
        return []
    
    client = OpenAI(api_key=api_key)
    
    prompt = f"""Analyze this YouTube video to identify companies that are mentioned as Pinecone customers, users, or partners.

Video Title: {video_title}

Video Description:
{text[:3000]}

Instructions:
1. Identify all company names that are explicitly mentioned as:
   - Using Pinecone
   - Being customers of Pinecone
   - Partners with Pinecone
   - Built with Pinecone
   - Using Pinecone's services

2. Return ONLY a JSON array of company names, like: ["Company1", "Company2"]
3. Do NOT include Pinecone itself
4. Do NOT include generic terms like "users" or "customers"
5. Use the exact company name as mentioned in the text

JSON array:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or gpt-4, gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts company names from text. Always return valid JSON arrays."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        # Try to parse JSON
        if content.startswith('['):
            companies = json.loads(content)
            return [c.strip() for c in companies if isinstance(c, str) and len(c) > 2]
        else:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'\[.*?\]', content, re.DOTALL)
            if json_match:
                companies = json.loads(json_match.group())
                return [c.strip() for c in companies if isinstance(c, str) and len(c) > 2]
    except Exception as e:
        print(f"  ⚠️  OpenAI API error: {e}")
    
    return []

def extract_customers_anthropic(text: str, video_title: str, api_key: str) -> List[str]:
    """Extract customers using Anthropic Claude API."""
    if not HAS_ANTHROPIC:
        return []
    
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = f"""Analyze this YouTube video to identify companies that are mentioned as Pinecone customers, users, or partners.

Video Title: {video_title}

Video Description:
{text[:3000]}

Identify all company names that are explicitly mentioned as:
- Using Pinecone
- Being customers of Pinecone
- Partners with Pinecone
- Built with Pinecone

Return ONLY a JSON array of company names, like: ["Company1", "Company2"]
Do NOT include Pinecone itself or generic terms."""

    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",  # or claude-3-opus, claude-3-haiku
            max_tokens=500,
            temperature=0.1,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        content = message.content[0].text.strip()
        # Try to parse JSON
        if content.startswith('['):
            companies = json.loads(content)
            return [c.strip() for c in companies if isinstance(c, str) and len(c) > 2]
        else:
            import re
            json_match = re.search(r'\[.*?\]', content, re.DOTALL)
            if json_match:
                companies = json.loads(json_match.group())
                return [c.strip() for c in companies if isinstance(c, str) and len(c) > 2]
    except Exception as e:
        print(f"  ⚠️  Anthropic API error: {e}")
    
    return []

def extract_customers_pattern(text: str, video_title: str) -> List[str]:
    """Fallback: Pattern-based extraction."""
    import re
    companies = set()
    full_text = f"{video_title}\n{text}".lower()
    
    # Look for explicit customer mentions
    patterns = [
        r'(?:customer|client|partner|using|with|from|at)\s+([A-Z][a-zA-Z0-9\s&]+(?:Inc|LLC|Ltd|Corp|Corporation|Technologies|AI|Systems|Software|Solutions)?)',
        r'@([a-zA-Z0-9_-]+)',  # @mentions
        r'([A-Z][a-zA-Z0-9\s&]+)\s+(?:is|are|uses|using|built|developed|created)\s+(?:with|using|on)\s+pinecone',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0] if match else ''
            match = match.strip()
            if (len(match) > 2 and 
                match.lower() not in ['pinecone', 'youtube', 'the', 'this', 'that']):
                companies.add(match)
    
    return list(companies)[:10]

def process_videos_llm(video_urls: List[str], 
                      provider: str = 'openai',
                      api_key: Optional[str] = None,
                      batch_size: int = 10) -> Dict:
    """Process videos using LLM to extract customers."""
    
    # Get API key
    if not api_key:
        if provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
        elif provider == 'anthropic':
            api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key and provider != 'pattern':
        print(f"⚠️  No API key found for {provider}. Using pattern-based extraction.")
        provider = 'pattern'
    
    results = {
        'total_videos': len(video_urls),
        'processed': 0,
        'provider': provider,
        'customers': {},
        'videos': []
    }
    
    print(f"Processing {len(video_urls)} videos using {provider}...")
    
    for i, url in enumerate(video_urls, 1):
        print(f"[{i}/{len(video_urls)}] Processing {url}...")
        
        metadata = get_video_metadata(url)
        if not metadata:
            print(f"  ⚠️  Failed to get metadata")
            continue
        
        # Extract customers based on provider
        if provider == 'openai' and api_key:
            customers = extract_customers_openai(
                metadata['description'], 
                metadata['title'], 
                api_key
            )
        elif provider == 'anthropic' and api_key:
            customers = extract_customers_anthropic(
                metadata['description'], 
                metadata['title'], 
                api_key
            )
        else:
            customers = extract_customers_pattern(
                metadata['description'], 
                metadata['title']
            )
        
        # Store results
        video_result = {
            'video_id': metadata['video_id'],
            'url': url,
            'title': metadata['title'],
            'customers_mentioned': customers
        }
        results['videos'].append(video_result)
        
        # Track customers
        for customer in customers:
            if customer not in results['customers']:
                results['customers'][customer] = []
            results['customers'][customer].append({
                'video_id': metadata['video_id'],
                'title': metadata['title'],
                'url': url
            })
        
        results['processed'] += 1
        
        # Rate limiting
        if i % batch_size == 0:
            print(f"  ⏸️  Pausing... ({i} videos processed)")
            time.sleep(1)
    
    return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract Pinecone customers from YouTube videos')
    parser.add_argument('--provider', choices=['openai', 'anthropic', 'pattern'], 
                       default='pattern', help='LLM provider to use')
    parser.add_argument('--api-key', help='API key (or set OPENAI_API_KEY/ANTHROPIC_API_KEY env var)')
    parser.add_argument('--batch-size', type=int, default=10, help='Batch size for processing')
    parser.add_argument('--limit', type=int, help='Limit number of videos to process (for testing)')
    
    args = parser.parse_args()
    
    # Load video URLs
    urls_file = Path('pinecone_ALL_video_urls_MASTER.txt')
    if not urls_file.exists():
        print(f"Error: {urls_file} not found!")
        return
    
    with open(urls_file, 'r') as f:
        video_urls = [line.strip() for line in f if line.strip()]
    
    if args.limit:
        video_urls = video_urls[:args.limit]
        print(f"⚠️  Limited to {args.limit} videos for testing")
    
    print(f"Loaded {len(video_urls)} video URLs")
    
    # Process videos
    results = process_videos_llm(
        video_urls, 
        provider=args.provider,
        api_key=args.api_key,
        batch_size=args.batch_size
    )
    
    # Save results
    output_file = Path('pinecone_customers_llm.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Create summary
    customer_counts = {k: len(v) for k, v in results['customers'].items()}
    summary = {
        'total_videos_processed': results['processed'],
        'total_unique_customers': len(results['customers']),
        'provider': results['provider'],
        'customers': customer_counts,
        'top_customers': sorted(
            results['customers'].items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:30]
    }
    
    summary_file = Path('pinecone_customers_summary_llm.json')
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Create CSV for easy viewing
    csv_file = Path('pinecone_customers.csv')
    with open(csv_file, 'w') as f:
        f.write('Customer,Video_Count,Videos\n')
        for customer, videos in sorted(
            results['customers'].items(),
            key=lambda x: len(x[1]),
            reverse=True
        ):
            video_ids = ','.join([v['video_id'] for v in videos])
            f.write(f'"{customer}",{len(videos)},"{video_ids}"\n')
    
    # Print summary
    print("\n" + "="*60)
    print("EXTRACTION COMPLETE")
    print("="*60)
    print(f"Provider: {results['provider']}")
    print(f"Videos processed: {results['processed']}/{len(video_urls)}")
    print(f"Unique customers found: {len(results['customers'])}")
    print(f"\nTop customers (by mention count):")
    for customer, videos in summary['top_customers'][:20]:
        print(f"  - {customer}: mentioned in {len(videos)} video(s)")
    print(f"\n📁 Results saved to:")
    print(f"   - {output_file}")
    print(f"   - {summary_file}")
    print(f"   - {csv_file}")

if __name__ == '__main__':
    main()
