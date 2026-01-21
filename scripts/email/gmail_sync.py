#!/usr/bin/env python3
"""
Gmail Sync for Chroma GTM
Syncs emails to markdown files that Claude can read as context.

This creates/updates:
- context/EMAILS.md - Summary of recent emails
- context/LEADS_INBOX.md - Emails from potential leads
- context/FOLLOW_UPS.md - Emails needing response
- context/email_threads/ - Full thread exports

Usage:
    python gmail_sync.py                    # Sync last 7 days
    python gmail_sync.py --days 14          # Sync last 14 days
    python gmail_sync.py --leads            # Only sync lead emails
    python gmail_sync.py --query "from:@"   # Custom query
"""

import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import re

from gmail_client import GmailClient

# Paths
PROJECT_DIR = Path(__file__).parent.parent
CONTEXT_DIR = PROJECT_DIR / 'context'
THREADS_DIR = CONTEXT_DIR / 'email_threads'

# Lead detection patterns (customize these)
LEAD_DOMAINS = [
    # Add domains you consider leads
]

EXCLUDE_DOMAINS = [
    'github.com', 'google.com', 'linkedin.com', 'twitter.com',
    'slack.com', 'notion.so', 'figma.com', 'stripe.com',
    'calendly.com', 'zoom.us', 'loom.com',
]

EXCLUDE_SENDERS = [
    'noreply', 'no-reply', 'notifications', 'mailer-daemon',
    'postmaster', 'support@', 'team@', 'info@',
]


def is_lead_email(email: Dict) -> bool:
    """Check if email is from a potential lead."""
    from_addr = email.get('from', '').lower()
    
    # Exclude known non-leads
    for pattern in EXCLUDE_SENDERS:
        if pattern in from_addr:
            return False
    
    for domain in EXCLUDE_DOMAINS:
        if domain in from_addr:
            return False
    
    # Check if from a lead domain
    for domain in LEAD_DOMAINS:
        if domain in from_addr:
            return True
    
    # Default: include if it's a real person email
    # (has a name, not automated)
    if '<' in email.get('from', ''):
        return True
    
    return False


def needs_followup(email: Dict) -> bool:
    """Check if email needs a follow-up response."""
    # Unread emails need attention
    if email.get('is_unread'):
        return True
    
    # Check for question marks in subject/body
    subject = email.get('subject', '').lower()
    body = email.get('body', '').lower()
    
    question_indicators = ['?', 'question', 'help', 'can you', 'could you', 'would you']
    for indicator in question_indicators:
        if indicator in subject or indicator in body[:500]:
            return True
    
    return False


def format_email_summary(email: Dict, include_body: bool = False) -> str:
    """Format email as markdown summary."""
    lines = []
    
    # Extract sender info
    from_addr = email.get('from', 'Unknown')
    name = extract_name(from_addr)
    email_addr = extract_email(from_addr)
    
    lines.append(f"### {name}")
    lines.append(f"**Email:** {email_addr}")
    lines.append(f"**Subject:** {email.get('subject', 'No subject')}")
    lines.append(f"**Date:** {email.get('date', 'Unknown')}")
    
    if email.get('is_unread'):
        lines.append("**Status:** 🔵 Unread")
    
    lines.append(f"**Preview:** {email.get('snippet', '')[:200]}...")
    lines.append(f"**Thread ID:** `{email.get('thread_id', '')}`")
    
    if include_body and email.get('body'):
        lines.append("")
        lines.append("<details>")
        lines.append("<summary>Full Email</summary>")
        lines.append("")
        lines.append("```")
        lines.append(email['body'][:2000])
        if len(email.get('body', '')) > 2000:
            lines.append("... [truncated]")
        lines.append("```")
        lines.append("</details>")
    
    lines.append("")
    return '\n'.join(lines)


def extract_name(from_header: str) -> str:
    """Extract name from email header."""
    match = re.search(r'^([^<]+)', from_header)
    if match:
        return match.group(1).strip().strip('"')
    return from_header.split('@')[0]


def extract_email(from_header: str) -> str:
    """Extract email address from header."""
    match = re.search(r'<([^>]+)>', from_header)
    if match:
        return match.group(1)
    return from_header


def sync_emails(days: int = 7, leads_only: bool = False, 
                custom_query: str = None, max_emails: int = 100):
    """Main sync function."""
    print(f"📧 Gmail Sync for Chroma GTM")
    print(f"   Syncing last {days} days...")
    
    # Ensure directories exist
    CONTEXT_DIR.mkdir(exist_ok=True)
    THREADS_DIR.mkdir(exist_ok=True)
    
    # Connect to Gmail
    gmail = GmailClient()
    print(f"✅ Connected as: {gmail.email_address}")
    
    # Fetch emails
    if custom_query:
        query = custom_query
    else:
        query = f'newer_than:{days}d'
    
    print(f"🔍 Query: {query}")
    emails = gmail.search_emails(query, max_results=max_emails)
    print(f"📬 Found {len(emails)} emails")
    
    # Categorize emails
    all_emails = []
    lead_emails = []
    followup_emails = []
    
    for email in emails:
        all_emails.append(email)
        
        if is_lead_email(email):
            lead_emails.append(email)
        
        if needs_followup(email):
            followup_emails.append(email)
    
    # Generate EMAILS.md - All recent emails summary
    print("📝 Writing EMAILS.md...")
    write_emails_summary(all_emails, days)
    
    # Generate LEADS_INBOX.md - Lead emails
    if lead_emails or not leads_only:
        print("📝 Writing LEADS_INBOX.md...")
        write_leads_inbox(lead_emails)
    
    # Generate FOLLOW_UPS.md - Emails needing response
    print("📝 Writing FOLLOW_UPS.md...")
    write_followups(followup_emails)
    
    # Summary
    print(f"\n✅ Sync complete!")
    print(f"   Total emails: {len(all_emails)}")
    print(f"   Lead emails: {len(lead_emails)}")
    print(f"   Need follow-up: {len(followup_emails)}")
    print(f"\n📂 Files updated in: {CONTEXT_DIR}")


def write_emails_summary(emails: List[Dict], days: int):
    """Write EMAILS.md with all recent emails."""
    lines = [
        "# Recent Emails",
        "",
        f"*Last synced: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        f"*Period: Last {days} days*",
        "",
        "---",
        "",
    ]
    
    # Group by date
    by_date = {}
    for email in emails:
        date_str = email.get('date', '')[:16]  # Rough date
        if date_str not in by_date:
            by_date[date_str] = []
        by_date[date_str].append(email)
    
    # Stats
    unread_count = sum(1 for e in emails if e.get('is_unread'))
    lines.append(f"## Summary")
    lines.append(f"- **Total:** {len(emails)} emails")
    lines.append(f"- **Unread:** {unread_count}")
    lines.append("")
    
    # List emails
    lines.append("## Emails")
    lines.append("")
    
    for email in emails[:50]:  # Limit to 50
        lines.append(format_email_summary(email))
        lines.append("---")
        lines.append("")
    
    if len(emails) > 50:
        lines.append(f"*... and {len(emails) - 50} more emails*")
    
    # Write file
    with open(CONTEXT_DIR / 'EMAILS.md', 'w') as f:
        f.write('\n'.join(lines))


def write_leads_inbox(emails: List[Dict]):
    """Write LEADS_INBOX.md with potential lead emails."""
    lines = [
        "# Leads Inbox",
        "",
        f"*Last synced: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        "",
        "Emails from potential leads and customers.",
        "",
        "---",
        "",
    ]
    
    if not emails:
        lines.append("*No lead emails found in this period.*")
    else:
        # Prioritize unread
        unread = [e for e in emails if e.get('is_unread')]
        read = [e for e in emails if not e.get('is_unread')]
        
        if unread:
            lines.append("## 🔵 Unread")
            lines.append("")
            for email in unread:
                lines.append(format_email_summary(email, include_body=True))
                lines.append("---")
                lines.append("")
        
        if read:
            lines.append("## ⚪ Recent")
            lines.append("")
            for email in read[:20]:
                lines.append(format_email_summary(email))
                lines.append("---")
                lines.append("")
    
    with open(CONTEXT_DIR / 'LEADS_INBOX.md', 'w') as f:
        f.write('\n'.join(lines))


def write_followups(emails: List[Dict]):
    """Write FOLLOW_UPS.md with emails needing response."""
    lines = [
        "# Follow-ups Needed",
        "",
        f"*Last synced: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        "",
        "Emails that may need a response.",
        "",
        "---",
        "",
    ]
    
    if not emails:
        lines.append("✅ *No pending follow-ups!*")
    else:
        lines.append(f"**{len(emails)} emails need attention:**")
        lines.append("")
        
        for email in emails:
            lines.append(format_email_summary(email, include_body=True))
            lines.append("---")
            lines.append("")
    
    with open(CONTEXT_DIR / 'FOLLOW_UPS.md', 'w') as f:
        f.write('\n'.join(lines))


def export_thread(gmail: GmailClient, thread_id: str):
    """Export a full email thread to markdown."""
    thread = gmail.get_thread(thread_id)
    
    lines = [
        f"# Thread: {thread['subject']}",
        "",
        f"*Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        f"*Messages: {thread['message_count']}*",
        "",
        "---",
        "",
    ]
    
    for msg in thread['messages']:
        lines.append(f"## From: {msg['from']}")
        lines.append(f"**Date:** {msg['date']}")
        lines.append("")
        lines.append(msg['body'] or msg['snippet'])
        lines.append("")
        lines.append("---")
        lines.append("")
    
    filename = f"thread_{thread_id[:10]}.md"
    with open(THREADS_DIR / filename, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"📄 Exported: {filename}")
    return filename


def main():
    parser = argparse.ArgumentParser(description='Sync Gmail to Chroma GTM context')
    parser.add_argument('--days', type=int, default=7, help='Days to sync (default: 7)')
    parser.add_argument('--leads', action='store_true', help='Only sync lead emails')
    parser.add_argument('--query', type=str, help='Custom Gmail query')
    parser.add_argument('--max', type=int, default=100, help='Max emails to fetch')
    parser.add_argument('--thread', type=str, help='Export specific thread by ID')
    
    args = parser.parse_args()
    
    if args.thread:
        gmail = GmailClient()
        export_thread(gmail, args.thread)
    else:
        sync_emails(
            days=args.days,
            leads_only=args.leads,
            custom_query=args.query,
            max_emails=args.max
        )


if __name__ == '__main__':
    main()

