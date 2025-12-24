#!/usr/bin/env python3
"""
Add Companies from Claude Research
===================================
Quick script to add companies you've researched using Claude.

Usage:
  python3 add_claude_research.py

This will open an interactive prompt to add companies one by one,
or you can edit the COMPANIES_TO_ADD list below to batch add.
"""

import json
import os
from datetime import datetime

LOCAL_DB_FILE = 'chroma_signal_companies.json'

# ============================================================
# BATCH ADD: Edit this list to add multiple companies at once
# ============================================================
COMPANIES_TO_ADD = [
    # Example format - uncomment and modify:
    # {
    #     "company_name": "Example Corp",
    #     "website": "https://example.com",
    #     "description": "AI-powered analytics platform",
    #     "tier": "1",  # 1=Enterprise High Value, 2=AI Native, 3=Competitor Customer, 4=Other
    #     "category": "enterprise",  # enterprise, ai_native, competitor_customer, partner, other
    #     "industry": "Analytics",
    #     "current_vector_db": "Pinecone",  # What they currently use (if known)
    #     "use_case": "Semantic search for customer data",
    #     "signal_strength": "high",  # high, medium, low
    #     "source_notes": "Found during Claude research - they mentioned vector DBs in their blog"
    # },
]

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_db():
    if os.path.exists(LOCAL_DB_FILE):
        with open(LOCAL_DB_FILE, 'r') as f:
            return json.load(f)
    return {"metadata": {"created": datetime.now().isoformat()}, "companies": {}}

def save_db(db):
    db["metadata"]["last_updated"] = datetime.now().isoformat()
    with open(LOCAL_DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

def generate_id(name):
    return f"manual_{name.lower().replace(' ', '_').replace('.', '').replace(',', '')}"

def add_company_interactive():
    """Add a single company interactively"""
    print("\n" + "="*60)
    print("ADD COMPANY FROM CLAUDE RESEARCH")
    print("="*60)
    
    company = {}
    
    company["company_name"] = input("\n📛 Company Name: ").strip()
    if not company["company_name"]:
        return None
    
    company["website"] = input("🌐 Website: ").strip() or None
    company["description"] = input("📝 Description: ").strip() or None
    
    print("\n🎯 Tier:")
    print("   1 = Enterprise High Value (Fortune 500, funded startups)")
    print("   2 = AI Native (Building AI products)")
    print("   3 = Competitor Customer (Using Pinecone/Weaviate/etc)")
    print("   4 = Other")
    company["tier"] = input("   Enter [1-4]: ").strip() or "2"
    
    print("\n🏷️  Category:")
    print("   1=enterprise, 2=ai_native, 3=competitor_customer, 4=partner, 5=other")
    cat_map = {'1': 'enterprise', '2': 'ai_native', '3': 'competitor_customer', '4': 'partner', '5': 'other'}
    company["category"] = cat_map.get(input("   Enter [1-5]: ").strip(), "other")
    
    company["industry"] = input("🏢 Industry: ").strip() or None
    company["current_vector_db"] = input("🗄️  Current Vector DB (if known): ").strip() or None
    company["use_case"] = input("💡 Use Case: ").strip() or None
    
    print("\n📶 Signal Strength:")
    print("   1=high (actively looking), 2=medium (likely need), 3=low (potential)")
    sig_map = {'1': 'high', '2': 'medium', '3': 'low'}
    company["signal_strength"] = sig_map.get(input("   Enter [1-3]: ").strip(), "medium")
    
    company["source_notes"] = input("📋 Research Notes: ").strip() or None
    
    # Set metadata
    company["source_type"] = "manual"
    company["added_date"] = datetime.now().strftime("%Y-%m-%d")
    company["added_by"] = "claude_research"
    company["last_updated"] = datetime.now().isoformat()
    
    return company

def add_batch_companies(db, companies):
    """Add multiple companies from the COMPANIES_TO_ADD list"""
    added = 0
    for company in companies:
        if not company.get("company_name"):
            continue
        
        company_id = generate_id(company["company_name"])
        
        # Add metadata
        company["source_type"] = "manual"
        company["added_date"] = datetime.now().strftime("%Y-%m-%d")
        company["added_by"] = "claude_research"
        company["last_updated"] = datetime.now().isoformat()
        
        if company_id not in db["companies"]:
            db["companies"][company_id] = company
            added += 1
            print(f"  ✅ Added: {company['company_name']}")
        else:
            print(f"  ⚠️  Skipped (exists): {company['company_name']}")
    
    return db, added

def main():
    db = load_db()
    
    print("\n" + "="*60)
    print("CHROMA SIGNAL LIST - ADD CLAUDE RESEARCH")
    print("="*60)
    print(f"\n📊 Current database: {len(db['companies'])} companies")
    
    # Check for batch additions
    if COMPANIES_TO_ADD:
        print(f"\n📦 Found {len(COMPANIES_TO_ADD)} companies in batch list...")
        db, added = add_batch_companies(db, COMPANIES_TO_ADD)
        if added > 0:
            save_db(db)
            print(f"\n✅ Added {added} companies from batch list!")
    
    # Interactive mode
    print("\n" + "-"*60)
    print("INTERACTIVE MODE")
    print("-"*60)
    print("Add companies one by one. Press Enter with empty name to finish.")
    
    while True:
        company = add_company_interactive()
        if not company:
            break
        
        company_id = generate_id(company["company_name"])
        
        if company_id in db["companies"]:
            print(f"⚠️  Company already exists: {company['company_name']}")
            overwrite = input("   Overwrite? [y/N]: ").strip().lower()
            if overwrite != 'y':
                continue
        
        db["companies"][company_id] = company
        save_db(db)
        print(f"✅ Saved: {company['company_name']}")
        
        another = input("\nAdd another? [Y/n]: ").strip().lower()
        if another == 'n':
            break
    
    print(f"\n📊 Final database: {len(db['companies'])} companies")
    print("💾 Saved to:", LOCAL_DB_FILE)

if __name__ == "__main__":
    main()

