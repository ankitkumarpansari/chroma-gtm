#!/usr/bin/env python3
"""
Data Sanitization Utilities for Chroma GTM

Provides functions to clean and standardize data before syncing to Google Sheets:
- URL cleaning (remove tracking params, ensure https://)
- Company name standardization (proper case, remove suffixes)
- Email validation (check format, lowercase)
- Cross-cohort deduplication

Usage:
    from sanitize import sanitize_company_data, deduplicate_across_cohorts
"""

import re
from typing import Dict, List, Set, Tuple, Optional
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode


# =============================================================================
# URL CLEANING
# =============================================================================

# Common tracking parameters to remove
TRACKING_PARAMS = {
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
    'fbclid', 'gclid', 'msclkid', 'ref', 'source', 'mc_cid', 'mc_eid',
    '_ga', '_gl', 'trk', 'trkInfo', 'originalReferer', 'refId'
}


def clean_url(url: Optional[str]) -> str:
    """
    Clean and standardize a URL.
    
    - Ensures https:// prefix
    - Removes tracking parameters
    - Removes trailing slashes
    - Handles LinkedIn URLs specially
    
    Examples:
        clean_url("uber.com") -> "https://uber.com"
        clean_url("https://example.com?utm_source=google") -> "https://example.com"
        clean_url("linkedin.com/in/john-doe/") -> "https://linkedin.com/in/john-doe"
    """
    if not url or not isinstance(url, str):
        return ""
    
    url = url.strip()
    if not url:
        return ""
    
    # Add scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception:
        return url  # Return original if parsing fails
    
    # Remove tracking parameters
    if parsed.query:
        query_params = parse_qs(parsed.query, keep_blank_values=False)
        filtered_params = {
            k: v for k, v in query_params.items() 
            if k.lower() not in TRACKING_PARAMS
        }
        new_query = urlencode(filtered_params, doseq=True) if filtered_params else ''
    else:
        new_query = ''
    
    # Remove trailing slash from path (except for root)
    path = parsed.path.rstrip('/') if parsed.path != '/' else parsed.path
    
    # Reconstruct URL
    cleaned = urlunparse((
        'https',  # Always use https
        parsed.netloc.lower(),
        path,
        '',  # params
        new_query,
        ''  # fragment
    ))
    
    return cleaned


def clean_linkedin_url(url: Optional[str]) -> str:
    """
    Clean LinkedIn URLs specifically.
    
    - Ensures proper linkedin.com domain
    - Removes tracking parameters
    - Standardizes format
    
    Examples:
        clean_linkedin_url("linkedin.com/in/john-doe") -> "https://linkedin.com/in/john-doe"
        clean_linkedin_url("www.linkedin.com/in/john-doe/") -> "https://linkedin.com/in/john-doe"
    """
    if not url or not isinstance(url, str):
        return ""
    
    url = url.strip()
    if not url:
        return ""
    
    # Check if it's a LinkedIn URL
    if 'linkedin' not in url.lower():
        return url
    
    # Clean the URL first
    cleaned = clean_url(url)
    
    # Remove www. prefix for LinkedIn
    cleaned = cleaned.replace('://www.linkedin', '://linkedin')
    
    return cleaned


# =============================================================================
# COMPANY NAME STANDARDIZATION
# =============================================================================

# Suffixes to remove from company names
COMPANY_SUFFIXES = [
    r',?\s*Inc\.?$',
    r',?\s*LLC\.?$',
    r',?\s*Ltd\.?$',
    r',?\s*Corp\.?$',
    r',?\s*Corporation$',
    r',?\s*Company$',
    r',?\s*Co\.?$',
    r',?\s*PLC$',
    r',?\s*GmbH$',
    r',?\s*AG$',
    r',?\s*SA$',
    r',?\s*SAS$',
    r',?\s*BV$',
    r',?\s*NV$',
    r',?\s*Pty\.?\s*Ltd\.?$',
    r',?\s*Limited$',
    r',?\s*Incorporated$',
]

# Words that should stay lowercase (unless at start)
LOWERCASE_WORDS = {'a', 'an', 'the', 'and', 'or', 'but', 'of', 'for', 'in', 'on', 'at', 'to', 'by'}

# Words/acronyms that should stay uppercase
UPPERCASE_WORDS = {'AI', 'ML', 'API', 'UI', 'UX', 'IT', 'HR', 'CRM', 'ERP', 'SaaS', 'PaaS', 'IaaS', 
                   'AWS', 'GCP', 'IBM', 'SAP', 'HP', 'HCL', 'TCS', 'NTT', 'CEO', 'CTO', 'CFO', 'COO',
                   'USA', 'UK', 'EU', 'EMEA', 'APAC', 'B2B', 'B2C', 'IoT', 'RAG', 'LLM', 'GPT'}


def standardize_company_name(name: Optional[str]) -> str:
    """
    Standardize a company name.
    
    - Converts to proper case (title case with exceptions)
    - Removes common suffixes (Inc., LLC, etc.)
    - Preserves known acronyms (AI, ML, etc.)
    - Cleans up extra whitespace
    
    Examples:
        standardize_company_name("UBER TECHNOLOGIES, INC.") -> "Uber Technologies"
        standardize_company_name("openai") -> "OpenAI"
        standardize_company_name("  acme corp  ") -> "Acme"
    """
    if not name or not isinstance(name, str):
        return ""
    
    name = name.strip()
    if not name:
        return ""
    
    # Remove suffixes
    for suffix_pattern in COMPANY_SUFFIXES:
        name = re.sub(suffix_pattern, '', name, flags=re.IGNORECASE)
    
    # Clean up whitespace
    name = ' '.join(name.split())
    
    # Apply title case with exceptions
    words = name.split()
    result_words = []
    
    for i, word in enumerate(words):
        # Check if it's a known uppercase word/acronym
        upper_word = word.upper()
        if upper_word in UPPERCASE_WORDS:
            result_words.append(upper_word)
        # Check if it's a lowercase word (not at start)
        elif i > 0 and word.lower() in LOWERCASE_WORDS:
            result_words.append(word.lower())
        # Default to title case
        else:
            # Handle special cases like "OpenAI" -> keep internal caps
            if any(c.isupper() for c in word[1:]) and any(c.islower() for c in word):
                result_words.append(word)  # Keep original mixed case
            else:
                result_words.append(word.capitalize())
    
    return ' '.join(result_words)


def standardize_person_name(name: Optional[str]) -> str:
    """
    Standardize a person's name to proper case.
    
    Examples:
        standardize_person_name("JOHN DOE") -> "John Doe"
        standardize_person_name("mary jane watson") -> "Mary Jane Watson"
    """
    if not name or not isinstance(name, str):
        return ""
    
    name = name.strip()
    if not name:
        return ""
    
    # Clean up whitespace
    name = ' '.join(name.split())
    
    # Apply title case
    return name.title()


# =============================================================================
# EMAIL VALIDATION
# =============================================================================

# Basic email regex pattern
EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)


def validate_email(email: Optional[str]) -> str:
    """
    Validate and clean an email address.
    
    - Converts to lowercase
    - Removes leading/trailing whitespace
    - Returns empty string if invalid format
    
    Examples:
        validate_email("John@UBER.COM") -> "john@uber.com"
        validate_email("invalid-email") -> ""
        validate_email("  user@example.com  ") -> "user@example.com"
    """
    if not email or not isinstance(email, str):
        return ""
    
    email = email.strip().lower()
    
    if not email:
        return ""
    
    # Check format
    if EMAIL_PATTERN.match(email):
        return email
    
    return ""  # Invalid format


# =============================================================================
# DEDUPLICATION
# =============================================================================

def normalize_company_for_matching(name: str) -> str:
    """
    Normalize a company name for duplicate matching.
    
    More aggressive normalization than standardize_company_name:
    - Lowercase
    - Remove all punctuation
    - Remove common words
    """
    if not name:
        return ""
    
    # Lowercase and remove punctuation
    normalized = re.sub(r'[^\w\s]', '', name.lower())
    
    # Remove common words
    words_to_remove = {'the', 'inc', 'llc', 'ltd', 'corp', 'corporation', 
                       'company', 'co', 'technologies', 'technology', 'tech',
                       'solutions', 'services', 'group', 'holdings', 'international'}
    
    words = normalized.split()
    filtered = [w for w in words if w not in words_to_remove]
    
    return ' '.join(filtered)


def deduplicate_across_cohorts(
    cohort_data: Dict[int, List[List[str]]],
    company_column_index: Dict[int, int]
) -> Tuple[Dict[int, List[List[str]]], Dict[str, List[int]]]:
    """
    Deduplicate companies across cohorts.
    
    Priority order (highest to lowest):
    1. Cohort 1 (Current Customers)
    2. Cohort 2 (In-Market)
    3. Cohort 3 (Competitors)
    4. Cohort 4 (SI Partners)
    
    Args:
        cohort_data: Dict mapping cohort number to list of rows
        company_column_index: Dict mapping cohort number to company name column index
    
    Returns:
        Tuple of:
        - Deduplicated cohort data (with "Duplicate" flag in notes)
        - Dict mapping normalized company name to list of cohorts it appears in
    """
    # Track which companies we've seen and in which cohort
    seen_companies: Dict[str, int] = {}  # normalized_name -> first cohort seen
    duplicates: Dict[str, List[int]] = {}  # normalized_name -> list of cohorts
    
    # Process cohorts in priority order
    priority_order = [1, 2, 3, 4]
    
    # First pass: identify all companies and duplicates
    for cohort in priority_order:
        if cohort not in cohort_data:
            continue
        
        col_idx = company_column_index.get(cohort, 0)
        
        for row in cohort_data[cohort]:
            if not row or len(row) <= col_idx:
                continue
            
            company_name = row[col_idx]
            normalized = normalize_company_for_matching(company_name)
            
            if not normalized:
                continue
            
            if normalized in seen_companies:
                # This is a duplicate
                if normalized not in duplicates:
                    duplicates[normalized] = [seen_companies[normalized]]
                duplicates[normalized].append(cohort)
            else:
                seen_companies[normalized] = cohort
    
    # Second pass: mark duplicates (keep in primary cohort, flag in others)
    result_data = {}
    
    for cohort in priority_order:
        if cohort not in cohort_data:
            continue
        
        col_idx = company_column_index.get(cohort, 0)
        result_rows = []
        
        for row in cohort_data[cohort]:
            if not row or len(row) <= col_idx:
                result_rows.append(row)
                continue
            
            company_name = row[col_idx]
            normalized = normalize_company_for_matching(company_name)
            
            if normalized and normalized in duplicates:
                primary_cohort = duplicates[normalized][0]
                if cohort != primary_cohort:
                    # This is a duplicate entry - add flag
                    row = list(row)  # Make mutable copy
                    # We'll add a note about the duplicate
                    # The sync script will handle adding the Notes column
                    row.append(f"Also in Cohort {primary_cohort}")
            
            result_rows.append(row)
        
        result_data[cohort] = result_rows
    
    return result_data, duplicates


# =============================================================================
# MAIN SANITIZATION FUNCTION
# =============================================================================

def sanitize_row(
    row: List[str],
    column_types: Dict[int, str]
) -> List[str]:
    """
    Sanitize a single row based on column types.
    
    Args:
        row: List of cell values
        column_types: Dict mapping column index to type ('company', 'email', 'url', 'linkedin', 'person', 'text')
    
    Returns:
        Sanitized row
    """
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
            # Default: just strip whitespace
            result.append(str(value).strip() if value else "")
    
    return result


def sanitize_cohort_data(
    rows: List[List[str]],
    column_types: Dict[int, str]
) -> List[List[str]]:
    """
    Sanitize all rows in a cohort.
    
    Args:
        rows: List of rows (each row is a list of cell values)
        column_types: Dict mapping column index to type
    
    Returns:
        List of sanitized rows
    """
    return [sanitize_row(row, column_types) for row in rows]


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    # Test URL cleaning
    print("Testing URL cleaning:")
    test_urls = [
        "uber.com",
        "https://example.com?utm_source=google&utm_medium=cpc",
        "http://www.linkedin.com/in/john-doe/",
        "linkedin.com/in/jane-smith?trk=public_profile",
        "",
        None
    ]
    for url in test_urls:
        print(f"  {repr(url)} -> {repr(clean_url(url))}")
    
    print("\nTesting company name standardization:")
    test_names = [
        "UBER TECHNOLOGIES, INC.",
        "openai",
        "  acme corp  ",
        "Microsoft Corporation",
        "x.AI",
        "HCL Technologies Ltd.",
        ""
    ]
    for name in test_names:
        print(f"  {repr(name)} -> {repr(standardize_company_name(name))}")
    
    print("\nTesting email validation:")
    test_emails = [
        "John@UBER.COM",
        "invalid-email",
        "  user@example.com  ",
        "test@test",
        ""
    ]
    for email in test_emails:
        print(f"  {repr(email)} -> {repr(validate_email(email))}")
    
    print("\nTesting person name standardization:")
    test_person_names = [
        "JOHN DOE",
        "mary jane watson",
        "  bob smith  ",
        ""
    ]
    for name in test_person_names:
        print(f"  {repr(name)} -> {repr(standardize_person_name(name))}")

