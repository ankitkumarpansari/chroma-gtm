#!/usr/bin/env python3
"""
Update Chroma database with all latest data
Run: python3 update_chroma_data.py
"""

import json
from datetime import datetime
from chroma_customer_db import ChromaCustomerDB

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    print("=" * 60)
    print("UPDATING CHROMA DATABASE WITH LATEST DATA")
    print("=" * 60)
    
    db = ChromaCustomerDB()
    
    # Get existing companies to avoid duplicates
    existing = db.get_all_customers()
    existing_names = {c.get('company_name', '').lower() for c in existing}
    print(f"\nExisting records: {len(existing)}")
    
    added_count = 0
    skipped_count = 0
    
    # 1. Load VERIFIED_COMPANIES_CLEAN.json
    print("\n--- Loading VERIFIED_COMPANIES_CLEAN.json ---")
    verified = load_json('VERIFIED_COMPANIES_CLEAN.json')
    
    # Add customers
    for company, data in verified.get('customers', {}).items():
        if company.lower() not in existing_names:
            db.add_customer(
                company_name=company,
                category="prospect",
                source=f"youtube_{data.get('source', 'unknown')}",
                vector_db_used=data.get('source'),
                notes=data.get('context', data.get('use_case', ''))
            )
            existing_names.add(company.lower())
            added_count += 1
        else:
            skipped_count += 1
    
    # Add partners
    for company, data in verified.get('partners', {}).items():
        if company.lower() not in existing_names:
            sources = ', '.join(data.get('sources', []))
            db.add_customer(
                company_name=company,
                category="partner",
                source="youtube_research",
                notes=f"Type: {data.get('type', '')}. Sources: {sources}"
            )
            existing_names.add(company.lower())
            added_count += 1
        else:
            skipped_count += 1
    
    # 2. Load vector_db_leads (job postings data)
    print("\n--- Loading vector_db_leads_20251210_153301.json ---")
    try:
        leads = load_json('vector_db_leads_20251210_153301.json')
        for lead in leads:
            if lead.get('match_status') == 'matched':
                company = lead.get('name', '')
                if company and company.lower() not in existing_names:
                    # Extract job posting info
                    job_info = lead.get('output', {}).get('has_vector_db_job_posting', {}).get('value', '')
                    
                    db.add_customer(
                        company_name=company,
                        category="lead",
                        source="job_postings",
                        source_url=lead.get('url', ''),
                        notes=f"{lead.get('description', '')[:200]}..."
                    )
                    existing_names.add(company.lower())
                    added_count += 1
                else:
                    skipped_count += 1
    except Exception as e:
        print(f"  Error loading leads: {e}")
    
    # 3. Load competitor company files
    competitor_files = [
        ('qdrant_COMPANIES_FINAL.json', 'Qdrant'),
        ('weaviate_COMPANIES_FINAL.json', 'Weaviate'),
        ('vespa_COMPANIES_FINAL.json', 'Vespa'),
        ('langchain_COMPANIES_FINAL.json', 'LangChain'),
    ]
    
    for filename, vector_db in competitor_files:
        print(f"\n--- Loading {filename} ---")
        try:
            data = load_json(filename)
            companies = data.get('companies', data)
            
            for company in companies.get('customers', []):
                name = company if isinstance(company, str) else company.get('name', '')
                if name and name.lower() not in existing_names:
                    db.add_customer(
                        company_name=name,
                        category="prospect",
                        source=f"youtube_{vector_db.lower()}",
                        notes=f"Uses {vector_db}"
                    )
                    # Update with vector_db info
                    db.update_customer(name, {"vector_db_used": vector_db})
                    existing_names.add(name.lower())
                    added_count += 1
                else:
                    skipped_count += 1
        except FileNotFoundError:
            print(f"  File not found: {filename}")
        except Exception as e:
            print(f"  Error: {e}")
    
    # Final count
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Added: {added_count}")
    print(f"Skipped (duplicates): {skipped_count}")
    print(f"Total records now: {db.collection.count()}")

if __name__ == "__main__":
    main()




