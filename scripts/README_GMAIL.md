# Gmail Integration for Chroma GTM

Direct Gmail API integration for reading emails, creating drafts, and syncing email context for Claude.

## Setup (One-Time)

### 1. Prerequisites
```bash
pip install google-auth-oauthlib google-api-python-client
```

### 2. Google Cloud Credentials
Place your `credentials.json` file (from Google Cloud Console) in this folder:
```
scripts/credentials.json
```

### 3. First-Time Authentication
Run any script - it will open a browser for OAuth:
```bash
python gmail_client.py
```

After authenticating, a `token.pickle` file is created for future use.

---

## Scripts

### `gmail_client.py` - Core API Client
The main Gmail API wrapper. Use it directly or import into other scripts.

```bash
# Check connection
python gmail_client.py

# Get recent emails
python gmail_client.py recent 7

# Search emails
python gmail_client.py search "from:leads"

# Create draft
python gmail_client.py draft "to@email.com" "Subject" "Body"
```

### `gmail_sync.py` - Sync Emails to Context
Syncs emails to markdown files that Claude can read.

```bash
# Sync last 7 days
python gmail_sync.py

# Sync last 14 days
python gmail_sync.py --days 14

# Custom query
python gmail_sync.py --query "from:@trychroma.com"

# Export specific thread
python gmail_sync.py --thread THREAD_ID
```

**Creates:**
- `context/EMAILS.md` - All recent emails
- `context/LEADS_INBOX.md` - Potential lead emails
- `context/FOLLOW_UPS.md` - Emails needing response
- `context/email_threads/` - Full thread exports

### `gmail_draft.py` - Create Drafts
Create Gmail drafts from Claude's output.

```bash
# Direct arguments
python gmail_draft.py "to@email.com" "Subject" "Body"

# From file (Claude's email format)
python gmail_draft.py --file email.txt

# From clipboard (copy Claude's output, then run)
python gmail_draft.py --clipboard

# Reply to thread
python gmail_draft.py --reply THREAD_ID "Thanks!"

# Interactive mode
python gmail_draft.py --interactive
```

---

## Workflow Examples

### Daily Email Sync
```bash
# Morning: sync emails and let Claude analyze
cd ~/Desktop/Chroma\ GTM
python scripts/gmail_sync.py --days 3

# Now Claude can see your emails in context/EMAILS.md
```

### Draft Email with Claude
```
1. Ask Claude: "@claude email philip@synca.ai"
2. Claude generates email draft
3. Copy the draft
4. Run: python scripts/gmail_draft.py --clipboard
5. Review in Gmail and send
```

### Reply to Lead
```bash
# Find thread ID from EMAILS.md or Gmail
python scripts/gmail_draft.py --reply abc123 "Thanks for reaching out! Let me..."
```

---

## Gmail Query Syntax

Use these in `gmail_sync.py --query` or `gmail_client.py search`:

| Query | Description |
|-------|-------------|
| `from:user@example.com` | From specific sender |
| `to:me` | Sent to you |
| `subject:meeting` | Subject contains "meeting" |
| `is:unread` | Unread emails |
| `is:starred` | Starred emails |
| `newer_than:7d` | Last 7 days |
| `older_than:1m` | Older than 1 month |
| `has:attachment` | Has attachments |
| `label:leads` | Has specific label |
| `in:inbox` | In inbox |
| `in:sent` | In sent folder |

Combine with AND/OR:
```
from:@trychroma.com newer_than:7d is:unread
```

---

## Security Notes

⚠️ **Never commit these files:**
- `credentials.json` - OAuth client config
- `token.pickle` - Your auth token

These are in `.gitignore` but double-check before pushing.

To revoke access:
1. Go to https://myaccount.google.com/permissions
2. Find "Chroma GTM" and remove access
3. Delete `token.pickle`

---

## Troubleshooting

### "credentials.json not found"
Download from Google Cloud Console → Credentials → OAuth 2.0 Client ID

### "Token expired"
Delete `token.pickle` and re-authenticate:
```bash
rm scripts/token.pickle
python scripts/gmail_client.py
```

### "Insufficient permissions"
Your OAuth consent screen may need additional scopes. Re-create credentials with all required scopes.

