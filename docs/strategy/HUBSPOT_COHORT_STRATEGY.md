# HubSpot Cohort Strategy for Chroma GTM

> **Goal**: $2M Revenue in Q1 2026
> **Strategy**: 4 Customer Cohorts with Clear Prioritization

---

## 📊 The 4 Cohorts Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Q1 2026 REVENUE STRATEGY                            │
│                              Target: $2M                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  🔴 COHORT 1: CURRENT CHROMA CUSTOMERS              HIGHEST PRIORITY        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • Already tried Chroma or have instances                                   │
│  • Currently in pipeline                                                    │
│  • Fastest path to Q1 revenue                                               │
│  • Action: Close deals, expand accounts                                     │
│                                                                             │
│  🟠 COHORT 2: IN-MARKET COMPANIES                   HIGH PRIORITY           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • Hiring AI Engineers (Applied AI, ML experts)                             │
│  • Building AI products                                                     │
│  • AI-native companies building RAG applications                            │
│  • Action: Outbound, demos, fast qualification                              │
│                                                                             │
│  🟡 COHORT 3: COMPETITOR CUSTOMERS                  MEDIUM PRIORITY         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • Using Pinecone, Weaviate, Qdrant, Elasticsearch, etc.                   │
│  • Keep warm, follow up regularly                                           │
│  • Longer sales cycle (Q2+ likely)                                          │
│  • Action: Nurture sequences, competitive intel                             │
│                                                                             │
│  🟢 COHORT 4: SI PARTNERS                           STRATEGIC               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • Implementing AI solutions for their customers                            │
│  • Partnership program participants                                         │
│  • Multiplier effect on revenue                                             │
│  • Action: Enable, support, co-sell                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔴 Cohort 1: Current Chroma Customers

### Definition
Companies that have:
- Active Chroma Cloud accounts (paid or free)
- Tried Chroma Cloud (trial, dormant)
- Open opportunities in pipeline
- Using Chroma OSS with interest in Cloud

### HubSpot Properties

| Property | Values | Purpose |
|----------|--------|---------|
| `customer_cohort` | `cohort_1_current_customer` | Primary segmentation |
| `chroma_customer_status` | active_paid, active_free, trial, pipeline, dormant, oss_only | Current status |
| `chroma_cloud_mrr` | Number | Current revenue |
| `chroma_expansion_potential` | high, medium, low | Upsell opportunity |
| `pipeline_stage` | awareness → closed_won | Deal progress |

### Key Views to Create

1. **"Cohort 1: Active Pipeline"**
   - Filter: `customer_cohort = cohort_1` AND `pipeline_stage` IN (evaluating, demo_scheduled, poc, proposal, negotiation)
   - Sort: Deal amount DESC
   - Columns: Name, Pipeline Stage, MRR, Expansion Potential, Last Activity

2. **"Cohort 1: Expansion Targets"**
   - Filter: `customer_cohort = cohort_1` AND `chroma_expansion_potential = high`
   - Action: Upsell campaigns

3. **"Cohort 1: Dormant Reactivation"**
   - Filter: `chroma_customer_status = dormant`
   - Action: $500 credit reactivation campaign

### Workflows

```
WORKFLOW: Cohort 1 - High Value Alert
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Trigger: Deal amount > $50K AND pipeline_stage changed
Actions:
  1. Send Slack to #gtm-deals
  2. Create task for Ankit
  3. Set q1_revenue_potential = high
```

```
WORKFLOW: Cohort 1 - Dormant Reactivation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Trigger: chroma_customer_status changed to "dormant"
Actions:
  1. Wait 3 days
  2. Send email: "$500 credit added"
  3. Wait 5 days
  4. Create task: "Personal follow-up"
```

### Metrics to Track

| Metric | Target | Dashboard Widget |
|--------|--------|------------------|
| Pipeline Value | $3M+ | Number |
| Deals in Proposal+ | 10+ | Number |
| Avg Deal Size | $30K+ | Number |
| Win Rate | 30%+ | Percentage |

---

## 🟠 Cohort 2: In-Market Companies

### Definition
Companies showing active buying signals:
- Hiring AI Engineers, Applied AI Engineers, ML experts
- Building AI products (detected from job posts, news)
- AI-native companies building RAG applications
- Vector DB mentioned in job posts

### Signal Sources

| Source | Signal Type | Property |
|--------|-------------|----------|
| **Sumble** | Job posts (AI/ML hiring) | `ai_hiring_status`, `ai_job_count` |
| **Reo.dev** | GitHub activity, OSS usage | `signal_source = reodev` |
| **LinkedIn** | Company updates, hiring | `signal_source = linkedin` |
| **Factors.ai** | Website visits | `signal_source = factors` |

### HubSpot Properties

| Property | Values | Purpose |
|----------|--------|---------|
| `customer_cohort` | `cohort_2_in_market` | Primary segmentation |
| `in_market_signals` | hiring_ai_engineers, building_ai_products, ai_native, building_rag, etc. | Multi-select signals |
| `ai_hiring_status` | actively_hiring_high, hiring, recently_hired, jobs_detected | Hiring intensity |
| `ai_job_count` | Number | Quantified signal |
| `company_type` | ai_native_startup, tech_adding_ai, enterprise_ai | Company classification |
| `use_case_detected` | rag, agent, search, doc_analysis, chatbot | Detected use cases |
| `signal_strength` | very_strong, strong, medium, weak | Overall signal quality |

### Key Views to Create

1. **"Cohort 2: Hot In-Market Signals"**
   - Filter: `customer_cohort = cohort_2` AND `signal_strength` IN (very_strong, strong)
   - Sort: `ai_job_count` DESC
   - Columns: Name, AI Hiring Status, Signals, Use Case, Last Engagement

2. **"Cohort 2: AI-Native Companies"**
   - Filter: `company_type = ai_native_startup` AND `in_market_signals` contains `building_rag`
   - Action: Prioritized outreach

3. **"Cohort 2: High Hiring Volume"**
   - Filter: `ai_hiring_status = actively_hiring_high` (5+ AI roles)
   - Action: Immediate outreach

### Workflows

```
WORKFLOW: Cohort 2 - Strong Signal Alert
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Trigger: Company created with signal_strength = very_strong
Actions:
  1. Set customer_cohort = cohort_2_in_market
  2. Set cohort_priority_score = 80
  3. Send Slack to #gtm-signals
  4. Create task: "Outreach within 24 hours"
  5. Enroll in "In-Market Outreach" sequence
```

```
WORKFLOW: Cohort 2 - AI Hiring Detected
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Trigger: ai_job_count > 3
Actions:
  1. Set ai_hiring_status = actively_hiring_high
  2. Set signal_strength = strong (if not already very_strong)
  3. Add to list "High AI Hiring - Q1"
```

### Outreach Sequence

**Sequence: In-Market Outreach**
```
Day 1: "Noticed [Company] is building AI - quick question"
Day 3: "How [Similar Company] reduced RAG latency 60%"
Day 7: "Quick demo of Chroma for [detected use case]?"
Day 14: "Last touch - here when you're ready"
```

### Metrics to Track

| Metric | Target | Dashboard Widget |
|--------|--------|------------------|
| New Signals/Week | 50+ | Line chart |
| Strong Signals | 20%+ of total | Percentage |
| Outreach Response Rate | 15%+ | Percentage |
| Signal → Demo Rate | 10%+ | Funnel |

---

## 🟡 Cohort 3: Competitor Customers

### Definition
Companies currently using competitor vector databases:
- Pinecone, Weaviate, Qdrant, Milvus, Vespa
- Elasticsearch/OpenSearch for vector search
- PGVector, MongoDB Atlas Vector Search
- Any other vector DB solution

### HubSpot Properties

| Property | Values | Purpose |
|----------|--------|---------|
| `customer_cohort` | `cohort_3_competitor` | Primary segmentation |
| `current_vector_db` | pinecone, weaviate, qdrant, elasticsearch, etc. | Multi-select |
| `competitor_source_channel` | youtube, case_study, job_posting, github | How we found them |
| `competitor_pain_points` | cost, performance, accuracy, scaling, ops_burden | Known issues |
| `competitor_relationship_status` | evaluating, open, satisfied, locked_in | Current state |
| `displacement_play` | elastic_displacement, pinecone_migration, cost_reduction | Sales approach |
| `follow_up_cadence` | weekly, biweekly, monthly, quarterly | Touch frequency |
| `next_follow_up_date` | Date | When to follow up |

### Key Views to Create

1. **"Cohort 3: Actively Evaluating"**
   - Filter: `competitor_relationship_status = evaluating`
   - Sort: Last activity DESC
   - Action: Prioritized follow-up

2. **"Cohort 3: Elasticsearch Targets"**
   - Filter: `current_vector_db` contains `elasticsearch` OR `opensearch`
   - Action: "2x faster, 10x cheaper" messaging

3. **"Cohort 3: Follow-up Due"**
   - Filter: `next_follow_up_date` <= TODAY
   - Action: Execute follow-up

4. **"Cohort 3: Pain Points Identified"**
   - Filter: `competitor_pain_points` is not empty
   - Action: Tailored outreach

### Workflows

```
WORKFLOW: Cohort 3 - Keep Warm Cadence
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Trigger: next_follow_up_date = TODAY
Actions:
  1. Create task: "Follow up with [Company]"
  2. Set next_follow_up_date = TODAY + [cadence interval]
```

```
WORKFLOW: Cohort 3 - Competitor Evaluating Alert
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Trigger: competitor_relationship_status changed to "evaluating"
Actions:
  1. Set cohort_priority_score = 70
  2. Set follow_up_cadence = weekly
  3. Send Slack to #gtm-signals: "🎯 [Company] evaluating alternatives!"
  4. Create high-priority task
```

### Nurture Sequence

**Sequence: Competitor Keep Warm**
```
Day 1: Value-add content (benchmark, case study)
Day 14: "Quick question about your [competitor] setup"
Day 30: New feature announcement relevant to their use case
Day 60: "Checking in - anything changed?"
Day 90: Case study of similar company that switched
```

### Sales Plays by Competitor

| Competitor | Play | Key Message |
|------------|------|-------------|
| **Elasticsearch** | Elastic Displacement | "2x faster, 10x cheaper, zero operational burden" |
| **Pinecone** | Pinecone Migration | "Better accuracy, lower cost, open-source foundation" |
| **Weaviate/Qdrant** | OSS Upgrade | "Enterprise features, managed service, same flexibility" |
| **PGVector** | Performance Upgrade | "Purpose-built for vectors, 10x faster at scale" |

### Metrics to Track

| Metric | Target | Dashboard Widget |
|--------|--------|------------------|
| Competitor Accounts | 500+ | Number |
| Actively Evaluating | 50+ | Number |
| Displacement Win Rate | 20%+ | Percentage |
| Avg Time to Convert | Track | Average |

---

## 🟢 Cohort 4: SI Partners

### Definition
System Integrators and agencies that:
- Implement AI solutions for their customers
- Have signed up for Chroma partnership program
- Bundle Chroma Cloud in their offerings
- Refer customers to Chroma

### HubSpot Properties

| Property | Values | Purpose |
|----------|--------|---------|
| `customer_cohort` | `cohort_4_si_partner` | Primary segmentation |
| `si_partner_status` | active_signed, implementing, signed_up, in_discussion, prospect | Partnership status |
| `si_partner_tier` | platinum, gold, silver, bronze | Partner level |
| `si_customer_count` | Number | Customers implemented |
| `si_revenue_potential` | high, medium, low | Revenue opportunity |
| `si_specialization` | healthcare, financial, legal, enterprise, startups | Focus areas |
| `si_company_type` | global_si, regional_si, boutique_ai, dev_shop, isv | SI classification |

### Key Views to Create

1. **"Cohort 4: Active Partners"**
   - Filter: `si_partner_status` IN (active_signed, implementing)
   - Sort: `si_customer_count` DESC
   - Columns: Name, Tier, Customers, Revenue Potential, Specialization

2. **"Cohort 4: High Potential Partners"**
   - Filter: `si_revenue_potential = high`
   - Action: Prioritized enablement

3. **"Cohort 4: Partner Pipeline"**
   - Filter: `si_partner_status = in_discussion`
   - Action: Close partnership

### Workflows

```
WORKFLOW: Cohort 4 - New Partner Onboarding
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Trigger: si_partner_status changed to "active_signed"
Actions:
  1. Send welcome email with partner resources
  2. Create task: "Schedule partner kickoff call"
  3. Add to "Active Partners" list
  4. Send Slack to #partnerships
```

```
WORKFLOW: Cohort 4 - Partner Customer Referral
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Trigger: lead_source = si_referral
Actions:
  1. Set customer_cohort = cohort_1_current_customer (high priority!)
  2. Set cohort_priority_score = 85
  3. Create task: "Follow up on SI referral"
  4. Notify referring partner
```

### Partner Tiers

| Tier | Criteria | Benefits |
|------|----------|----------|
| **Platinum** | 10+ customers, $100K+ revenue | Dedicated support, co-marketing, referral bonus |
| **Gold** | 5-9 customers, $50K+ revenue | Priority support, joint webinars |
| **Silver** | 2-4 customers, $10K+ revenue | Partner portal, training |
| **Bronze** | 1 customer or signed | Basic resources |

### Metrics to Track

| Metric | Target | Dashboard Widget |
|--------|--------|------------------|
| Active Partners | 20+ | Number |
| Partner-Sourced Deals | 10+ | Number |
| Partner Revenue | $200K+ | Number |
| Avg Customers/Partner | 3+ | Average |

---

## 📊 Master Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CHROMA GTM - Q1 2026 COMMAND CENTER                      │
│                         Target: $2M Revenue                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ Q1 Pipeline     │  │ Closed Won      │  │ Days Left in Q1 │             │
│  │ $2.8M          │  │ $450K          │  │ 77              │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                        COMPANIES BY COHORT                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  🔴 Cohort 1: Current Customers    ████████████████  312            │   │
│  │  🟠 Cohort 2: In-Market            ██████████████████████  589      │   │
│  │  🟡 Cohort 3: Competitors          ████████████████████████  847    │   │
│  │  🟢 Cohort 4: SI Partners          ████  67                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  PIPELINE BY COHORT                    │  Q1 REVENUE BY COHORT             │
│  ┌─────────────────────────────────┐   │  ┌─────────────────────────────┐  │
│  │ Cohort 1: $1.8M ████████████    │   │  │ Cohort 1: $350K (78%)       │  │
│  │ Cohort 2: $650K █████           │   │  │ Cohort 2: $75K (17%)        │  │
│  │ Cohort 3: $280K ██              │   │  │ Cohort 3: $15K (3%)         │  │
│  │ Cohort 4: $120K █               │   │  │ Cohort 4: $10K (2%)         │  │
│  └─────────────────────────────────┘   │  └─────────────────────────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  THIS WEEK'S PRIORITIES                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • 5 Cohort 1 deals in Proposal stage - need to close                │   │
│  │ • 12 new strong signals in Cohort 2 - outreach today                │   │
│  │ • 3 Cohort 3 accounts now evaluating - schedule demos               │   │
│  │ • 2 SI partners ready to sign - send agreements                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Implementation Checklist

### Week 1: Foundation

- [ ] Run `python hubspot_cohort_setup.py` to create all properties
- [ ] Create the 4 main cohort views
- [ ] Set up Slack integration
- [ ] Import existing pipeline data as Cohort 1
- [ ] Import Chroma Signal data as Cohort 2
- [ ] Import competitor customer data as Cohort 3
- [ ] Import SI partner data as Cohort 4

### Week 2: Automation

- [ ] Create cohort assignment workflows
- [ ] Set up signal alert workflows
- [ ] Create follow-up cadence workflows
- [ ] Build email sequences for each cohort
- [ ] Connect Sumble for job data signals
- [ ] Connect Reo.dev for GitHub signals

### Week 3: Reporting

- [ ] Build Q1 Command Center dashboard
- [ ] Create cohort-specific reports
- [ ] Set up weekly email reports
- [ ] Create Slack digest for daily signals

### Ongoing

- [ ] Daily: Review Cohort 1 pipeline, Cohort 2 new signals
- [ ] Weekly: Follow up on Cohort 3, check SI partner activity
- [ ] Monthly: Review cohort performance, adjust scoring

---

## 📞 Quick Reference

### Daily Priorities

1. **Morning (15 min)**
   - Check "Cohort 1: Active Pipeline" - any deals need attention?
   - Check "Cohort 2: Hot Signals" - any new strong signals?
   - Check Slack #gtm-signals for alerts

2. **Throughout Day**
   - Execute Cohort 2 outreach (new signals)
   - Follow up on Cohort 1 deals
   - Respond to Cohort 3 follow-up tasks

3. **End of Day (10 min)**
   - Update deal stages
   - Log engagement notes
   - Set tomorrow's priorities

### Key HubSpot Filters

| Quick Filter | Property | Value |
|--------------|----------|-------|
| All Cohort 1 | `customer_cohort` | `cohort_1_current_customer` |
| All Cohort 2 | `customer_cohort` | `cohort_2_in_market` |
| All Cohort 3 | `customer_cohort` | `cohort_3_competitor` |
| All Cohort 4 | `customer_cohort` | `cohort_4_si_partner` |
| High Priority | `cohort_priority_score` | > 70 |
| Q1 Targets | `q1_revenue_potential` | `high` |

---

*Last Updated: January 13, 2026*
*Strategy Owner: Ankit Pansari*

