#!/usr/bin/env python3
"""
Google Sheets Sync for Chroma GTM

Syncs customer data from local JSON/CSV files to Google Sheets with separate
tabs per cohort, matching the HubSpot cohort strategy.

Features:
- Data sanitization (URL cleaning, name standardization, email validation)
- Cross-cohort deduplication
- Status dropdown for tracking outreach
- Formatted headers and data validation

Cohorts:
1. Current Chroma Customers (HIGHEST PRIORITY - Q1 Revenue)
2. In-Market Companies (AI hiring signals, AI-native companies)
3. Competitor Customers (Keep warm, follow up)
4. SI Partners (Partnership program)

Usage:
    python google_sheets_sync.py              # Full sync (all cohorts)
    python google_sheets_sync.py --cohort 1   # Sync specific cohort only
    python google_sheets_sync.py --dry-run    # Preview without pushing
    python google_sheets_sync.py --list       # List current sheet stats

Setup:
    1. Follow credentials/README.md to set up Google Cloud
    2. Add GOOGLE_SHEET_ID to your .env file
    3. Run: pip install gspread google-auth
"""

import os
import json
import csv
import argparse
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

try:
    import gspread
    from google.oauth2.service_account import Credentials
    from gspread_formatting import DataValidationRule, BooleanCondition, set_data_validation_for_cell_range
except ImportError:
    print("ERROR: Missing dependencies. Run: pip install gspread google-auth gspread-formatting")
    exit(1)

from dotenv import load_dotenv

# Import sanitization functions
from sanitize import (
    clean_url,
    clean_linkedin_url,
    standardize_company_name,
    standardize_person_name,
    validate_email,
    normalize_company_for_matching
)

load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path(__file__).parent
CREDENTIALS_FILE = os.getenv(
    "GOOGLE_SHEETS_CREDENTIALS_FILE",
    str(BASE_DIR / "credentials" / "google_service_account.json")
)
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

# Google Sheets API scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Tab names for each cohort
TAB_NAMES = {
    "home": "Home",
    1: "Cohort 1: Current Customers",
    "1.2": "Cohort 1.2: Business Users",
    "1.3": "Cohort 1.3: All Users",
    2: "Cohort 2: In-Market",
    3: "Cohort 3: Competitors",
    4: "Cohort 4: SI Partners",
    "vip": "VIP Users",
    "dashboard": "Dashboard"
}

# Status options for dropdown
STATUS_OPTIONS = [
    "New",
    "Contacted",
    "Qualified",
    "Meeting Scheduled",
    "Closed Won",
    "Closed Lost"
]

# Column headers for each cohort (with Status column added)
COHORT_HEADERS = {
    1: [
        "Company", "Domain", "Email", "Contact Name", "Job Title", "Location",
        "LinkedIn", "Lead Score", "Is VIP", "Status", "Notes"
    ],
    "1.2": [
        "Company", "Domain", "Email", "User ID", "Created At", "Status", "Notes"
    ],
    "1.3": [
        "Company", "Domain", "Email", "User ID", "Created At", "Email Type", "Status", "Notes"
    ],
    2: [
        "Company", "Website", "Tier", "Category", "Signal Strength",
        "Use Case", "Source", "Status", "Added Date", "Notes"
    ],
    3: [
        "Company", "Current Vector DB", "Industry", "Company Size", "Headquarters",
        "Use Case", "Why They Chose", "Website", "Status", "Added Date", "Notes"
    ],
    4: [
        "Company", "SI Type", "Email", "Contact Name", "Title",
        "LinkedIn", "Score", "Status", "Notes"
    ],
    "vip": [
        "Company", "Domain", "Email", "User ID", "Last Active", "VIP Score",
        "Status", "Notes"
    ],
    "dashboard": [
        "Metric", "Value", "Last Updated"
    ]
}

# Column types for sanitization (index -> type)
# Types: 'company', 'email', 'url', 'linkedin', 'person', 'text'
COHORT_COLUMN_TYPES = {
    1: {0: 'company', 2: 'email', 3: 'person', 6: 'linkedin'},
    "1.2": {0: 'company', 2: 'email'},
    "1.3": {0: 'company', 2: 'email'},
    2: {0: 'company', 1: 'url'},
    3: {0: 'company', 7: 'url'},
    4: {0: 'company', 2: 'email', 3: 'person', 5: 'linkedin'},
    "vip": {0: 'company', 2: 'email'}
}

# Status column index for each cohort
STATUS_COLUMN_INDEX = {
    1: 9,  # Column J (updated for new columns)
    "1.2": 5,  # Column F
    "1.3": 6,  # Column G
    2: 7,  # Column H
    3: 8,  # Column I (updated for new columns)
    4: 7,  # Column H
    "vip": 6  # Column G
}

# Status colors for conditional formatting
STATUS_COLORS = {
    "New": {"red": 0.85, "green": 0.85, "blue": 0.85},           # Light gray
    "Contacted": {"red": 0.68, "green": 0.85, "blue": 0.90},     # Light blue
    "Qualified": {"red": 0.56, "green": 0.77, "blue": 0.49},     # Green
    "Meeting Scheduled": {"red": 1.0, "green": 0.85, "blue": 0.4}, # Yellow/Gold
    "Closed Won": {"red": 0.26, "green": 0.62, "blue": 0.28},    # Dark green
    "Closed Lost": {"red": 0.90, "green": 0.49, "blue": 0.45},   # Red
}


# =============================================================================
# DATA LOADERS (with sanitization)
# =============================================================================

def load_json_file(filepath: str) -> Optional[Dict]:
    """Load a JSON file and return its contents."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"  Warning: File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"  Warning: Invalid JSON in {filepath}: {e}")
        return None


def load_csv_file(filepath: str) -> Optional[List[Dict]]:
    """Load a CSV file and return its contents as list of dicts."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        print(f"  Warning: File not found: {filepath}")
        return None


def sanitize_row(row: List[str], column_types: Dict[int, str]) -> List[str]:
    """Sanitize a single row based on column types."""
    result = []
    for i, value in enumerate(row):
        col_type = column_types.get(i, 'text')
        if col_type == 'company':
            result.append(standardize_company_name(value))
        elif col_type == 'email':
            result.append(validate_email(value))
        elif col_type == 'url':
            result.append(clean_url(value))
        elif col_type == 'linkedin':
            result.append(clean_linkedin_url(value))
        elif col_type == 'person':
            result.append(standardize_person_name(value))
        else:
            result.append(str(value).strip() if value else "")
    return result


def load_cohort_1_data() -> List[List[str]]:
    """
    Load Cohort 1: Current Chroma Customers
    
    Sources:
    - all_business_users.csv (all business users who signed up)
    
    Deduplicates by email to get unique users.
    """
    print("Loading Cohort 1 data (Current Customers)...")
    rows = []
    seen_emails = set()
    
    # Load all business users from CSV
    csv_data = load_csv_file(BASE_DIR / "all_business_users.csv")
    if csv_data:
        for user in csv_data:
            email = user.get("email", "").strip().lower()
            
            # Skip duplicates (same email)
            if not email or email in seen_emails:
                continue
            seen_emails.add(email)
            
            # Get company name (prefer enriched_company, fallback to domain)
            company = user.get("enriched_company", "").strip()
            domain = user.get("domain", "").strip()
            if not company:
                # Use domain as company name (capitalize first letter)
                company = domain.split('.')[0].title() if domain else ""
            
            # Determine VIP status
            is_vip = user.get("is_vip", "").strip().lower() == "true"
            
            row = [
                company,
                domain,
                email,
                user.get("name", "").strip(),
                user.get("enriched_job_title", "").strip(),
                user.get("enriched_location", "").strip(),
                user.get("enriched_linkedin_url", "").strip(),
                user.get("lead_score", "").strip(),
                "Yes" if is_vip else "No",
                "New",  # Status - default to New
                ""  # Notes
            ]
            # Sanitize the row
            sanitized = sanitize_row(row, COHORT_COLUMN_TYPES[1])
            rows.append(sanitized)
    
    print(f"  Loaded {len(rows)} unique users for Cohort 1")
    return rows


# Personal email domains to filter out
PERSONAL_EMAIL_DOMAINS = {
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com',
    'live.com', 'aol.com', 'protonmail.com', 'mail.com', 'ymail.com',
    'msn.com', 'googlemail.com', 'qq.com', '163.com', '126.com',
    'proton.me', 'tutanota.com', 'zoho.com', 'fastmail.com', 'hey.com',
    'me.com', 'mac.com', 'inbox.com', 'gmx.com', 'gmx.de', 'web.de',
    'yandex.com', 'yandex.ru', 'mail.ru', 'rambler.ru', 'seznam.cz',
    'naver.com', 'daum.net', 'hanmail.net', 'sina.com', 'sina.cn',
    'rediffmail.com', 'aim.com', 'att.net', 'sbcglobal.net', 'verizon.net',
    'comcast.net', 'cox.net', 'charter.net', 'earthlink.net', 'juno.com',
    'bellsouth.net', 'btinternet.com', 'virginmedia.com', 'sky.com',
    'orange.fr', 'free.fr', 'laposte.net', 'wanadoo.fr', 'sfr.fr',
    't-online.de', 'freenet.de', 'arcor.de', 'libero.it', 'virgilio.it',
    'alice.it', 'tiscali.it', 'tin.it', 'telenet.be', 'ziggo.nl',
    'xs4all.nl', 'kpnmail.nl', 'uol.com.br', 'bol.com.br', 'terra.com.br',
    'ig.com.br', 'globo.com', 'r7.com'
}


def is_business_email(email: str) -> bool:
    """Check if email is a business email (not personal)."""
    if not email or '@' not in email:
        return False
    domain = email.split('@')[-1].lower()
    return domain not in PERSONAL_EMAIL_DOMAINS


def load_cohort_1_2_data() -> List[List[str]]:
    """
    Load Cohort 1.2: New Users (Business Emails Only)
    
    Sources:
    - export (3).csv (all users from export)
    
    Filters out personal email domains (Gmail, Yahoo, etc.)
    """
    print("Loading Cohort 1.2 data (New Users - Business Only)...")
    rows = []
    seen_emails = set()
    
    csv_data = load_csv_file(BASE_DIR / "export (3).csv")
    if csv_data:
        for user in csv_data:
            # The column name is "Person.display_name" which contains the email
            email = user.get("Person.display_name", "").strip().lower()
            
            # Skip if not a business email
            if not is_business_email(email):
                continue
            
            # Skip duplicates
            if email in seen_emails:
                continue
            seen_emails.add(email)
            
            # Extract domain from email
            domain = email.split('@')[-1] if '@' in email else ""
            
            # Get company name from domain
            company = domain.split('.')[0].title() if domain else ""
            
            # Format created_at date
            created_at = user.get("created_at", "").strip()
            if created_at and ' ' in created_at:
                created_at = created_at.split(' ')[0]  # Just the date part
            
            row = [
                company,
                domain,
                email,
                user.get("Person.id", "").strip(),
                created_at,
                "New",  # Status
                ""  # Notes
            ]
            # Sanitize the row
            sanitized = sanitize_row(row, COHORT_COLUMN_TYPES["1.2"])
            rows.append(sanitized)
    
    print(f"  Loaded {len(rows)} business users for Cohort 1.2")
    return rows


def load_cohort_1_3_data(existing_emails: set = None) -> List[List[str]]:
    """
    Load Cohort 1.3: All Users (including personal emails)
    
    Sources:
    - export (3).csv (all users from export)
    
    Excludes emails already in Cohort 1 and Cohort 1.2 to avoid duplicates.
    """
    print("Loading Cohort 1.3 data (All Users)...")
    rows = []
    seen_emails = existing_emails.copy() if existing_emails else set()
    skipped_duplicates = 0
    
    csv_data = load_csv_file(BASE_DIR / "export (3).csv")
    if csv_data:
        for user in csv_data:
            # The column name is "Person.display_name" which contains the email
            email = user.get("Person.display_name", "").strip().lower()
            
            if not email or '@' not in email:
                continue
            
            # Skip duplicates (already in Cohort 1 or 1.2)
            if email in seen_emails:
                skipped_duplicates += 1
                continue
            seen_emails.add(email)
            
            # Extract domain from email
            domain = email.split('@')[-1] if '@' in email else ""
            
            # Get company name from domain
            company = domain.split('.')[0].title() if domain else ""
            
            # Determine email type
            email_type = "Personal" if not is_business_email(email) else "Business"
            
            # Format created_at date
            created_at = user.get("created_at", "").strip()
            if created_at and ' ' in created_at:
                created_at = created_at.split(' ')[0]  # Just the date part
            
            row = [
                company,
                domain,
                email,
                user.get("Person.id", "").strip(),
                created_at,
                email_type,
                "New",  # Status
                ""  # Notes
            ]
            # Sanitize the row
            sanitized = sanitize_row(row, COHORT_COLUMN_TYPES["1.3"])
            rows.append(sanitized)
    
    print(f"  Loaded {len(rows)} users for Cohort 1.3 (skipped {skipped_duplicates} duplicates)")
    return rows


def load_cohort_2_data() -> List[List[str]]:
    """
    Load Cohort 2: In-Market Companies
    
    Sources:
    - chroma_signal_companies.json (AI hiring signals, in-market companies)
    
    Filter: tier 1-2, high signal strength, enterprise/ai_native categories
    """
    print("Loading Cohort 2 data (In-Market Companies)...")
    rows = []
    
    data = load_json_file(BASE_DIR / "chroma_signal_companies.json")
    if data and "companies" in data:
        for company_id, company in data["companies"].items():
            # Filter for in-market signals (not competitor customers)
            category = company.get("category", "")
            tier = company.get("tier", "")
            
            # Skip competitor customers (they go to Cohort 3)
            if category == "competitor_customer":
                continue
            
            # Include tier 1-2 companies with enterprise/ai_native categories
            if tier in ["1", "2"] or category in ["enterprise", "ai_native", "startup"]:
                row = [
                    company.get("company_name", ""),
                    company.get("website", ""),
                    tier,
                    category,
                    company.get("signal_strength", ""),
                    company.get("use_case", ""),
                    company.get("source_channel", ""),
                    "New",  # Status
                    company.get("added_date", ""),
                    ""  # Notes
                ]
                # Sanitize the row
                sanitized = sanitize_row(row, COHORT_COLUMN_TYPES[2])
                rows.append(sanitized)
    
    print(f"  Loaded {len(rows)} companies for Cohort 2")
    return rows


def load_cohort_3_data() -> List[List[str]]:
    """
    Load Cohort 3: Competitor Customers
    
    Sources:
    - competitor_customers_enriched.json (enriched data with industry, size, etc.)
    - competitor_accounts_export.csv (fallback)
    - CUSTOMERS_ONLY.json (fallback)
    """
    print("Loading Cohort 3 data (Competitor Customers)...")
    rows = []
    seen_companies = set()
    
    # Try to load enriched data first
    enriched_data = load_json_file(BASE_DIR / "competitor_customers_enriched.json")
    enriched_companies = {}
    if enriched_data and "companies" in enriched_data:
        enriched_companies = enriched_data["companies"]
        print(f"  Found enriched data for {len(enriched_companies)} companies")
    
    # Load from competitor_accounts_export.csv
    csv_data = load_csv_file(BASE_DIR / "competitor_accounts_export.csv")
    if csv_data:
        for row_data in csv_data:
            company_name = row_data.get("clean_name") or row_data.get("company_name", "")
            normalized = normalize_company_for_matching(company_name)
            if normalized and normalized not in seen_companies:
                seen_companies.add(normalized)
                
                # Get enriched data if available
                enriched = enriched_companies.get(company_name, {})
                
                # Parse use case and website from document field
                doc = row_data.get("document", "")
                use_case = doc.split("Use Case: ")[-1].split(".")[0] if "Use Case:" in doc else ""
                website = doc.split("Website: ")[-1].strip() if "Website:" in doc else ""
                
                row = [
                    company_name,
                    row_data.get("competitor_db", ""),
                    enriched.get("industry", ""),
                    enriched.get("company_size", ""),
                    enriched.get("headquarters", ""),
                    enriched.get("use_case") or use_case,
                    enriched.get("why_they_chose", ""),
                    enriched.get("website") or website,
                    "New",  # Status
                    row_data.get("added_date", ""),
                    ""  # Notes
                ]
                sanitized = sanitize_row(row, COHORT_COLUMN_TYPES[3])
                rows.append(sanitized)
    
    # Load from CUSTOMERS_ONLY.json
    json_data = load_json_file(BASE_DIR / "CUSTOMERS_ONLY.json")
    if json_data and "customers" in json_data:
        for company_name, info in json_data["customers"].items():
            normalized = normalize_company_for_matching(company_name)
            if normalized and normalized not in seen_companies:
                seen_companies.add(normalized)
                
                # Get enriched data if available
                enriched = enriched_companies.get(company_name, {})
                
                row = [
                    company_name,
                    info.get("source", ""),
                    enriched.get("industry", ""),
                    enriched.get("company_size", ""),
                    enriched.get("headquarters", ""),
                    enriched.get("use_case") or info.get("use_case", ""),
                    enriched.get("why_they_chose", ""),
                    enriched.get("website", ""),
                    "New",  # Status
                    "",  # Added date
                    ""  # Notes
                ]
                sanitized = sanitize_row(row, COHORT_COLUMN_TYPES[3])
                rows.append(sanitized)
    
    print(f"  Loaded {len(rows)} companies for Cohort 3")
    return rows


def load_cohort_4_data() -> List[List[str]]:
    """
    Load Cohort 4: SI Partners
    
    Sources:
    - si_partner_prospects.csv (SI partners and agencies)
    """
    print("Loading Cohort 4 data (SI Partners)...")
    rows = []
    
    csv_data = load_csv_file(BASE_DIR / "si_partner_prospects.csv")
    if csv_data:
        for row_data in csv_data:
            description = row_data.get("Description", "")
            row = [
                row_data.get("Company", ""),
                row_data.get("SI_Type", ""),
                row_data.get("Email", ""),
                row_data.get("Name", ""),
                row_data.get("Title", ""),
                row_data.get("LinkedIn", ""),
                row_data.get("Score", ""),
                "New",  # Status
                description[:200] if description else ""  # Truncated description as notes
            ]
            sanitized = sanitize_row(row, COHORT_COLUMN_TYPES[4])
            rows.append(sanitized)
    
    print(f"  Loaded {len(rows)} partners for Cohort 4")
    return rows


def load_vip_users_data() -> List[List[str]]:
    """
    Load VIP Users segment
    
    Sources:
    - vip_users.csv (high-value users identified by activity/engagement)
    
    These are top priority users who should receive white-glove treatment.
    """
    print("Loading VIP Users data...")
    rows = []
    seen_emails = set()
    
    csv_data = load_csv_file(BASE_DIR / "vip_users.csv")
    if csv_data:
        for user in csv_data:
            email = user.get("email", "").strip().lower()
            
            # Skip duplicates
            if not email or email in seen_emails:
                continue
            seen_emails.add(email)
            
            # Extract domain from email
            domain = email.split('@')[-1] if '@' in email else ""
            
            # Get company name from domain (capitalize first letter of domain)
            company = domain.split('.')[0].title() if domain else ""
            
            # Format last active date
            last_active = user.get("last_active", "").strip()
            # Extract just the date part if it includes timezone
            if last_active and ' ' in last_active:
                last_active = last_active.split(' ')[0]
            
            row = [
                company,
                domain,
                email,
                user.get("user_id", "").strip(),
                last_active,
                user.get("vip_score", "1").strip(),
                "New",  # Status
                ""  # Notes
            ]
            # Sanitize the row
            sanitized = sanitize_row(row, COHORT_COLUMN_TYPES["vip"])
            rows.append(sanitized)
    
    print(f"  Loaded {len(rows)} VIP users")
    return rows


# =============================================================================
# DEDUPLICATION
# =============================================================================

def deduplicate_across_cohorts(
    cohort_data: Dict
) -> Tuple[Dict, int]:
    """
    Deduplicate companies across cohorts.
    
    Priority order (highest to lowest):
    1. Cohort 1 (Current Customers)
    1.2. Cohort 1.2 (New Users)
    2. Cohort 2 (In-Market)
    3. Cohort 3 (Competitors)
    4. Cohort 4 (SI Partners)
    
    Returns:
        Tuple of (deduplicated data, duplicate count)
    """
    print("\nDeduplicating across cohorts...")
    
    # Company name is always column 0
    seen_companies: Dict[str, Any] = {}  # normalized_name -> cohort
    duplicate_count = 0
    
    # Priority order for cohorts
    cohort_priority = [1, "1.2", "1.3", 2, 3, 4]
    
    # First pass: identify primary cohort for each company
    for cohort in cohort_priority:
        if cohort not in cohort_data:
            continue
        for row in cohort_data[cohort]:
            if not row:
                continue
            company_name = row[0]
            normalized = normalize_company_for_matching(company_name)
            if normalized and normalized not in seen_companies:
                seen_companies[normalized] = cohort
    
    # Second pass: mark duplicates
    result = {}
    for cohort in cohort_priority:
        if cohort not in cohort_data:
            continue
        
        result_rows = []
        notes_col = len(COHORT_HEADERS[cohort]) - 1  # Notes is last column
        
        for row in cohort_data[cohort]:
            if not row:
                result_rows.append(row)
                continue
            
            company_name = row[0]
            normalized = normalize_company_for_matching(company_name)
            
            if normalized and normalized in seen_companies:
                primary_cohort = seen_companies[normalized]
                if cohort != primary_cohort:
                    # This is a duplicate - add note
                    row = list(row)
                    # Ensure row has enough columns
                    while len(row) < len(COHORT_HEADERS[cohort]):
                        row.append("")
                    existing_note = row[notes_col]
                    dup_note = f"Also in Cohort {primary_cohort}"
                    row[notes_col] = f"{existing_note}; {dup_note}" if existing_note else dup_note
                    duplicate_count += 1
            
            result_rows.append(row)
        
        result[cohort] = result_rows
    
    print(f"  Found {duplicate_count} duplicate entries (flagged in Notes)")
    return result, duplicate_count


# =============================================================================
# DASHBOARD DATA
# =============================================================================

def generate_dashboard_data(
    cohort_counts: Dict,
    vip_count: int = 0,
    duplicate_count: int = 0
) -> List[List[str]]:
    """Generate dashboard summary data."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    total = sum(cohort_counts.values())
    
    return [
        ["Total Companies", str(total), now],
        ["Cohort 1: Current Customers", str(cohort_counts.get(1, 0)), now],
        ["Cohort 1.2: Business Users", str(cohort_counts.get("1.2", 0)), now],
        ["Cohort 1.3: All Users", str(cohort_counts.get("1.3", 0)), now],
        ["Cohort 2: In-Market", str(cohort_counts.get(2, 0)), now],
        ["Cohort 3: Competitors", str(cohort_counts.get(3, 0)), now],
        ["Cohort 4: SI Partners", str(cohort_counts.get(4, 0)), now],
        ["", "", ""],
        ["VIP Users", str(vip_count), now],
        ["Duplicates Flagged", str(duplicate_count), now],
        ["Q1 2026 Revenue Target", "$2M", now],
        ["Last Sync", now, now],
    ]


# =============================================================================
# HOME PAGE DATA
# =============================================================================

def generate_home_page_data() -> List[List[str]]:
    """Generate the Home page content with cohort definitions and Q1 goals."""
    now = datetime.now().strftime("%Y-%m-%d")
    
    return [
        # Title Section
        ["CHROMA GTM - CUSTOMER TRACKER", "", ""],
        ["Q1 2026 Revenue Strategy", "", ""],
        ["", "", ""],
        
        # Goal Section
        ["Q1 2026 GOALS", "", ""],
        ["Revenue Target", "$2M", ""],
        ["Pipeline Target", "$3M+", ""],
        ["Avg Deal Size", "$30K+", ""],
        ["Win Rate Target", "30%+", ""],
        ["", "", ""],
        
        # Cohort Overview
        ["THE 4 COHORTS", "Priority", "Description"],
        ["", "", ""],
        
        # Cohort 1
        ["COHORT 1: CURRENT CUSTOMERS", "HIGHEST", ""],
        ["Definition:", "Companies that have tried or are using Chroma", ""],
        ["Includes:", "Active paid accounts, free tier users, dormant accounts, pipeline deals", ""],
        ["Action:", "Close deals, expand accounts, reactivate dormant users", ""],
        ["Why Priority:", "Fastest path to Q1 revenue - already know the product", ""],
        ["", "", ""],
        
        # Cohort 2
        ["COHORT 2: IN-MARKET COMPANIES", "HIGH", ""],
        ["Definition:", "Companies showing active buying signals for AI/vector DB", ""],
        ["Includes:", "Hiring AI Engineers, building AI products, AI-native companies", ""],
        ["Signals:", "Job posts for ML/AI roles, building RAG applications, vector DB mentions", ""],
        ["Action:", "Outbound outreach, demos, fast qualification", ""],
        ["Why Priority:", "Active need - shorter sales cycle than cold outreach", ""],
        ["", "", ""],
        
        # Cohort 3
        ["COHORT 3: COMPETITOR CUSTOMERS", "MEDIUM", ""],
        ["Definition:", "Companies currently using competitor vector databases", ""],
        ["Competitors:", "Pinecone, Weaviate, Qdrant, Milvus, Elasticsearch, PGVector", ""],
        ["Action:", "Nurture sequences, competitive intel, keep warm", ""],
        ["Why Priority:", "Longer sales cycle (Q2+), but validated need for vector DB", ""],
        ["", "", ""],
        
        # Cohort 4
        ["COHORT 4: SI PARTNERS", "STRATEGIC", ""],
        ["Definition:", "System Integrators implementing AI solutions for clients", ""],
        ["Includes:", "Global SIs (Accenture, Deloitte), boutique AI agencies, dev shops", ""],
        ["Action:", "Enable, support, co-sell through partnership program", ""],
        ["Why Priority:", "Multiplier effect - one partner can bring multiple customers", ""],
        ["", "", ""],
        
        # Status Definitions
        ["STATUS DEFINITIONS", "", ""],
        ["New", "Not yet contacted", ""],
        ["Contacted", "Initial outreach sent", ""],
        ["Qualified", "Confirmed interest and fit", ""],
        ["Meeting Scheduled", "Demo or call booked", ""],
        ["Closed Won", "Deal signed!", ""],
        ["Closed Lost", "Not moving forward", ""],
        ["", "", ""],
        
        # Weekly Priorities
        ["WEEKLY PRIORITIES", "", ""],
        ["Daily:", "Check Cohort 1 pipeline, review Cohort 2 new signals", ""],
        ["Weekly:", "Follow up on Cohort 3, check SI partner activity", ""],
        ["Monthly:", "Review cohort performance, adjust prioritization", ""],
        ["", "", ""],
        
        # Footer
        ["Last Updated:", now, ""],
        ["Owner:", "Ankit Pansari", ""],
    ]


def sync_home_page(
    spreadsheet: gspread.Spreadsheet,
    dry_run: bool = False
) -> None:
    """Sync the Home page tab."""
    tab_name = TAB_NAMES["home"]
    rows = generate_home_page_data()
    
    print(f"\nSyncing {tab_name}...")
    
    if dry_run:
        print(f"  [DRY RUN] Would write Home page")
        return
    
    # Get or create worksheet
    try:
        worksheet = spreadsheet.worksheet(tab_name)
        print(f"  Found existing tab: {tab_name}")
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=tab_name,
            rows=100,
            cols=5
        )
        print(f"  Created new tab: {tab_name}")
    
    # Clear existing data
    worksheet.clear()
    
    # Write all rows
    worksheet.update(values=rows, range_name=f'A1:C{len(rows)}')
    
    # Format title (row 1)
    worksheet.format('A1:C1', {
        'textFormat': {'bold': True, 'fontSize': 18},
        'horizontalAlignment': 'CENTER'
    })
    
    # Format subtitle (row 2)
    worksheet.format('A2:C2', {
        'textFormat': {'bold': True, 'fontSize': 14},
        'horizontalAlignment': 'CENTER'
    })
    
    # Format section headers (Q1 GOALS, THE 4 COHORTS, etc.)
    section_rows = [4, 10, 13, 19, 25, 31, 37, 43, 51]
    for row_num in section_rows:
        if row_num <= len(rows):
            worksheet.format(f'A{row_num}:C{row_num}', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })
    
    # Format cohort headers with colors
    cohort_formats = [
        (13, {'red': 0.8, 'green': 0.2, 'blue': 0.2}),   # Cohort 1 - Red
        (19, {'red': 0.9, 'green': 0.5, 'blue': 0.1}),   # Cohort 2 - Orange
        (25, {'red': 0.9, 'green': 0.8, 'blue': 0.2}),   # Cohort 3 - Yellow
        (31, {'red': 0.2, 'green': 0.7, 'blue': 0.3}),   # Cohort 4 - Green
    ]
    for row_num, bg_color in cohort_formats:
        if row_num <= len(rows):
            worksheet.format(f'A{row_num}:C{row_num}', {
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
                'backgroundColor': bg_color
            })
    
    # Freeze first two rows
    worksheet.freeze(rows=2)
    
    # Move Home tab to first position
    try:
        worksheets = spreadsheet.worksheets()
        if worksheets[0].title != tab_name:
            spreadsheet.reorder_worksheets([worksheet] + [ws for ws in worksheets if ws.title != tab_name])
            print(f"  Moved Home tab to first position")
    except Exception as e:
        print(f"  Note: Could not reorder tabs: {e}")
    
    print(f"  Home page updated")
    
    # Brief pause to avoid rate limits
    time.sleep(2)


# =============================================================================
# GOOGLE SHEETS FUNCTIONS
# =============================================================================

def get_sheets_client() -> gspread.Client:
    """Authenticate and return a Google Sheets client."""
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(
            f"Credentials file not found: {CREDENTIALS_FILE}\n"
            "Please follow the setup instructions in credentials/README.md"
        )
    
    credentials = Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=SCOPES
    )
    return gspread.authorize(credentials)


def get_or_create_worksheet(
    spreadsheet: gspread.Spreadsheet,
    tab_name: str,
    headers: List[str]
) -> gspread.Worksheet:
    """Get an existing worksheet or create a new one."""
    try:
        worksheet = spreadsheet.worksheet(tab_name)
        print(f"  Found existing tab: {tab_name}")
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=tab_name,
            rows=1000,
            cols=len(headers) + 2  # Extra columns for future use
        )
        print(f"  Created new tab: {tab_name}")
    
    return worksheet


def column_letter(col_index: int) -> str:
    """Convert column index (0-based) to letter (A, B, C, ...)."""
    result = ""
    while col_index >= 0:
        result = chr(col_index % 26 + ord('A')) + result
        col_index = col_index // 26 - 1
    return result


def apply_status_dropdown(
    worksheet: gspread.Worksheet,
    status_col_index: int,
    num_rows: int
) -> None:
    """Apply dropdown validation to the Status column."""
    try:
        col_letter = column_letter(status_col_index)
        
        # Create validation rule for dropdown
        validation_rule = DataValidationRule(
            BooleanCondition('ONE_OF_LIST', STATUS_OPTIONS),
            showCustomUi=True
        )
        
        # Apply to the Status column (row 2 to end of data)
        range_str = f"{col_letter}2:{col_letter}{num_rows + 1}"
        set_data_validation_for_cell_range(worksheet, range_str, validation_rule)
        
        print(f"  Applied dropdown validation to column {col_letter}")
    except Exception as e:
        print(f"  Warning: Could not apply dropdown validation: {e}")


def apply_status_conditional_formatting(
    spreadsheet: gspread.Spreadsheet,
    worksheet: gspread.Worksheet,
    status_col_index: int,
    num_rows: int
) -> None:
    """Apply conditional formatting colors to the Status column."""
    try:
        col_letter = column_letter(status_col_index)
        sheet_id = worksheet.id
        
        # Build conditional formatting rules
        requests = []
        
        for status, color in STATUS_COLORS.items():
            rule = {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{
                            "sheetId": sheet_id,
                            "startRowIndex": 1,  # Skip header
                            "endRowIndex": num_rows + 1,
                            "startColumnIndex": status_col_index,
                            "endColumnIndex": status_col_index + 1
                        }],
                        "booleanRule": {
                            "condition": {
                                "type": "TEXT_EQ",
                                "values": [{"userEnteredValue": status}]
                            },
                            "format": {
                                "backgroundColor": color,
                                "textFormat": {
                                    "bold": True,
                                    "foregroundColor": {"red": 0, "green": 0, "blue": 0} if status not in ["Closed Won", "Closed Lost"] else {"red": 1, "green": 1, "blue": 1}
                                }
                            }
                        }
                    },
                    "index": 0
                }
            }
            requests.append(rule)
        
        # Execute batch update
        if requests:
            spreadsheet.batch_update({"requests": requests})
            print(f"  Applied status colors to column {col_letter}")
    except Exception as e:
        print(f"  Warning: Could not apply status colors: {e}")


def sync_cohort_to_sheet(
    spreadsheet: gspread.Spreadsheet,
    cohort,  # Can be int or str (e.g., "1.2")
    rows: List[List[str]],
    dry_run: bool = False
) -> int:
    """Sync a cohort's data to its Google Sheet tab."""
    tab_name = TAB_NAMES[cohort]
    headers = COHORT_HEADERS[cohort]
    
    print(f"\nSyncing {tab_name}...")
    
    if dry_run:
        print(f"  [DRY RUN] Would write {len(rows)} rows to '{tab_name}'")
        return len(rows)
    
    worksheet = get_or_create_worksheet(spreadsheet, tab_name, headers)
    
    # Clear existing data
    worksheet.clear()
    
    # Write headers
    worksheet.update(values=[headers], range_name='A1')
    
    # Format header row (bold, colored background)
    header_range = f'A1:{column_letter(len(headers) - 1)}1'
    worksheet.format(header_range, {
        'textFormat': {'bold': True},
        'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.6},
        'horizontalAlignment': 'CENTER',
        'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
    })
    
    # Write data rows
    if rows:
        # Ensure all rows have the correct number of columns
        padded_rows = []
        for row in rows:
            padded_row = list(row)
            while len(padded_row) < len(headers):
                padded_row.append("")
            padded_rows.append(padded_row[:len(headers)])  # Trim if too long
        
        end_col = column_letter(len(headers) - 1)
        worksheet.update(values=padded_rows, range_name=f'A2:{end_col}{len(rows) + 1}')
    
    # Apply dropdown validation to Status column
    if cohort in STATUS_COLUMN_INDEX:
        apply_status_dropdown(worksheet, STATUS_COLUMN_INDEX[cohort], len(rows))
        # Apply conditional formatting colors
        apply_status_conditional_formatting(spreadsheet, worksheet, STATUS_COLUMN_INDEX[cohort], len(rows))
    
    # Freeze header row
    worksheet.freeze(rows=1)
    
    print(f"  Wrote {len(rows)} rows to '{tab_name}'")
    
    # Brief pause to avoid rate limits
    time.sleep(1)
    
    return len(rows)


def sync_vip_users_to_sheet(
    spreadsheet: gspread.Spreadsheet,
    rows: List[List[str]],
    dry_run: bool = False
) -> int:
    """Sync VIP users data to its Google Sheet tab."""
    tab_name = TAB_NAMES["vip"]
    headers = COHORT_HEADERS["vip"]
    
    print(f"\nSyncing {tab_name}...")
    
    if dry_run:
        print(f"  [DRY RUN] Would write {len(rows)} rows to '{tab_name}'")
        return len(rows)
    
    worksheet = get_or_create_worksheet(spreadsheet, tab_name, headers)
    
    # Clear existing data
    worksheet.clear()
    
    # Write headers
    worksheet.update(values=[headers], range_name='A1')
    
    # Format header row (bold, colored background - gold for VIP)
    header_range = f'A1:{column_letter(len(headers) - 1)}1'
    worksheet.format(header_range, {
        'textFormat': {'bold': True},
        'backgroundColor': {'red': 0.85, 'green': 0.65, 'blue': 0.13},  # Gold
        'horizontalAlignment': 'CENTER',
        'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
    })
    
    # Write data rows
    if rows:
        # Ensure all rows have the correct number of columns
        padded_rows = []
        for row in rows:
            padded_row = list(row)
            while len(padded_row) < len(headers):
                padded_row.append("")
            padded_rows.append(padded_row[:len(headers)])
        
        end_col = column_letter(len(headers) - 1)
        worksheet.update(values=padded_rows, range_name=f'A2:{end_col}{len(rows) + 1}')
    
    # Apply dropdown validation to Status column
    apply_status_dropdown(worksheet, STATUS_COLUMN_INDEX["vip"], len(rows))
    # Apply conditional formatting colors
    apply_status_conditional_formatting(spreadsheet, worksheet, STATUS_COLUMN_INDEX["vip"], len(rows))
    
    # Freeze header row
    worksheet.freeze(rows=1)
    
    print(f"  Wrote {len(rows)} rows to '{tab_name}'")
    
    # Brief pause to avoid rate limits
    time.sleep(1)
    
    return len(rows)


def sync_dashboard(
    spreadsheet: gspread.Spreadsheet,
    cohort_counts: Dict[int, int],
    vip_count: int = 0,
    duplicate_count: int = 0,
    dry_run: bool = False
) -> None:
    """Sync the dashboard summary tab."""
    tab_name = TAB_NAMES["dashboard"]
    headers = COHORT_HEADERS["dashboard"]
    rows = generate_dashboard_data(cohort_counts, vip_count, duplicate_count)
    
    print(f"\nSyncing {tab_name}...")
    
    if dry_run:
        print(f"  [DRY RUN] Would write dashboard summary")
        return
    
    worksheet = get_or_create_worksheet(spreadsheet, tab_name, headers)
    
    # Clear existing data
    worksheet.clear()
    
    # Write headers
    worksheet.update(values=[headers], range_name='A1')
    
    # Format header row
    worksheet.format('A1:C1', {
        'textFormat': {'bold': True},
        'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.6},
        'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
    })
    
    # Write data
    worksheet.update(values=rows, range_name=f'A2:C{len(rows) + 1}')
    
    # Freeze header row
    worksheet.freeze(rows=1)
    
    print(f"  Dashboard updated")


def list_sheet_stats(spreadsheet: gspread.Spreadsheet) -> None:
    """List current statistics from the Google Sheet."""
    print("\nCurrent Google Sheet Statistics:")
    print("-" * 50)
    
    for worksheet in spreadsheet.worksheets():
        try:
            values = worksheet.get_all_values()
            data_rows = len(values) - 1 if values else 0
        except Exception:
            data_rows = "Unknown"
        
        print(f"  {worksheet.title}: {data_rows} rows")


# =============================================================================
# MAIN SYNC FUNCTION
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Sync Chroma GTM data to Google Sheets"
    )
    parser.add_argument(
        "--cohort",
        type=int,
        choices=[1, 2, 3, 4],
        help="Sync specific cohort only (1-4)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without pushing to Google Sheets"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List current sheet statistics"
    )
    parser.add_argument(
        "--no-dedup",
        action="store_true",
        help="Skip deduplication step"
    )
    
    args = parser.parse_args()
    
    # Validate configuration
    if not GOOGLE_SHEET_ID:
        print("ERROR: GOOGLE_SHEET_ID not set in .env file")
        print("Add: GOOGLE_SHEET_ID=your-sheet-id-here")
        exit(1)
    
    print("=" * 60)
    print("CHROMA GTM - GOOGLE SHEETS SYNC")
    print("=" * 60)
    print(f"Sheet ID: {GOOGLE_SHEET_ID[:20]}...")
    print(f"Credentials: {CREDENTIALS_FILE}")
    if args.dry_run:
        print("MODE: DRY RUN (no changes will be made)")
    print()
    
    # Connect to Google Sheets
    try:
        client = get_sheets_client()
        spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
        print(f"Connected to: {spreadsheet.title}")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        exit(1)
    except gspread.SpreadsheetNotFound:
        print(f"ERROR: Spreadsheet not found. Check your GOOGLE_SHEET_ID.")
        print("Make sure the sheet is shared with the service account email.")
        exit(1)
    except Exception as e:
        print(f"ERROR connecting to Google Sheets: {e}")
        exit(1)
    
    # List mode
    if args.list:
        list_sheet_stats(spreadsheet)
        return
    
    # Load data for requested cohorts
    cohort_data = {}
    cohorts_to_sync = [args.cohort] if args.cohort else [1, "1.2", "1.3", 2, 3, 4]
    
    print("\n" + "=" * 60)
    print("LOADING & SANITIZING DATA")
    print("=" * 60)
    
    # Track emails to avoid duplicates across cohorts 1, 1.2, 1.3
    existing_emails = set()
    
    if 1 in cohorts_to_sync:
        cohort_data[1] = load_cohort_1_data()
        # Collect emails from Cohort 1 (email is column 2)
        for row in cohort_data[1]:
            if len(row) > 2 and row[2]:
                existing_emails.add(row[2].lower())
    
    if "1.2" in cohorts_to_sync:
        cohort_data["1.2"] = load_cohort_1_2_data()
        # Collect emails from Cohort 1.2 (email is column 2)
        for row in cohort_data["1.2"]:
            if len(row) > 2 and row[2]:
                existing_emails.add(row[2].lower())
    
    if "1.3" in cohorts_to_sync:
        # Pass existing emails to avoid duplicates
        cohort_data["1.3"] = load_cohort_1_3_data(existing_emails)
    
    if 2 in cohorts_to_sync:
        cohort_data[2] = load_cohort_2_data()
    if 3 in cohorts_to_sync:
        cohort_data[3] = load_cohort_3_data()
    if 4 in cohorts_to_sync:
        cohort_data[4] = load_cohort_4_data()
    
    # Deduplicate across cohorts
    duplicate_count = 0
    if not args.no_dedup and not args.cohort:
        cohort_data, duplicate_count = deduplicate_across_cohorts(cohort_data)
    
    # Sync to Google Sheets
    print("\n" + "=" * 60)
    print("SYNCING TO GOOGLE SHEETS")
    print("=" * 60)
    
    # Sync Home page first (on full sync only)
    if not args.cohort:
        sync_home_page(spreadsheet, args.dry_run)
    
    cohort_counts = {}
    for cohort, rows in cohort_data.items():
        count = sync_cohort_to_sheet(spreadsheet, cohort, rows, args.dry_run)
        cohort_counts[cohort] = count
    
    # Sync VIP users (on full sync only)
    vip_count = 0
    if not args.cohort:
        vip_rows = load_vip_users_data()
        vip_count = sync_vip_users_to_sheet(spreadsheet, vip_rows, args.dry_run)
    
    # Update dashboard
    if not args.cohort:  # Only update dashboard on full sync
        sync_dashboard(spreadsheet, cohort_counts, vip_count, duplicate_count, args.dry_run)
    
    # Summary
    print("\n" + "=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    total = sum(cohort_counts.values())
    print(f"Total companies synced: {total}")
    # Sort cohorts by converting to string for consistent ordering
    for cohort, count in sorted(cohort_counts.items(), key=lambda x: str(x[0])):
        print(f"  Cohort {cohort}: {count} companies")
    if vip_count > 0:
        print(f"  VIP Users: {vip_count}")
    if duplicate_count > 0:
        print(f"  Duplicates flagged: {duplicate_count}")
    
    if not args.dry_run:
        print(f"\nView your data: https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}")


if __name__ == "__main__":
    main()
