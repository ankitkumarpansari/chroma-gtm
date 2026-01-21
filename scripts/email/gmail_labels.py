#!/usr/bin/env python3
"""
Gmail Labels Manager for Chroma GTM
Create labels, tag outbound emails as leads, organize emails.

Usage:
    python gmail_labels.py setup                    # Create GTM labels
    python gmail_labels.py tag-outbound             # Tag recent outbound as leads
    python gmail_labels.py tag-outbound --days 30  # Tag last 30 days
    python gmail_labels.py list                     # List all labels
"""

import argparse
from datetime import datetime
from gmail_client import GmailClient

# Labels to create
GTM_LABELS = [
    'GTM/Leads',
    'GTM/Leads/Outbound',
    'GTM/Leads/Inbound',
    'GTM/Leads/Replied',
    'GTM/Partners',
    'GTM/Customers',
    'GTM/Follow-up',
]

# Domains to exclude from lead tagging (internal, automated, etc.)
EXCLUDE_DOMAINS = [
    'trychroma.com',
    'github.com',
    'google.com',
    'linkedin.com',
    'slack.com',
    'notion.so',
    'hubspot.com',
    'stripe.com',
    'calendly.com',
    'zoom.us',
]


class GmailLabelsManager:
    def __init__(self):
        self.gmail = GmailClient()
        self.service = self.gmail.service
        self._labels_cache = None
    
    def get_labels(self) -> dict:
        """Get all labels as {name: id} dict."""
        if self._labels_cache is None:
            results = self.service.users().labels().list(userId='me').execute()
            self._labels_cache = {l['name']: l['id'] for l in results.get('labels', [])}
        return self._labels_cache
    
    def create_label(self, name: str) -> str:
        """Create a label if it doesn't exist."""
        labels = self.get_labels()
        
        if name in labels:
            print(f"  ✓ Label exists: {name}")
            return labels[name]
        
        # Create the label
        label_body = {
            'name': name,
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show',
        }
        
        result = self.service.users().labels().create(
            userId='me',
            body=label_body
        ).execute()
        
        print(f"  ✅ Created label: {name}")
        self._labels_cache = None  # Clear cache
        return result['id']
    
    def setup_gtm_labels(self):
        """Create all GTM labels."""
        print("📁 Setting up GTM labels...")
        
        for label in GTM_LABELS:
            self.create_label(label)
        
        print("\n✅ GTM labels ready!")
        print("   You can now see them in Gmail under 'GTM' folder.")
    
    def add_label_to_message(self, message_id: str, label_id: str):
        """Add a label to a message."""
        self.service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'addLabelIds': [label_id]}
        ).execute()
    
    def tag_outbound_as_leads(self, days: int = 7):
        """Tag outbound emails as leads."""
        print(f"🏷️  Tagging outbound emails from last {days} days as leads...")
        
        # Ensure labels exist
        labels = self.get_labels()
        if 'GTM/Leads/Outbound' not in labels:
            print("   Creating GTM labels first...")
            self.setup_gtm_labels()
            labels = self.get_labels()
        
        outbound_label_id = labels['GTM/Leads/Outbound']
        leads_label_id = labels['GTM/Leads']
        
        # Search for sent emails
        query = f'in:sent newer_than:{days}d'
        results = self.service.users().messages().list(
            userId='me',
            q=query,
            maxResults=100
        ).execute()
        
        messages = results.get('messages', [])
        print(f"   Found {len(messages)} sent emails")
        
        tagged_count = 0
        skipped_count = 0
        
        for msg in messages:
            # Get message details
            msg_data = self.service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata',
                metadataHeaders=['To', 'Cc']
            ).execute()
            
            # Check if already labeled
            existing_labels = msg_data.get('labelIds', [])
            if outbound_label_id in existing_labels:
                skipped_count += 1
                continue
            
            # Get recipient
            headers = {h['name'].lower(): h['value'] 
                      for h in msg_data['payload'].get('headers', [])}
            to_addr = headers.get('to', '').lower()
            
            # Skip internal/excluded domains
            should_skip = False
            for domain in EXCLUDE_DOMAINS:
                if domain in to_addr:
                    should_skip = True
                    break
            
            if should_skip:
                skipped_count += 1
                continue
            
            # Add labels
            self.service.users().messages().modify(
                userId='me',
                id=msg['id'],
                body={'addLabelIds': [outbound_label_id, leads_label_id]}
            ).execute()
            
            tagged_count += 1
            
            # Extract recipient for display
            recipient = to_addr.split(',')[0].strip()
            if '<' in recipient:
                recipient = recipient.split('<')[1].split('>')[0]
            print(f"   ✅ Tagged: {recipient[:40]}")
        
        print(f"\n✅ Done!")
        print(f"   Tagged: {tagged_count} emails")
        print(f"   Skipped: {skipped_count} (already tagged or internal)")
    
    def tag_replies_as_leads(self, days: int = 7):
        """Tag inbound replies from leads."""
        print(f"🏷️  Tagging inbound replies from last {days} days...")
        
        labels = self.get_labels()
        if 'GTM/Leads/Replied' not in labels:
            self.setup_gtm_labels()
            labels = self.get_labels()
        
        replied_label_id = labels['GTM/Leads/Replied']
        leads_label_id = labels['GTM/Leads']
        
        # Find threads where we sent outbound and got a reply
        outbound_label_id = labels.get('GTM/Leads/Outbound')
        if not outbound_label_id:
            print("   No outbound emails tagged yet. Run 'tag-outbound' first.")
            return
        
        # Get threads with outbound label
        results = self.service.users().threads().list(
            userId='me',
            labelIds=[outbound_label_id],
            maxResults=50
        ).execute()
        
        threads = results.get('threads', [])
        print(f"   Found {len(threads)} outbound threads")
        
        replied_count = 0
        
        for thread in threads:
            thread_data = self.service.users().threads().get(
                userId='me',
                id=thread['id'],
                format='metadata',
                metadataHeaders=['From']
            ).execute()
            
            messages = thread_data.get('messages', [])
            
            # Check if there's a reply (message not from us)
            has_reply = False
            for msg in messages:
                headers = {h['name'].lower(): h['value'] 
                          for h in msg['payload'].get('headers', [])}
                from_addr = headers.get('from', '').lower()
                
                if 'trychroma.com' not in from_addr:
                    has_reply = True
                    
                    # Tag the reply
                    existing_labels = msg.get('labelIds', [])
                    if replied_label_id not in existing_labels:
                        self.service.users().messages().modify(
                            userId='me',
                            id=msg['id'],
                            body={'addLabelIds': [replied_label_id, leads_label_id]}
                        ).execute()
                        replied_count += 1
                        print(f"   ✅ Reply from: {from_addr[:40]}")
        
        print(f"\n✅ Done! Tagged {replied_count} replies.")
    
    def list_labels(self):
        """List all labels."""
        print("📁 Gmail Labels:\n")
        labels = self.get_labels()
        
        # Group by prefix
        gtm_labels = []
        other_labels = []
        
        for name in sorted(labels.keys()):
            if name.startswith('GTM/'):
                gtm_labels.append(name)
            elif not name.startswith(('CATEGORY_', 'CHAT', 'SENT', 'INBOX', 'TRASH', 'DRAFT', 'SPAM', 'STARRED', 'UNREAD', 'IMPORTANT')):
                other_labels.append(name)
        
        if gtm_labels:
            print("GTM Labels:")
            for name in gtm_labels:
                print(f"  • {name}")
            print()
        
        if other_labels:
            print("Other Labels:")
            for name in other_labels:
                print(f"  • {name}")


def main():
    parser = argparse.ArgumentParser(description='Gmail Labels Manager')
    parser.add_argument('command', choices=['setup', 'tag-outbound', 'tag-replies', 'list'],
                       help='Command to run')
    parser.add_argument('--days', type=int, default=7, help='Days to look back')
    
    args = parser.parse_args()
    
    manager = GmailLabelsManager()
    
    if args.command == 'setup':
        manager.setup_gtm_labels()
    elif args.command == 'tag-outbound':
        manager.tag_outbound_as_leads(days=args.days)
    elif args.command == 'tag-replies':
        manager.tag_replies_as_leads(days=args.days)
    elif args.command == 'list':
        manager.list_labels()


if __name__ == '__main__':
    main()

