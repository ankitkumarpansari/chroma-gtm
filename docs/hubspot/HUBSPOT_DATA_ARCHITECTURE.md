# Chroma HubSpot Data Architecture

> **Goal**: Create a unified view of all customers and prospects in HubSpot by connecting data from PostHog, Orb, and signal tools.

---

## 📊 Data Source Map

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        CHROMA DATA ARCHITECTURE                                  │
│                     HubSpot as Single Source of Truth                           │
└─────────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │    HUBSPOT      │
                              │  (CRM - SSOT)   │
                              └────────┬────────┘
                                       │
           ┌───────────────────────────┼───────────────────────────┐
           │                           │                           │
           ▼                           ▼                           ▼
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   COHORT 1 DATA     │    │   COHORT 2 & 3      │    │   COHORT 4 DATA     │
│  Current Customers  │    │   Pipeline Data     │    │    SI Partners      │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
           │                           │                           │
           ▼                           ▼                           ▼
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│ • PostHog (Signups) │    │ • Sumble (Jobs)     │    │ • Manual Entry      │
│ • Admin Panel       │    │ • Reo.dev (GitHub)  │    │ • SI Program CSV    │
│ • Orb (Billing)     │    │ • Factors.ai (Web)  │    │ • Partner Portal    │
│                     │    │ • LinkedIn Sales Nav│    │                     │
│                     │    │ • Competitor Intel  │    │                     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

---

## 🔴 Cohort 1: Current Customers - Data Sources

### Primary Sources

| Source | Data Type | Sync Method | Frequency |
|--------|-----------|-------------|-----------|
| **PostHog** | Signups, Product Usage | API/Webhook | Real-time or Daily |
| **Admin Panel** | Account Details, Instances | API | Daily |
| **Orb** | Billing, MRR, Plan | API/Webhook | Real-time |

### Data Flow: PostHog → HubSpot

```
PostHog Event: "user_signed_up"
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Extract from PostHog:                                       │
│  • email                                                     │
│  • company_name (from email domain or form)                  │
│  • signup_date                                               │
│  • signup_source (UTM params)                                │
│  • initial_use_case (if captured)                            │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Create/Update in HubSpot:                                   │
│  • Company: domain, name                                     │
│  • Contact: email, name                                      │
│  • Set: customer_cohort = "cohort_1_current_customer"       │
│  • Set: chroma_customer_status = "active_free" or "trial"   │
│  • Set: lead_source = "product_signup"                       │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow: Orb → HubSpot

```
Orb Webhook: "subscription.created" / "invoice.paid"
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Extract from Orb:                                           │
│  • customer_id                                               │
│  • plan_name                                                 │
│  • mrr_amount                                                │
│  • billing_email                                             │
│  • subscription_status                                       │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Update in HubSpot (match by email/domain):                  │
│  • Set: chroma_cloud_mrr = mrr_amount                        │
│  • Set: chroma_customer_status = "active_paid"               │
│  • Set: chroma_usage_tier = map_plan_to_tier(plan_name)     │
│  • Set: q1_revenue_potential = "high" (if paying)            │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow: Admin Panel → HubSpot

```
Admin Panel API: GET /accounts
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Extract from Admin:                                         │
│  • account_id                                                │
│  • company_name                                              │
│  • num_collections (instances)                               │
│  • total_vectors                                             │
│  • last_active_date                                          │
│  • is_active                                                 │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Update in HubSpot:                                          │
│  • Set: chroma_instances = num_collections                   │
│  • Set: chroma_customer_status based on last_active_date    │
│    - Active if last_active < 30 days                         │
│    - Dormant if last_active > 30 days                        │
│  • Set: chroma_expansion_potential based on usage            │
└─────────────────────────────────────────────────────────────┘
```

### Cohort 1 HubSpot Properties (Updated)

| Property | Source | Update Trigger |
|----------|--------|----------------|
| `customer_cohort` | System | On first signup |
| `chroma_customer_status` | Orb + Admin | Subscription change, Activity check |
| `chroma_cloud_mrr` | Orb | Invoice/Subscription events |
| `chroma_instances` | Admin Panel | Daily sync |
| `chroma_usage_tier` | Orb | Plan change |
| `chroma_expansion_potential` | Calculated | Usage thresholds |
| `pipeline_stage` | Manual/Workflow | Sales activity |

---

## 🟠 Cohort 2: In-Market Companies - Data Sources

### Primary Sources

| Source | Signal Type | Data Provided |
|--------|-------------|---------------|
| **Sumble** | Job Posts | AI hiring signals, job count, tech stack |
| **Reo.dev** | GitHub/OSS | Stars, forks, contributors from target companies |
| **Factors.ai** | Website Visits | Anonymous company identification, page views |
| **LinkedIn Sales Nav** | Prospecting | Target company lists, contacts |

### Data Flow: Sumble → HubSpot

```
Sumble API/Webhook: Job Signal Detected
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Extract from Sumble:                                        │
│  • company_name                                              │
│  • company_domain                                            │
│  • job_titles (AI Engineer, ML Engineer, etc.)              │
│  • job_count                                                 │
│  • tech_stack_mentions (vector DB, LLM, RAG)                │
│  • urgency_score                                             │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Create/Update in HubSpot:                                   │
│  • Set: customer_cohort = "cohort_2_in_market"              │
│  • Set: ai_hiring_status based on job_count                  │
│  • Set: ai_job_count = job_count                             │
│  • Set: in_market_signals = ["hiring_ai_engineers", ...]    │
│  • Set: signal_source = ["sumble"]                           │
│  • Set: signal_strength based on urgency_score               │
│  • Set: lead_source = "chroma_signal"                        │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow: Reo.dev → HubSpot

```
Reo.dev: GitHub Activity Detected
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Extract from Reo.dev:                                       │
│  • company_name (from GitHub profile/email)                  │
│  • github_activity (star, fork, PR, issue)                  │
│  • repo_interacted (chroma, langchain, etc.)                │
│  • developer_email                                           │
│  • enriched_company_data                                     │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Create/Update in HubSpot:                                   │
│  • Set: customer_cohort = "cohort_2_in_market"              │
│  • Set: in_market_signals += ["ai_native"]                  │
│  • Set: signal_source += ["reodev"]                          │
│  • Set: use_case_detected based on repo                      │
│  • Create Contact with github_url                            │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow: Factors.ai → HubSpot

```
Factors.ai: Anonymous Company Identified
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Extract from Factors.ai:                                    │
│  • company_name                                              │
│  • company_domain                                            │
│  • pages_visited                                             │
│  • visit_count                                               │
│  • time_on_site                                              │
│  • referral_source                                           │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Create/Update in HubSpot:                                   │
│  • Set: customer_cohort = "cohort_2_in_market"              │
│  • Set: signal_source += ["factors"]                         │
│  • Set: signal_strength based on engagement                  │
│  • Set: lead_source = "inbound"                              │
└─────────────────────────────────────────────────────────────┘
```

### Cohort 2 HubSpot Properties

| Property | Source | Update Trigger |
|----------|--------|----------------|
| `customer_cohort` | System | First signal detected |
| `in_market_signals` | Sumble, Reo.dev | New signal |
| `ai_hiring_status` | Sumble | Job post detected |
| `ai_job_count` | Sumble | Daily sync |
| `company_type` | Enrichment | On create |
| `use_case_detected` | Reo.dev, Manual | GitHub activity, Conversation |
| `signal_source` | Multiple | Each signal adds to list |
| `signal_strength` | Calculated | Based on signal count/recency |

---

## 🟡 Cohort 3: Competitor Customers - Data Sources

### Primary Sources

| Source | Data Type | How Collected |
|--------|-----------|---------------|
| **YouTube Research** | Competitor case studies | Manual + Script |
| **Job Posts (Sumble)** | Tech stack mentions | Automated |
| **GitHub** | Competitor SDK usage | Reo.dev |
| **Competitive Intel Tools** | Customer lists | Manual research |

### Data Flow: Competitor Intel → HubSpot

```
Research/Sumble: Competitor Usage Detected
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Identify from:                                              │
│  • Job posts mentioning Pinecone, Weaviate, etc.            │
│  • YouTube videos/case studies                               │
│  • GitHub repos importing competitor SDKs                    │
│  • Direct conversation                                       │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Create/Update in HubSpot:                                   │
│  • Set: customer_cohort = "cohort_3_competitor"             │
│  • Set: current_vector_db = ["pinecone", "weaviate", etc.]  │
│  • Set: competitor_source_channel = how we found them        │
│  • Set: competitor_relationship_status = "unknown"           │
│  • Set: follow_up_cadence = "monthly"                        │
│  • Set: lead_source = "competitor_research"                  │
└─────────────────────────────────────────────────────────────┘
```

### Cohort 3 Enrichment Logic

```python
# When competitor signal detected, also check Cohort 1 & 2 signals

if company in cohort_1_customers:
    # They're already a customer - update competitor intel
    # but don't change cohort
    update_property("current_vector_db", competitor)
    
elif company in cohort_2_in_market:
    # They're in-market AND using competitor
    # Keep in Cohort 2 (higher priority) but add competitor data
    update_property("current_vector_db", competitor)
    update_property("displacement_play", determine_play(competitor))
    
else:
    # Pure competitor customer - Cohort 3
    set_cohort("cohort_3_competitor")
```

---

## 🟢 Cohort 4: SI Partners - Data Sources

### Primary Sources

| Source | Data Type | Sync Method |
|--------|-----------|-------------|
| **Partner Portal** | Partner signups, activity | API/Manual |
| **SI Program CSV** | Initial partner list | Import |
| **Referral Tracking** | Customer referrals | Manual |

### Data Flow: Partner Activity → HubSpot

```
Partner Portal / Manual Entry
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Track:                                                      │
│  • Partner company name                                      │
│  • Partner tier                                              │
│  • Customers referred/implemented                            │
│  • Revenue generated                                         │
│  • Specialization areas                                      │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Create/Update in HubSpot:                                   │
│  • Set: customer_cohort = "cohort_4_si_partner"             │
│  • Set: si_partner_status = current status                   │
│  • Set: si_partner_tier = tier level                         │
│  • Set: si_customer_count = referral count                   │
│  • Set: si_revenue_potential = estimated value               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Cohort Transition Rules

### Priority Order (Highest to Lowest)
1. **Cohort 1** - Current Customer (always wins)
2. **Cohort 4** - SI Partner (strategic relationship)
3. **Cohort 2** - In-Market (active buying signals)
4. **Cohort 3** - Competitor (nurture/keep warm)

### Transition Logic

```
┌─────────────────────────────────────────────────────────────┐
│                    COHORT TRANSITIONS                        │
└─────────────────────────────────────────────────────────────┘

Cohort 3 (Competitor) ──► Cohort 2 (In-Market)
  Trigger: Shows buying signals (job posts, website visits)
  Action: Move to Cohort 2, keep competitor_data

Cohort 2 (In-Market) ──► Cohort 1 (Customer)
  Trigger: Signs up for Chroma Cloud
  Action: Move to Cohort 1, keep all signal history

Cohort 3 (Competitor) ──► Cohort 1 (Customer)
  Trigger: Signs up for Chroma Cloud
  Action: Move to Cohort 1, track as "competitor_displaced"

Any Cohort ──► Cohort 4 (SI Partner)
  Trigger: Joins partner program
  Action: Move to Cohort 4 (unless already Cohort 1)

Cohort 1 (Customer) ──► Cohort 1 (Dormant)
  Trigger: No activity for 30+ days
  Action: Stay in Cohort 1, set status = "dormant"
```

### HubSpot Workflow: Cohort Transition

```
WORKFLOW: Auto-Assign Cohort on Signup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Trigger: Contact created with chroma_customer_status != null

Actions:
  1. Find associated Company
  2. Set company.customer_cohort = "cohort_1_current_customer"
  3. If company had competitor data:
     - Set deal.competitor_displaced = company.current_vector_db
     - Log: "Competitor displacement!"
  4. If company was Cohort 2:
     - Preserve signal_source, use_case_detected
     - Log: "In-market converted!"
```

---

## 📊 Unified Data Schema

### Company Record Structure

```json
{
  "name": "Acme Corp",
  "domain": "acme.com",
  
  // COHORT ASSIGNMENT
  "customer_cohort": "cohort_1_current_customer",
  "cohort_priority_score": 85,
  "q1_revenue_potential": "high",
  
  // COHORT 1 DATA (from PostHog, Orb, Admin)
  "chroma_customer_status": "active_paid",
  "chroma_cloud_mrr": 2500,
  "chroma_instances": 3,
  "chroma_usage_tier": "growth",
  "chroma_expansion_potential": "high",
  "pipeline_stage": "closed_won",
  
  // COHORT 2 DATA (from Sumble, Reo.dev, Factors)
  "in_market_signals": ["hiring_ai_engineers", "building_rag"],
  "ai_hiring_status": "actively_hiring_high",
  "ai_job_count": 7,
  "company_type": "ai_native_startup",
  "use_case_detected": ["rag", "agent"],
  "signal_source": ["sumble", "reodev", "factors"],
  "signal_strength": "very_strong",
  
  // COHORT 3 DATA (from Research)
  "current_vector_db": ["pinecone"],
  "competitor_source_channel": "job_posting",
  "competitor_pain_points": ["cost", "performance"],
  "competitor_relationship_status": "evaluating",
  "displacement_play": "pinecone_migration",
  
  // COHORT 4 DATA (from Partner Program)
  "si_partner_status": null,
  "si_partner_tier": null,
  
  // TRACKING
  "lead_source": "product_signup",
  "linkedin_company_url": "https://linkedin.com/company/acme",
  "engagement_notes": "Met at AI Summit, very interested in Search Agent"
}
```

---

## 🔌 Integration Architecture

### Recommended Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INTEGRATION ARCHITECTURE                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   PostHog   │     │     Orb     │     │   Sumble    │     │   Reo.dev   │
│  (Product)  │     │  (Billing)  │     │   (Jobs)    │     │  (GitHub)   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       │ Webhook           │ Webhook           │ API               │ Webhook
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                        INTEGRATION LAYER                                     │
│                                                                             │
│   Option A: Segment (CDP)                                                   │
│   Option B: Custom Python Scripts (current)                                 │
│   Option C: Zapier/Make (low-code)                                         │
│   Option D: HubSpot Operations Hub (native)                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                          ┌─────────────────┐
                          │     HUBSPOT     │
                          │   (CRM - SSOT)  │
                          └─────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              ┌──────────┐   ┌──────────┐   ┌──────────┐
              │  Slack   │   │ Dashboards│   │  Sales   │
              │ Alerts   │   │ & Reports │   │ Actions  │
              └──────────┘   └──────────┘   └──────────┘
```

### Integration Options

| Option | Pros | Cons | Cost | Recommendation |
|--------|------|------|------|----------------|
| **Segment** | Clean data flow, many integrations | Cost, complexity | $$$$ | Best for scale |
| **Custom Scripts** | Full control, no extra cost | Maintenance burden | $ | Current approach |
| **Zapier/Make** | Easy setup, no code | Limited logic, per-task cost | $$ | Quick wins |
| **HubSpot Ops Hub** | Native, powerful workflows | HubSpot lock-in | $$$ | If all-in on HubSpot |

### Recommended Approach (Phased)

**Phase 1 (Now)**: Custom Python Scripts
- Continue with current scripts
- Add PostHog → HubSpot sync
- Add Orb → HubSpot sync

**Phase 2 (Q2)**: Add Zapier for Quick Wins
- Sumble → HubSpot (if they have Zapier)
- Slack alerts

**Phase 3 (Scale)**: Evaluate Segment
- When volume justifies cost
- When team grows

---

## 📋 Implementation Checklist

### Week 1: PostHog Integration
- [ ] Identify PostHog events to track (signup, activation, etc.)
- [ ] Create PostHog → HubSpot sync script
- [ ] Map PostHog user properties to HubSpot contact/company
- [ ] Test with sample data

### Week 2: Orb Integration
- [ ] Set up Orb webhooks for subscription events
- [ ] Create Orb → HubSpot sync script
- [ ] Map Orb customer to HubSpot company (by email/domain)
- [ ] Test billing data flow

### Week 3: Signal Tool Integrations
- [ ] Connect Sumble API (if available)
- [ ] Connect Reo.dev webhooks
- [ ] Connect Factors.ai
- [ ] Test signal → cohort assignment

### Week 4: Automation & Alerts
- [ ] Create cohort transition workflows
- [ ] Set up Slack alerts for key events
- [ ] Build dashboard for cohort health
- [ ] Document runbooks

---

## 🔑 Key Identifiers for Matching

### How to Match Records Across Systems

| System | Primary ID | Secondary ID | Match Strategy |
|--------|------------|--------------|----------------|
| **PostHog** | distinct_id (email) | company domain | Email → Contact → Company |
| **Orb** | customer_id, email | billing domain | Email → Contact → Company |
| **Sumble** | company domain | company name | Domain → Company |
| **Reo.dev** | GitHub username | email, company | Email → Contact → Company |
| **Factors.ai** | company domain | IP-based | Domain → Company |
| **HubSpot** | company ID | domain, name | Primary key |

### Matching Logic

```python
def find_or_create_company(data):
    """
    Priority order for matching:
    1. Domain (most reliable)
    2. Email domain (extract from contact email)
    3. Company name (fuzzy match)
    """
    
    # Try domain first
    if data.get('domain'):
        company = hubspot.search_by_domain(data['domain'])
        if company:
            return company
    
    # Try email domain
    if data.get('email'):
        domain = extract_domain(data['email'])
        company = hubspot.search_by_domain(domain)
        if company:
            return company
    
    # Try company name (fuzzy)
    if data.get('company_name'):
        company = hubspot.search_by_name(data['company_name'])
        if company:
            return company
    
    # Create new
    return hubspot.create_company(data)
```

---

## 📊 Data Quality Rules

### Required Fields by Cohort

| Cohort | Required Fields | Nice to Have |
|--------|-----------------|--------------|
| **Cohort 1** | name, domain, chroma_customer_status | MRR, instances, usage_tier |
| **Cohort 2** | name, at least one signal | domain, signal_strength, use_case |
| **Cohort 3** | name, current_vector_db | domain, pain_points, relationship_status |
| **Cohort 4** | name, si_partner_status | tier, customer_count, specialization |

### Validation Rules

```python
def validate_company(company, cohort):
    errors = []
    
    # Universal
    if not company.get('name'):
        errors.append("Missing company name")
    
    # Cohort-specific
    if cohort == 'cohort_1':
        if not company.get('chroma_customer_status'):
            errors.append("Cohort 1 requires customer status")
    
    elif cohort == 'cohort_2':
        if not any([
            company.get('in_market_signals'),
            company.get('ai_hiring_status'),
            company.get('signal_source')
        ]):
            errors.append("Cohort 2 requires at least one signal")
    
    elif cohort == 'cohort_3':
        if not company.get('current_vector_db'):
            errors.append("Cohort 3 requires competitor info")
    
    elif cohort == 'cohort_4':
        if not company.get('si_partner_status'):
            errors.append("Cohort 4 requires partner status")
    
    return errors
```

---

*Last Updated: January 13, 2026*
*Owner: Ankit Pansari*

