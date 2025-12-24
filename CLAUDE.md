# Chroma GTM Workspace

This is the Go-To-Market workspace for Chroma, the AI-native embedding database.

## About Chroma
- 100M+ downloads, 25k+ GitHub stars
- YC W23 company
- Positioning: "Context layer + Search Agent" (NOT "vector database")
- ICP: 2,000-5,000 high-value accounts (high-touch, not volume)

## Key Files to Read First

### Strategy & Context
- `context/GTM_CONTEXT.md` - **Master strategy document** (read this first)
- `context/MEETING_INDEX.md` - Index of all meeting notes
- `CHROMA_COMPETITORS.md` - Competitor analysis

### Companies & Leads
- `MASTER_COMPANY_LIST.md` - Target companies overview
- `*_COMPANIES_FINAL.json` - Company data by source (langchain, qdrant, weaviate, etc.)
- `chroma_signal_companies.json` - Signal data (companies hiring AI engineers)
- `tier1_*.csv` to `tier4_*.csv` - Tiered company lists

### LinkedIn & Outreach
- `LINKEDIN_STRATEGY_PLAYBOOK.md` - Full LinkedIn strategy
- `LINKEDIN_OUTREACH_TEMPLATES.md` - Message templates
- `LINKEDIN_CONTENT_CALENDAR.md` - Content planning
- `DUXSOUP_CAMPAIGN_GUIDE.md` - Automation guide

### Meeting Notes
- `meetings/notes/` - All meeting notes (use `_TEMPLATE.md` for new ones)

### SEO Strategy
- `seo_strategy/` - SVG diagrams of SEO strategy

## Common Tasks

### Add a New Meeting Note
1. Copy `meetings/notes/_TEMPLATE.md`
2. Name it `YYYY-MM-DD_topic-name.md`
3. Fill in the template

### Update Company Data
- Edit relevant JSON file in root
- Include: company name, source, use case, tier

### Create LinkedIn Content
- Reference `LINKEDIN_CONTENT_CALENDAR.md` for schedule
- Use templates from `LINKEDIN_OUTREACH_TEMPLATES.md`

### Run Scripts
Key Python scripts:
- `chroma_signal_list.py` - Signal discovery
- `sync_companies_to_attio.py` - CRM sync
- `linkedin_sales_nav_automation.py` - LinkedIn automation
- `slack_lead_notifier.py` - Slack notifications

## Current Priorities (Q1 2025)
1. Series A Fundraise - Jan 2025
2. 8-Week Content Push
3. Fix GTM Infrastructure (HubSpot, UTMs)
4. Search Agent GTM

## Style Guidelines
- Meeting notes: Use existing format in `meetings/notes/`
- Company data: Include company name, source, use case
- Commit messages: Be descriptive (e.g., "Add notes from Demand Curve call")

## File Organization
```
/
├── context/           # Strategy docs
├── meetings/notes/    # Meeting notes
├── seo_strategy/      # SEO diagrams
├── linkedin-sales-nav-extension/  # Chrome extension
├── *.py               # Automation scripts
├── *.json             # Company/lead data
├── *.csv              # Exported data (Git LFS)
├── *.md               # Documentation
└── *.ipynb            # Analysis notebooks (Git LFS)
```

