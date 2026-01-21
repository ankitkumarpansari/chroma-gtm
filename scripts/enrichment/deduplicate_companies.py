#!/usr/bin/env python3
"""
Deduplicate Companies in Chroma Signal List
============================================
Removes duplicate company names from the database, keeping the best record.

Priority order for keeping records:
1. Higher tier (Tier 1 > Tier 2 > Tier 3)
2. Higher signal strength (high > medium > low)
3. More data (YouTube with context > Parallel API > Manual)

Run: python3 deduplicate_companies.py
"""

import json
import chromadb
from datetime import datetime
from collections import defaultdict

# Configuration
LOCAL_DB_FILE = 'chroma_signal_companies.json'
API_KEY = 'ck-A1VwR2zrmYsA3YvHqxahBTbmzqkrKB49hZ7UYSckwPfx'
TENANT = 'f23eab93-f8a3-493b-b775-a29c3582dee4'
DATABASE = 'GTM Signal'
COLLECTION_NAME = 'chroma_signal_list'

def load_db():
    """Load the local JSON database"""
    with open(LOCAL_DB_FILE, 'r') as f:
        return json.load(f)

def save_db(db):
    """Save the local JSON database"""
    db["metadata"]["last_updated"] = datetime.now().isoformat()
    with open(LOCAL_DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)
    print(f"💾 Saved to {LOCAL_DB_FILE}")

def get_priority_score(company):
    """Calculate a priority score for a company record (higher = better)"""
    score = 0
    
    # Tier priority (Tier 1 = 30 points, Tier 2 = 20, Tier 3 = 10)
    tier = company.get('tier', '3')
    tier_scores = {'1': 30, '2': 20, '3': 10, '4': 5}
    score += tier_scores.get(tier, 5)
    
    # Signal strength priority
    signal = company.get('signal_strength', 'low')
    signal_scores = {'high': 15, 'medium': 10, 'low': 5}
    score += signal_scores.get(signal, 5)
    
    # Source priority (YouTube with context is best)
    source = company.get('source_type', '')
    if source == 'youtube':
        score += 10
        # Bonus for having use_case/context
        if company.get('use_case'):
            score += 5
    elif source == 'parallel_api':
        score += 8
    elif source == 'manual':
        score += 6
    
    # Bonus for having more data
    if company.get('website'):
        score += 2
    if company.get('description'):
        score += 2
    if company.get('industry'):
        score += 1
    
    return score

def find_duplicates(db):
    """Find all duplicate company names"""
    companies = db['companies']
    
    # Group by normalized company name
    name_groups = defaultdict(list)
    for company_id, company_data in companies.items():
        name = company_data.get('company_name', '').strip().lower()
        name_groups[name].append((company_id, company_data))
    
    # Find groups with more than one entry
    duplicates = {name: records for name, records in name_groups.items() if len(records) > 1}
    
    return duplicates

def deduplicate(db, dry_run=True):
    """Remove duplicates, keeping the best record for each company"""
    duplicates = find_duplicates(db)
    
    if not duplicates:
        print("✅ No duplicates found!")
        return db, 0
    
    print(f"\n{'='*60}")
    print(f"DUPLICATE ANALYSIS")
    print(f"{'='*60}")
    print(f"Found {len(duplicates)} company names with duplicates")
    
    total_removed = 0
    ids_to_remove = []
    
    for name, records in sorted(duplicates.items()):
        # Sort by priority score (highest first)
        sorted_records = sorted(records, key=lambda x: get_priority_score(x[1]), reverse=True)
        
        # Keep the first (best) record
        keep_id, keep_data = sorted_records[0]
        remove_records = sorted_records[1:]
        
        print(f"\n📋 '{keep_data['company_name']}'")
        print(f"   ✓ KEEP: {keep_id} (Tier {keep_data.get('tier', '?')}, {keep_data.get('signal_strength', '?')} signal, {keep_data.get('source_type', '?')})")
        
        for remove_id, remove_data in remove_records:
            print(f"   ✗ REMOVE: {remove_id} (Tier {remove_data.get('tier', '?')}, {remove_data.get('signal_strength', '?')} signal, {remove_data.get('source_type', '?')})")
            ids_to_remove.append(remove_id)
            total_removed += 1
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total duplicates to remove: {total_removed}")
    print(f"Records after deduplication: {len(db['companies']) - total_removed}")
    
    if dry_run:
        print(f"\n⚠️  DRY RUN - No changes made")
        print(f"   Run with dry_run=False to apply changes")
    else:
        # Actually remove the duplicates
        for remove_id in ids_to_remove:
            del db['companies'][remove_id]
        
        print(f"\n✅ Removed {total_removed} duplicate records")
    
    return db, total_removed

def sync_to_chroma(db):
    """Sync the deduplicated database to Chroma Cloud"""
    print(f"\n{'='*60}")
    print("SYNCING TO CHROMA CLOUD")
    print(f"{'='*60}")
    
    client = chromadb.CloudClient(
        api_key=API_KEY,
        tenant=TENANT,
        database=DATABASE
    )
    print("✅ Connected to Chroma Cloud")
    
    # Delete existing collection
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"   Deleted existing collection: {COLLECTION_NAME}")
    except:
        pass
    
    # Create new collection
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description": "Chroma Signal List - Deduplicated",
            "created": datetime.now().isoformat()
        }
    )
    print(f"✅ Created collection: {COLLECTION_NAME}")
    
    # Prepare data
    documents = []
    metadatas = []
    ids = []
    
    for company_id, company in db["companies"].items():
        # Create document text
        doc_parts = [f"Company: {company['company_name']}"]
        if company.get('description'):
            doc_parts.append(f"Description: {company['description']}")
        if company.get('use_case'):
            doc_parts.append(f"Use Case: {company['use_case']}")
        
        documents.append(". ".join(doc_parts))
        
        # Metadata
        meta = {
            "company_name": company.get("company_name", ""),
            "source_type": company.get("source_type", ""),
            "source_channel": company.get("source_channel", "") or "",
            "tier": company.get("tier", ""),
            "category": company.get("category", ""),
            "signal_strength": company.get("signal_strength", ""),
            "added_date": company.get("added_date", ""),
        }
        metadatas.append(meta)
        ids.append(company_id)
    
    # Add in batches
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        collection.add(
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
            ids=ids[i:i+batch_size]
        )
        print(f"   Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
    
    print(f"\n✅ Synced {len(documents)} companies to Chroma Cloud!")

def main():
    print("="*60)
    print("CHROMA SIGNAL LIST - DEDUPLICATION")
    print("="*60)
    
    # Load database
    db = load_db()
    print(f"\n📊 Current records: {len(db['companies'])}")
    
    # First, do a dry run to show what would be removed
    print("\n" + "="*60)
    print("PHASE 1: DRY RUN (Preview)")
    print("="*60)
    _, to_remove = deduplicate(db, dry_run=True)
    
    if to_remove == 0:
        print("\n✅ Database is already clean - no duplicates!")
        return
    
    # Ask for confirmation
    print("\n" + "-"*60)
    response = input("Apply deduplication? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("❌ Cancelled - no changes made")
        return
    
    # Apply deduplication
    print("\n" + "="*60)
    print("PHASE 2: APPLYING CHANGES")
    print("="*60)
    db, removed = deduplicate(db, dry_run=False)
    
    # Save locally
    save_db(db)
    
    # Ask to sync to Chroma
    print("\n" + "-"*60)
    sync_response = input("Sync to Chroma Cloud? (yes/no): ").strip().lower()
    
    if sync_response == 'yes':
        sync_to_chroma(db)
    else:
        print("⚠️  Local database updated but Chroma Cloud not synced")
        print("   Run: python3 chroma_signal_list.py --sync-chroma")
    
    # Final summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    print(f"✅ Removed {removed} duplicate records")
    print(f"📊 Final count: {len(db['companies'])} unique companies")

if __name__ == "__main__":
    main()

