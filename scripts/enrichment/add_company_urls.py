#!/usr/bin/env python3
"""
Add Company URLs to Chroma Signal List
======================================
Enriches the database with company website URLs.

Run: python3 add_company_urls.py
"""

import json
import chromadb
from datetime import datetime

# Configuration
LOCAL_DB_FILE = 'chroma_signal_companies.json'
API_KEY = 'ck-A1VwR2zrmYsA3YvHqxahBTbmzqkrKB49hZ7UYSckwPfx'
TENANT = 'f23eab93-f8a3-493b-b775-a29c3582dee4'
DATABASE = 'GTM Signal'
COLLECTION_NAME = 'chroma_signal_list'

# Known company URLs - add more as needed
KNOWN_URLS = {
    # Enterprise (Tier 1 from LangChain)
    "Uber": "https://uber.com",
    "LinkedIn": "https://linkedin.com",
    "BlackRock": "https://blackrock.com",
    "JP Morgan": "https://jpmorgan.com",
    "Cisco": "https://cisco.com",
    "Monday.com": "https://monday.com",
    "Box": "https://box.com",
    "Rippling": "https://rippling.com",
    "PagerDuty": "https://pagerduty.com",
    "Rakuten": "https://rakuten.com",
    "Pigment": "https://pigment.com",
    "Vizient": "https://vizient.com",
    "Morningstar": "https://morningstar.com",
    "Modern Treasury": "https://moderntreasury.com",
    "Harvey AI": "https://harvey.ai",
    "11x": "https://11x.ai",
    "Prosper": "https://prosper.com",
    "City of Hope": "https://cityofhope.org",
    "Clay": "https://clay.com",
    "Tabs": "https://tabs.inc",
    "Writer": "https://writer.com",
    "Decagon": "https://decagon.ai",
    "Character.AI": "https://character.ai",
    "Replit": "https://replit.com",
    "Cognition (Devin)": "https://cognition.ai",
    "Factory": "https://factory.ai",
    "Quora/Poe": "https://poe.com",
    "Unify": "https://unify.ai",
    "Outshift (Cisco)": "https://outshift.cisco.com",
    "Shortwave": "https://shortwave.com",
    "Superagent": "https://superagent.sh",
    "Quivr": "https://quivr.app",
    "Plastic Labs": "https://plasticlabs.ai",
    
    # LLM Providers
    "OpenAI": "https://openai.com",
    "Anthropic": "https://anthropic.com",
    "Google": "https://google.com",
    "Meta": "https://meta.com",
    "Mistral": "https://mistral.ai",
    "Cohere": "https://cohere.com",
    "Groq": "https://groq.com",
    "DeepSeek": "https://deepseek.com",
    "Ollama": "https://ollama.ai",
    "Fireworks AI": "https://fireworks.ai",
    
    # Integration Partners
    "Airbyte": "https://airbyte.com",
    "AssemblyAI": "https://assemblyai.com",
    "Exa": "https://exa.ai",
    "CodiumAI": "https://codium.ai",
    "NVIDIA": "https://nvidia.com",
    "n8n": "https://n8n.io",
    "Arcade AI": "https://arcade-ai.com",
    
    # Qdrant Customers
    "Antz AI": "https://antz.ai",
    "Arize AI": "https://arize.com",
    "AskNews": "https://asknews.app",
    "AugmentCode": "https://augmentcode.com",
    "Baseten": "https://baseten.co",
    "Camel AI": "https://camel-ai.org",
    "Cheshire Cat AI": "https://cheshirecat.ai",
    "Cognee": "https://cognee.ai",
    "Delivery Hero": "https://deliveryhero.com",
    "Dust": "https://dust.tt",
    "Equal": "https://equal.ai",
    "GoodData": "https://gooddata.com",
    "Indexify": "https://indexify.io",
    "KI Reply": "https://ki-reply.com",
    "Lettria": "https://lettria.com",
    "Linkup": "https://linkup.so",
    "Quotient": "https://quotient.co",
    "Razroo": "https://razroo.com",
    "Sentrev": "https://sentrev.ai",
    "Superlinked": "https://superlinked.com",
    "Tensorlake": "https://tensorlake.ai",
    "Twelve Labs": "https://twelvelabs.io",
    "Unstructured": "https://unstructured.io",
    "VirtualBrain": "https://virtualbrain.ai",
    "bakdata": "https://bakdata.com",
    "iCompetence": "https://icompetence.ai",
    
    # Qdrant Partners
    "Apache Kafka": "https://kafka.apache.org",
    "Google DeepMind": "https://deepmind.google",
    "Google Gemini": "https://gemini.google.com",
    "Jina AI": "https://jina.ai",
    "Neo4j": "https://neo4j.com",
    "deepset": "https://deepset.ai",
    
    # Weaviate Customers
    "Alltius AI": "https://alltius.ai",
    "Arctic (Snowflake)": "https://snowflake.com",
    "BAIK": "https://baik.ai",
    "Box AI": "https://box.com",
    "Cartesia AI": "https://cartesia.ai",
    "Contextual AI": "https://contextual.ai",
    "Emissary": "https://emissary.ai",
    "FeatureForm": "https://featureform.com",
    "Fine": "https://fine.dev",
    "GPT4All": "https://gpt4all.io",
    "Haize Labs": "https://haizelabs.com",
    "Kapa AI": "https://kapa.ai",
    "Keenious": "https://keenious.com",
    "Kraftful": "https://kraftful.com",
    "Letta AI": "https://letta.com",
    "Masterful AI": "https://masterfulai.com",
    "Mem": "https://mem.ai",
    "Metarank": "https://metarank.ai",
    "Metro AG": "https://metroag.de",
    "Mixpeek": "https://mixpeek.com",
    "MosaicML Cloud": "https://mosaicml.com",
    "Neum AI": "https://neum.ai",
    "Orchest": "https://orchest.io",
    "Patronus AI": "https://patronus.ai",
    "PodcastGPT": "https://podcastgpt.ai",
    "Portkey": "https://portkey.ai",
    "Pyversity": "https://pyversity.com",
    "Super People": "https://superpeople.com",
    "TARS": "https://hellotars.com",
    "Tactic": "https://tactic.fyi",
    "Tactic Generate": "https://tactic.fyi",
    "VectorFlow": "https://vectorflow.dev",
    "Vody": "https://vody.com",
    "WPSolr": "https://wpsolr.com",
    "You.com": "https://you.com",
    "Zencastr": "https://zencastr.com",
    
    # Weaviate Partners
    "AWS": "https://aws.amazon.com",
    "Confluent": "https://confluent.io",
    "GitHub": "https://github.com",
    "MosaicML": "https://mosaicml.com",
    "Neural Magic": "https://neuralmagic.com",
    "Nomic AI": "https://nomic.ai",
    "SAS": "https://sas.com",
    "Vertex AI": "https://cloud.google.com/vertex-ai",
    "Voyage AI": "https://voyageai.com",
    
    # Vespa Customers
    "Vinted": "https://vinted.com",
    
    # Pinecone Customers
    "Notion": "https://notion.so",
    "Zapier": "https://zapier.com",
    "Gong": "https://gong.io",
    "Shopify": "https://shopify.com",
    "Canva": "https://canva.com",
    "Hubspot": "https://hubspot.com",
    "DigitalOcean": "https://digitalocean.com",
    "Calm": "https://calm.com",
    "Convoy": "https://convoy.com",
    "Chipper Cash": "https://chippercash.com",
    
    # AI Tools
    "DSPy": "https://dspy-docs.vercel.app",
    "ColBERT": "https://github.com/stanford-futuredata/ColBERT",
    "MemGPT": "https://memgpt.ai",
    "Nomic": "https://nomic.ai",
    "ColPali": "https://github.com/illuin-tech/colpali",
    "Haystack": "https://haystack.deepset.ai",
    "LangChain": "https://langchain.com",
    "LlamaIndex": "https://llamaindex.ai",
    "Gorilla": "https://gorilla.cs.berkeley.edu",
    "RAGAS": "https://ragas.io",
    "BERTopic": "https://maartengr.github.io/BERTopic",
    "Instructor": "https://instructor-ai.github.io/instructor",
    "LMQL": "https://lmql.ai",
}

def load_db():
    with open(LOCAL_DB_FILE, 'r') as f:
        return json.load(f)

def save_db(db):
    db["metadata"]["last_updated"] = datetime.now().isoformat()
    with open(LOCAL_DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

def add_urls(db):
    """Add URLs to companies that don't have them"""
    companies = db['companies']
    updated = 0
    still_missing = []
    
    for company_id, company in companies.items():
        name = company.get('company_name', '')
        
        # Skip if already has a website
        if company.get('website'):
            continue
        
        # Check if we have a known URL
        if name in KNOWN_URLS:
            company['website'] = KNOWN_URLS[name]
            updated += 1
        else:
            still_missing.append(name)
    
    return db, updated, still_missing

def sync_to_chroma(db):
    """Sync updated database to Chroma Cloud"""
    print("\n🔗 Connecting to Chroma Cloud...")
    client = chromadb.CloudClient(
        api_key=API_KEY,
        tenant=TENANT,
        database=DATABASE
    )
    print("✅ Connected!")
    
    # Delete and recreate collection
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except:
        pass
    
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Chroma Signal List with URLs", "updated": datetime.now().isoformat()}
    )
    
    # Prepare data
    documents = []
    metadatas = []
    ids = []
    
    for company_id, company in db["companies"].items():
        doc_parts = [f"Company: {company['company_name']}"]
        if company.get('description'):
            doc_parts.append(f"Description: {company['description']}")
        if company.get('use_case'):
            doc_parts.append(f"Use Case: {company['use_case']}")
        if company.get('website'):
            doc_parts.append(f"Website: {company['website']}")
        
        documents.append(". ".join(doc_parts))
        
        meta = {
            "company_name": company.get("company_name", ""),
            "website": company.get("website", "") or "",
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
    
    print(f"✅ Synced {len(documents)} companies to Chroma Cloud!")

def main():
    print("="*60)
    print("ADD COMPANY URLs TO CHROMA SIGNAL LIST")
    print("="*60)
    
    # Load database
    db = load_db()
    
    # Count current status
    companies = db['companies']
    with_url = sum(1 for c in companies.values() if c.get('website'))
    without_url = len(companies) - with_url
    
    print(f"\n📊 Current Status:")
    print(f"   Total companies: {len(companies)}")
    print(f"   With URL: {with_url}")
    print(f"   Without URL: {without_url}")
    
    # Add URLs
    print(f"\n🔄 Adding URLs from known list...")
    db, updated, still_missing = add_urls(db)
    
    print(f"\n✅ Added {updated} URLs")
    
    # New counts
    with_url_new = sum(1 for c in db['companies'].values() if c.get('website'))
    without_url_new = len(db['companies']) - with_url_new
    
    print(f"\n📊 Updated Status:")
    print(f"   With URL: {with_url_new}")
    print(f"   Without URL: {without_url_new}")
    
    if still_missing:
        print(f"\n⚠️  Companies still missing URLs ({len(still_missing)}):")
        for name in sorted(still_missing)[:20]:
            print(f"   - {name}")
        if len(still_missing) > 20:
            print(f"   ... and {len(still_missing) - 20} more")
    
    # Save locally
    save_db(db)
    print(f"\n💾 Saved to {LOCAL_DB_FILE}")
    
    # Sync to Chroma
    print("\n" + "-"*60)
    sync = input("Sync to Chroma Cloud? (yes/no): ").strip().lower()
    if sync == 'yes':
        sync_to_chroma(db)

if __name__ == "__main__":
    main()

