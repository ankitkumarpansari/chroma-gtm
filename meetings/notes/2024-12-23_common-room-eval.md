# Meeting Notes: Common Room Platform Evaluation

## Metadata
- **Date**: December 23, 2024
- **Participants**: Ankit Pansari, Common Room AE
- **Meeting Type**: Vendor/Platform Evaluation (GTM/Data Infrastructure)

---

## Summary

Discovery/demo conversation with Common Room focused on unifying Chroma's sales, product, and intent data to support GTM for dev tools. The AE pitched Common Room as an identity resolution and signal aggregation layer (especially around GitHub) to power pipeline generation, while Ankit explained Chroma's current scrappy internal solution and evaluation of other tools. They aligned on doing a deeper custom demo after the holidays to inform vendor selection by early January.

---

## Key Discussion Points

### 1) Common Room Value Prop & Architecture

- Aggregates first-party data (CRM, web visits, marketing, sales calls) AND third-party signals (GitHub, LinkedIn, job data, intent data)
- Unified contact records = "CDP for your target account universe"
- Strong emphasis on **identity resolution** across tools and over time (e.g., when contacts change jobs)

**Key insight**: This directly matches what Chroma tried to build internally. Main differentiator is robust identity resolution + unified, actionable segments.

### 2) Identity Resolution vs. Point Tools

**The AE's argument**: The hard part isn't collecting signals — it's stitching them into one identity.

| Tool Type | Limitation |
|-----------|------------|
| Rio.dev | GitHub signals only, weak identity resolution |
| Signal scrapers | Quickly become outdated, un-actionable |
| Reverse ETL | Data pipelines, not unified views |

**Common Room claim**: Uniquely consolidates first- AND third-party data (including GitHub) into one contact, keeps it current as people/jobs change.

### 3) Devtool/Open-Source GTM Use Cases

**Semgrep case study** (marquee devtool customer):
- Connect GitHub, product usage, and other signals
- Monitor own/competitive repos
- Surface prioritized accounts to BDRs

**Demo showed**: De-anonymizing GitHub contributors in repos like OpenAI's, then layering filters (company size, website visits) to build GTM segments.

**Insight**: Repeatable pattern for converting GitHub/developer signals into enterprise pipeline — directly applicable to Chroma.

### 4) Chroma's Current GTM Model & Data Needs

| Motion | Details |
|--------|---------|
| **Enterprise** | High-touch, consultative, 6-figure deals, engineering-heavy |
| **Self-serve** | Bottom-up, $5-15k deals, CRO/website optimization critical |

**Current state**: Homegrown AI-based signal tool (scrappy but works)

**Gaps**:
- No reliable single system of record for GTM data
- No robust identity resolution across GitHub, CRM, web, signals
- Need to support new STR/SDR with actionable views

**Success metric**: Sales qualified leads for consultative sales

### 5) Tooling Evaluation & Timing

| Tool | Category | Status |
|------|----------|--------|
| **Common Room** | Identity resolution + signal aggregation | Evaluating (this call) |
| **High Touch** | Reverse ETL / data activation | Evaluating |
| **Rio.dev** | GitHub signal tracking | Evaluating |

**Pricing**: ~$12-15k for smaller customers, much higher for enterprise

**Timeline**: Pick a solution by **second week of January**

---

## Decisions Made

| Decision | Details |
|----------|---------|
| **Custom demo** | Proceed with deeper Common Room demo after holidays |
| **Demo timing** | Dec 29 or week of Jan 5 |
| **Evaluation timeline** | Decide on tooling by second week of January |

---

## Action Items

### Ankit
- [ ] Email Common Room AE with:
  - Preferred demo date (Dec 29 or week of Jan 5)
  - Additional product questions
  - Names of other platforms being evaluated (High Touch, Rio.dev)
- [ ] Review Common Room case studies for devtool/open-source companies (Semgrep playbook) before demo

### Common Room AE
- [ ] Put placeholder calendar block on Dec 29 (afternoon)
- [ ] Prepare custom demo focused on:
  - GitHub engagement pull
  - Product usage data ingestion (PostHog/webhooks)
  - End-to-end GTM segments and campaigns for Chroma

---

## GTM Insights

### Customer Signals (Chroma's Needs)
- **Gap**: No reliable single system of record for GTM data
- **Gap**: No robust identity resolution across GitHub, CRM, web
- **Need**: Platform that surfaces SQLs for consultative sales
- **Need**: Support both enterprise top-down AND bottom-up self-serve
- **Uncertainty**: Still early in understanding lead times, inbound vs outbound effectiveness, self-serve dynamics

### Competitive Intelligence (GTM Tools)

| Tool | Strength | Weakness |
|------|----------|----------|
| **Common Room** | Identity resolution, unified signals | Price? |
| **Rio.dev** | GitHub signals | Weak identity resolution, no cross-signal context |
| **High Touch** | Reverse ETL, data activation | Not identity-focused? |

### Positioning / Messaging
**"Hard part" framing resonated**: It's not collecting signals; it's connecting and unifying them.

**Phrases that landed**:
- "Single system of record" / "central hub" for GTM data
- "CDP for your target account universe"
- "De-anonymize GitHub and unify history into one place"

### Market Insights
- Strong demand for turning **GitHub/community activity → qualified enterprise pipeline**
- Identity resolution + continuous enrichment = key differentiator vs. simple signal collectors
- Many devtool companies struggling to connect GitHub, product, web, intent signals for new SDRs
- Moving toward **unified, action-oriented views** rather than raw data pipelines

### LinkedIn / Outreach Ideas

**Content themes**:
- "The hard part of GTM for devtools isn't collecting more signals — it's stitching them into a single identity you can actually sell to."
- "How to turn ambiguous GitHub activity into enterprise pipeline."
- "From scrappy internal signal scripts to a real GTM data foundation."
- "Why devtool GTM teams need identity resolution as much as they need intent data."

**Outreach hooks**:
- "Are your GitHub stars and PRs actually connected to your CRM and web intent data?"
- "If an engineer who loves your repo changes jobs, does that context follow them in your GTM systems?"
- "Can a new SDR look at one screen and know exactly which accounts to hit today?"

---

## Follow-up Required

- **Custom demo**: Dec 29 or week of Jan 5
- **Decision deadline**: Second week of January
- **Loop in later**: STR/SDR and engineering leaders once closer to implementation

---

## Tags
`#vendor-eval` `#common-room` `#gtm-infrastructure` `#identity-resolution` `#github` `#signals`

