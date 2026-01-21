# Chroma GTM Executive Summary
## For Jeff | January 2026

---

## 🎯 Mission

> **"Use GTM engineering and AI to avoid needing a 40-person sales org."**

Build automated systems that do the work of a large sales team. Every manual process becomes a repeatable, scalable workflow.

---

## 📊 Revenue Context

| Source | 2026 Target | Current State |
|--------|-------------|---------------|
| **PLG** | $1-2M max | Supporting channel |
| **Enterprise/OEM** | ~$18M | Primary focus |
| **Total** | **$20M ARR** | ~$1M run rate today |

**Key Insight**: PLG has a ceiling. Enterprise/OEM is where the revenue comes from. Target universe is only ~2,000–5,000 companies.

---

## 🔧 GTM Tool Stack

### 🗄️ LAYER 1: DATA FOUNDATION
*Clean, unified data pipelines that give a 360° view of prospects and customers.*

| Tool | Purpose | Status | Cost |
|------|---------|--------|------|
| **HubSpot** | CRM & system of record | ✅ Active | Existing |
| **PostHog** | Product analytics & user behavior | ✅ Active | Existing |
| **Reo.dev** | Developer signals (GitHub, docs, CLI) + identity resolution | 🟡 Trial | ~$30K/yr |
| **Chroma Signal (Internal)** | Target company database (~5,800 companies) | ✅ Active | Internal |

### 🧠 LAYER 2: MODELLING
*Intelligent segmentation, ICP scoring, and enrichment.*

| Tool | Purpose | Status | Cost |
|------|---------|--------|------|
| **Factors.ai** | Account identification + attribution + ICP scoring | 🟡 Trial | ~$20K/yr |
| **Sumble** | Job-post signals + account scoring + urgency ranking | 🟡 Evaluating | TBD |
| **Parallel.ai FindAll** | Web-scale entity discovery + technographics | ✅ Active | ~$3-15/mo |

### ⚡ LAYER 3: ACTIVATION
*Automated, scalable workflows across email, ads, and outbound channels.*

| Tool | Purpose | Status | Cost |
|------|---------|--------|------|
| **Dux-Soup** | LinkedIn automation (visits, connections, nurture) | ✅ Active | ~$50/mo |
| **LinkedIn Sales Navigator** | Prospecting & lead lists | ✅ Active | ~$100/mo |
| **Slack Webhooks** | Real-time lead alerts | ✅ Active | Free |
| **Demand Curve** | Paid ads agency (LinkedIn ABM, Google, Reddit) | 📋 Planned | $5-10K/mo |
| **SmartLead** | Email automation sequences | 📋 Evaluating | ~$100-200/mo |
| **Instantly** | Email automation (alternative) | 📋 Evaluating | ~$100-200/mo |
| **HeyReach** | LinkedIn automation (alternative to Dux-Soup) | 📋 Evaluating | ~$100/mo |
| **Premium Inboxes** | Gmail deliverability for cold email | 📋 Evaluating | TBD |
| **Vector** | ABM advertising platform | 📋 Considering | TBD |
| **Influ2** | ABM advertising platform | 📋 Considering | TBD |
| **Sendoso** | Gifting for high-value prospects | 📋 Considering | TBD |
| **SDR Agency** | Outbound calling | 📋 Negotiating | ~$10K/mo |

---

## 🤝 GTM Partners & Services

| Partner | Type | Purpose | Status | Cost |
|---------|------|---------|--------|------|
| **Reify** | Fractional CMO | Packaging, positioning, architecture content | 📋 Evaluating | TBD (quarterly retainer) |
| **Demand Curve** | Paid Ads Agency | LinkedIn ABM, Google, Reddit execution | 📋 NDA signed | $5-10K/mo |
| **SDR Agency** | Outbound Agency | Cold calling, meeting setting | 📋 Negotiating | ~$10K/mo |

---

## 💰 Projected Monthly GTM Costs

### Scenario A: Lean Stack (Current + Trials)

| Layer | Tools | Monthly Cost |
|-------|-------|--------------|
| **🗄️ Data Foundation** | HubSpot, PostHog, Reo.dev | ~$2,500 |
| **🧠 Modelling** | Factors.ai, Parallel.ai | ~$1,715 |
| **⚡ Activation** | Dux-Soup, Sales Nav, Slack | ~$150 |
| **TOTAL** | | **~$4,400/mo** |

### Scenario B: Full Stack (With Paid Ads & SDR)

| Layer | Tools | Monthly Cost |
|-------|-------|--------------|
| **🗄️ Data Foundation** | HubSpot, PostHog, Reo.dev | ~$2,500 |
| **🧠 Modelling** | Factors.ai, Parallel.ai, Sumble | ~$2,200 |
| **⚡ Activation** | HeyReach, Sales Nav, Demand Curve, Email, Ads, SDR | ~$27,700 |
| **TOTAL** | | **~$32,400/mo** |

*Note: Activation is where the majority of spend goes in full-stack mode (ads + agency).*

---

## 🚀 Active GTM Motions

### Motion 1: Automated LinkedIn Outreach
```
Profile Visit → Connection Request → Nurture Sequence → Meeting
```
- **Volume**: 400 visits/week, 100 requests/week
- **Target**: 30% accept rate, 20% response rate
- **Goal**: 5+ meetings/week

### Motion 2: OSS → Paid Conversion (NEW via Reo.dev)
```
GitHub/PyPI Activity → Docs/Product Visits → Account Enrichment → Sales Outreach
```
- **Leverage**: 100M PyPI downloads, 40K signups
- **Goal**: Systematic bottom-up → top-down motion

### Motion 3: Account-Based Paid Ads (Coming via Demand Curve)
```
Upload 2K Target Companies → LinkedIn ABM → Google Retargeting → Pipeline
```
- **Budget**: ~$10K/mo ad spend
- **Goal**: SQLs from high-intent accounts

---

## 📈 Key Metrics to Track

| Metric | Target | Current |
|--------|--------|---------|
| LinkedIn connections/week | 30+ | TBD |
| Meetings booked/week | 5+ | TBD |
| Pipeline created/month | Track | TBD |
| Qualified opportunities/month | 20+ | TBD |

---

## 🛠️ What I've Built

1. **Chroma Signal Database** - 5,800+ companies with AI hiring signals
2. **Competitor Customer Lists** - Extracted from Pinecone, Weaviate, Qdrant YouTube channels
3. **LinkedIn Automation Pipeline** - Dux-Soup campaigns with tiered targeting
4. **Lead Discovery Engine** - Automated FindAll → Slack → CRM workflow
5. **GTM Context Documentation** - All strategy, learnings, and decisions captured

---

## 🔍 Prospect Generation: Tools, Scripts & Prompts

### Overview
We use a combination of **AI-powered web discovery**, **competitor intelligence extraction**, and **automated filtering** to generate high-quality prospects at scale.

### Tool #1: Parallel.ai FindAll API
**Purpose**: Web-scale entity discovery to find companies hiring for vector DB roles.

**How it works**:
1. Send natural language query to FindAll API
2. API searches the entire web and extracts matching entities
3. Returns enriched company data with job postings, tech stack, funding

**Script**: `run_lead_discovery.py` (automated daily pipeline)

**Prompt Used**:
```
Find companies with job postings for AI engineers, ML engineers, or data 
scientists that mention vector databases, RAG pipelines, semantic search, 
or embeddings
```

**Match Conditions**:
- `has_vector_job`: Company has job postings mentioning vector databases, RAG, embeddings, or semantic search
- `hiring_tech`: Company is hiring technical roles

**Enrichments Extracted**:
- Industry (AI/ML, FinTech, Healthcare, etc.)
- Vector DB mentioned (Pinecone, Weaviate, Chroma, RAG, embeddings)
- Job titles (ML Engineer, AI Engineer, Data Engineer)
- Funding stage (Seed, Series A/B/C, Public)
- Company size
- Headquarters location

**Cost**: ~$0.10-0.50 per query (~$3-15/month at daily cadence)

---

### Tool #2: YouTube Competitor Intelligence
**Purpose**: Extract customer names from competitor YouTube channels (Pinecone, Weaviate, Qdrant, Vespa, LangChain).

**How it works**:
1. Scrape all video URLs from competitor YouTube channels
2. Extract video descriptions using `yt-dlp`
3. Use LLM (GPT-4o-mini or Claude) to identify customer mentions
4. Aggregate and deduplicate across all videos

**Script**: `extract_customers_llm.py`

**LLM Prompt Used**:
```
Analyze this YouTube video to identify companies that are mentioned as 
Pinecone customers, users, or partners.

Video Title: {video_title}
Video Description: {text}

Instructions:
1. Identify all company names explicitly mentioned as:
   - Using Pinecone
   - Being customers of Pinecone
   - Partners with Pinecone
   - Built with Pinecone

2. Return ONLY a JSON array of company names: ["Company1", "Company2"]
3. Do NOT include Pinecone itself
4. Do NOT include generic terms like "users" or "customers"
```

**Channels Processed**:
- Pinecone (141 videos)
- Weaviate
- Qdrant
- Vespa
- LangChain

**Cost**: ~$1-3 total (GPT-4o-mini at ~$0.01/video)

**Output**: `CUSTOMERS_ONLY.json`, `*_COMPANIES_VERIFIED.json`

---

### Tool #3: LinkedIn Profile Discovery
**Purpose**: Find LinkedIn profiles for target personas at identified companies.

**Script**: `parallel_linkedin_search.py`

**Prompt Used**:
```
FindAll people who spoke at AI Engineer conferences or AI Engineer World's Fair.
Looking specifically for: {names_list}.
These are AI/ML engineers, founders, and technical leaders.
```

**Enrichments**:
- LinkedIn URL
- Twitter handle
- Current company
- Current role

---

### Tool #4: Chroma Signal Aggregator
**Purpose**: Unified database combining all prospect sources.

**Script**: `chroma_signal_list.py`

**Data Sources Aggregated**:
1. YouTube extraction (competitor customers)
2. Parallel API (job posting signals)
3. Claude research (manual deep research)
4. Comprehensive company reports

**Schema**:
```
- company_name, website, description
- source_type: youtube | parallel_api | manual
- tier: 1 (highest) to 4
- category: enterprise | ai_native | competitor_customer | partner
- signal_strength: high | medium | low
- current_vector_db (if known)
```

**Output**: `chroma_signal_companies.json` (5,800+ companies)

---

### Tool #5: Automated Filtering & Alerts
**Purpose**: Filter out competitors and large enterprises, send real-time Slack alerts.

**Script**: `slack_lead_notifier.py`

**Filters Applied**:
1. **Competitor Filter** (auto-excluded):
   - Vector DB companies: Pinecone, Weaviate, Qdrant, Milvus, Turbopuffer, Vespa
   - Embedding companies: Cohere, Voyage, Jina, Nomic
   - Cloud DBs with vector: MongoDB, Redis, Elasticsearch, Supabase

2. **Large Enterprise Filter** (auto-excluded):
   - Big Tech: Amazon, Microsoft, Google, Meta, Apple, Oracle, IBM
   - Consulting: Accenture, Deloitte, McKinsey, TCS, Infosys
   - Large Finance: JPMorgan, Goldman Sachs, Capital One

3. **Hot Lead Detection** (priority alerts):
   - Mentions "Chroma" in job posting → 🔥 HOT LEAD
   - Shows switching signals ("alternative", "migration", "replacing")
   - Enterprise company with vector DB needs

**Output**: Slack notifications to #chroma-leads with:
- Company details
- Vector DB mentioned
- Job titles hiring
- Direct links to website, LinkedIn, Attio CRM

---

### End-to-End Pipeline Flow
```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PROSPECT GENERATION PIPELINE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   1. DISCOVERY (Daily Cron Job)                                         │
│      ├── Parallel.ai FindAll → Companies with vector DB job posts       │
│      ├── YouTube Extraction → Competitor customers                       │
│      └── Manual Research → Claude deep research                          │
│                                                                          │
│   2. FILTERING                                                           │
│      ├── 🚫 Remove vector DB competitors                                │
│      ├── 🏢 Remove large enterprises (won't buy from startup)           │
│      └── ⏭️  Skip duplicates (already in database)                      │
│                                                                          │
│   3. ENRICHMENT                                                          │
│      ├── Industry, funding, size, location                              │
│      ├── Vector DB tech mentioned                                        │
│      └── Job posting URLs                                                │
│                                                                          │
│   4. STORAGE                                                             │
│      └── Save to Chroma Cloud (hiring_leads collection)                 │
│                                                                          │
│   5. NOTIFICATION                                                        │
│      ├── 📱 Individual Slack notification per lead                      │
│      ├── 🔥 Hot lead alerts (mentions Chroma)                           │
│      └── 📊 Sync to Attio CRM                                           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Results to Date
- **5,800+ companies** in Chroma Signal database
- **647 IT services/SI partners** identified (Infosys, Deloitte, EPAM, IBM, ThoughtWorks)
- **700+ LinkedIn Sales Navigator targets** (Brex, Canva, etc.)
- **Competitor customers extracted**: Pinecone, Weaviate, Qdrant, Vespa, LangChain

---

## 🎯 Recommended Tool Stack Decision

### ADOPT (High Confidence)
- ✅ **Reo.dev** - Critical for OSS → paid conversion
- ✅ **Factors.ai** - Best for LinkedIn ABM attribution
- ✅ **Demand Curve** - Expert execution on paid ads

### EVALUATE FURTHER
- 🟡 **Sumble** - Good for account scoring, weak on contacts
- 🟡 **SDR Agency** - Quality concerns for high-value ICP

### SKIP
- ❌ **Common Room** - Lower ID rate (8-10% vs Reo's 20%), weaker ABM

---

## 📅 Next Steps

| Timeline | Action |
|----------|--------|
| **This Week** | Complete Reo.dev beacon deployment on docs/product |
| **This Week** | Review Factors.ai trial data |
| **Next Week** | Sumble account-scoring proposal review |
| **Next Week** | Finalize Demand Curve engagement |
| **End of January** | Tool stack decisions finalized |
| **February** | Full paid ads launch |

---

## 💡 Key Strategic Insights

1. **Budget lives in Elasticsearch/OpenSearch** - Target displacement, not net-new vector DB budget
2. **Target teams, not companies** - AI/ML orgs inside enterprises have the budget
3. **OSS is the GTM engine** - 100M downloads = primary lead source, not vanity metric
4. **High-touch, not volume** - Only 2-5K accounts matter; quality over quantity

---

*Last Updated: January 9, 2026*
*Owner: Ankit Pansari*

