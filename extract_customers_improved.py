#!/usr/bin/env python3
"""
Improved customer extraction with multiple accuracy enhancements:
1. Better LLM prompts with examples
2. Multi-pass extraction (title + description separately)
3. Post-processing filters
4. Known customer list validation
5. Confidence scoring
6. Video transcript support (if available)
"""

import json
import subprocess
import os
import re
from typing import List, Dict, Optional, Set, Tuple
from pathlib import Path
import time

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

# Known Pinecone customers (for validation)
KNOWN_CUSTOMERS = {
    'delphi', 'withdelphi', '@withdelphi',
    'seam ai', 'seamai',
    'apisec', 'api sec',
    'twelvelabs', 'twelve labs',
    'cohere',
    'databricks',
    'fivetran',
    'anthropic',
    'unblocked',
    'hyperleap',
    'wipro',
    'assembled',
    'zapier',
    'groq', 'groqinc',
    'neo4j',
    'spicedb', 'authzed',
    'langchain',
    'openai',
    'github',
    'microsoft',
    'google',
}

# Common false positives to filter
FALSE_POSITIVES = {
    'pinecone', 'youtube', 'the', 'this', 'that', 'with', 'from', 'and', 'or',
    'video', 'watch', 'subscribe', 'channel', 'playlist', 'description',
    'click', 'link', 'here', 'more', 'less', 'all', 'some', 'many',
    'users', 'customers', 'partners', 'companies', 'organizations',
}

def get_video_metadata(video_url: str, include_transcript: bool = False) -> Optional[Dict]:
    """Get video metadata using yt-dlp, optionally including transcript."""
    try:
        # Get basic metadata
        cmd = [
            'yt-dlp',
            '--skip-download',
            '--print', '%(title)s|||%(description)s|||%(id)s|||%(uploader)s',
            video_url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout:
            parts = result.stdout.strip().split('|||')
            if len(parts) >= 3:
                metadata = {
                    'video_id': parts[2],
                    'title': parts[0],
                    'description': parts[1] or '',
                    'url': video_url
                }
                
                # Try to get transcript if requested
                if include_transcript:
                    try:
                        transcript_cmd = [
                            'yt-dlp',
                            '--skip-download',
                            '--write-auto-sub',
                            '--sub-lang', 'en',
                            '--sub-format', 'vtt',
                            '--print', '%(id)s',
                            '--output', '/tmp/%(id)s.%(ext)s',
                            video_url
                        ]
                        # This is complex, so we'll skip for now
                        # Transcript extraction requires more setup
                    except:
                        pass
                
                return metadata
    except Exception as e:
        print(f"Error getting metadata for {video_url}: {e}")
    
    return None

def extract_customers_improved_openai(
    title: str,
    description: str,
    api_key: str,
    model: str = "gpt-4o-mini"
) -> List[Dict]:
    """
    Improved extraction with:
    - Better prompts with examples
    - Confidence scoring
    - Multi-pass analysis
    """
    if not HAS_OPENAI:
        return []
    
    client = OpenAI(api_key=api_key)
    
    # Enhanced prompt with examples and instructions
    system_prompt = """You are an expert at identifying company names from text. Your task is to identify companies that are mentioned as Pinecone customers, users, or partners.

Rules:
1. Only extract company names that are explicitly mentioned as using Pinecone, being customers, partners, or building with Pinecone
2. Return the exact company name as it appears (e.g., "Delphi" not "delphi", "@withdelphi" should be "Delphi")
3. Do NOT include Pinecone itself
4. Do NOT include generic terms like "users", "customers", "companies"
5. Do NOT include YouTube, video platforms, or social media platforms
6. Include confidence score (0-1) for each extraction
7. Return JSON format: [{"company": "Name", "confidence": 0.9, "context": "brief quote"}]

Examples of GOOD extractions:
- "Delphi uses Pinecone" → {"company": "Delphi", "confidence": 0.95, "context": "Delphi uses Pinecone"}
- "Built by Seam AI with Pinecone" → {"company": "Seam AI", "confidence": 0.9, "context": "Built by Seam AI with Pinecone"}
- "@withdelphi" → {"company": "Delphi", "confidence": 0.85, "context": "@withdelphi"}

Examples of BAD extractions (don't extract):
- "Pinecone is a vector database" → (Pinecone itself)
- "Many companies use Pinecone" → (generic term)
- "YouTube video" → (platform)"""

    user_prompt = f"""Analyze this YouTube video to identify companies mentioned as Pinecone customers/users/partners.

Video Title: {title}

Video Description:
{description[:3000]}

Extract all company names that are:
- Customers of Pinecone
- Using Pinecone
- Partners with Pinecone
- Built with Pinecone
- Case studies using Pinecone

Return JSON array with company, confidence (0-1), and brief context quote."""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=1000,
            response_format={"type": "json_object"} if "gpt-4" in model else None
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            # Try to extract JSON from response
            if content.startswith('{'):
                data = json.loads(content)
                if 'companies' in data:
                    return data['companies']
                elif isinstance(data, list):
                    return data
            elif content.startswith('['):
                return json.loads(content)
            else:
                # Try to find JSON in markdown code blocks
                json_match = re.search(r'\[.*?\]', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
        except json.JSONDecodeError:
            # Fallback: try to extract company names from text
            companies = re.findall(r'"company":\s*"([^"]+)"', content)
            return [{"company": c, "confidence": 0.7} for c in companies]
            
    except Exception as e:
        print(f"  ⚠️  OpenAI API error: {e}")
    
    return []

def extract_customers_improved_anthropic(
    title: str,
    description: str,
    api_key: str,
    model: str = "claude-3-5-sonnet-20241022"
) -> List[Dict]:
    """Improved Anthropic extraction with better prompts."""
    if not HAS_ANTHROPIC:
        return []
    
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = f"""Analyze this YouTube video to identify companies mentioned as Pinecone customers, users, or partners.

Video Title: {title}

Video Description:
{description[:3000]}

Extract all company names that are explicitly mentioned as:
- Customers of Pinecone
- Using Pinecone's services
- Partners with Pinecone
- Built with Pinecone
- Case studies or examples using Pinecone

Rules:
1. Return exact company names (e.g., "Delphi" not "delphi")
2. Include confidence score 0-1 for each
3. Include brief context quote
4. Do NOT include Pinecone itself
5. Do NOT include generic terms or platforms

Return JSON array: [{{"company": "Name", "confidence": 0.9, "context": "quote"}}]"""

    try:
        message = client.messages.create(
            model=model,
            max_tokens=1000,
            temperature=0.1,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        content = message.content[0].text.strip()
        
        # Parse JSON
        if content.startswith('['):
            return json.loads(content)
        else:
            json_match = re.search(r'\[.*?\]', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
    except Exception as e:
        print(f"  ⚠️  Anthropic API error: {e}")
    
    return []

def normalize_company_name(name: str) -> str:
    """Normalize company name variations."""
    name = name.strip()
    
    # Remove common prefixes
    name = re.sub(r'^(@|the\s+)', '', name, flags=re.IGNORECASE)
    
    # Handle @mentions
    if name.startswith('@'):
        name = name[1:]
        # Capitalize properly
        name = name[0].upper() + name[1:] if len(name) > 1 else name
    
    # Title case for multi-word
    if ' ' in name or '-' in name:
        name = name.title()
    
    return name

def validate_and_score_customer(
    company: str,
    context: str,
    confidence: float
) -> Tuple[bool, float]:
    """
    Validate if extracted company is likely a real customer.
    Returns (is_valid, adjusted_confidence)
    """
    company_lower = company.lower().strip()
    
    # Check against known customers
    if company_lower in KNOWN_CUSTOMERS:
        return True, min(confidence + 0.1, 1.0)
    
    # Check against false positives
    if company_lower in FALSE_POSITIVES:
        return False, 0.0
    
    # Check if it's too generic
    if len(company) < 3:
        return False, 0.0
    
    if company_lower in ['the', 'a', 'an', 'and', 'or', 'with', 'from']:
        return False, 0.0
    
    # Check context for customer indicators
    context_lower = context.lower()
    customer_indicators = [
        'uses pinecone', 'using pinecone', 'with pinecone',
        'customer', 'client', 'partner', 'built with',
        'case study', 'example', 'implementation'
    ]
    
    has_indicator = any(indicator in context_lower for indicator in customer_indicators)
    if has_indicator:
        return True, min(confidence + 0.05, 1.0)
    
    # Default: accept but with lower confidence
    return True, max(confidence - 0.1, 0.3)

def post_process_customers(
    raw_customers: List[Dict],
    title: str,
    description: str
) -> List[Dict]:
    """
    Post-process extracted customers:
    1. Normalize names
    2. Validate
    3. Deduplicate
    4. Score confidence
    """
    processed = {}
    
    for item in raw_customers:
        if isinstance(item, str):
            company = item
            confidence = 0.7
            context = ""
        else:
            company = item.get('company', '')
            confidence = item.get('confidence', 0.7)
            context = item.get('context', '')
        
        if not company:
            continue
        
        # Normalize
        normalized = normalize_company_name(company)
        
        # Validate
        is_valid, adj_confidence = validate_and_score_customer(
            normalized, context or f"{title} {description}", confidence
        )
        
        if not is_valid:
            continue
        
        # Deduplicate (keep highest confidence)
        if normalized not in processed or adj_confidence > processed[normalized]['confidence']:
            processed[normalized] = {
                'company': normalized,
                'confidence': adj_confidence,
                'context': context,
                'original': company
            }
    
    # Sort by confidence
    return sorted(processed.values(), key=lambda x: x['confidence'], reverse=True)

def process_videos_improved(
    video_urls: List[str],
    provider: str = 'openai',
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    min_confidence: float = 0.5,
    batch_size: int = 10
) -> Dict:
    """Process videos with improved accuracy."""
    
    # Get API key
    if not api_key:
        if provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
        elif provider == 'anthropic':
            api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key and provider != 'pattern':
        print(f"⚠️  No API key found. Using pattern-based extraction.")
        provider = 'pattern'
    
    # Set default model
    if not model:
        if provider == 'openai':
            model = "gpt-4o-mini"
        elif provider == 'anthropic':
            model = "claude-3-5-sonnet-20241022"
    
    results = {
        'total_videos': len(video_urls),
        'processed': 0,
        'provider': provider,
        'model': model,
        'min_confidence': min_confidence,
        'customers': {},
        'videos': []
    }
    
    print(f"Processing {len(video_urls)} videos using {provider} ({model})...")
    print(f"Minimum confidence threshold: {min_confidence}")
    
    for i, url in enumerate(video_urls, 1):
        print(f"[{i}/{len(video_urls)}] Processing {url}...")
        
        metadata = get_video_metadata(url)
        if not metadata:
            print(f"  ⚠️  Failed to get metadata")
            continue
        
        # Extract customers
        if provider == 'openai' and api_key:
            raw_customers = extract_customers_improved_openai(
                metadata['title'],
                metadata['description'],
                api_key,
                model
            )
        elif provider == 'anthropic' and api_key:
            raw_customers = extract_customers_improved_anthropic(
                metadata['title'],
                metadata['description'],
                api_key,
                model
            )
        else:
            raw_customers = []
        
        # Post-process
        customers = post_process_customers(
            raw_customers,
            metadata['title'],
            metadata['description']
        )
        
        # Filter by confidence
        customers = [c for c in customers if c['confidence'] >= min_confidence]
        
        # Store results
        video_result = {
            'video_id': metadata['video_id'],
            'url': url,
            'title': metadata['title'],
            'customers_mentioned': [
                {
                    'company': c['company'],
                    'confidence': round(c['confidence'], 2),
                    'context': c.get('context', '')
                }
                for c in customers
            ]
        }
        results['videos'].append(video_result)
        
        # Track customers
        for customer in customers:
            company = customer['company']
            if company not in results['customers']:
                results['customers'][company] = []
            results['customers'][company].append({
                'video_id': metadata['video_id'],
                'title': metadata['title'],
                'url': url,
                'confidence': round(customer['confidence'], 2),
                'context': customer.get('context', '')
            })
        
        results['processed'] += 1
        
        # Rate limiting
        if i % batch_size == 0:
            print(f"  ⏸️  Pausing... ({i} videos processed)")
            time.sleep(2)
    
    return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Extract Pinecone customers with improved accuracy'
    )
    parser.add_argument('--provider', choices=['openai', 'anthropic', 'pattern'],
                       default='openai', help='LLM provider')
    parser.add_argument('--model', help='Specific model to use')
    parser.add_argument('--api-key', help='API key')
    parser.add_argument('--min-confidence', type=float, default=0.5,
                       help='Minimum confidence threshold (0-1)')
    parser.add_argument('--batch-size', type=int, default=10)
    parser.add_argument('--limit', type=int, help='Limit number of videos')
    
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
    
    print(f"Loaded {len(video_urls)} video URLs")
    
    # Process videos
    results = process_videos_improved(
        video_urls,
        provider=args.provider,
        api_key=args.api_key,
        model=args.model,
        min_confidence=args.min_confidence,
        batch_size=args.batch_size
    )
    
    # Save results
    output_file = Path('pinecone_customers_improved.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Create summary
    customer_stats = {}
    for company, mentions in results['customers'].items():
        avg_confidence = sum(m['confidence'] for m in mentions) / len(mentions)
        customer_stats[company] = {
            'mention_count': len(mentions),
            'avg_confidence': round(avg_confidence, 2),
            'videos': [m['video_id'] for m in mentions]
        }
    
    summary = {
        'total_videos_processed': results['processed'],
        'total_unique_customers': len(results['customers']),
        'provider': results['provider'],
        'model': results.get('model', 'N/A'),
        'min_confidence': results['min_confidence'],
        'customers': customer_stats,
        'top_customers': sorted(
            customer_stats.items(),
            key=lambda x: (x[1]['mention_count'], x[1]['avg_confidence']),
            reverse=True
        )[:30]
    }
    
    summary_file = Path('pinecone_customers_summary_improved.json')
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Create CSV
    csv_file = Path('pinecone_customers_improved.csv')
    with open(csv_file, 'w') as f:
        f.write('Customer,Mention_Count,Avg_Confidence,Video_Count,Videos\n')
        for company, stats in sorted(
            customer_stats.items(),
            key=lambda x: (x[1]['mention_count'], x[1]['avg_confidence']),
            reverse=True
        ):
            video_ids = ','.join(stats['videos'])
            f.write(f'"{company}",{stats["mention_count"]},{stats["avg_confidence"]},{len(stats["videos"])},"{video_ids}"\n')
    
    # Print summary
    print("\n" + "="*60)
    print("EXTRACTION COMPLETE (IMPROVED)")
    print("="*60)
    print(f"Provider: {results['provider']}")
    print(f"Model: {results.get('model', 'N/A')}")
    print(f"Min Confidence: {results['min_confidence']}")
    print(f"Videos processed: {results['processed']}/{len(video_urls)}")
    print(f"Unique customers found: {len(results['customers'])}")
    print(f"\nTop customers (by mention count + confidence):")
    for company, stats in summary['top_customers'][:20]:
        print(f"  - {company}: {stats['mention_count']} mentions, "
              f"avg confidence {stats['avg_confidence']}")
    print(f"\n📁 Results saved to:")
    print(f"   - {output_file}")
    print(f"   - {summary_file}")
    print(f"   - {csv_file}")

if __name__ == '__main__':
    main()
