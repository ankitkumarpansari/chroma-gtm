#!/usr/bin/env python3
"""
Export Chroma Signal List to Google Sheets format for Looker Studio
====================================================================
Creates a well-formatted CSV that can be uploaded to Google Sheets
and connected to Looker Studio for visualization.

Run: python3 export_for_looker.py
"""

import json
import csv
from datetime import datetime

LOCAL_DB_FILE = 'chroma_signal_companies.json'
OUTPUT_CSV = 'chroma_signal_looker_export.csv'

def load_db():
    with open(LOCAL_DB_FILE, 'r') as f:
        return json.load(f)

def export_to_csv(db):
    """Export database to a Looker Studio-friendly CSV"""
    companies = db['companies']
    
    # Define columns for Looker Studio
    columns = [
        'Company Name',
        'Website',
        'Tier',
        'Tier Label',
        'Category',
        'Signal Strength',
        'Source Type',
        'Source Channel',
        'Industry',
        'Use Case',
        'Description',
        'Current Vector DB',
        'Funding Stage',
        'Location',
        'LinkedIn URL',
        'Fit Score',
        'Added Date',
        'Notes'
    ]
    
    rows = []
    for company_id, company in companies.items():
        # Map tier to label for better visualization
        tier = company.get('tier', '')
        tier_labels = {
            '1': 'Tier 1 - Hot Lead',
            '2': 'Tier 2 - High Potential',
            '3': 'Tier 3 - Partner/Tool',
            '4': 'Tier 4 - Other'
        }
        tier_label = tier_labels.get(tier, 'Unknown')
        
        row = {
            'Company Name': company.get('company_name', ''),
            'Website': company.get('website', ''),
            'Tier': tier,
            'Tier Label': tier_label,
            'Category': company.get('category', ''),
            'Signal Strength': company.get('signal_strength', ''),
            'Source Type': company.get('source_type', ''),
            'Source Channel': company.get('source_channel', ''),
            'Industry': company.get('industry', ''),
            'Use Case': company.get('use_case', ''),
            'Description': company.get('description', ''),
            'Current Vector DB': company.get('current_vector_db', ''),
            'Funding Stage': company.get('funding_stage', ''),
            'Location': company.get('location', ''),
            'LinkedIn URL': company.get('linkedin_url', ''),
            'Fit Score': company.get('fit_score', ''),
            'Added Date': company.get('added_date', ''),
            'Notes': company.get('notes', '')
        }
        rows.append(row)
    
    # Sort by Tier then Company Name
    rows.sort(key=lambda x: (x['Tier'] or '9', x['Company Name']))
    
    # Write CSV
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    
    return len(rows)

def print_summary(db):
    """Print summary statistics"""
    companies = list(db['companies'].values())
    
    print("\n" + "="*60)
    print("EXPORT SUMMARY")
    print("="*60)
    
    print(f"\n📊 Total Companies: {len(companies)}")
    
    # By Source
    print("\n📁 By Source:")
    sources = {}
    for c in companies:
        src = c.get('source_type', 'unknown')
        sources[src] = sources.get(src, 0) + 1
    for src, count in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"   {src}: {count}")
    
    # By Tier
    print("\n🎯 By Tier:")
    tiers = {}
    for c in companies:
        tier = c.get('tier', 'unknown')
        tiers[tier] = tiers.get(tier, 0) + 1
    tier_labels = {'1': 'Tier 1 - Hot Lead', '2': 'Tier 2 - High Potential', '3': 'Tier 3 - Partner/Tool'}
    for tier in sorted(tiers.keys()):
        label = tier_labels.get(tier, f'Tier {tier}')
        print(f"   {label}: {tiers[tier]}")
    
    # By Signal
    print("\n📶 By Signal Strength:")
    signals = {}
    for c in companies:
        sig = c.get('signal_strength', 'unknown')
        signals[sig] = signals.get(sig, 0) + 1
    for sig, count in sorted(signals.items(), key=lambda x: -x[1]):
        print(f"   {sig}: {count}")
    
    # With URLs
    with_url = sum(1 for c in companies if c.get('website'))
    print(f"\n🔗 With Website URL: {with_url} ({with_url/len(companies)*100:.1f}%)")

def main():
    print("="*60)
    print("EXPORT CHROMA SIGNAL LIST FOR LOOKER STUDIO")
    print("="*60)
    
    # Load database
    db = load_db()
    
    # Export to CSV
    count = export_to_csv(db)
    
    print(f"\n✅ Exported {count} companies to: {OUTPUT_CSV}")
    
    # Print summary
    print_summary(db)
    
    # Instructions
    print("\n" + "="*60)
    print("NEXT STEPS FOR LOOKER STUDIO")
    print("="*60)
    print("""
1. Upload CSV to Google Sheets:
   - Go to sheets.google.com
   - File → Import → Upload → Select 'chroma_signal_looker_export.csv'
   - Choose "Replace spreadsheet" or "Insert new sheet"

2. Connect to Looker Studio:
   - Go to lookerstudio.google.com
   - Create → Data Source → Google Sheets
   - Select your uploaded sheet
   - Click "Connect"

3. Create Dashboard:
   - Add charts for:
     • Pie chart: Companies by Tier
     • Bar chart: Companies by Source
     • Table: Hot Leads (Tier 1)
     • Scorecard: Total Companies
     • Bar chart: Signal Strength distribution

4. Recommended Filters:
   - Tier (dropdown)
   - Source Type (dropdown)
   - Signal Strength (dropdown)
   - Category (dropdown)
""")

if __name__ == "__main__":
    main()

