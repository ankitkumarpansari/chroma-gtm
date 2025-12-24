# 🚀 Lead Discovery Automation Setup

## Quick Start

Run the discovery engine manually:

```bash
cd "/Users/ankitpansari/Desktop/Chroma GTM"
python3 run_lead_discovery.py --limit 10
```

## What It Does

```
┌─────────────────────────────────────────────────────────────┐
│                  LEAD DISCOVERY ENGINE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   1. FindAll Query                                          │
│      └── Discover companies hiring for vector DB roles       │
│                                                              │
│   2. Smart Filtering                                        │
│      ├── 🚫 Remove vector DB competitors                    │
│      ├── 🏢 Remove large enterprises (won't buy)            │
│      └── ⏭️  Skip duplicates                                 │
│                                                              │
│   3. Save to Chroma                                         │
│      └── Qualified leads stored in hiring_leads              │
│                                                              │
│   4. Slack Notification                                     │
│      ├── 📱 Individual notification per lead                │
│      └── 🔥 Hot lead alerts (mentions Chroma)               │
│                                                              │
│   5. Attio CRM Sync                                         │
│      └── Company added to "Companies with RAG Jobs" list     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Option 1: Cron Job (Mac/Linux)

Run daily at 9am:

```bash
# Open crontab editor
crontab -e

# Add this line (adjust path as needed):
0 9 * * * cd "/Users/ankitpansari/Desktop/Chroma GTM" && /usr/bin/python3 run_lead_discovery.py --limit 15 >> /tmp/lead_discovery.log 2>&1
```

### Cron Schedule Examples:

| Schedule | Cron Expression |
|----------|-----------------|
| Daily at 9am | `0 9 * * *` |
| Weekdays at 9am | `0 9 * * 1-5` |
| Every Monday at 9am | `0 9 * * 1` |
| Every 6 hours | `0 */6 * * *` |

---

## Option 2: macOS launchd (Better for Mac)

Create a plist file:

```bash
# Create the plist
cat > ~/Library/LaunchAgents/com.chroma.leadgen.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.chroma.leadgen</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/ankitpansari/Desktop/Chroma GTM/run_lead_discovery.py</string>
        <string>--limit</string>
        <string>15</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/ankitpansari/Desktop/Chroma GTM</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/lead_discovery.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/lead_discovery_error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
EOF

# Load the job
launchctl load ~/Library/LaunchAgents/com.chroma.leadgen.plist

# Check status
launchctl list | grep chroma
```

### Control Commands:

```bash
# Stop the job
launchctl unload ~/Library/LaunchAgents/com.chroma.leadgen.plist

# Start the job
launchctl load ~/Library/LaunchAgents/com.chroma.leadgen.plist

# Run immediately (for testing)
launchctl start com.chroma.leadgen

# View logs
tail -f /tmp/lead_discovery.log
```

---

## Option 3: GitHub Actions (Cloud-based, Free)

Create `.github/workflows/lead-discovery.yml`:

```yaml
name: Lead Discovery

on:
  schedule:
    - cron: '0 14 * * *'  # 9am EST (14:00 UTC)
  workflow_dispatch:  # Manual trigger

jobs:
  discover:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run discovery
        env:
          PARALLEL_API_KEY: ${{ secrets.PARALLEL_API_KEY }}
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          ATTIO_API_KEY: ${{ secrets.ATTIO_API_KEY }}
        run: |
          python run_lead_discovery.py --limit 15
```

Then add secrets in GitHub repo settings.

---

## Monitoring

### Check Logs:

```bash
# View recent log
tail -50 /tmp/lead_discovery.log

# Watch live
tail -f /tmp/lead_discovery.log
```

### Slack Alerts

You'll automatically get notified in #chroma-leads when:
- 📱 New lead discovered
- 🔥 Hot lead (mentions Chroma)

---

## Troubleshooting

### "PARALLEL_API_KEY not found"
```bash
# Check .env file
cat .env | grep PARALLEL
```

### "No new leads"
- Leads may already be in database (dedup working)
- Try increasing --limit
- Check Parallel API credits

### Cron not running
```bash
# Check cron service
sudo service cron status

# View cron logs
grep CRON /var/log/syslog
```

---

## Cost Considerations

| Service | Cost |
|---------|------|
| Parallel FindAll | ~$0.10-0.50 per query (depends on match_limit) |
| Chroma Cloud | Free tier available |
| Slack | Free |
| Attio | Free tier available |

**Recommendation**: Run with `--limit 10-15` daily = ~$3-15/month

---

## Questions?

The pipeline is fully automated. Just set up the cron/launchd and leads will flow into:
1. ✅ Chroma (database)
2. ✅ Slack (notifications)
3. ✅ Attio (CRM follow-up)

