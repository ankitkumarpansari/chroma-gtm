#!/usr/bin/env python3
"""
Gmail API Client for Chroma GTM
Direct Gmail API integration - no MCP, just pure Python.

Features:
- Read emails (inbox, sent, all)
- Search emails with Gmail query syntax
- Create drafts
- Send emails
- Get thread conversations

Setup:
1. Place credentials.json in this folder (from Google Cloud Console)
2. Run any script - it will prompt for OAuth on first use
3. Token is saved for future use

Usage:
    from gmail_client import GmailClient
    
    gmail = GmailClient()
    emails = gmail.get_recent_emails(days=7)
    gmail.create_draft("to@email.com", "Subject", "Body")
"""

import os
import pickle
import base64
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import List, Dict, Optional
import re

try:
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("❌ Missing dependencies. Run:")
    print("   pip install google-auth-oauthlib google-api-python-client")
    exit(1)

# Scopes for Gmail access
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.modify',
]

SCRIPT_DIR = Path(__file__).parent
CREDENTIALS_FILE = SCRIPT_DIR / 'credentials.json'
TOKEN_FILE = SCRIPT_DIR / 'token.pickle'


class GmailClient:
    """Gmail API client for Chroma GTM."""
    
    def __init__(self):
        self.service = self._authenticate()
        self._profile = None
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None
        
        # Load existing token
        if TOKEN_FILE.exists():
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not CREDENTIALS_FILE.exists():
                    raise FileNotFoundError(
                        f"Missing {CREDENTIALS_FILE}\n"
                        "Download from Google Cloud Console → Credentials → OAuth 2.0 Client ID"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_FILE), SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        
        return build('gmail', 'v1', credentials=creds)
    
    @property
    def profile(self) -> Dict:
        """Get user profile."""
        if not self._profile:
            self._profile = self.service.users().getProfile(userId='me').execute()
        return self._profile
    
    @property
    def email_address(self) -> str:
        """Get authenticated email address."""
        return self.profile['emailAddress']
    
    # =========================================================================
    # READ EMAILS
    # =========================================================================
    
    def get_recent_emails(self, days: int = 7, max_results: int = 50, 
                          label: str = 'INBOX') -> List[Dict]:
        """Get recent emails from inbox."""
        query = f'newer_than:{days}d'
        return self.search_emails(query, max_results=max_results, label=label)
    
    def search_emails(self, query: str, max_results: int = 50, 
                      label: str = None) -> List[Dict]:
        """
        Search emails using Gmail query syntax.
        
        Examples:
            gmail.search_emails("from:user@example.com")
            gmail.search_emails("subject:meeting")
            gmail.search_emails("is:unread newer_than:3d")
            gmail.search_emails("from:leads has:attachment")
        """
        params = {
            'userId': 'me',
            'maxResults': max_results,
            'q': query,
        }
        if label:
            params['labelIds'] = [label]
        
        results = self.service.users().messages().list(**params).execute()
        messages = results.get('messages', [])
        
        emails = []
        for msg in messages:
            email_data = self.get_email(msg['id'])
            if email_data:
                emails.append(email_data)
        
        return emails
    
    def get_email(self, message_id: str, include_body: bool = True) -> Dict:
        """Get a single email by ID."""
        msg = self.service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        # Parse headers
        headers = {}
        for header in msg['payload'].get('headers', []):
            name = header['name'].lower()
            if name in ['from', 'to', 'cc', 'bcc', 'subject', 'date', 'reply-to']:
                headers[name] = header['value']
        
        # Parse body
        body = ''
        if include_body:
            body = self._extract_body(msg['payload'])
        
        # Parse labels
        labels = msg.get('labelIds', [])
        
        return {
            'id': msg['id'],
            'thread_id': msg['threadId'],
            'from': headers.get('from', ''),
            'to': headers.get('to', ''),
            'cc': headers.get('cc', ''),
            'subject': headers.get('subject', ''),
            'date': headers.get('date', ''),
            'snippet': msg.get('snippet', ''),
            'body': body,
            'labels': labels,
            'is_unread': 'UNREAD' in labels,
        }
    
    def _extract_body(self, payload: Dict) -> str:
        """Extract email body from payload."""
        body = ''
        
        if 'body' in payload and payload['body'].get('data'):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
        
        if 'parts' in payload:
            for part in payload['parts']:
                mime_type = part.get('mimeType', '')
                if mime_type == 'text/plain':
                    if part['body'].get('data'):
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                        break
                elif mime_type.startswith('multipart/'):
                    body = self._extract_body(part)
                    if body:
                        break
        
        return body.strip()
    
    def get_thread(self, thread_id: str) -> Dict:
        """Get full email thread/conversation."""
        thread = self.service.users().threads().get(
            userId='me',
            id=thread_id,
            format='full'
        ).execute()
        
        messages = []
        for msg in thread.get('messages', []):
            headers = {}
            for header in msg['payload'].get('headers', []):
                name = header['name'].lower()
                if name in ['from', 'to', 'subject', 'date']:
                    headers[name] = header['value']
            
            messages.append({
                'id': msg['id'],
                'from': headers.get('from', ''),
                'to': headers.get('to', ''),
                'subject': headers.get('subject', ''),
                'date': headers.get('date', ''),
                'snippet': msg.get('snippet', ''),
                'body': self._extract_body(msg['payload']),
            })
        
        return {
            'id': thread_id,
            'subject': messages[0]['subject'] if messages else '',
            'messages': messages,
            'message_count': len(messages),
        }
    
    # =========================================================================
    # WRITE EMAILS
    # =========================================================================
    
    def create_draft(self, to: str, subject: str, body: str, 
                     cc: str = None, reply_to_id: str = None) -> Dict:
        """
        Create a draft email.
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body (plain text)
            cc: CC recipients (optional)
            reply_to_id: Message ID to reply to (optional)
        
        Returns:
            Draft info with ID and link
        """
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        if cc:
            message['cc'] = cc
        
        message.attach(MIMEText(body, 'plain'))
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        draft_body = {'message': {'raw': raw}}
        if reply_to_id:
            draft_body['message']['threadId'] = reply_to_id
        
        draft = self.service.users().drafts().create(
            userId='me',
            body=draft_body
        ).execute()
        
        return {
            'id': draft['id'],
            'message_id': draft['message']['id'],
            'to': to,
            'subject': subject,
            'link': 'https://mail.google.com/mail/u/0/#drafts',
        }
    
    def send_email(self, to: str, subject: str, body: str, 
                   cc: str = None) -> Dict:
        """Send an email directly (use with caution!)."""
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        if cc:
            message['cc'] = cc
        
        message.attach(MIMEText(body, 'plain'))
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        sent = self.service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()
        
        return {
            'id': sent['id'],
            'to': to,
            'subject': subject,
        }
    
    # =========================================================================
    # LABELS
    # =========================================================================
    
    def get_labels(self) -> List[Dict]:
        """Get all Gmail labels."""
        results = self.service.users().labels().list(userId='me').execute()
        return results.get('labels', [])
    
    def get_emails_by_label(self, label_name: str, max_results: int = 50) -> List[Dict]:
        """Get emails with a specific label."""
        # Find label ID
        labels = self.get_labels()
        label_id = None
        for label in labels:
            if label['name'].lower() == label_name.lower():
                label_id = label['id']
                break
        
        if not label_id:
            return []
        
        return self.search_emails('', max_results=max_results, label=label_id)
    
    # =========================================================================
    # HELPERS
    # =========================================================================
    
    def extract_email_address(self, from_header: str) -> str:
        """Extract email from 'Name <email@domain.com>' format."""
        match = re.search(r'<([^>]+)>', from_header)
        if match:
            return match.group(1)
        return from_header
    
    def extract_name(self, from_header: str) -> str:
        """Extract name from 'Name <email@domain.com>' format."""
        match = re.search(r'^([^<]+)', from_header)
        if match:
            return match.group(1).strip().strip('"')
        return from_header.split('@')[0]
    
    def get_unread_count(self) -> int:
        """Get count of unread emails in inbox."""
        results = self.service.users().messages().list(
            userId='me',
            labelIds=['INBOX', 'UNREAD'],
            maxResults=1
        ).execute()
        return results.get('resultSizeEstimate', 0)


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """Command-line interface for testing."""
    import sys
    
    gmail = GmailClient()
    print(f"✅ Connected as: {gmail.email_address}")
    print(f"📬 Unread emails: {gmail.get_unread_count()}")
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'recent':
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            emails = gmail.get_recent_emails(days=days, max_results=10)
            print(f"\n📧 Recent emails ({days} days):")
            for email in emails:
                status = "🔵" if email['is_unread'] else "⚪"
                print(f"{status} {email['from'][:40]}")
                print(f"   {email['subject'][:60]}")
                print()
        
        elif command == 'search':
            query = ' '.join(sys.argv[2:])
            emails = gmail.search_emails(query, max_results=10)
            print(f"\n🔍 Search: {query}")
            for email in emails:
                print(f"• {email['from'][:40]}")
                print(f"  {email['subject'][:60]}")
                print()
        
        elif command == 'thread':
            thread_id = sys.argv[2]
            thread = gmail.get_thread(thread_id)
            print(f"\n📧 Thread: {thread['subject']}")
            print(f"   Messages: {thread['message_count']}")
            for msg in thread['messages']:
                print(f"\n   From: {msg['from']}")
                print(f"   {msg['snippet'][:100]}...")
        
        elif command == 'draft':
            to = sys.argv[2]
            subject = sys.argv[3] if len(sys.argv) > 3 else "Test"
            body = sys.argv[4] if len(sys.argv) > 4 else "Test email"
            draft = gmail.create_draft(to, subject, body)
            print(f"✅ Draft created: {draft['link']}")
        
        else:
            print(f"Unknown command: {command}")
            print("Commands: recent [days], search <query>, thread <id>, draft <to> <subject> <body>")
    else:
        print("\nUsage:")
        print("  python gmail_client.py recent [days]")
        print("  python gmail_client.py search <query>")
        print("  python gmail_client.py thread <thread_id>")
        print("  python gmail_client.py draft <to> <subject> <body>")


if __name__ == '__main__':
    main()

