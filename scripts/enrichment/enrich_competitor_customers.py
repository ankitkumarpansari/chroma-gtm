#!/usr/bin/env python3
"""
Enrich Competitor Customer Data

Scrapes competitor websites (Pinecone, Qdrant, Weaviate, etc.) to gather
additional information about their customers for Cohort 3 enrichment.

Usage:
    python enrich_competitor_customers.py              # Enrich all companies
    python enrich_competitor_customers.py --company "Notion"  # Enrich specific company
    python enrich_competitor_customers.py --limit 10   # Limit to first N companies
"""

import os
import json
import csv
import argparse
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import requests
except ImportError:
    print("ERROR: Missing requests. Run: pip install requests")
    exit(1)

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
OUTPUT_FILE = BASE_DIR / "competitor_customers_enriched.json"

# Competitor case study/customer pages
COMPETITOR_PAGES = {
    "Pinecone": {
        "customers_url": "https://www.pinecone.io/customers/",
        "case_studies_url": "https://www.pinecone.io/learn/",
    },
    "Qdrant": {
        "customers_url": "https://qdrant.tech/",
        "case_studies_url": "https://qdrant.tech/blog/",
    },
    "Weaviate": {
        "customers_url": "https://weaviate.io/case-studies",
        "case_studies_url": "https://weaviate.io/blog",
    },
    "Milvus": {
        "customers_url": "https://milvus.io/use-cases",
        "case_studies_url": "https://milvus.io/blog",
    },
}


def load_existing_data() -> Dict[str, Any]:
    """Load existing competitor customer data."""
    companies = {}
    
    # Load from competitor_accounts_export.csv
    csv_path = BASE_DIR / "competitor_accounts_export.csv"
    if csv_path.exists():
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                company_name = row.get("clean_name") or row.get("company_name", "")
                if company_name:
                    # Parse website from document field
                    doc = row.get("document", "")
                    website = ""
                    if "Website:" in doc:
                        website = doc.split("Website:")[-1].strip()
                    
                    # Parse use case from document field
                    use_case = ""
                    if "Use Case:" in doc:
                        use_case = doc.split("Use Case:")[-1].split(".")[0].strip()
                    
                    companies[company_name] = {
                        "company_name": company_name,
                        "competitor_db": row.get("competitor_db", ""),
                        "use_case": use_case,
                        "website": website,
                        "source_channel": row.get("source_channel", ""),
                        "added_date": row.get("added_date", ""),
                        # Fields to enrich
                        "industry": "",
                        "company_size": "",
                        "headquarters": "",
                        "description": "",
                        "why_they_chose": "",
                        "case_study_url": "",
                    }
    
    # Load from CUSTOMERS_ONLY.json
    json_path = BASE_DIR / "CUSTOMERS_ONLY.json"
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for company_name, info in data.get("customers", {}).items():
                if company_name not in companies:
                    companies[company_name] = {
                        "company_name": company_name,
                        "competitor_db": info.get("source", ""),
                        "use_case": info.get("use_case", ""),
                        "website": "",
                        "source_channel": info.get("source", ""),
                        "added_date": "",
                        "industry": "",
                        "company_size": "",
                        "headquarters": "",
                        "description": "",
                        "why_they_chose": "",
                        "case_study_url": "",
                    }
    
    return companies


def enrich_with_web_search(company: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich company data using web search.
    
    This is a placeholder - in production you'd use:
    - Clearbit API
    - Apollo.io API
    - Or scrape company websites
    """
    company_name = company.get("company_name", "")
    competitor = company.get("competitor_db", "")
    
    # Known company enrichments (manual data for key companies)
    known_companies = {
        "Notion": {
            "industry": "Productivity Software",
            "company_size": "500-1000",
            "headquarters": "San Francisco, CA",
            "description": "All-in-one workspace for notes, docs, wikis, and project management",
            "why_they_chose": "Semantic search for knowledge base, AI features",
        },
        "Shopify": {
            "industry": "E-commerce",
            "company_size": "10,000+",
            "headquarters": "Ottawa, Canada",
            "description": "E-commerce platform powering millions of online stores",
            "why_they_chose": "Product search, recommendations, Shop AI assistant",
        },
        "Canva": {
            "industry": "Design Software",
            "company_size": "5,000+",
            "headquarters": "Sydney, Australia",
            "description": "Online design and visual communication platform",
            "why_they_chose": "Template search, design recommendations, Magic Design AI",
        },
        "Zapier": {
            "industry": "Automation",
            "company_size": "500-1000",
            "headquarters": "San Francisco, CA (Remote)",
            "description": "Workflow automation connecting 6,000+ apps",
            "why_they_chose": "App discovery, workflow recommendations",
        },
        "HubSpot": {
            "industry": "CRM / Marketing",
            "company_size": "5,000+",
            "headquarters": "Cambridge, MA",
            "description": "CRM platform for marketing, sales, and customer service",
            "why_they_chose": "Content recommendations, chatbot, knowledge base search",
        },
        "DigitalOcean": {
            "industry": "Cloud Infrastructure",
            "company_size": "1,000-5,000",
            "headquarters": "New York, NY",
            "description": "Cloud computing platform for developers",
            "why_they_chose": "Documentation search, support chatbot",
        },
        "Calm": {
            "industry": "Health & Wellness",
            "company_size": "200-500",
            "headquarters": "San Francisco, CA",
            "description": "Mental health and meditation app",
            "why_they_chose": "Content recommendations, personalized meditation suggestions",
        },
        "Morningstar": {
            "industry": "Financial Services",
            "company_size": "10,000+",
            "headquarters": "Chicago, IL",
            "description": "Investment research and management services",
            "why_they_chose": "Intelligence Engine for financial research and analysis",
        },
        "Box": {
            "industry": "Enterprise Software",
            "company_size": "2,000-5,000",
            "headquarters": "Redwood City, CA",
            "description": "Cloud content management and file sharing",
            "why_they_chose": "Box AI for document intelligence and search",
        },
        "Arize AI": {
            "industry": "ML Ops",
            "company_size": "100-200",
            "headquarters": "Berkeley, CA",
            "description": "ML observability and LLM evaluation platform",
            "why_they_chose": "Embedding drift detection, trace search",
        },
        "You.com": {
            "industry": "Search Engine",
            "company_size": "50-100",
            "headquarters": "Palo Alto, CA",
            "description": "AI-powered search engine",
            "why_they_chose": "Core search infrastructure, RAG for AI answers",
        },
        "Delivery Hero": {
            "industry": "Food Delivery",
            "company_size": "10,000+",
            "headquarters": "Berlin, Germany",
            "description": "Global food delivery and quick commerce platform",
            "why_they_chose": "Restaurant and product search optimization",
        },
    }
    
    if company_name in known_companies:
        enrichment = known_companies[company_name]
        company.update({
            "industry": enrichment.get("industry", company.get("industry", "")),
            "company_size": enrichment.get("company_size", company.get("company_size", "")),
            "headquarters": enrichment.get("headquarters", company.get("headquarters", "")),
            "description": enrichment.get("description", company.get("description", "")),
            "why_they_chose": enrichment.get("why_they_chose", company.get("why_they_chose", "")),
        })
    
    return company


def save_enriched_data(companies: Dict[str, Any]) -> None:
    """Save enriched data to JSON file."""
    output = {
        "metadata": {
            "created": datetime.now().isoformat(),
            "total_companies": len(companies),
            "enriched_count": sum(1 for c in companies.values() if c.get("industry")),
        },
        "companies": companies
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nSaved enriched data to: {OUTPUT_FILE}")


def main():
    parser = argparse.ArgumentParser(description="Enrich competitor customer data")
    parser.add_argument("--company", type=str, help="Enrich specific company only")
    parser.add_argument("--limit", type=int, help="Limit to first N companies")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("COMPETITOR CUSTOMER ENRICHMENT")
    print("=" * 60)
    
    # Load existing data
    print("\nLoading existing competitor customer data...")
    companies = load_existing_data()
    print(f"  Found {len(companies)} companies")
    
    # Filter if specific company requested
    if args.company:
        if args.company in companies:
            companies = {args.company: companies[args.company]}
        else:
            print(f"  Company '{args.company}' not found")
            return
    
    # Limit if requested
    if args.limit:
        companies = dict(list(companies.items())[:args.limit])
    
    # Enrich each company
    print("\nEnriching company data...")
    enriched_count = 0
    
    for company_name, company_data in companies.items():
        enriched = enrich_with_web_search(company_data)
        companies[company_name] = enriched
        
        if enriched.get("industry"):
            enriched_count += 1
            print(f"  ✓ {company_name}: {enriched.get('industry')}")
        else:
            print(f"  - {company_name}: (no enrichment data)")
    
    # Save results
    save_enriched_data(companies)
    
    print("\n" + "=" * 60)
    print("ENRICHMENT COMPLETE")
    print("=" * 60)
    print(f"Total companies: {len(companies)}")
    print(f"Enriched: {enriched_count}")


if __name__ == "__main__":
    main()

