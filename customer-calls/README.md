# 📞 Chroma Customer Calls Repository

> A searchable knowledge base of customer conversations to accelerate sales team ramp-up and capture institutional knowledge.

## Why This Exists

Every customer call contains gold:
- **Pain points** that inform our messaging
- **Objections** that train new reps
- **Competitive intel** we can't get elsewhere
- **Use cases** that shape our product and positioning

This repo ensures none of that knowledge is lost.

---

## 🚀 Quick Start

### Recording a New Call

1. **Have your call** with Granola running
2. **After the call**, use the Granola prompt (see below)
3. **Save the output** to the appropriate folder
4. **Commit and push**

```bash
# Example
git add calls/customers/2026-01-09_acme-discovery.md
git commit -m "Add Acme Corp discovery call notes"
git push
```

### Granola Prompt

Copy this into Granola after your meeting:

```
I just had a meeting and I need you to extract structured notes for my Chroma GTM project. Focus on what's actionable and relevant to go-to-market strategy.

Please extract the following:

## 1. Meeting Metadata
- Date and participants
- What type of meeting was this? (Customer call, internal sync, strategy session, partner meeting)

## 2. Summary (2-3 sentences max)
What was this meeting fundamentally about?

## 3. Key Discussion Points
List the 3-5 most important topics discussed. For each:
- What was discussed
- Any conclusions or insights

## 4. Decisions Made
What was decided or agreed upon?

## 5. Action Items
Extract ALL action items mentioned, with:
- Who owns it
- What needs to be done
- Any deadline mentioned

## 6. GTM-Relevant Insights
Specifically extract anything related to:
- **Customer signals**: Pain points, needs, feedback, objections
- **Competitive intelligence**: Mentions of Pinecone, Weaviate, Qdrant, or other vector DBs
- **Positioning/Messaging**: What resonated, what didn't, how we should talk about Chroma
- **Market insights**: Trends, opportunities, threats

## 7. Follow-up Required
- Any follow-up meetings scheduled?
- Who needs to be looped in?

Format the output in clean markdown that I can save directly to a file.
```

---

## 📁 Folder Structure

```
customer-calls/
├── README.md                    # You are here
├── CALL_INDEX.md               # Master index of all calls (searchable)
├── INSIGHTS_SUMMARY.md         # Aggregated learnings across calls
│
├── calls/
│   ├── customers/              # Calls with paying customers
│   ├── prospects/              # Discovery, demo, negotiation calls
│   ├── churned/                # Exit interviews, churn analysis
│   └── partners/               # SI partners, integrations, vendors
│
├── playbooks/
│   ├── OBJECTION_HANDLING.md   # Common objections + responses
│   ├── DISCOVERY_QUESTIONS.md  # Questions that work
│   ├── COMPETITIVE_BATTLES.md  # How to win against each competitor
│   └── USE_CASE_LIBRARY.md     # Validated use cases with examples
│
└── templates/
    ├── _CALL_TEMPLATE.md       # Template for new call notes
    ├── _DISCOVERY_TEMPLATE.md  # Discovery call specific
    └── _DEMO_TEMPLATE.md       # Demo call specific
```

---

## 📝 File Naming Convention

**Format**: `YYYY-MM-DD_company-name_call-type.md`

**Examples**:
- `2026-01-09_acme-corp_discovery.md`
- `2026-01-10_capital-one_demo.md`
- `2026-01-12_bloomberg_technical-deep-dive.md`
- `2026-01-15_ex-customer_exit-interview.md`

---

## 🔍 Finding Information

### By Company
```bash
# Find all calls with a specific company
grep -r "Acme" calls/
```

### By Competitor
```bash
# Find all mentions of Pinecone
grep -ri "pinecone" calls/
```

### By Pain Point
```bash
# Find discussions about scaling issues
grep -ri "scale\|scaling\|performance" calls/
```

### By Tag
All call notes include tags at the bottom. Search by tag:
```bash
grep -l "#enterprise" calls/**/*.md
```

---

## 🏷️ Standard Tags

Add these at the bottom of each call note:

| Tag | Use When |
|-----|----------|
| `#discovery` | Initial discovery call |
| `#demo` | Product demo |
| `#technical` | Technical deep-dive |
| `#negotiation` | Pricing/contract discussion |
| `#closed-won` | Deal closed |
| `#closed-lost` | Deal lost |
| `#churn` | Customer churning |
| `#expansion` | Upsell/expansion opportunity |
| `#enterprise` | Enterprise deal (>$50k) |
| `#startup` | Startup/SMB deal |
| `#pinecone` | Pinecone competitive |
| `#weaviate` | Weaviate competitive |
| `#elastic` | Elasticsearch displacement |
| `#rag` | RAG use case |
| `#agents` | AI agents use case |

---

## 📊 Call Types & What to Capture

### Discovery Calls
**Priority**: 🔴 Critical
- Current stack and pain points
- Why they're looking at Chroma
- Decision-making process
- Timeline and budget
- Competitors they're evaluating

### Demo Calls
**Priority**: 🔴 Critical
- Features that resonated
- Questions/concerns raised
- Technical requirements surfaced
- Next steps agreed

### Technical Deep-Dives
**Priority**: 🟡 High
- Architecture requirements
- Integration challenges
- Performance expectations
- Security/compliance needs

### Negotiation Calls
**Priority**: 🟡 High
- Pricing objections
- Contract terms discussed
- Stakeholders involved
- Decision timeline

### Customer Check-ins
**Priority**: 🟢 Medium
- Usage and satisfaction
- Feature requests
- Expansion opportunities
- Reference potential

### Exit Interviews
**Priority**: 🔴 Critical
- Why they churned
- What we could have done better
- Where they're going

---

## 🎯 For New Sales Reps

Start here to ramp up:

1. **Read `INSIGHTS_SUMMARY.md`** - Aggregated learnings
2. **Review `playbooks/OBJECTION_HANDLING.md`** - Know the common objections
3. **Study 5 recent won deals** in `calls/customers/`
4. **Study 3 recent lost deals** - Learn from losses
5. **Review `playbooks/COMPETITIVE_BATTLES.md`** - Know your enemies

---

## 🤝 Contributing

### After Every Call
1. Process notes through Granola with the prompt above
2. Save to the appropriate folder
3. Add entry to `CALL_INDEX.md`
4. Commit and push

### Weekly
- Review calls and update `INSIGHTS_SUMMARY.md` with new patterns
- Update playbooks if you discovered new objections or battle cards

### Monthly
- Review churn calls and update learnings
- Refresh competitive intelligence

---

## 🔒 Privacy & Confidentiality

- **No PII**: Don't include personal contact info beyond names
- **No secrets**: Don't include customer's proprietary technical details
- **Paraphrase**: Use your own words, not verbatim transcripts
- **Internal only**: This repo is private and for Chroma team only

---

## Questions?

Ping @ankit or @jeff in Slack.

