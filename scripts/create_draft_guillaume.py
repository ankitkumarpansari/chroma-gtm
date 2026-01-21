#!/usr/bin/env python3
"""Create draft email for Guillaume Garcia at HRC Software"""

import sys
from pathlib import Path

# Add scripts/email to path
sys.path.insert(0, str(Path(__file__).parent / 'email'))

from gmail_client import GmailClient
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

# Initialize Gmail client
gmail = GmailClient()

# Email details
to = 'guillaume.garcia@hrc-software.com'
cc = 'jeff@trychroma.com'
subject = 'Chroma Cloud + HRC Software'
body = '''Hey Guillaume,

I see you're trying out Chroma Cloud - welcome!

Checked out HRC Software - excited to see what you're building!

There are a bunch of ways Chroma can help, especially around semantic search, RAG, and intelligent content retrieval for AI applications.

Happy to set you up with:
- Extended credits to test at scale
- Direct Slack channel for technical support
- Call to discuss your use case

If you're building a retrieval app, check out our Search API: https://docs.trychroma.com/cloud/search-api/overview

I'm happy to hop on a call or set up a shared Slack channel, whatever works best for you.

Have cc'd Jeff, founder of Chroma to the thread. Talk soon!

PS: Bumped your credits to $1,000 to get you started!'''

# Create message with CC
message = MIMEMultipart()
message['to'] = to
message['cc'] = cc
message['subject'] = subject
message.attach(MIMEText(body, 'plain'))

# Encode and create draft
raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
draft_body = {'message': {'raw': raw}}

draft = gmail.service.users().drafts().create(
    userId='me',
    body=draft_body
).execute()

print('✅ Draft created!')
print(f'Draft ID: {draft["id"]}')
print(f'To: {to}')
print(f'Cc: {cc}')
print(f'Subject: {subject}')
print('\nOpen your drafts: https://mail.google.com/mail/u/0/#drafts')


