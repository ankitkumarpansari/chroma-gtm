#!/usr/bin/env python3
"""
Gmail Draft Creator for Chroma GTM
Creates email drafts in Gmail from Claude's output or command line.

Usage:
    # Direct arguments
    python gmail_draft.py "to@email.com" "Subject" "Body text"
    
    # From file (supports Claude's email format)
    python gmail_draft.py --file email_draft.txt
    
    # Interactive mode
    python gmail_draft.py --interactive
    
    # Reply to thread
    python gmail_draft.py --reply <thread_id> "Body text"
"""

import sys
import argparse
import re
from pathlib import Path

from gmail_client import GmailClient


def parse_claude_email(content: str) -> dict:
    """
    Parse email from Claude's output format.
    
    Handles formats like:
    ```
    From: Ankit Pansari <ankit@trychroma.com>
    To: philip@synca.ai
    Cc: jeff@trychroma.com
    Subject: Partnership Opportunity
    
    Hey Philip,
    
    [body]
    
    Talk soon!
    ```
    """
    result = {
        'to': '',
        'cc': '',
        'subject': '',
        'body': '',
    }
    
    lines = content.strip().split('\n')
    body_start = 0
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        
        # Skip markdown code fences
        if line.strip().startswith('```'):
            continue
        
        # Parse headers
        if line_lower.startswith('to:'):
            result['to'] = extract_email_from_line(line)
        elif line_lower.startswith('cc:'):
            result['cc'] = extract_email_from_line(line)
        elif line_lower.startswith('subject:'):
            result['subject'] = line.split(':', 1)[1].strip()
        elif line_lower.startswith('from:') or line_lower.startswith('date:'):
            continue  # Skip these
        elif line.strip() == '':
            # Empty line after headers = start of body
            body_start = i + 1
            break
        elif not any(line_lower.startswith(h) for h in ['to:', 'cc:', 'subject:', 'from:', 'date:']):
            # No more headers, this is body
            body_start = i
            break
    
    # Extract body
    body_lines = []
    for line in lines[body_start:]:
        # Stop at closing code fence
        if line.strip() == '```':
            break
        body_lines.append(line)
    
    result['body'] = '\n'.join(body_lines).strip()
    
    return result


def extract_email_from_line(line: str) -> str:
    """Extract email address(es) from a header line."""
    # Remove header prefix
    value = line.split(':', 1)[1].strip() if ':' in line else line
    
    # Extract email from "Name <email>" format
    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', value)
    if emails:
        return ', '.join(emails)
    
    return value


def create_draft_interactive():
    """Interactive mode for creating drafts."""
    print("📧 Gmail Draft Creator")
    print("=" * 40)
    
    to = input("To: ").strip()
    cc = input("Cc (optional): ").strip()
    subject = input("Subject: ").strip()
    
    print("Body (enter empty line to finish):")
    body_lines = []
    while True:
        line = input()
        if line == '':
            break
        body_lines.append(line)
    body = '\n'.join(body_lines)
    
    # Confirm
    print("\n" + "=" * 40)
    print(f"To: {to}")
    if cc:
        print(f"Cc: {cc}")
    print(f"Subject: {subject}")
    print(f"Body:\n{body[:200]}...")
    print("=" * 40)
    
    confirm = input("\nCreate draft? (y/n): ").strip().lower()
    if confirm == 'y':
        gmail = GmailClient()
        draft = gmail.create_draft(to, subject, body, cc=cc if cc else None)
        print(f"\n✅ Draft created!")
        print(f"   Open in Gmail: {draft['link']}")
    else:
        print("❌ Cancelled")


def create_draft_from_file(filepath: str):
    """Create draft from file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Try to parse as Claude's email format
    email = parse_claude_email(content)
    
    if not email['to']:
        print("❌ Could not find 'To:' in file")
        print("   Expected format:")
        print("   To: email@example.com")
        print("   Subject: Your subject")
        print("   ")
        print("   Body text...")
        sys.exit(1)
    
    print(f"📧 Creating draft:")
    print(f"   To: {email['to']}")
    if email['cc']:
        print(f"   Cc: {email['cc']}")
    print(f"   Subject: {email['subject']}")
    print(f"   Body: {email['body'][:100]}...")
    
    gmail = GmailClient()
    draft = gmail.create_draft(
        to=email['to'],
        subject=email['subject'],
        body=email['body'],
        cc=email['cc'] if email['cc'] else None
    )
    
    print(f"\n✅ Draft created!")
    print(f"   Draft ID: {draft['id']}")
    print(f"   Open in Gmail: {draft['link']}")


def create_reply_draft(thread_id: str, body: str):
    """Create a reply draft in an existing thread."""
    gmail = GmailClient()
    
    # Get thread to find recipient
    thread = gmail.get_thread(thread_id)
    if not thread['messages']:
        print(f"❌ Thread not found: {thread_id}")
        sys.exit(1)
    
    # Get the last message to reply to
    last_msg = thread['messages'][-1]
    
    # Determine who to reply to
    from_addr = gmail.extract_email_address(last_msg['from'])
    if from_addr == gmail.email_address:
        # We sent the last message, reply to the original recipient
        to = gmail.extract_email_address(last_msg.get('to', ''))
    else:
        to = from_addr
    
    subject = last_msg['subject']
    if not subject.lower().startswith('re:'):
        subject = f"Re: {subject}"
    
    print(f"📧 Creating reply draft:")
    print(f"   Thread: {thread['subject']}")
    print(f"   To: {to}")
    
    draft = gmail.create_draft(
        to=to,
        subject=subject,
        body=body,
        reply_to_id=thread_id
    )
    
    print(f"\n✅ Reply draft created!")
    print(f"   Open in Gmail: {draft['link']}")


def main():
    parser = argparse.ArgumentParser(description='Create Gmail drafts')
    parser.add_argument('to', nargs='?', help='Recipient email')
    parser.add_argument('subject', nargs='?', help='Email subject')
    parser.add_argument('body', nargs='?', help='Email body')
    parser.add_argument('--cc', help='CC recipients')
    parser.add_argument('--file', '-f', help='Create draft from file')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--reply', '-r', help='Reply to thread ID')
    parser.add_argument('--clipboard', '-c', action='store_true', help='Read from clipboard')
    
    args = parser.parse_args()
    
    if args.interactive:
        create_draft_interactive()
    elif args.file:
        create_draft_from_file(args.file)
    elif args.reply:
        body = args.to or ''  # First positional arg is body for reply
        if not body:
            print("Usage: gmail_draft.py --reply <thread_id> 'Reply body'")
            sys.exit(1)
        create_reply_draft(args.reply, body)
    elif args.clipboard:
        try:
            import subprocess
            content = subprocess.check_output(['pbpaste']).decode('utf-8')
            email = parse_claude_email(content)
            if email['to']:
                gmail = GmailClient()
                draft = gmail.create_draft(
                    to=email['to'],
                    subject=email['subject'],
                    body=email['body'],
                    cc=email['cc'] if email['cc'] else None
                )
                print(f"✅ Draft created from clipboard!")
                print(f"   To: {email['to']}")
                print(f"   Subject: {email['subject']}")
                print(f"   Open in Gmail: {draft['link']}")
            else:
                print("❌ Could not parse email from clipboard")
        except Exception as e:
            print(f"❌ Error reading clipboard: {e}")
    elif args.to:
        gmail = GmailClient()
        draft = gmail.create_draft(
            to=args.to,
            subject=args.subject or 'No Subject',
            body=args.body or '',
            cc=args.cc
        )
        print(f"✅ Draft created!")
        print(f"   To: {args.to}")
        print(f"   Subject: {args.subject or 'No Subject'}")
        print(f"   Open in Gmail: {draft['link']}")
    else:
        parser.print_help()
        print("\nExamples:")
        print('  python gmail_draft.py "john@example.com" "Hello" "Hey John, ..."')
        print('  python gmail_draft.py --file email.txt')
        print('  python gmail_draft.py --clipboard  # From copied Claude output')
        print('  python gmail_draft.py --interactive')
        print('  python gmail_draft.py --reply THREAD_ID "Thanks for your email!"')


if __name__ == '__main__':
    main()
