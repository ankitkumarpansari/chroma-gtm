#!/usr/bin/env python3
"""
Save all extracted company data to Chroma Cloud Database
Run: python3 save_to_chroma.py

Data Source: Competitor YouTube channels (Qdrant, Weaviate, Vespa, Pinecone)
Excludes: LangChain (framework partner, not competitor)
"""

import chromadb
import json
import os
from datetime import datetime

# ============================================================
# CONFIGURATION - UPDATE YOUR API KEY HERE
# ============================================================
API_KEY = os.environ.get('CHROMA_API_KEY', 'YOUR_API_KEY')  # Set via env or replace here
TENANT = 'aa8f571e-03dc-4cd8-b888-723bd00b83f0'
DATABASE = 'customer'

# ============================================================
# Connect to Chroma Cloud
# ============================================================
def connect_to_chroma():
    """Connect to Chroma Cloud"""
    print("🔗 Connecting to Chroma Cloud...")
    client = chromadb.CloudClient(
        api_key=API_KEY,
        tenant=TENANT,
        database=DATABASE
    )
    print("✅ Connected to Chroma Cloud!")
    return client

# ============================================================
# Load all company data from JSON files
# ============================================================
def load_all_company_data():
    """Load CUSTOMERS ONLY from CUSTOMERS_ONLY.json (no technology names)"""
    all_companies = []
    
    filepath = 'CUSTOMERS_ONLY.json'
    print(f"📂 Loading {filepath}...")
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Load customers only
    for company_name, company_data in data['customers'].items():
        all_companies.append({
            'company_name': company_name,
            'source_channel': company_data['source'],
            'category': 'customer',
            'use_case': company_data['use_case']
        })
    
    print(f"📊 Loaded {len(all_companies)} customer records")
    return all_companies

# ============================================================
# Save to Chroma
# ============================================================
def save_to_chroma(client, companies):
    """Save company data to Chroma collection"""
    
    # Create or get collection
    collection_name = "competitor_youtube_companies"
    print(f"\n📦 Creating/getting collection: {collection_name}")
    
    try:
        # Try to delete existing collection first
        client.delete_collection(name=collection_name)
        print("   Deleted existing collection")
    except:
        pass
    
    collection = client.create_collection(
        name=collection_name,
        metadata={"description": "Companies extracted from competitor YouTube channels for Chroma GTM"}
    )
    print(f"✅ Collection created: {collection_name}")
    
    # Prepare data for insertion
    documents = []
    metadatas = []
    ids = []
    
    for i, company in enumerate(companies):
        # Create document text for embedding
        doc_text = f"Company: {company['company_name']}. Category: {company['category']}. Source: {company['source_channel']}."
        if 'context' in company:
            doc_text += f" Context: {company['context']}"
        
        documents.append(doc_text)
        metadatas.append({
            'company_name': company['company_name'],
            'source_channel': company['source_channel'],
            'category': company['category'],
            'context': company.get('context', ''),
            'extracted_from': company['extracted_from'],
            'added_date': datetime.now().isoformat()
        })
        ids.append(f"{company['source_channel'].lower()}_{i}")
    
    # Add to collection in batches
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_metas = metadatas[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]
        
        collection.add(
            documents=batch_docs,
            metadatas=batch_metas,
            ids=batch_ids
        )
        print(f"   Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
    
    print(f"\n✅ Successfully saved {len(documents)} company records to Chroma!")
    return collection

# ============================================================
# Create summary collection
# ============================================================
def create_summary_collection(client, companies):
    """Create a summary collection with unique companies"""
    
    collection_name = "gtm_target_companies"
    print(f"\n📦 Creating summary collection: {collection_name}")
    
    try:
        client.delete_collection(name=collection_name)
    except:
        pass
    
    collection = client.create_collection(
        name=collection_name,
        metadata={"description": "Unique target companies for Chroma GTM outreach"}
    )
    
    # Deduplicate companies
    unique_companies = {}
    for company in companies:
        name = company['company_name']
        if name not in unique_companies:
            unique_companies[name] = {
                'company_name': name,
                'sources': [company['source_channel']],
                'categories': [company['category']],
            }
        else:
            if company['source_channel'] not in unique_companies[name]['sources']:
                unique_companies[name]['sources'].append(company['source_channel'])
            if company['category'] not in unique_companies[name]['categories']:
                unique_companies[name]['categories'].append(company['category'])
    
    # Prepare for insertion
    documents = []
    metadatas = []
    ids = []
    
    for i, (name, data) in enumerate(unique_companies.items()):
        doc_text = f"Company: {name}. Found in: {', '.join(data['sources'])}. Categories: {', '.join(data['categories'])}."
        
        documents.append(doc_text)
        metadatas.append({
            'company_name': name,
            'found_in_channels': ', '.join(data['sources']),
            'categories': ', '.join(data['categories']),
            'mention_count': len(data['sources'])
        })
        ids.append(f"company_{i}")
    
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"✅ Created summary with {len(unique_companies)} unique companies")
    return collection, unique_companies

# ============================================================
# Main
# ============================================================
def main():
    print("="*70)
    print("CHROMA GTM - SAVE COMPANY DATA TO CHROMA CLOUD")
    print("="*70)
    
    # Check API key
    if API_KEY == 'YOUR_API_KEY':
        print("\n⚠️  Please set your API key!")
        print("   Option 1: export CHROMA_API_KEY='your-key'")
        print("   Option 2: Edit this file and replace 'YOUR_API_KEY'")
        return
    
    # Connect to Chroma
    client = connect_to_chroma()
    
    # Load data
    companies = load_all_company_data()
    
    if not companies:
        print("❌ No company data found. Run extraction scripts first.")
        return
    
    # Save to Chroma
    save_to_chroma(client, companies)
    
    # Create summary
    summary_collection, unique = create_summary_collection(client, companies)
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"📊 Total records saved: {len(companies)}")
    print(f"🏢 Unique companies: {len(unique)}")
    print(f"📦 Collections created:")
    print(f"   - competitor_youtube_companies (all records)")
    print(f"   - gtm_target_companies (unique companies)")
    
    # Show top companies by mention count
    print(f"\n🔥 Top companies (mentioned in multiple channels):")
    sorted_companies = sorted(unique.items(), key=lambda x: len(x[1]['sources']), reverse=True)
    for name, data in sorted_companies[:15]:
        if len(data['sources']) > 1:
            print(f"   - {name}: {', '.join(data['sources'])}")

if __name__ == "__main__":
    main()
