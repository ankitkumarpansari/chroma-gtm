#!/usr/bin/env python3
"""
Test accuracy of customer extraction by:
1. Running extraction on sample videos
2. Comparing different methods
3. Calculating precision/recall
4. Allowing manual verification
"""

import json
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Tuple
import sys

def get_video_metadata(video_url: str) -> Dict:
    """Get video metadata."""
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
        print(f"Error: {e}")
    
    return None

def extract_manual_review(video: Dict) -> List[str]:
    """
    Display video info and ask user to manually identify customers.
    Returns list of customer names.
    """
    print("\n" + "="*80)
    print(f"VIDEO: {video['title']}")
    print("="*80)
    print(f"URL: {video['url']}")
    print(f"\nDescription (first 500 chars):")
    print(video['description'][:500] + "..." if len(video['description']) > 500 else video['description'])
    print("\n" + "-"*80)
    
    print("\nPlease identify companies mentioned as Pinecone customers/users/partners.")
    print("Enter company names (one per line, or comma-separated).")
    print("Press Enter twice when done, or 'skip' to skip this video:")
    
    customers = []
    while True:
        line = input().strip()
        if not line:
            break
        if line.lower() == 'skip':
            return []
        # Split by comma if multiple
        for customer in line.split(','):
            customer = customer.strip()
            if customer:
                customers.append(customer)
    
    return customers

def run_extraction_method(video: Dict, method: str, api_key: str = None) -> List[str]:
    """Run extraction using specified method."""
    if method == 'pattern':
        # Import pattern extraction
        from extract_customers_llm import extract_customers_pattern
        return extract_customers_pattern(video['description'], video['title'])
    
    elif method == 'openai':
        from extract_customers_improved import extract_customers_improved_openai
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            results = extract_customers_improved_openai(
                video['title'],
                video['description'],
                api_key,
                model="gpt-4o-mini"
            )
            return [r.get('company', r) if isinstance(r, dict) else r for r in results]
        return []
    
    elif method == 'openai-gpt4':
        from extract_customers_improved import extract_customers_improved_openai
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            results = extract_customers_improved_openai(
                video['title'],
                video['description'],
                api_key,
                model="gpt-4"
            )
            return [r.get('company', r) if isinstance(r, dict) else r for r in results]
        return []
    
    return []

def normalize_name(name: str) -> str:
    """Normalize company name for comparison."""
    name = name.lower().strip()
    # Remove common prefixes
    name = name.replace('@', '').replace('the ', '')
    return name

def calculate_metrics(
    predicted: List[str],
    actual: List[str]
) -> Dict:
    """Calculate precision, recall, F1 score."""
    predicted_set = {normalize_name(p) for p in predicted}
    actual_set = {normalize_name(a) for a in actual}
    
    # True positives: correctly identified
    tp = len(predicted_set & actual_set)
    
    # False positives: incorrectly identified
    fp = len(predicted_set - actual_set)
    
    # False negatives: missed
    fn = len(actual_set - predicted_set)
    
    # Calculate metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        'precision': round(precision, 3),
        'recall': round(recall, 3),
        'f1': round(f1, 3),
        'tp': tp,
        'fp': fp,
        'fn': fn,
        'predicted': list(predicted_set),
        'actual': list(actual_set),
        'correct': list(predicted_set & actual_set),
        'false_positives': list(predicted_set - actual_set),
        'false_negatives': list(actual_set - predicted_set)
    }

def test_accuracy(
    video_urls: List[str],
    methods: List[str] = ['pattern', 'openai'],
    manual_review: bool = True,
    api_key: str = None
) -> Dict:
    """
    Test accuracy by comparing extraction methods to manual review.
    """
    results = {
        'total_videos': len(video_urls),
        'methods': methods,
        'videos': [],
        'overall_metrics': {}
    }
    
    print(f"Testing accuracy on {len(video_urls)} videos")
    print(f"Methods to test: {', '.join(methods)}")
    print(f"Manual review: {'Yes' if manual_review else 'No (using ground truth file)'}")
    print("\n" + "="*80)
    
    for i, url in enumerate(video_urls, 1):
        print(f"\n[{i}/{len(video_urls)}] Processing video...")
        
        video = get_video_metadata(url)
        if not video:
            print(f"  ⚠️  Failed to get metadata")
            continue
        
        # Get ground truth (manual review or from file)
        if manual_review:
            actual_customers = extract_manual_review(video)
        else:
            # Try to load from ground truth file
            gt_file = Path('ground_truth.json')
            if gt_file.exists():
                with open(gt_file, 'r') as f:
                    gt_data = json.load(f)
                    actual_customers = gt_data.get(video['video_id'], [])
            else:
                print(f"  ⚠️  No ground truth found. Skipping...")
                continue
        
        if not actual_customers:
            print(f"  ℹ️  No customers identified (skipped or none found)")
            continue
        
        print(f"  ✓ Ground truth: {', '.join(actual_customers)}")
        
        # Test each method
        video_results = {
            'video_id': video['video_id'],
            'title': video['title'],
            'url': url,
            'actual_customers': actual_customers,
            'methods': {}
        }
        
        for method in methods:
            print(f"  Testing {method}...")
            try:
                predicted = run_extraction_method(video, method, api_key)
                metrics = calculate_metrics(predicted, actual_customers)
                video_results['methods'][method] = metrics
                
                print(f"    Precision: {metrics['precision']}, Recall: {metrics['recall']}, F1: {metrics['f1']}")
                if metrics['false_positives']:
                    print(f"    False positives: {', '.join(metrics['false_positives'])}")
                if metrics['false_negatives']:
                    print(f"    False negatives: {', '.join(metrics['false_negatives'])}")
            except Exception as e:
                print(f"    ⚠️  Error: {e}")
                video_results['methods'][method] = {'error': str(e)}
        
        results['videos'].append(video_results)
    
    # Calculate overall metrics
    for method in methods:
        all_precisions = []
        all_recalls = []
        all_f1s = []
        
        for video_result in results['videos']:
            if method in video_result['methods'] and 'precision' in video_result['methods'][method]:
                all_precisions.append(video_result['methods'][method]['precision'])
                all_recalls.append(video_result['methods'][method]['recall'])
                all_f1s.append(video_result['methods'][method]['f1'])
        
        if all_precisions:
            results['overall_metrics'][method] = {
                'avg_precision': round(sum(all_precisions) / len(all_precisions), 3),
                'avg_recall': round(sum(all_recalls) / len(all_recalls), 3),
                'avg_f1': round(sum(all_f1s) / len(all_f1s), 3),
                'videos_tested': len(all_precisions)
            }
    
    return results

def create_ground_truth_file(video_urls: List[str]) -> None:
    """Interactive tool to create ground truth file."""
    print("Creating ground truth file...")
    print("For each video, identify the actual customers.")
    print("This will be saved to ground_truth.json for future testing.\n")
    
    ground_truth = {}
    
    for i, url in enumerate(video_urls, 1):
        video = get_video_metadata(url)
        if not video:
            continue
        
        customers = extract_manual_review(video)
        if customers:
            ground_truth[video['video_id']] = customers
    
    # Save ground truth
    with open('ground_truth.json', 'w') as f:
        json.dump(ground_truth, f, indent=2)
    
    print(f"\n✓ Saved ground truth for {len(ground_truth)} videos to ground_truth.json")

def main():
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='Test accuracy of customer extraction')
    parser.add_argument('--limit', type=int, default=5, help='Number of videos to test')
    parser.add_argument('--methods', nargs='+', 
                       choices=['pattern', 'openai', 'openai-gpt4'],
                       default=['pattern', 'openai'],
                       help='Methods to test')
    parser.add_argument('--no-manual', action='store_true',
                       help='Use ground_truth.json instead of manual review')
    parser.add_argument('--create-gt', action='store_true',
                       help='Create ground truth file')
    parser.add_argument('--api-key', help='API key for OpenAI')
    
    args = parser.parse_args()
    
    # Load video URLs
    urls_file = Path('pinecone_ALL_video_urls_MASTER.txt')
    if not urls_file.exists():
        print(f"Error: {urls_file} not found!")
        return
    
    with open(urls_file, 'r') as f:
        video_urls = [line.strip() for line in f if line.strip()]
    
    if args.create_gt:
        create_ground_truth_file(video_urls[:args.limit])
        return
    
    # Limit videos for testing
    video_urls = video_urls[:args.limit]
    
    print(f"Testing on {len(video_urls)} videos")
    
    # Get API key
    api_key = args.api_key or os.getenv('OPENAI_API_KEY')
    
    # Run tests
    results = test_accuracy(
        video_urls,
        methods=args.methods,
        manual_review=not args.no_manual,
        api_key=api_key
    )
    
    # Save results
    output_file = Path('accuracy_test_results.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "="*80)
    print("ACCURACY TEST RESULTS")
    print("="*80)
    
    for method, metrics in results['overall_metrics'].items():
        print(f"\n{method.upper()}:")
        print(f"  Average Precision: {metrics['avg_precision']}")
        print(f"  Average Recall: {metrics['avg_recall']}")
        print(f"  Average F1 Score: {metrics['avg_f1']}")
        print(f"  Videos Tested: {metrics['videos_tested']}")
    
    print(f"\n📁 Detailed results saved to: {output_file}")
    
    # Create comparison table
    print("\n" + "="*80)
    print("COMPARISON TABLE")
    print("="*80)
    print(f"{'Method':<20} {'Precision':<12} {'Recall':<12} {'F1 Score':<12}")
    print("-"*80)
    for method, metrics in results['overall_metrics'].items():
        print(f"{method:<20} {metrics['avg_precision']:<12} {metrics['avg_recall']:<12} {metrics['avg_f1']:<12}")

if __name__ == '__main__':
    main()
