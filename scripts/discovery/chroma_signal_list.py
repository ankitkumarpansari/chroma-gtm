#!/usr/bin/env python3
"""
Chroma Signal List - Unified Company Database
==============================================
A comprehensive Chroma collection to store all companies mentioned in Chroma Signal.

Sources:
1. YouTube Extraction (Competitor Channels): LangChain, Qdrant, Weaviate, Vespa, Pinecone
2. Parallel API (Job Postings): Companies hiring for vector DB roles
3. Manual Research (Claude): Companies added from manual research

Run: python3 chroma_signal_list.py

Commands:
  python3 chroma_signal_list.py --list              # List all companies
  python3 chroma_signal_list.py --add               # Add a new company interactively
  python3 chroma_signal_list.py --sync              # Sync all data to Chroma Cloud
  python3 chroma_signal_list.py --export            # Export to JSON/CSV
"""

import chromadb
import json
import os
import csv
import argparse
from datetime import datetime
from typing import Optional, List, Dict, Any

# ============================================================
# CONFIGURATION
# ============================================================
API_KEY = os.environ.get('CHROMA_API_KEY', 'ck-A1VwR2zrmYsA3YvHqxahBTbmzqkrKB49hZ7UYSckwPfx')
TENANT = 'f23eab93-f8a3-493b-b775-a29c3582dee4'
DATABASE = 'GTM Signal'
COLLECTION_NAME = 'chroma_signal_list'

# Local JSON file to store all companies (source of truth)
LOCAL_DB_FILE = 'chroma_signal_companies.json'

# ============================================================
# SCHEMA DEFINITION
# ============================================================
"""
Standard Company Schema:
{
    "id": "unique_id",                    # Auto-generated unique ID
    "company_name": "Company Name",       # Required: Company name
    "website": "https://...",             # Optional: Company website
    "description": "...",                 # Optional: Brief description
    
    # Source Information
    "source_type": "youtube|parallel_api|manual",  # Required: How we found them
    "source_channel": "LangChain|Qdrant|...",      # For YouTube sources
    "source_query": "vector db jobs...",           # For Parallel API sources
    "source_notes": "...",                         # For manual research notes
    
    # Classification
    "tier": "1|2|3|4",                    # Priority tier (1=highest)
    "category": "enterprise|ai_native|competitor_customer|partner|other",
    "industry": "...",                    # Industry vertical
    "company_size": "startup|smb|mid|enterprise",
    
    # Vector DB Context
    "current_vector_db": "...",           # What they currently use (if known)
    "use_case": "...",                    # How they use vector DBs
    "signal_strength": "high|medium|low", # How strong is the buying signal
    
    # Engagement
    "video_title": "...",                 # For YouTube sources
    "video_url": "...",                   # Video URL if applicable
    "job_posting_url": "...",             # For job posting sources
    
    # Metadata
    "added_date": "2024-12-19",           # When added
    "added_by": "system|manual",          # How it was added
    "last_updated": "2024-12-19",         # Last update
    "notes": "..."                        # Additional notes
}
"""

# ============================================================
# DATA LOADING FUNCTIONS
# ============================================================

def load_local_db() -> Dict:
    """Load the local JSON database"""
    if os.path.exists(LOCAL_DB_FILE):
        with open(LOCAL_DB_FILE, 'r') as f:
            return json.load(f)
    return {
        "metadata": {
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "version": "1.0"
        },
        "companies": {}
    }

def save_local_db(data: Dict):
    """Save to local JSON database"""
    data["metadata"]["last_updated"] = datetime.now().isoformat()
    with open(LOCAL_DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"💾 Saved to {LOCAL_DB_FILE}")

def generate_id(company_name: str, source_type: str) -> str:
    """Generate a unique ID for a company"""
    clean_name = company_name.lower().replace(' ', '_').replace('.', '').replace(',', '')
    return f"{source_type}_{clean_name}"

# ============================================================
# LOAD FROM YOUTUBE EXTRACTION
# ============================================================

def load_youtube_companies() -> List[Dict]:
    """Load all companies from YouTube extraction JSON files"""
    companies = []
    today = datetime.now().strftime("%Y-%m-%d")
    
    # LangChain Companies
    try:
        with open('langchain_COMPANIES_VERIFIED.json', 'r') as f:
            data = json.load(f)
            
        # Enterprise customers
        for name, context in data['companies'].get('enterprise_customers', {}).items():
            companies.append({
                "company_name": name,
                "source_type": "youtube",
                "source_channel": "LangChain",
                "tier": "1",
                "category": "enterprise",
                "use_case": context,
                "signal_strength": "high",
                "added_date": today,
                "added_by": "system"
            })
        
        # LLM Providers (partners)
        for name, context in data['companies'].get('llm_providers', {}).items():
            companies.append({
                "company_name": name,
                "source_type": "youtube",
                "source_channel": "LangChain",
                "tier": "3",
                "category": "partner",
                "use_case": context,
                "signal_strength": "low",
                "added_date": today,
                "added_by": "system"
            })
        
        # Integration partners
        for name, context in data['companies'].get('integration_partners', {}).items():
            companies.append({
                "company_name": name,
                "source_type": "youtube",
                "source_channel": "LangChain",
                "tier": "3",
                "category": "partner",
                "use_case": context,
                "signal_strength": "medium",
                "added_date": today,
                "added_by": "system"
            })
            
        print(f"  ✓ LangChain: {len(data['companies'].get('enterprise_customers', {}))} enterprise customers")
    except FileNotFoundError:
        print("  ⚠ langchain_COMPANIES_VERIFIED.json not found")
    
    # Qdrant Companies
    try:
        with open('qdrant_COMPANIES_VERIFIED.json', 'r') as f:
            data = json.load(f)
        
        for name in data['companies'].get('customers', []):
            companies.append({
                "company_name": name,
                "source_type": "youtube",
                "source_channel": "Qdrant",
                "tier": "2",
                "category": "competitor_customer",
                "current_vector_db": "Qdrant",
                "signal_strength": "high",
                "added_date": today,
                "added_by": "system"
            })
        
        for name in data['companies'].get('partners', []):
            companies.append({
                "company_name": name,
                "source_type": "youtube",
                "source_channel": "Qdrant",
                "tier": "3",
                "category": "partner",
                "signal_strength": "low",
                "added_date": today,
                "added_by": "system"
            })
            
        print(f"  ✓ Qdrant: {len(data['companies'].get('customers', []))} customers")
    except FileNotFoundError:
        print("  ⚠ qdrant_COMPANIES_VERIFIED.json not found")
    
    # Weaviate Companies
    try:
        with open('weaviate_COMPANIES_FINAL.json', 'r') as f:
            data = json.load(f)
        
        for name in data['companies'].get('customers', []):
            # Skip generic/non-company entries
            if any(x in name.lower() for x in ['benchmark', 'retrieval', 'search', 'learning', 'quantization', 'tabular', 'applications']):
                continue
            companies.append({
                "company_name": name,
                "source_type": "youtube",
                "source_channel": "Weaviate",
                "tier": "2",
                "category": "competitor_customer",
                "current_vector_db": "Weaviate",
                "signal_strength": "high",
                "added_date": today,
                "added_by": "system"
            })
        
        for name in data['companies'].get('partners', []):
            companies.append({
                "company_name": name,
                "source_type": "youtube",
                "source_channel": "Weaviate",
                "tier": "3",
                "category": "partner",
                "signal_strength": "low",
                "added_date": today,
                "added_by": "system"
            })
            
        print(f"  ✓ Weaviate: {len(data['companies'].get('customers', []))} customers")
    except FileNotFoundError:
        print("  ⚠ weaviate_COMPANIES_FINAL.json not found")
    
    # Vespa Companies
    try:
        with open('vespa_COMPANIES_FINAL.json', 'r') as f:
            data = json.load(f)
        
        for name in data['companies'].get('customers', []):
            if name.lower() not in ['vespa', 'generativeai']:  # Skip self-references
                companies.append({
                    "company_name": name,
                    "source_type": "youtube",
                    "source_channel": "Vespa",
                    "tier": "2",
                    "category": "competitor_customer",
                    "current_vector_db": "Vespa",
                    "signal_strength": "high",
                    "added_date": today,
                    "added_by": "system"
                })
                
        print(f"  ✓ Vespa: {len(data['companies'].get('customers', []))} customers")
    except FileNotFoundError:
        print("  ⚠ vespa_COMPANIES_FINAL.json not found")
    
    # Pinecone Companies (from CUSTOMERS_ONLY.json)
    try:
        with open('CUSTOMERS_ONLY.json', 'r') as f:
            data = json.load(f)
        
        pinecone_count = 0
        for name, info in data['customers'].items():
            if 'Pinecone' in info.get('source', ''):
                companies.append({
                    "company_name": name,
                    "source_type": "youtube",
                    "source_channel": "Pinecone",
                    "tier": "2",
                    "category": "competitor_customer",
                    "current_vector_db": "Pinecone",
                    "use_case": info.get('use_case', ''),
                    "signal_strength": "high",
                    "added_date": today,
                    "added_by": "system"
                })
                pinecone_count += 1
                
        print(f"  ✓ Pinecone: {pinecone_count} customers")
    except FileNotFoundError:
        print("  ⚠ CUSTOMERS_ONLY.json not found")
    
    return companies

# ============================================================
# LOAD FROM PARALLEL API
# ============================================================

def load_parallel_api_companies() -> List[Dict]:
    """Load companies from Parallel API job posting results"""
    companies = []
    seen_names = set()  # Track duplicates
    today = datetime.now().strftime("%Y-%m-%d")
    
    # JSON files from Parallel API
    json_files = [
        ('vector_db_leads_20251210_153301.json', 'Vector DB Job Postings'),
        ('expanded_leads_20251210_162836.json', 'Expanded Pinecone/Vector DB Leads'),
    ]
    
    for json_file, query_desc in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            file_count = 0
            for entry in data:
                # Only include matched companies
                if entry.get('match_status') != 'matched':
                    continue
                
                name = entry.get('name', '')
                if not name or name in seen_names:
                    continue
                
                seen_names.add(name)
                file_count += 1
                
                # Extract query source if available
                query_source = entry.get('query_source', query_desc)
                
                companies.append({
                    "company_name": name,
                    "website": entry.get('url', ''),
                    "description": entry.get('description', ''),
                    "source_type": "parallel_api",
                    "source_query": query_source,
                    "tier": "1",  # High intent - actively hiring
                    "category": "enterprise",
                    "signal_strength": "high",
                    "added_date": today,
                    "added_by": "system"
                })
            
            print(f"  ✓ {json_file}: {file_count} matched companies")
        except FileNotFoundError:
            print(f"  ⚠ {json_file} not found")
        except json.JSONDecodeError:
            print(f"  ⚠ {json_file} is not valid JSON")
    
    print(f"  ✓ Parallel API Total: {len(companies)} unique companies")
    return companies

# ============================================================
# LOAD FROM COMPREHENSIVE COMPANY REPORT (Claude Research)
# ============================================================

def load_comprehensive_report() -> List[Dict]:
    """Load companies from comprehensive_company_report.csv (Claude research)"""
    companies = []
    today = datetime.now().strftime("%Y-%m-%d")
    
    csv_file = 'comprehensive_company_report.csv'
    
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                company_name = row.get('Company Name', '').strip()
                if not company_name:
                    continue
                
                # Map fit score to tier
                fit_score = row.get('Fit Score', '')
                if fit_score:
                    try:
                        score = int(fit_score)
                        if score >= 8:
                            tier = "1"
                        elif score >= 7:
                            tier = "2"
                        else:
                            tier = "3"
                    except:
                        tier = "2"
                else:
                    tier = "3"
                
                # Map category
                category_raw = row.get('Category', '').lower()
                if 'yc' in category_raw or 'startup' in category_raw:
                    category = "ai_native"
                elif any(x in category_raw for x in ['enterprise', 'sales', 'financial', 'healthcare']):
                    category = "enterprise"
                else:
                    category = "other"
                
                # Determine signal strength from hiring signal
                hiring = row.get('Hiring Signal', '').lower()
                if hiring and any(x in hiring for x in ['engineer', 'ai', 'ml', 'active']):
                    signal = "high"
                elif hiring:
                    signal = "medium"
                else:
                    signal = "low"
                
                companies.append({
                    "company_name": company_name,
                    "website": row.get('Website', ''),
                    "description": row.get('Why Hot Lead', '') or row.get('Deep Research Signal', ''),
                    "source_type": "manual",
                    "source_notes": f"Claude Research - {row.get('Source', '')}",
                    "tier": tier,
                    "category": category,
                    "industry": row.get('Category', '') or row.get('Subcategory', ''),
                    "use_case": row.get('Subcategory', ''),
                    "signal_strength": signal,
                    "funding_stage": row.get('Funding Stage', ''),
                    "funding_amount": row.get('Funding Amount', ''),
                    "location": row.get('Location', ''),
                    "linkedin_url": row.get('Company LinkedIn URL', ''),
                    "notes": row.get('Notes', ''),
                    "fit_score": row.get('Fit Score', ''),
                    "added_date": today,
                    "added_by": "claude_research"
                })
        
        print(f"  ✓ Comprehensive Report: {len(companies)} companies from Claude research")
    except FileNotFoundError:
        print(f"  ⚠ {csv_file} not found")
    
    return companies

# ============================================================
# MANUAL COMPANY ADDITIONS
# ============================================================

def add_manual_company(db: Dict) -> Dict:
    """Interactive function to add a company manually"""
    print("\n" + "="*60)
    print("ADD NEW COMPANY (Manual Research)")
    print("="*60)
    
    company = {}
    
    # Required fields
    company["company_name"] = input("\n📛 Company Name (required): ").strip()
    if not company["company_name"]:
        print("❌ Company name is required!")
        return db
    
    # Optional fields
    company["website"] = input("🌐 Website URL: ").strip() or None
    company["description"] = input("📝 Description: ").strip() or None
    
    # Source
    company["source_type"] = "manual"
    company["source_notes"] = input("📋 Research Notes: ").strip() or None
    
    # Classification
    print("\n📊 Tier (1=Enterprise High Value, 2=AI Native, 3=Competitor Customer, 4=Other)")
    tier = input("   Enter tier [1-4]: ").strip()
    company["tier"] = tier if tier in ['1', '2', '3', '4'] else '2'
    
    print("\n🏷️  Category:")
    print("   1. enterprise")
    print("   2. ai_native")
    print("   3. competitor_customer")
    print("   4. partner")
    print("   5. other")
    cat_choice = input("   Enter choice [1-5]: ").strip()
    categories = {'1': 'enterprise', '2': 'ai_native', '3': 'competitor_customer', '4': 'partner', '5': 'other'}
    company["category"] = categories.get(cat_choice, 'other')
    
    company["industry"] = input("🏢 Industry: ").strip() or None
    company["current_vector_db"] = input("🗄️  Current Vector DB (if known): ").strip() or None
    company["use_case"] = input("💡 Use Case: ").strip() or None
    
    print("\n📶 Signal Strength:")
    print("   1. high (actively evaluating/using vector DBs)")
    print("   2. medium (likely needs vector DB)")
    print("   3. low (potential future need)")
    sig_choice = input("   Enter choice [1-3]: ").strip()
    signals = {'1': 'high', '2': 'medium', '3': 'low'}
    company["signal_strength"] = signals.get(sig_choice, 'medium')
    
    company["notes"] = input("📝 Additional Notes: ").strip() or None
    
    # Metadata
    company["added_date"] = datetime.now().strftime("%Y-%m-%d")
    company["added_by"] = "manual"
    company["last_updated"] = datetime.now().isoformat()
    
    # Generate ID and add to database
    company_id = generate_id(company["company_name"], "manual")
    db["companies"][company_id] = company
    
    print(f"\n✅ Added: {company['company_name']} (ID: {company_id})")
    return db

def add_companies_batch(db: Dict, companies: List[Dict]) -> Dict:
    """Add multiple companies from a list (for programmatic additions)"""
    added = 0
    for company in companies:
        company_id = generate_id(
            company["company_name"], 
            company.get("source_type", "manual")
        )
        
        # Don't overwrite existing entries
        if company_id not in db["companies"]:
            company["last_updated"] = datetime.now().isoformat()
            db["companies"][company_id] = company
            added += 1
    
    print(f"✅ Added {added} new companies (skipped {len(companies) - added} duplicates)")
    return db

# ============================================================
# SYNC TO CHROMA CLOUD
# ============================================================

def sync_to_chroma(db: Dict):
    """Sync local database to Chroma Cloud"""
    if API_KEY == 'YOUR_API_KEY':
        print("\n⚠️  Please set your CHROMA_API_KEY!")
        print("   export CHROMA_API_KEY='your-key'")
        return
    
    print("\n🔗 Connecting to Chroma Cloud...")
    client = chromadb.CloudClient(
        api_key=API_KEY,
        tenant=TENANT,
        database=DATABASE
    )
    print("✅ Connected!")
    
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
            "description": "Chroma Signal List - All companies from YouTube extraction, Parallel API, and manual research",
            "created": datetime.now().isoformat()
        }
    )
    print(f"✅ Created collection: {COLLECTION_NAME}")
    
    # Prepare data
    documents = []
    metadatas = []
    ids = []
    
    for company_id, company in db["companies"].items():
        # Create document text for embedding
        doc_parts = [f"Company: {company['company_name']}"]
        if company.get('description'):
            doc_parts.append(f"Description: {company['description']}")
        if company.get('use_case'):
            doc_parts.append(f"Use Case: {company['use_case']}")
        if company.get('industry'):
            doc_parts.append(f"Industry: {company['industry']}")
        if company.get('current_vector_db'):
            doc_parts.append(f"Current Vector DB: {company['current_vector_db']}")
        
        documents.append(". ".join(doc_parts))
        
        # Metadata (Chroma requires string values)
        meta = {
            "company_name": company.get("company_name", ""),
            "source_type": company.get("source_type", ""),
            "source_channel": company.get("source_channel", "") or "",
            "tier": company.get("tier", ""),
            "category": company.get("category", ""),
            "signal_strength": company.get("signal_strength", ""),
            "current_vector_db": company.get("current_vector_db", "") or "",
            "added_date": company.get("added_date", ""),
            "added_by": company.get("added_by", "")
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

# ============================================================
# EXPORT FUNCTIONS
# ============================================================

def export_to_csv(db: Dict, filename: str = "chroma_signal_list_export.csv"):
    """Export database to CSV"""
    if not db["companies"]:
        print("❌ No companies to export!")
        return
    
    # Get all unique keys
    all_keys = set()
    for company in db["companies"].values():
        all_keys.update(company.keys())
    
    fieldnames = sorted(list(all_keys))
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for company in db["companies"].values():
            writer.writerow(company)
    
    print(f"✅ Exported to {filename}")

def export_to_json(db: Dict, filename: str = "chroma_signal_list_export.json"):
    """Export database to JSON"""
    with open(filename, 'w') as f:
        json.dump(db, f, indent=2)
    print(f"✅ Exported to {filename}")

# ============================================================
# LIST AND DISPLAY
# ============================================================

def list_companies(db: Dict, filter_source: str = None, filter_tier: str = None):
    """List all companies with optional filters"""
    companies = db["companies"]
    
    if not companies:
        print("📭 No companies in database. Run --sync-sources first.")
        return
    
    # Apply filters
    filtered = companies.values()
    if filter_source:
        filtered = [c for c in filtered if c.get("source_type") == filter_source]
    if filter_tier:
        filtered = [c for c in filtered if c.get("tier") == filter_tier]
    
    filtered = list(filtered)
    
    print(f"\n{'='*80}")
    print(f"CHROMA SIGNAL LIST - {len(filtered)} Companies")
    print(f"{'='*80}")
    
    # Group by source
    by_source = {}
    for c in filtered:
        source = c.get("source_type", "unknown")
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(c)
    
    for source, companies_list in by_source.items():
        print(f"\n📁 {source.upper()} ({len(companies_list)} companies)")
        print("-" * 40)
        
        # Sort by tier then name
        sorted_companies = sorted(companies_list, key=lambda x: (x.get("tier", "9"), x.get("company_name", "")))
        
        for c in sorted_companies:
            tier = c.get("tier", "?")
            name = c.get("company_name", "Unknown")
            category = c.get("category", "")
            signal = c.get("signal_strength", "")
            channel = c.get("source_channel", "")
            
            tier_emoji = {"1": "🔴", "2": "🟡", "3": "🟢", "4": "⚪"}.get(tier, "⚪")
            
            line = f"  {tier_emoji} T{tier} | {name}"
            if channel:
                line += f" [{channel}]"
            if category:
                line += f" ({category})"
            if signal:
                line += f" - {signal} signal"
            
            print(line)
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    
    tier_counts = {}
    for c in filtered:
        tier = c.get("tier", "unknown")
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    for tier in sorted(tier_counts.keys()):
        print(f"  Tier {tier}: {tier_counts[tier]} companies")

def show_stats(db: Dict):
    """Show database statistics"""
    companies = list(db["companies"].values())
    
    if not companies:
        print("📭 No companies in database.")
        return
    
    print(f"\n{'='*60}")
    print("CHROMA SIGNAL LIST - STATISTICS")
    print(f"{'='*60}")
    
    print(f"\n📊 Total Companies: {len(companies)}")
    
    # By source type
    print("\n📁 By Source:")
    by_source = {}
    for c in companies:
        source = c.get("source_type", "unknown")
        by_source[source] = by_source.get(source, 0) + 1
    for source, count in sorted(by_source.items()):
        print(f"   {source}: {count}")
    
    # By tier
    print("\n🎯 By Tier:")
    by_tier = {}
    for c in companies:
        tier = c.get("tier", "unknown")
        by_tier[tier] = by_tier.get(tier, 0) + 1
    for tier in sorted(by_tier.keys()):
        print(f"   Tier {tier}: {by_tier[tier]}")
    
    # By category
    print("\n🏷️  By Category:")
    by_cat = {}
    for c in companies:
        cat = c.get("category", "unknown")
        by_cat[cat] = by_cat.get(cat, 0) + 1
    for cat, count in sorted(by_cat.items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count}")
    
    # By signal strength
    print("\n📶 By Signal Strength:")
    by_signal = {}
    for c in companies:
        sig = c.get("signal_strength", "unknown")
        by_signal[sig] = by_signal.get(sig, 0) + 1
    for sig, count in sorted(by_signal.items()):
        print(f"   {sig}: {count}")
    
    # YouTube channels breakdown
    print("\n📺 YouTube Channels:")
    by_channel = {}
    for c in companies:
        if c.get("source_type") == "youtube":
            channel = c.get("source_channel", "unknown")
            by_channel[channel] = by_channel.get(channel, 0) + 1
    for channel, count in sorted(by_channel.items(), key=lambda x: -x[1]):
        print(f"   {channel}: {count}")

# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Chroma Signal List - Unified Company Database")
    parser.add_argument("--list", action="store_true", help="List all companies")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--add", action="store_true", help="Add a company manually")
    parser.add_argument("--sync-sources", action="store_true", help="Sync from all source files")
    parser.add_argument("--sync-chroma", action="store_true", help="Sync to Chroma Cloud")
    parser.add_argument("--export-csv", action="store_true", help="Export to CSV")
    parser.add_argument("--export-json", action="store_true", help="Export to JSON")
    parser.add_argument("--filter-source", type=str, help="Filter by source (youtube, parallel_api, manual)")
    parser.add_argument("--filter-tier", type=str, help="Filter by tier (1, 2, 3, 4)")
    
    args = parser.parse_args()
    
    # Load local database
    db = load_local_db()
    
    # Handle commands
    if args.sync_sources:
        print("\n" + "="*60)
        print("SYNCING FROM ALL SOURCES")
        print("="*60)
        
        print("\n📺 Loading YouTube Extraction...")
        youtube_companies = load_youtube_companies()
        db = add_companies_batch(db, youtube_companies)
        
        print("\n🔍 Loading Parallel API...")
        parallel_companies = load_parallel_api_companies()
        db = add_companies_batch(db, parallel_companies)
        
        print("\n🧠 Loading Claude Research (Comprehensive Report)...")
        claude_companies = load_comprehensive_report()
        db = add_companies_batch(db, claude_companies)
        
        save_local_db(db)
        show_stats(db)
    
    elif args.add:
        db = add_manual_company(db)
        save_local_db(db)
    
    elif args.sync_chroma:
        sync_to_chroma(db)
    
    elif args.export_csv:
        export_to_csv(db)
    
    elif args.export_json:
        export_to_json(db)
    
    elif args.list:
        list_companies(db, args.filter_source, args.filter_tier)
    
    elif args.stats:
        show_stats(db)
    
    else:
        # Default: show help
        print("\n" + "="*60)
        print("CHROMA SIGNAL LIST")
        print("Unified Company Database for Chroma GTM")
        print("="*60)
        
        if db["companies"]:
            print(f"\n📊 Current Status: {len(db['companies'])} companies in database")
            show_stats(db)
        else:
            print("\n📭 Database is empty. Run with --sync-sources to populate.")
        
        print("\n📖 Commands:")
        print("   --sync-sources    Sync from all source files (YouTube, Parallel API)")
        print("   --add             Add a company manually")
        print("   --list            List all companies")
        print("   --stats           Show statistics")
        print("   --sync-chroma     Sync to Chroma Cloud")
        print("   --export-csv      Export to CSV")
        print("   --export-json     Export to JSON")
        print("\n📝 Filters:")
        print("   --filter-source   Filter by source (youtube, parallel_api, manual)")
        print("   --filter-tier     Filter by tier (1, 2, 3, 4)")

if __name__ == "__main__":
    main()

