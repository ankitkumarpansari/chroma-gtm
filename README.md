# Chroma Signal 🎯

**GTM Intelligence & Automation Platform for Chroma**

Chroma Signal is the internal tooling that powers Chroma's Go-To-Market operations - from identifying high-intent accounts to automating outreach and syncing with CRMs.

---

## 🤖 For AI Agents (Cursor/Claude/Copilot)

> **⚠️ START HERE**: Before writing ANY code, read these files in order:

1. **[CLAUDE.md](CLAUDE.md)** - AI agent context, script registry, what exists
2. **[SCRIPT_REGISTRY.md](SCRIPT_REGISTRY.md)** - Complete list of all 70+ scripts
3. **[context/GTM_CONTEXT.md](context/GTM_CONTEXT.md)** - Strategy and priorities

**Rule**: Search existing scripts before creating new ones!

---

## 📁 Repository Structure

```
chroma-signal/
├── 📄 README.md                    # You are here
├── 📄 CONTRIBUTING.md              # How to contribute & sync
├── 📄 CLAUDE.md                    # AI assistant context (for Cursor/Claude)
├── 📄 sync.sh                      # Quick sync script
│
├── 📂 context/                     # Strategy & Planning
│   ├── GTM_CONTEXT.md              # Master GTM strategy document
│   ├── GTM_TASKS.md                # Current tasks & priorities
│   └── MEETING_INDEX.md            # Index of meeting notes
│
├── 📂 diagrams/                    # All SVG diagrams (SEO, architecture, etc.)
├── 📂 customer-calls/              # Customer call system
│   ├── templates/                  # Call note templates
│   ├── playbooks/                  # Sales playbooks & battlecards
│   └── README.md
│
├── 📂 linkedin-sales-nav-extension/ # Chrome extension for Sales Navigator
├── 📂 seo_strategy/                # SEO strategy diagrams (SVG)
├── 📂 src/                         # Core source code modules
├── 📂 tests/                       # Test suite
│
├── 📄 *.py                         # Automation scripts (root level)
├── 📄 *.md                         # Documentation files
├── 📄 *.json/*.csv                 # Company & lead data (Git LFS)
│
└── 📄 requirements.txt             # Python dependencies
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/chroma-core/chroma-signal.git
cd chroma-signal

# Install Git LFS (required for large data files)
git lfs install
git lfs pull

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
# Copy example env file
cp .env.example .env

# Add your API keys:
# - OPENAI_API_KEY (for customer extraction)
# - HUBSPOT_API_KEY (for CRM sync)
# - SLACK_WEBHOOK_URL (for notifications)
```

### 3. Run Key Scripts

```bash
# Discover companies hiring AI engineers
python chroma_signal_list.py

# Sync companies to HubSpot
python sync_companies_to_hubspot.py

# Send lead alerts to Slack
python slack_lead_notifier.py
```

---

## 🔧 Key Scripts

### Signal Discovery
| Script | Purpose |
|--------|---------|
| `chroma_signal_list.py` | Discover companies with AI hiring signals |
| `ai_engineer_speakers.py` | Find AI engineer conference speakers |
| `findall_vector_db_leads.py` | Find companies using vector databases |
| `findall_expanded_leads.py` | Expand lead lists with enrichment |

### LinkedIn Automation
| Script | Purpose |
|--------|---------|
| `linkedin_sales_nav_automation.py` | Automate Sales Navigator searches |
| `linkedin_sales_nav_playwright.py` | Playwright-based LinkedIn automation |
| `linkedin_profile_agent.py` | AI agent for LinkedIn profile analysis |
| `find_linkedin_profiles.py` | Find LinkedIn profiles for leads |
| `parallel_linkedin_search.py` | Parallel LinkedIn search (faster) |

### CRM & Integrations (HubSpot)
| Script | Purpose |
|--------|---------|
| `sync_companies_to_hubspot.py` | Sync companies to HubSpot CRM |
| `hubspot_master_sync.py` | Master HubSpot sync orchestration |
| `hubspot_setup_properties.py` | Set up custom HubSpot properties |
| `create_vector_db_property.py` | Create vector DB tracking property |
| `enrich_ping_identity_to_hubspot.py` | Enrich specific accounts |
| `slack_lead_notifier.py` | Send lead notifications to Slack |
| `export_for_looker.py` | Export data for Looker dashboards |

### Data Processing
| Script | Purpose |
|--------|---------|
| `extract_customers_llm.py` | Extract customers from video content using LLM |
| `extract_customers_improved.py` | Improved customer extraction |
| `deduplicate_companies.py` | Deduplicate company lists |
| `chroma_customer_db.py` | Customer database management |

### Visualization
| Script | Purpose |
|--------|---------|
| `chroma_viewer.py` | Streamlit app for viewing signal data |
| `diagram_generator.py` | Generate strategy diagrams |

---

## 📊 Data Files

All large data files use **Git LFS**. After cloning, run `git lfs pull`.

### Company Data
| File | Description |
|------|-------------|
| `chroma_signal_companies.json` | Companies with AI hiring signals (~5,800) |
| `*_COMPANIES_FINAL.json` | Verified customers of competitors (Pinecone, Weaviate, etc.) |
| `VERIFIED_COMPANIES_CLEAN.json` | Cleaned, verified company list |
| `tier1_enterprise_tech.csv` | Tier 1: Enterprise tech companies |
| `tier2_ai_ml_startups.csv` | Tier 2: AI/ML startups |
| `tier3_tech_agencies.csv` | Tier 3: Tech agencies & SIs |
| `tier4_other_business.csv` | Tier 4: Other business accounts |

### Analysis Notebooks
| File | Description |
|------|-------------|
| `Chroma Signal.ipynb` | Main signal analysis notebook |
| `chroma_signal_explorer.ipynb` | Interactive signal explorer |
| `dormant_users_analysis.ipynb` | Dormant user reactivation analysis |
| `si_partner_program_analysis.ipynb` | SI partner program analysis |

---

## 📚 Documentation

### Strategy
- **[GTM Context](context/GTM_CONTEXT.md)** - Master strategy document (read first!)
- **[Competitors](CHROMA_COMPETITORS.md)** - Competitor analysis
- **[Master Company List](MASTER_COMPANY_LIST.md)** - Target accounts overview

### LinkedIn
- **[LinkedIn Strategy Playbook](LINKEDIN_STRATEGY_PLAYBOOK.md)** - Full LinkedIn GTM strategy
- **[Outreach Templates](LINKEDIN_OUTREACH_TEMPLATES.md)** - Message templates
- **[Content Calendar](LINKEDIN_CONTENT_CALENDAR.md)** - Content planning
- **[Dux-Soup Guide](DUXSOUP_CAMPAIGN_GUIDE.md)** - Automation with Dux-Soup

### Setup Guides
- **[Automation Setup](AUTOMATION_SETUP.md)** - How to set up automations
- **[Testing Guide](TESTING_GUIDE.md)** - How to test scripts

---

## 🔌 Chrome Extension

The `linkedin-sales-nav-extension/` folder contains a Chrome extension for LinkedIn Sales Navigator that helps with:
- Extracting company data from searches
- Bulk exporting lead information
- Automating repetitive tasks

See [extension README](linkedin-sales-nav-extension/README.md) for installation.

---

## 🎨 SEO Strategy Diagrams

The `seo_strategy/` folder contains SVG diagrams outlining Chroma's SEO strategy:
- `00_master_overview.svg` - Strategy overview
- `01_keywords.svg` - Keyword strategy
- `02_programmatic.svg` - Programmatic SEO approach
- `03_ai_search.svg` - AI search optimization
- And more...

---

## 🔐 Environment Variables

Create a `.env` file with:

```bash
# Required for customer extraction
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...

# Required for CRM sync
HUBSPOT_API_KEY=pat-...

# Required for Slack notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/...

# Optional
CHROMA_API_KEY=...
```

---

## 📦 Dependencies

Key dependencies (see `requirements.txt` for full list):
- `streamlit` - Web app for data viewing
- `pandas` - Data manipulation
- `playwright` - Browser automation
- `requests` - API calls
- `plotly` - Visualizations

---

## 🔄 Syncing with GitHub

### Quick Sync (Recommended)

```bash
# Use the sync script
./sync.sh "Your commit message"
```

### Manual Sync

```bash
git add -A
git commit -m "Your message"
git push chroma-signal main
```

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for detailed guidelines on:
- File organization & naming conventions
- What gets synced vs excluded
- Git LFS setup
- Commit message guidelines

---

## 📝 For AI Assistants (Cursor/Claude)

Read `CLAUDE.md` first - it contains context about:
- Chroma's positioning and ICP
- Current priorities
- File organization
- Common tasks

---

## 📞 Questions?

Reach out to the GTM team in Slack: `#gtm-signal`

