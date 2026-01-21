#!/usr/bin/env python3
"""
Prepare NYC Contacts for Attio Sync

Consolidates contacts from:
1. nyc_dinner_top_accounts.csv (primary contacts)
2. AI Engineer speakers (NYC-based)
3. VIP users
4. Sumble enrichment results

Creates:
- nyc_dinner_contacts.csv (all contacts)
- nyc_dinner_companies_final.csv (companies with domains)
- sumble_enrichment_queue.csv (companies needing contact enrichment)

Usage:
    python scripts/sync/prepare_nyc_contacts.py
"""

import csv
import json
import re
import os
from typing import Dict, List, Optional, Set
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NYC_CSV_PATH = os.path.join(BASE_DIR, "data/exports/nyc_dinner_top_accounts.csv")
AI_SPEAKERS_PATH = os.path.join(BASE_DIR, "data/linkedin/ai_engineer_speakers.json")
VIP_USERS_PATH = os.path.join(BASE_DIR, "data/users/vip_users.csv")
SUMBLE_RESULTS_PATH = os.path.join(BASE_DIR, "data/exports/nyc_dinner_enriched_*.json")

OUTPUT_DIR = os.path.join(BASE_DIR, "data/exports")
CONTACTS_OUTPUT = os.path.join(OUTPUT_DIR, "nyc_dinner_contacts.csv")
COMPANIES_OUTPUT = os.path.join(OUTPUT_DIR, "nyc_dinner_companies_final.csv")
ENRICHMENT_QUEUE = os.path.join(OUTPUT_DIR, "sumble_enrichment_queue.csv")
AI_SPEAKERS_OUTPUT = os.path.join(OUTPUT_DIR, "nyc_dinner_ai_speakers.csv")

# NYC-based companies from AI Engineer speakers
NYC_COMPANIES = {
    'blackrock', 'bloomberg', 'morgan stanley', 'jp morgan', 'jane street',
    'ramp', 'the browser company', 'the browser company of new york', 
    'datadog', 'mongodb', 'tinder', 'promptlayer', 'arize', 'brightwave',
    'hex', 'nixtla', 'clerk', 'humanloop', 'hasura', 'lux capital',
    'mastercard', 'writer', 'clay', 'clay gtm', 'perplexity', 'browserbase',
    'south park commons', 'method financial', 'ionic commerce', 'letta',
    'neon', 'stride', 'galileo', 'vercel', 'two sigma', 'd.e. shaw',
    'citadel', 'point72', 'bridgewater'
}

# Domain mappings for common companies
COMPANY_DOMAINS = {
    'blackrock': 'blackrock.com',
    'jp morgan': 'jpmorgan.com',
    'morgan stanley': 'morganstanley.com',
    'bloomberg': 'bloomberg.com',
    'jane street': 'janestreet.com',
    'honeyhive': 'honeyhive.ai',
    'monk.io': 'monk.io',
    'datafold': 'datafold.com',
    'shaped': 'shaped.ai',
    'ramp': 'ramp.com',
    'the browser company': 'thebrowser.company',
    'rogo': 'rogo.ai',
    'koyfin': 'koyfin.com',
    'spotnana': 'spotnana.com',
    'peloton': 'onepeloton.com',
    'peloton interactive': 'onepeloton.com',
    'clay': 'clay.com',
    'harvey ai': 'harvey.ai',
    'digitalocean': 'digitalocean.com',
    'datadog': 'datadoghq.com',
    'mongodb': 'mongodb.com',
    'notion': 'notion.so',
    'attentive': 'attentive.com',
    'lemonade': 'lemonade.com',
    'two sigma': 'twosigma.com',
    'd.e. shaw': 'deshaw.com',
    'citadel': 'citadel.com',
    'point72': 'point72.com',
    'bridgewater': 'bridgewater.com',
    'hebbia': 'hebbia.ai',
    'alphasense': 'alpha-sense.com',
    'promptlayer': 'promptlayer.com',
    'arize': 'arize.com',
    'brightwave': 'brightwave.io',
    'humanloop': 'humanloop.com',
    'hasura': 'hasura.io',
    'mastercard': 'mastercard.com',
    'writer': 'writer.com',
    'perplexity': 'perplexity.ai',
    'galileo': 'rungalileo.io',
    'vercel': 'vercel.com',
    'hex': 'hex.tech',
    'nixtla': 'nixtla.io',
    'clerk': 'clerk.com',
    'letta': 'letta.com',
    'neon': 'neon.tech',
    'tinder': 'tinder.com',
    'lux capital': 'luxcapital.com',
    'compound vc': 'compoundvc.com',
    'xai': 'x.ai',
    'accenture': 'accenture.com',
    'deloitte': 'deloitte.com',
    'ibm': 'ibm.com',
    'salesforce': 'salesforce.com',
    'optum': 'optum.com',
    'travelers': 'travelers.com',
    'oscar health': 'hioscar.com',
    'spring health': 'springhealth.com',
    'brex': 'brex.com',
    'justworks': 'justworks.com',
    'sprinklr': 'sprinklr.com',
    'compass': 'compass.com',
    'dataminr': 'dataminr.com',
    'yipitdata': 'yipitdata.com',
}


def extract_domain_from_email(email: str) -> Optional[str]:
    """Extract domain from email address."""
    if not email or '@' not in email:
        return None
    return email.split('@')[1].lower()


def normalize_company_name(name: str) -> str:
    """Normalize company name for matching."""
    return re.sub(r'[^a-z0-9\s]', '', name.lower()).strip()


def get_company_domain(company: str, email: str = None) -> Optional[str]:
    """Get domain for a company."""
    # Try email first
    if email:
        domain = extract_domain_from_email(email)
        if domain and domain not in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']:
            return domain
    
    # Try lookup
    normalized = normalize_company_name(company)
    for key, domain in COMPANY_DOMAINS.items():
        if key in normalized or normalized in key:
            return domain
    
    return None


def calculate_icp_score(contact: Dict) -> int:
    """Calculate ICP score (1-10) based on title and company priority."""
    score = 5  # Base score
    
    title = (contact.get('title') or '').lower()
    priority = (contact.get('priority') or '').upper()
    category = (contact.get('category') or '').lower()
    
    # Title scoring
    if any(t in title for t in ['cto', 'chief technology', 'chief ai', 'chief data', 'ceo', 'founder']):
        score += 3
    elif any(t in title for t in ['vp', 'vice president', 'head of']):
        score += 2
    elif any(t in title for t in ['director', 'principal', 'staff']):
        score += 1
    elif any(t in title for t in ['engineer', 'developer', 'scientist']):
        score += 0
    
    # Priority scoring
    if priority == 'CRITICAL':
        score += 2
    elif priority == 'HIGH':
        score += 1
    
    # Category scoring
    if 'active' in category or 'vip' in category:
        score += 1
    if 'competitor' in category:
        score += 1  # Displacement opportunity
    
    return min(10, max(1, score))


def load_csv_contacts() -> List[Dict]:
    """Load contacts from NYC dinner CSV."""
    contacts = []
    companies = {}
    
    with open(NYC_CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            company = row.get('Company', '').strip()
            if not company:
                continue
            
            # Store company info
            if company not in companies:
                companies[company] = {
                    'company': company,
                    'category': row.get('Category', ''),
                    'tier': row.get('Tier', ''),
                    'priority': row.get('Priority', ''),
                    'why_selected': row.get('Why Selected', ''),
                    'tech_stack': row.get('Tech Stack', ''),
                    'notes': row.get('Notes', ''),
                }
            
            # Parse contacts (may have multiple)
            contact_names = row.get('Contact Name', '').split(',')
            titles = row.get('Title', '').split(',')
            emails = row.get('Email', '').split(',')
            linkedin = row.get('LinkedIn', '')
            
            for i, name in enumerate(contact_names):
                name = name.strip()
                if not name or name == 'TBD' or name.startswith('TBD '):
                    continue
                
                title = titles[i].strip() if i < len(titles) else ''
                email = emails[i].strip() if i < len(emails) else ''
                
                # Get domain
                domain = get_company_domain(company, email)
                
                contact = {
                    'name': name,
                    'company': company,
                    'domain': domain,
                    'title': title,
                    'email': email if '@' in str(email) else '',
                    'linkedin': linkedin if i == 0 else '',  # LinkedIn usually for first contact
                    'source': 'CSV',
                    'category': row.get('Category', ''),
                    'tier': row.get('Tier', ''),
                    'priority': row.get('Priority', ''),
                }
                contact['icp_score'] = calculate_icp_score(contact)
                contacts.append(contact)
    
    return contacts, companies


def load_ai_engineer_speakers() -> List[Dict]:
    """Load NYC-based AI Engineer speakers."""
    contacts = []
    
    if not os.path.exists(AI_SPEAKERS_PATH):
        print(f"⚠️ AI speakers file not found: {AI_SPEAKERS_PATH}")
        return contacts
    
    with open(AI_SPEAKERS_PATH, 'r', encoding='utf-8') as f:
        speakers = json.load(f)
    
    for speaker in speakers:
        company = speaker.get('company', '').lower()
        
        # Check if NYC-based
        is_nyc = False
        for nyc_co in NYC_COMPANIES:
            if nyc_co in company:
                is_nyc = True
                break
        
        if not is_nyc:
            continue
        
        name = speaker.get('name', '')
        if not name or name in ['TBD', 'NLW']:  # Skip placeholders
            continue
        
        linkedin = speaker.get('linkedin_url') or speaker.get('linkedin') or ''
        # Clean up non-LinkedIn URLs
        if linkedin and 'linkedin.com' not in linkedin:
            linkedin = ''
        
        contact = {
            'name': name,
            'company': speaker.get('company', ''),
            'domain': get_company_domain(speaker.get('company', '')),
            'title': speaker.get('role') or 'AI Engineer Speaker',
            'email': speaker.get('email', ''),
            'linkedin': linkedin,
            'source': 'AI Engineer Speaker',
            'talk_title': speaker.get('video', ''),
            'category': 'AI Engineer Speaker',
            'tier': '3',
            'priority': 'HIGH',
        }
        contact['icp_score'] = calculate_icp_score(contact)
        contacts.append(contact)
    
    return contacts


def load_vip_users() -> List[Dict]:
    """Load VIP users with NYC company domains."""
    contacts = []
    
    if not os.path.exists(VIP_USERS_PATH):
        print(f"⚠️ VIP users file not found: {VIP_USERS_PATH}")
        return contacts
    
    # NYC company domains to look for
    nyc_domains = set(COMPANY_DOMAINS.values())
    
    with open(VIP_USERS_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '')
            domain = extract_domain_from_email(email)
            
            if not domain:
                continue
            
            # Check if NYC company
            if domain in nyc_domains:
                contact = {
                    'name': '',  # Will need Sumble enrichment
                    'company': '',  # Will need lookup
                    'domain': domain,
                    'title': '',
                    'email': email,
                    'linkedin': '',
                    'source': 'VIP User',
                    'category': 'VIP Customer',
                    'tier': '2',
                    'priority': 'HIGH',
                    'vip_score': row.get('vip_score', ''),
                }
                contact['icp_score'] = 7  # VIP users get high score
                contacts.append(contact)
    
    return contacts


def deduplicate_contacts(contacts: List[Dict]) -> List[Dict]:
    """Deduplicate contacts by email or name+company."""
    seen_emails = set()
    seen_name_company = set()
    unique = []
    
    # Sort by source priority: CSV > AI Speaker > VIP
    source_priority = {'CSV': 0, 'AI Engineer Speaker': 1, 'VIP User': 2, 'Sumble': 3}
    contacts.sort(key=lambda x: source_priority.get(x.get('source', ''), 99))
    
    for contact in contacts:
        email = contact.get('email', '').lower()
        name = contact.get('name', '').lower()
        company = contact.get('company', '').lower()
        
        # Check email
        if email and email in seen_emails:
            continue
        
        # Check name+company
        key = f"{name}|{company}"
        if name and company and key in seen_name_company:
            continue
        
        if email:
            seen_emails.add(email)
        if name and company:
            seen_name_company.add(key)
        
        unique.append(contact)
    
    return unique


def identify_enrichment_needs(contacts: List[Dict], companies: Dict) -> List[Dict]:
    """Identify companies/contacts that need Sumble enrichment."""
    needs_enrichment = []
    
    # Companies without any contacts
    companies_with_contacts = {c.get('company', '').lower() for c in contacts if c.get('name')}
    
    for company, info in companies.items():
        normalized = company.lower()
        if normalized not in companies_with_contacts:
            domain = get_company_domain(company)
            needs_enrichment.append({
                'company': company,
                'domain': domain or 'NEEDS_DOMAIN',
                'category': info.get('category', ''),
                'tier': info.get('tier', ''),
                'priority': info.get('priority', ''),
                'reason': 'No contacts found',
            })
    
    # Contacts without email or title
    for contact in contacts:
        if contact.get('name') and (not contact.get('email') or not contact.get('title')):
            domain = contact.get('domain') or get_company_domain(contact.get('company', ''))
            needs_enrichment.append({
                'company': contact.get('company', ''),
                'domain': domain or 'NEEDS_DOMAIN',
                'name': contact.get('name', ''),
                'linkedin': contact.get('linkedin', ''),
                'category': contact.get('category', ''),
                'tier': contact.get('tier', ''),
                'priority': contact.get('priority', ''),
                'reason': 'Missing email/title',
            })
    
    return needs_enrichment


def main():
    print("=" * 60)
    print("🗽 NYC CONTACTS PREPARATION")
    print("=" * 60)
    
    # Load contacts from all sources
    print("\n📂 Loading contacts from CSV...")
    csv_contacts, companies = load_csv_contacts()
    print(f"   Found {len(csv_contacts)} contacts from {len(companies)} companies")
    
    print("\n🎤 Loading AI Engineer speakers...")
    speaker_contacts = load_ai_engineer_speakers()
    print(f"   Found {len(speaker_contacts)} NYC-based speakers")
    
    print("\n⭐ Loading VIP users...")
    vip_contacts = load_vip_users()
    print(f"   Found {len(vip_contacts)} VIP contacts")
    
    # Combine and deduplicate
    all_contacts = csv_contacts + speaker_contacts + vip_contacts
    print(f"\n📊 Total contacts before dedup: {len(all_contacts)}")
    
    unique_contacts = deduplicate_contacts(all_contacts)
    print(f"   After deduplication: {len(unique_contacts)}")
    
    # Identify enrichment needs
    enrichment_queue = identify_enrichment_needs(unique_contacts, companies)
    print(f"\n🔍 Contacts needing Sumble enrichment: {len(enrichment_queue)}")
    
    # Save contacts CSV
    print(f"\n💾 Saving contacts to {CONTACTS_OUTPUT}...")
    contact_fields = [
        'name', 'company', 'domain', 'title', 'email', 'linkedin',
        'source', 'category', 'tier', 'priority', 'icp_score', 'talk_title'
    ]
    with open(CONTACTS_OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=contact_fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(unique_contacts)
    
    # Save companies CSV
    print(f"💾 Saving companies to {COMPANIES_OUTPUT}...")
    company_fields = ['company', 'domain', 'category', 'tier', 'priority', 'why_selected', 'tech_stack', 'notes']
    company_rows = []
    for name, info in companies.items():
        info['company'] = name
        info['domain'] = get_company_domain(name)
        company_rows.append(info)
    
    with open(COMPANIES_OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=company_fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(company_rows)
    
    # Save enrichment queue
    print(f"💾 Saving enrichment queue to {ENRICHMENT_QUEUE}...")
    enrichment_fields = ['company', 'domain', 'name', 'linkedin', 'category', 'tier', 'priority', 'reason']
    with open(ENRICHMENT_QUEUE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=enrichment_fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(enrichment_queue)
    
    # Save AI speakers separately
    print(f"💾 Saving AI speakers to {AI_SPEAKERS_OUTPUT}...")
    with open(AI_SPEAKERS_OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=contact_fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(speaker_contacts)
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    print(f"Total unique contacts: {len(unique_contacts)}")
    print(f"  - From CSV: {len([c for c in unique_contacts if c.get('source') == 'CSV'])}")
    print(f"  - AI Speakers: {len([c for c in unique_contacts if c.get('source') == 'AI Engineer Speaker'])}")
    print(f"  - VIP Users: {len([c for c in unique_contacts if c.get('source') == 'VIP User'])}")
    print(f"\nCompanies: {len(companies)}")
    print(f"Enrichment needed: {len(enrichment_queue)}")
    
    # ICP Score distribution
    scores = [c.get('icp_score', 0) for c in unique_contacts]
    print(f"\nICP Score distribution:")
    print(f"  - Score 8-10 (Critical): {len([s for s in scores if s >= 8])}")
    print(f"  - Score 6-7 (High): {len([s for s in scores if 6 <= s < 8])}")
    print(f"  - Score 4-5 (Medium): {len([s for s in scores if 4 <= s < 6])}")
    print(f"  - Score 1-3 (Low): {len([s for s in scores if s < 4])}")
    
    print("\n✅ Files created:")
    print(f"   {CONTACTS_OUTPUT}")
    print(f"   {COMPANIES_OUTPUT}")
    print(f"   {ENRICHMENT_QUEUE}")
    print(f"   {AI_SPEAKERS_OUTPUT}")
    
    return unique_contacts, companies, enrichment_queue


if __name__ == "__main__":
    main()

