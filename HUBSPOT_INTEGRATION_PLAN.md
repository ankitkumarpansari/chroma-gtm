# HubSpot Integration Plan: Consolidating Chroma GTM Data

> **Goal**: Create a single source of truth in HubSpot for all customer and lead data across the Chroma GTM ecosystem.

---

## 📊 Current Data Landscape

### Data Sources Identified

| Source | Type | Records (Est.) | Location | Current State |
|--------|------|----------------|----------|---------------|
| **Chroma Signal Database** | Companies with AI hiring signals | ~5,800 | Chroma Cloud (`chroma_signal_list` collection) | ✅ Has sync script |
| **Deep Research Pipeline** | Target companies by category | ~200+ | `sync_companies_to_hubspot.py` (hardcoded) | ✅ Has sync script |
| **Competitor Customer Lists** | Pinecone/Weaviate/Qdrant customers | ~500+ | `*_COMPANIES_FINAL.json` files | ⚠️ No sync script |
| **Tier 1-4 User Lists** | Enriched leads from product signups | ~1,000+ | `tier1_enterprise_tech.csv`, `tier2_*.csv`, etc. | ⚠️ No sync script |
| **LinkedIn Target Companies** | Sales Nav prospects | ~700 | `LINKEDIN_TARGET_COMPANIES_CONSOLIDATED.json` | ⚠️ No sync script |
| **AI Engineer Speakers** | Conference speakers | ~100+ | `ai_engineer_speakers_enriched.json` | ⚠️ No sync script |
| **Dormant Business Users** | Reactivation targets | ~500+ | `dormant_business_users_identified.json` | ⚠️ No sync script |
| **Attio CRM** | Existing leads | Unknown | Attio API | ⚠️ Separate CRM |

### Existing Scripts

| Script | Purpose | Status |
|--------|---------|--------|
| `sync_companies_to_hubspot.py` | Syncs Deep Research Pipeline companies | ✅ Working |
| `sync_chroma_signal_to_hubspot.py` | Syncs Chroma Signal database | ✅ Working |
| `attio_sync.py` | Syncs to Attio CRM | ⚠️ Separate system |
| `create_vector_db_property.py` | Creates custom HubSpot properties | ✅ Working |
| `enrich_ping_identity_to_hubspot.py` | Enriches specific company | ✅ Working |

---

## 🎯 Phase 1: HubSpot Setup & Configuration (Week 1)

### 1.1 Create HubSpot Private App

```
Location: Settings → Integrations → Private Apps
```

**Required Scopes:**
- `crm.objects.companies.read`
- `crm.objects.companies.write`
- `crm.objects.contacts.read`
- `crm.objects.contacts.write`
- `crm.objects.deals.read`
- `crm.objects.deals.write`
- `crm.schemas.companies.read`
- `crm.schemas.companies.write`

**Action Items:**
- [ ] Create private app in HubSpot
- [ ] Copy API key to `.env` as `HUBSPOT_API_KEY`
- [ ] Test connection: `python sync_companies_to_hubspot.py --test`

### 1.2 Create Custom Properties for Companies

Run the property creation script or create manually:

| Property Name | Internal Name | Type | Description |
|--------------|---------------|------|-------------|
| Lead Source | `lead_source` | Dropdown | Signal, Deep Research, Competitor Customer, Product Signup |
| Signal Tier | `signal_tier` | Dropdown | Tier 1, Tier 2, Tier 3, Tier 4 |
| Signal Strength | `signal_strength` | Dropdown | High, Medium, Low |
| Current Vector DB | `current_vector_db` | Text | Pinecone, Weaviate, Qdrant, PGVector, etc. |
| Competitor Source | `competitor_source` | Dropdown | Pinecone, Weaviate, Qdrant, Vespa, LangChain |
| Use Case | `use_case` | Text | RAG, Agent, Search, etc. |
| LinkedIn URL | `linkedin_company_url` | URL | Company LinkedIn page |
| Funding Stage | `funding_stage` | Dropdown | Seed, Series A, B, C, D+, Public |
| Chroma Signal ID | `chroma_signal_id` | Text | ID from Chroma Signal database |

### 1.3 Create Custom Properties for Contacts

| Property Name | Internal Name | Type | Description |
|--------------|---------------|------|-------------|
| GitHub URL | `github_url` | URL | GitHub profile |
| Twitter URL | `twitter_url` | URL | Twitter/X profile |
| Lead Score | `lead_score` | Number | 1-10 score |
| VIP Status | `is_vip` | Boolean | VIP customer flag |
| Enrichment Source | `enrichment_source` | Text | How contact was enriched |

---

## 🔄 Phase 2: Data Migration Scripts (Week 1-2)

### 2.1 Master Sync Script Architecture

Create a unified sync orchestrator:

```
hubspot_master_sync.py
├── sync_chroma_signal()        # From Chroma Cloud
├── sync_deep_research()        # From hardcoded list
├── sync_competitor_customers() # From *_COMPANIES_FINAL.json
├── sync_tiered_users()         # From tier*.csv files
├── sync_linkedin_targets()     # From LINKEDIN_TARGET_COMPANIES_CONSOLIDATED.json
├── sync_ai_speakers()          # From ai_engineer_speakers_enriched.json
└── sync_dormant_users()        # From dormant_business_users_identified.json
```

### 2.2 Scripts to Create

#### Script 1: `sync_competitor_customers_to_hubspot.py`

**Purpose:** Sync all competitor customer data from JSON files

**Data Sources:**
- `langchain_COMPANIES_FINAL.json`
- `qdrant_COMPANIES_FINAL.json`
- `weaviate_COMPANIES_FINAL.json`
- `vespa_COMPANIES_FINAL.json`
- `pinecone_customers_llm.json`

**Properties to Set:**
- `lead_source` = "Competitor Customer"
- `competitor_source` = [Pinecone/Weaviate/etc.]
- `current_vector_db` = [detected from source]

#### Script 2: `sync_tiered_users_to_hubspot.py`

**Purpose:** Sync enriched user signups with their companies

**Data Sources:**
- `tier1_enterprise_tech.csv`
- `tier2_ai_ml_startups.csv`
- `tier3_tech_agencies.csv`
- `tier4_other_business.csv`

**Logic:**
1. Create/update Company record
2. Create/update Contact record
3. Associate Contact → Company

#### Script 3: `sync_linkedin_targets_to_hubspot.py`

**Purpose:** Sync LinkedIn Sales Navigator target list

**Data Source:** `LINKEDIN_TARGET_COMPANIES_CONSOLIDATED.json`

**Properties to Set:**
- `lead_source` = "LinkedIn Sales Nav"
- `linkedin_company_url` = [LinkedIn URL]

#### Script 4: `hubspot_master_sync.py`

**Purpose:** Orchestrate all syncs with deduplication

**Features:**
- Deduplication by domain/company name
- Merge records from multiple sources
- Track sync history
- Generate sync reports

---

## 📋 Phase 3: Data Quality & Deduplication (Week 2)

### 3.1 Deduplication Strategy

**Primary Key:** Company domain (normalized)
**Secondary Key:** Company name (fuzzy match)

```python
# Deduplication priority (higher = preferred)
SOURCE_PRIORITY = {
    "Product Signup": 10,      # Highest - real users
    "Chroma Signal": 8,        # High - hiring signals
    "Deep Research": 7,        # Curated list
    "Competitor Customer": 6,  # Validated users
    "LinkedIn Sales Nav": 5,   # Prospecting
    "AI Speakers": 4,          # Conference leads
}
```

### 3.2 Merge Rules

When duplicates found:
1. Keep record with highest source priority
2. Merge unique properties from all sources
3. Append all use cases/signals
4. Keep earliest `created_date`

### 3.3 Data Validation

- [ ] Normalize all domains (remove www., https://, trailing slashes)
- [ ] Validate email formats
- [ ] Check for obvious test/spam entries
- [ ] Remove internal Chroma emails

---

## 🔌 Phase 4: Integrations & Automation (Week 2-3)

### 4.1 Integration with Signal Tools

| Tool | Integration Type | Purpose |
|------|-----------------|---------|
| **Reo.dev** | HubSpot native | Developer signals → HubSpot contacts |
| **Factors.ai** | HubSpot native | Account identification → HubSpot companies |
| **Sumble** | API/Webhook | Job post signals → HubSpot properties |
| **PostHog** | Via Segment/CDP | Product usage → HubSpot events |

### 4.2 Automated Workflows

**Workflow 1: New High-Value Signal**
```
Trigger: Company created with signal_tier = "Tier 1"
Actions:
  1. Create task for sales team
  2. Send Slack notification
  3. Add to "Hot Leads" list
```

**Workflow 2: Competitor Customer Identified**
```
Trigger: Company created with competitor_source != null
Actions:
  1. Set lifecycle_stage = "Lead"
  2. Add to "Competitor Displacement" campaign
  3. Assign to SDR queue
```

**Workflow 3: Product Signup Enrichment**
```
Trigger: Contact created from product signup
Actions:
  1. Enrich via Clearbit/Apollo
  2. Score lead
  3. Route to appropriate tier list
```

### 4.3 Slack Integration

Modify `slack_lead_notifier.py` to:
- Pull from HubSpot instead of Chroma directly
- Include HubSpot record links
- Respect HubSpot deduplication

---

## 📊 Phase 5: Reporting & Dashboards (Week 3)

### 5.1 HubSpot Reports to Create

| Report | Purpose | Filters |
|--------|---------|---------|
| **Signal Pipeline** | Track companies by tier | Group by signal_tier |
| **Competitor Displacement** | Track competitor customers | Filter by competitor_source |
| **Lead Source Performance** | Attribution | Group by lead_source |
| **Weekly New Signals** | Velocity tracking | Created date = last 7 days |

### 5.2 Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│                    CHROMA GTM DASHBOARD                      │
├─────────────────────┬───────────────────────────────────────┤
│ Total Companies     │ Companies by Tier (Pie)               │
│ [5,800+]           │ [T1: 15%, T2: 25%, T3: 35%, T4: 25%]  │
├─────────────────────┼───────────────────────────────────────┤
│ New This Week       │ Companies by Source (Bar)             │
│ [125]              │ [Signal, Research, Competitor, etc.]  │
├─────────────────────┼───────────────────────────────────────┤
│ Competitor Targets  │ Funnel: Signal → SQL → Closed         │
│ [500+]             │ [Conversion rates]                     │
└─────────────────────┴───────────────────────────────────────┘
```

---

## 🚀 Implementation Checklist

### Week 1: Setup
- [ ] Create HubSpot private app with required scopes
- [ ] Add `HUBSPOT_API_KEY` to `.env`
- [ ] Test connection with `--test` flag
- [ ] Create custom company properties
- [ ] Create custom contact properties
- [ ] Run initial Deep Research sync
- [ ] Run initial Chroma Signal sync

### Week 2: Migration
- [ ] Create `sync_competitor_customers_to_hubspot.py`
- [ ] Create `sync_tiered_users_to_hubspot.py`
- [ ] Create `sync_linkedin_targets_to_hubspot.py`
- [ ] Create `hubspot_master_sync.py` orchestrator
- [ ] Run full data migration
- [ ] Verify deduplication worked
- [ ] Spot-check 20 random records

### Week 3: Automation
- [ ] Set up Reo.dev → HubSpot integration
- [ ] Set up Factors.ai → HubSpot integration
- [ ] Create HubSpot workflows
- [ ] Update `slack_lead_notifier.py` to use HubSpot
- [ ] Create HubSpot reports
- [ ] Build GTM dashboard
- [ ] Document runbooks

### Ongoing
- [ ] Schedule weekly sync job (cron)
- [ ] Monitor for duplicates
- [ ] Review and tune lead scoring
- [ ] Deprecate Attio sync (if migrating fully)

---

## 📁 File Structure After Implementation

```
/Chroma GTM/
├── hubspot/
│   ├── hubspot_master_sync.py          # Main orchestrator
│   ├── sync_competitor_customers.py    # Competitor data sync
│   ├── sync_tiered_users.py            # User tier sync
│   ├── sync_linkedin_targets.py        # LinkedIn sync
│   ├── hubspot_utils.py                # Shared utilities
│   ├── hubspot_properties.py           # Property definitions
│   └── hubspot_dedup.py                # Deduplication logic
├── sync_companies_to_hubspot.py        # Existing (keep)
├── sync_chroma_signal_to_hubspot.py    # Existing (keep)
└── .env                                # API keys
```

---

## ⚠️ Known Issues to Address

1. **HubSpot configuration broken** (from GTM_CONTEXT.md)
   - Need to audit current HubSpot setup
   - May need to clean existing data before migration

2. **UTM tracking not working**
   - Fix before running paid campaigns
   - Ensure proper attribution setup

3. **No identity resolution**
   - Consider Common Room or Reo.dev for identity stitching
   - HubSpot alone won't solve cross-channel identity

4. **Attio vs HubSpot**
   - Currently using both - need to pick one
   - Recommendation: Consolidate to HubSpot (more integrations)

---

## 🔑 Environment Variables Required

```bash
# .env file
HUBSPOT_API_KEY=pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Optional but recommended
CHROMA_API_KEY=ck-xxxxx
CHROMA_TENANT=xxxxx
CHROMA_DATABASE=GTM Signal

# For Slack notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/xxx/xxx
```

---

## 📞 Next Steps

1. **Immediate**: Get HubSpot API key and test connection
2. **Today**: Run existing sync scripts to populate base data
3. **This Week**: Create missing sync scripts for competitor/tier data
4. **Next Week**: Set up integrations and workflows

---

*Last Updated: January 9, 2026*
*Author: GTM Automation Agent*

