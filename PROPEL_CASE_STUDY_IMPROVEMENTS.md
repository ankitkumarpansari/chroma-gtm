# 🔍 Propel Case Study Analysis & Improvement Recommendations

> **Current Version**: Staging at `nextjs-app-git-tj-propel-case-study-chromacore.vercel.app`
> **Analysis Date**: January 14, 2026
> **Goal**: Optimize for Cohort 1 conversion and competitive differentiation

---

## 📊 Current Case Study Scorecard

| Element | Current State | Score | Priority |
|---------|---------------|-------|----------|
| **Headline** | ✅ Clear, benefit-focused | 8/10 | - |
| **Hero Metrics** | ❌ Missing entirely | 2/10 | 🔴 Critical |
| **Customer Quote** | ⚠️ Present but weak attribution | 5/10 | 🟠 High |
| **Challenge Section** | ✅ Well-articulated | 8/10 | - |
| **Solution Section** | ✅ Good technical depth | 8/10 | - |
| **Results Section** | ⚠️ Qualitative only, no metrics | 4/10 | 🔴 Critical |
| **Visual Elements** | ⚠️ Minimal | 4/10 | 🟠 High |
| **CTA** | ✅ Present | 7/10 | 🟢 Low |
| **Overall** | **Solid foundation, needs metrics** | **5.8/10** | - |

---

## 🔴 Critical Improvements (Must Do)

### 1. Add Hero Metrics

**Current State**: No metrics visible above the fold

**Recommendation**: Add 3 metric cards immediately below the headline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SUGGESTED HERO METRICS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │      XX%        │  │      XXx        │  │     <XXms       │             │
│  │   Review        │  │    Faster       │  │    Retrieval    │             │
│  │   Accuracy      │  │    Reviews      │  │    Latency      │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
│  METRICS TO REQUEST FROM PROPEL:                                            │
│  • Code review accuracy rate                                                │
│  • Speed improvement vs. manual review                                      │
│  • Retrieval latency for context                                            │
│  • Number of repositories indexed                                           │
│  • Token cost savings (vs. scanning entire codebase)                        │
│  • Number of PRs reviewed per day/week                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Action Items**:
- [ ] Contact Tony Dong at Propel to gather specific metrics
- [ ] Ask for: accuracy %, speed improvement, scale numbers

---

### 2. Quantify the Results Section

**Current State**: Results are qualitative only

```
Current Results:
- Reasons across entire repositories, not just local diffs
- Grounds feedback in precise symbol level evidence
- Accurately accounts for third party dependency behavior
- Delivers consistent, high quality reviews without excessive token usage
```

**Recommendation**: Transform each bullet into a quantified outcome

```markdown
## SUGGESTED REWRITE - Results Section

By building on Chroma Cloud from the start, Propel designed its agent around 
deep, structured context. The results speak for themselves:

| Metric | Outcome |
|--------|---------|
| **Repository Coverage** | 100% codebase context (vs. single-file analysis) |
| **Review Accuracy** | XX% accuracy rate on code suggestions |
| **Token Efficiency** | XXx reduction in token usage vs. full codebase scans |
| **Latency** | <XXms retrieval time for relevant context |
| **Scale** | XX repositories indexed, XX million lines of code |

The result is an agent that:
- **Reasons across entire repositories**, not just local diffs
- **Grounds feedback in precise symbol-level evidence** from Regex search
- **Accurately accounts for third-party dependency behavior** via Package Search
- **Delivers consistent, high-quality reviews** without excessive token usage
```

**Action Items**:
- [ ] Schedule call with Propel to gather metrics
- [ ] Request before/after comparison data if available

---

## 🟠 High-Priority Improvements

### 3. Strengthen Customer Quote & Attribution

**Current State**:
```
"Chroma is the obvious choice for Propel, enabling our agents to reason 
across entire repositories and dependencies. The result is more accurate 
reviews and a higher standard of feedback."

Tony Dong
Customer Success, Propel
```

**Issues**:
- "Customer Success" is not a technical decision-maker title
- Quote is good but could be more specific
- Missing photo

**Recommendation**:

```markdown
## OPTION A: Get quote from technical leader

Request a quote from Propel's CTO, Head of Engineering, or Founder.
Better titles for credibility:
- Co-founder & CTO
- Head of Engineering
- VP of Product

## OPTION B: Enhance current quote with specifics

"Chroma is the obvious choice for Propel. We evaluated [X alternatives], 
but Chroma's combination of semantic search and Regex matching—plus 
Package Search for dependency intelligence—was unmatched. Our agents 
now reason across entire repositories, delivering [XX%] more accurate 
reviews than local-only analysis."

[Photo] Tony Dong
Co-founder, Propel  (or get actual founder/CTO)

## OPTION C: Add a second technical quote

Add a quote from an engineer about the developer experience:

"Integrating Chroma took [X days/weeks]. The API is intuitive, and 
the combination of semantic and exact-match search is exactly what 
we needed for code intelligence."

[Name]
Senior Engineer, Propel
```

**Action Items**:
- [ ] Request headshot photo from Propel
- [ ] Ask if founder/CTO can provide a quote
- [ ] Verify Tony Dong's correct title

---

### 4. Add Visual Elements

**Current State**: Text-heavy, no diagrams or visuals

**Recommendation**: Add architecture diagram showing how Propel uses Chroma

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROPEL + CHROMA ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐                                                        │
│  │   GitHub PR     │                                                        │
│  │   Webhook       │                                                        │
│  └────────┬────────┘                                                        │
│           │                                                                 │
│           ▼                                                                 │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
│  │  Propel Agent   │────▶│  Chroma Cloud   │────▶│ Relevant Code   │       │
│  │                 │     │                 │     │ Context         │       │
│  │  • Analyzes PR  │     │ • Semantic      │     │                 │       │
│  │  • Requests     │     │   Search        │     │ • Related files │       │
│  │    context      │     │ • Regex Match   │     │ • Patterns      │       │
│  │                 │     │ • Package       │     │ • Dependencies  │       │
│  └─────────────────┘     │   Search MCP    │     └─────────────────┘       │
│           │              └─────────────────┘                                │
│           │                      │                                          │
│           │                      ▼                                          │
│           │              ┌─────────────────┐                                │
│           │              │ Open Source     │                                │
│           │              │ Package Index   │                                │
│           │              │ (via MCP)       │                                │
│           │              └─────────────────┘                                │
│           │                                                                 │
│           ▼                                                                 │
│  ┌─────────────────┐                                                        │
│  │ Senior-Engineer │                                                        │
│  │ Quality Review  │                                                        │
│  └─────────────────┘                                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Action Items**:
- [ ] Create professional architecture diagram
- [ ] Request Propel's approval on architecture representation
- [ ] Consider adding code snippet example

---

### 5. Add "Why Chroma" Section

**Current State**: Missing evaluation context

**Recommendation**: Add a section explaining why Propel chose Chroma

```markdown
## Why Chroma

Propel evaluated several vector database solutions before choosing 
Chroma Cloud as their foundational infrastructure:

| Requirement | Why Chroma Won |
|-------------|----------------|
| **Search Accuracy** | Chroma's semantic search consistently outperformed alternatives in code retrieval benchmarks |
| **Hybrid Search** | Unique combination of semantic + Regex for both conceptual and exact symbol matching |
| **Package Search** | No other solution offered dependency intelligence via MCP |
| **Developer Experience** | Simple API, fast integration, excellent documentation |
| **Enterprise Security** | Strong tenant isolation for serving enterprise customers |

"We looked at [alternatives], but Chroma was the only solution that 
combined semantic understanding with precise symbol-level search. 
For code review, you need both."
— [Technical Leader], Propel
```

**Action Items**:
- [ ] Ask Propel what alternatives they evaluated
- [ ] Get quote about decision criteria

---

## 🟢 Nice-to-Have Improvements

### 6. Enhance Company Introduction

**Current State**:
```
Propel builds AI agents that review pull requests at the level of 
senior engineers. From the outset, the team knew that high quality 
reviews require more than analyzing the files changed in a single PR.
```

**Recommendation**: Add traction/credibility indicators

```markdown
## SUGGESTED REWRITE

Propel builds AI agents that review pull requests at the level of 
senior engineers. Backed by [investors/accelerator if applicable], 
the San Francisco-based startup serves [XX] engineering teams who 
process [XX] pull requests monthly through their platform.

From the outset, the team knew that high-quality reviews require 
more than analyzing the files changed in a single PR—they require 
understanding the entire codebase and its dependencies.
```

**Action Items**:
- [ ] Request traction metrics from Propel (customers, PRs reviewed, etc.)
- [ ] Ask about funding/investors if public

---

### 7. Add Related Case Studies / Social Proof

**Current State**: No related content

**Recommendation**: Add section at bottom

```markdown
## See how other companies use Chroma

[Card: Company A] - RAG for customer support
[Card: Company B] - AI search for documents
[Card: Company C] - Code intelligence (similar use case)
```

---

### 8. Improve CTA Section

**Current State**:
```
Get $5 in free credits on Chroma Cloud
Sign up now | View pricing
```

**Recommendation**: Make CTA more relevant to the use case

```markdown
## Build AI agents with deep context

Start building code intelligence, RAG applications, or AI agents 
with Chroma Cloud.

[Primary CTA] Get started free →
[Secondary CTA] Talk to sales | View pricing

Or explore:
• Documentation for code search →
• Package Search MCP →
• Enterprise security features →
```

---

## 📝 Suggested Copy Rewrites

### Rewritten Hero Section

```markdown
# Propel uses Chroma Cloud to power code review agents

Deep repository and dependency context for faster, higher quality code reviews.

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│      XX%        │  │      XXx        │  │     100%        │
│   Review        │  │    Faster       │  │   Repository    │
│   Accuracy      │  │    Context      │  │   Coverage      │
│                 │  │   Retrieval     │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘

"Chroma is the obvious choice for Propel. The combination of semantic 
search, Regex matching, and Package Search gives our agents the deep 
context they need to review code like senior engineers."

[Photo] [Name]
CTO & Co-founder, Propel

─────────────────────────────────────────────────────────────────────
INDUSTRY          COMPANY STAGE          HQ
AI Code Review    Seed                   San Francisco, CA
─────────────────────────────────────────────────────────────────────
```

### Rewritten Results Section

```markdown
## Results

By building on Chroma Cloud from the start, Propel designed its agent 
around deep, structured context.

| Metric | Outcome |
|--------|---------|
| **Repository Coverage** | 100% codebase context vs. single-file analysis |
| **Review Quality** | XX% of suggestions accepted by engineers |
| **Token Efficiency** | XXx reduction vs. full codebase scanning |
| **Retrieval Speed** | <XXms to surface relevant context |

### What this enables:

✅ **Repository-wide reasoning** — The agent understands patterns and 
   conventions across the entire codebase, not just the changed files.

✅ **Symbol-level precision** — Regex search grounds recommendations in 
   concrete code, validating suggestions against real usage patterns.

✅ **Dependency intelligence** — Package Search reveals internal behavior 
   of third-party libraries, catching issues that local analysis would miss.

✅ **Cost-effective at scale** — Targeted retrieval eliminates the need 
   for expensive full-codebase scans on every PR.

Chroma Cloud plays a core role in enabling Propel's agent to reason more 
like an experienced engineer, drawing on knowledge embedded across both 
the codebase and the open source ecosystem it depends on.
```

---

## 📋 Action Item Summary

### Immediate (Before Publishing)

| Priority | Action | Owner | Status |
|----------|--------|-------|--------|
| 🔴 | Request metrics from Propel | | [ ] |
| 🔴 | Add hero metric cards | | [ ] |
| 🔴 | Quantify results section | | [ ] |
| 🟠 | Get founder/CTO quote | | [ ] |
| 🟠 | Request headshot photo | | [ ] |
| 🟠 | Create architecture diagram | | [ ] |

### Before Launch

| Priority | Action | Owner | Status |
|----------|--------|-------|--------|
| 🟠 | Add "Why Chroma" section | | [ ] |
| 🟠 | Verify quote attribution/title | | [ ] |
| 🟢 | Add traction metrics to intro | | [ ] |
| 🟢 | Improve CTA relevance | | [ ] |

### Post-Launch

| Priority | Action | Owner | Status |
|----------|--------|-------|--------|
| 🟢 | Add related case studies | | [ ] |
| 🟢 | Create video testimonial | | [ ] |

---

## 📧 Email Template: Requesting Metrics from Propel

```
Subject: Chroma Case Study - Quick metrics request

Hi Tony,

Thanks again for participating in our case study! The content looks 
great, and we're excited to publish it.

To make the case study as impactful as possible for readers (and for 
Propel!), we'd love to include some specific metrics. Could you share 
any of the following?

**Performance Metrics:**
- Code review accuracy rate (% of suggestions accepted/useful)
- Speed improvement vs. manual review or previous approach
- Retrieval latency for context

**Scale Metrics:**
- Number of repositories indexed
- Lines of code / vectors stored
- PRs reviewed per day/week/month

**Efficiency Metrics:**
- Token cost savings vs. full codebase scanning
- Time saved per review

Even rough numbers or ranges would be helpful! We can also frame them 
as "up to X" or "approximately X" if exact figures are sensitive.

Also, a couple quick requests:
1. Could we get a headshot photo for the quote attribution?
2. Would [Founder/CTO name] be willing to provide a brief quote as well?

Let me know if you have any questions!

Best,
[Your name]
```

---

## 🎯 Expected Impact

After implementing these improvements:

| Metric | Current | Expected |
|--------|---------|----------|
| **Time on Page** | Baseline | +30-50% |
| **CTA Click Rate** | Baseline | +20-40% |
| **Cohort 1 Resonance** | Medium | High |
| **Competitive Differentiation** | Low | High |
| **SEO Value** | Medium | High |

---

*Analysis by: GTM Team*
*Date: January 14, 2026*


