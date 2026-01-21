# Chroma GTM Workspace - AI Agent Context

> **⚠️ CRITICAL: Before writing ANY code, run the search tool first!**

```bash
python query_workspace.py "your task description"
```

This is the Go-To-Market workspace for Chroma, the AI-native embedding database.

## About Chroma
- 100M+ downloads, 25k+ GitHub stars
- YC W23 company
- Positioning: "Context layer + Search Agent" (NOT "vector database")
- ICP: 2,000-5,000 high-value accounts (high-touch, not volume)
- **Goal**: $20M ARR by EOY 2026

---

## 🔍 STEP 1: ALWAYS SEARCH FIRST

Before creating ANY new script or file, search the workspace:

```bash
# Search for scripts related to your task
python query_workspace.py "sync companies to HubSpot" --type scripts

# Search documentation
python query_workspace.py "LinkedIn strategy" --type docs

# Search everything
python query_workspace.py "your task description"

# Show index stats
python query_workspace.py --stats
```

**If the search finds something relevant → READ IT and MODIFY IT instead of creating new!**

---

## 📁 File Structure

```
/
├── 📋 ROOT (Entry points only)
│   ├── CLAUDE.md                 # THIS FILE - Read first!
│   ├── README.md                 # Project overview
│   ├── SCRIPT_REGISTRY.md        # Script documentation
│   ├── index_workspace.py        # Build search index
│   ├── query_workspace.py        # Search the workspace
│   └── requirements.txt          # Dependencies
│
├── 📂 scripts/                   # ALL Python automation
│   ├── linkedin/                 # LinkedIn automation
│   ├── hubspot/                  # HubSpot CRM sync
│   ├── discovery/                # Lead discovery
│   ├── extraction/               # Customer extraction
│   ├── enrichment/               # Data enrichment
│   ├── notifications/            # Slack alerts
│   ├── sync/                     # External syncs (Sheets, Attio)
│   ├── email/                    # Gmail automation
│   ├── visualization/            # Viewers, diagrams
│   ├── chroma/                   # Chroma DB operations
│   ├── utils/                    # Utilities
│   └── browser/                  # Browser automation
│
├── 📂 docs/                      # ALL documentation
│   ├── strategy/                 # GTM strategy docs
│   ├── competitors/              # Competitor analysis
│   ├── linkedin/                 # LinkedIn playbooks
│   ├── hubspot/                  # HubSpot docs
│   ├── events/                   # Events calendar
│   ├── case-studies/             # Case study materials
│   ├── guides/                   # How-to guides
│   ├── work-plans/               # Personal work plans
│   └── outreach/                 # Outreach templates
│
├── 📂 data/                      # ALL data files
│   ├── companies/                # Company lists (JSON)
│   ├── competitors/              # Competitor customer data
│   │   ├── pinecone/
│   │   ├── weaviate/
│   │   ├── qdrant/
│   │   ├── vespa/
│   │   └── langchain/
│   ├── tiers/                    # Tiered lists (CSV)
│   ├── linkedin/                 # LinkedIn exports
│   ├── users/                    # User data
│   └── exports/                  # Reports & exports
│
├── 📂 notebooks/                 # Jupyter notebooks
├── 📂 meetings/notes/            # Meeting notes
├── 📂 customer-calls/            # Call notes & playbooks
├── 📂 context/                   # Strategy context
├── 📂 diagrams/                  # Generated diagrams
├── 📂 tests/                     # Test files
├── 📂 logs/                      # Log files
├── 📂 config/                    # Configuration
├── 📂 credentials/               # API credentials
└── 📂 archive/                   # Old/unused files
```

---

## 🚨 BEFORE CREATING ANY SCRIPT

### Step 1: Search the workspace
```bash
python query_workspace.py "what you want to do"
```

### Step 2: If found, READ the existing script
```bash
cat scripts/hubspot/sync_companies_to_hubspot.py
```

### Step 3: MODIFY existing code, don't create new

### Step 4: If you MUST create new:
1. Put it in the correct `scripts/` subfolder
2. Add a docstring explaining purpose
3. Follow naming: `{verb}_{noun}_{detail}.py`

---

## 📜 Script Categories

| Category | Location | Purpose |
|----------|----------|---------|
| **LinkedIn** | `scripts/linkedin/` | Sales Nav automation, profile search |
| **HubSpot** | `scripts/hubspot/` | CRM sync, properties, contacts |
| **Discovery** | `scripts/discovery/` | Find leads, signals, speakers |
| **Extraction** | `scripts/extraction/` | Extract customers from YouTube |
| **Enrichment** | `scripts/enrichment/` | Enrich company/contact data |
| **Notifications** | `scripts/notifications/` | Slack alerts |
| **Sync** | `scripts/sync/` | Google Sheets, Attio, external |
| **Email** | `scripts/email/` | Gmail drafts, automation |
| **Visualization** | `scripts/visualization/` | Viewers, diagrams, exports |
| **Chroma** | `scripts/chroma/` | Chroma DB operations |
| **Utils** | `scripts/utils/` | Utilities |
| **Browser** | `scripts/browser/` | Screenshots, browser automation |

---

## 🔧 Common Tasks

### Sync companies to HubSpot
```bash
python scripts/hubspot/sync_companies_to_hubspot.py
```

### Find LinkedIn profiles
```bash
python scripts/linkedin/find_linkedin_profiles.py
# Or parallel:
python scripts/linkedin/parallel_linkedin_search.py
```

### Send Slack alerts
```bash
python scripts/notifications/slack_lead_notifier.py
```

### Sync to Google Sheets
```bash
python scripts/sync/google_sheets_sync.py
```

### Run lead discovery
```bash
python scripts/discovery/run_lead_discovery.py
```

### Extract competitor customers
```bash
python scripts/extraction/extract_customers_llm.py --provider openai
```

---

## 📊 Key Data Files

| File | Location | Description |
|------|----------|-------------|
| `chroma_signal_companies.json` | `data/companies/` | 5,800+ companies with signals |
| `VERIFIED_COMPANIES_CLEAN.json` | `data/companies/` | Verified company list |
| `tier1_enterprise_tech.csv` | `data/tiers/` | Tier 1 companies |
| `pinecone_customers_llm.json` | `data/competitors/pinecone/` | Pinecone customers |
| `ai_engineer_speakers.json` | `data/linkedin/` | AI conference speakers |

---

## 🔑 Environment Variables

```bash
# CRM
HUBSPOT_API_KEY=pat-...

# AI/LLM
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/...

# Google
GOOGLE_SHEETS_CREDENTIALS=path/to/credentials.json
```

---

## 📋 Strategy Documents

| Document | Location | Purpose |
|----------|----------|---------|
| `GTM_CONTEXT.md` | `docs/strategy/` | Master strategy |
| `EXECUTIVE_SUMMARY_GTM.md` | `docs/strategy/` | High-level summary |
| `HUBSPOT_COHORT_STRATEGY.md` | `docs/strategy/` | 4-cohort revenue strategy |
| `LINKEDIN_STRATEGY_PLAYBOOK.md` | `docs/linkedin/` | LinkedIn GTM strategy |
| `CHROMA_COMPETITORS.md` | `docs/competitors/` | Competitor analysis |

---

## 🎯 The 4 Customer Cohorts

| Cohort | Description | Priority |
|--------|-------------|----------|
| 🔴 **Cohort 1** | Current Chroma customers | HIGHEST |
| 🟠 **Cohort 2** | In-market (hiring AI engineers) | HIGH |
| 🟡 **Cohort 3** | Competitor customers | MEDIUM |
| 🟢 **Cohort 4** | SI Partners | STRATEGIC |

---

## 🔄 Keeping the Index Updated

After adding new scripts or docs, rebuild the index:

```bash
# Full index (scripts, docs, companies, meetings)
python index_workspace.py

# Quick index (scripts + docs only)
python index_workspace.py --quick
```

---

## ⚠️ Things to AVOID

1. **Don't create scripts in root** → Put in `scripts/{category}/`
2. **Don't create duplicate scripts** → Search first!
3. **Don't hardcode credentials** → Use environment variables
4. **Don't put data in root** → Use `data/` folder
5. **Don't skip the search** → Always query first!

---

## 🔄 Current Priorities (Q1 2026)

1. **Fundraising Prep** - Demo, pitch deck, GTM plan
2. **ISV Outreach** - 700 emails to understand usage
3. **LinkedIn Automation** - DuxSoup campaigns
4. **HubSpot Fix** - Infrastructure, UTMs, attribution
5. **Content Calendar** - 8-week push into fundraise

---

*Last Updated: January 2026*
*Owner: Ankit Pansari*
