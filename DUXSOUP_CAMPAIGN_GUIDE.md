# 🤖 Dux-Soup Campaign Design - Chroma GTM

## Overview

This guide configures Dux-Soup campaigns for LinkedIn outreach targeting AI/ML companies that could benefit from Chroma's embedding database.

---

## 🎯 Campaign Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DUX-SOUP CAMPAIGN FUNNEL                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   CAMPAIGN 1          CAMPAIGN 2          CAMPAIGN 3                    │
│   ───────────         ───────────         ───────────                   │
│   Profile Visit  →    Connection    →     Nurture                       │
│   (Warm-up)           Request             Sequence                      │
│                                                                         │
│   ↓                   ↓                   ↓                             │
│   Day 1-3             Day 4-7             Day 8-30                      │
│   View profiles       Send requests       Multi-touch                   │
│   (50-100/day)        (20-30/day)         messages                      │
│                                                                         │
│                                           ↓                             │
│                                     MEETING BOOKED                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Campaign 1: Profile Warm-Up (Visit Only)

### Purpose
Warm up prospects before connection request. When you visit a profile, they see you in "Who Viewed Your Profile" - this creates familiarity.

### Dux-Soup Settings

| Setting | Value |
|---------|-------|
| **Campaign Name** | `Chroma_Warmup_[Segment]` |
| **Action** | Visit Profile Only |
| **Daily Limit** | 80-100 profiles |
| **Delay Between Actions** | 45-90 seconds |
| **Working Hours** | 9 AM - 6 PM (target's timezone) |

### Target Segments

Create separate warm-up campaigns for each segment:

#### Segment A: AI Engineers
```
LinkedIn Search URL (Sales Navigator):
Title: ("AI Engineer" OR "ML Engineer" OR "Machine Learning Engineer")
Company Size: 11-500
Industry: Computer Software, Internet
```

#### Segment B: Technical Leaders
```
LinkedIn Search URL (Sales Navigator):
Title: ("CTO" OR "VP Engineering" OR "Head of Engineering" OR "Director of Engineering")
Company Size: 11-200
Keywords: ("AI" OR "ML" OR "machine learning")
```

#### Segment C: Platform/Infra Engineers
```
LinkedIn Search URL (Sales Navigator):
Title: ("Platform Engineer" OR "Infrastructure Engineer" OR "Staff Engineer")
Keywords: ("AI" OR "ML" OR "embeddings" OR "vector")
```

### Execution Timeline
- **Day 1-3**: Run warm-up campaign
- **Day 4**: Move warmed profiles to Campaign 2

---

## 📋 Campaign 2: Connection Requests

### Purpose
Send personalized connection requests to warmed-up prospects.

### Dux-Soup Settings

| Setting | Value |
|---------|-------|
| **Campaign Name** | `Chroma_Connect_[Segment]` |
| **Action** | Send Connection Request |
| **Daily Limit** | 20-30 requests |
| **Delay Between Actions** | 60-120 seconds |
| **Working Hours** | 9 AM - 5 PM |
| **Personalization** | Use Dux-Soup variables |

### Connection Request Messages

#### Message A: No Note (Highest Accept Rate)
> Leave the note field EMPTY
> Your optimized profile headline does the work
> **Expected Accept Rate: 40-50%**

#### Message B: Short & Curious
```
Hi {FirstName}, building in the AI space too - would love to connect and follow your work at {Company}.
```
**Characters: 95** | **Expected Accept Rate: 35-40%**

#### Message C: Mutual Interest
```
Hi {FirstName}, saw you're working on AI at {Company}. Always great to connect with others in the space!
```
**Characters: 98** | **Expected Accept Rate: 30-35%**

#### Message D: Specific Hook (For High-Value Targets)
```
Hi {FirstName}, been following {Company}'s AI work - impressive stuff. Would love to connect.
```
**Characters: 89** | **Expected Accept Rate: 35-40%**

### A/B Testing Strategy
- **Week 1**: Send 50% with no note, 50% with Message B
- **Week 2**: Analyze accept rates, use winner
- **Week 3**: Test winner against Message C or D

---

## 📋 Campaign 3: Nurture Sequence (Multi-Touch Drip)

### Purpose
Engage new connections with a value-first message sequence that leads to a meeting.

### Dux-Soup Settings

| Setting | Value |
|---------|-------|
| **Campaign Name** | `Chroma_Nurture_[Segment]` |
| **Action** | Send Message Sequence |
| **Trigger** | Connection Accepted |
| **Message Delays** | See sequence below |

---

## 💬 Message Sequences by Segment

### Sequence A: AI Engineers

#### Message 1 (Day 0 - Immediately after accept)
```
Hey {FirstName}, thanks for connecting!

I noticed you're building AI at {Company}. We work with a lot of ML teams on their embedding infrastructure.

Quick question: are you using RAG in any of your projects? Curious how teams are approaching retrieval these days.

No pitch, just genuinely interested in what you're building.
```
**Characters: 340** | **Goal: Start conversation**

#### Message 2 (Day 3 - If no response)
```
{FirstName}, one thing I've been seeing a lot lately:

Teams spending weeks on embedding infrastructure when they could ship in days.

We put together a quick guide on "Production RAG in 5 Days" based on patterns from 500+ AI teams.

Want me to send it over?
```
**Characters: 280** | **Goal: Offer value**

#### Message 3 (Day 7 - If no response)
```
Hey {FirstName}, last thought from me:

If you ever want to chat about RAG architecture, embedding strategies, or just swap notes on what's working in AI - I'm always up for it.

No agenda. Just like talking shop with people building cool stuff.

Either way, enjoy following your work!
```
**Characters: 295** | **Goal: Soft close**

#### Message 4 (Day 14 - If no response)
```
{FirstName}, quick one:

We're hosting a small virtual roundtable on "RAG in Production" with engineers from [Company 1] and [Company 2].

Thought you might find it interesting given what {Company} is building.

Want me to send the details?
```
**Characters: 250** | **Goal: Event invite**

---

### Sequence B: Technical Leaders (CTO/VP Eng)

#### Message 1 (Day 0 - Immediately after accept)
```
{FirstName}, appreciate the connection!

I lead growth at Chroma - we're the open-source embedding database powering RAG for companies like [Customer 1] and [Customer 2].

Given {Company}'s work in AI, curious: is embedding infrastructure on your radar, or is the team handling it differently?

Either way, would love to learn more about what you're building.
```
**Characters: 380** | **Goal: Qualify interest**

#### Message 2 (Day 4 - If no response)
```
{FirstName}, one pattern we're seeing:

Engineering teams spending 2-3 months building vector search infrastructure, then rebuilding it 6 months later when it doesn't scale.

We helped [Similar Company] avoid this - shipped production RAG in 2 weeks, now handling 10M+ vectors.

Would a 15-min call be useful to see if we could help {Company} move faster?
```
**Characters: 365** | **Goal: Create urgency**

#### Message 3 (Day 10 - If no response)
```
{FirstName}, last note:

Put together a one-pager on "Build vs Buy for Embedding Infrastructure" - the real costs most teams miss.

Happy to share if useful. No strings attached.

Either way, enjoy following {Company}'s journey!
```
**Characters: 240** | **Goal: Value offer + soft close**

---

### Sequence C: Platform/Infra Engineers

#### Message 1 (Day 0 - Immediately after accept)
```
Hey {FirstName}, thanks for connecting!

Fellow infrastructure person here. I work on Chroma - the embedding database that a lot of AI teams use for RAG.

Curious: how is {Company} handling vector storage and retrieval? Always interested in how different teams approach it.
```
**Characters: 290** | **Goal: Peer-to-peer conversation**

#### Message 2 (Day 3 - If no response)
```
{FirstName}, one thing I've been thinking about:

The "right" embedding infrastructure depends heavily on scale and use case. There's no one-size-fits-all.

We put together a decision framework: "When to use pgvector vs dedicated vector DB vs in-memory"

Want me to share it?
```
**Characters: 290** | **Goal: Offer technical value**

#### Message 3 (Day 7 - If no response)
```
{FirstName}, if you ever want to nerd out about:

- Embedding model selection
- Chunking strategies
- Hybrid search architectures
- Scaling vector search

I'm always down to chat. No sales pitch, just enjoy talking infra.

DM me anytime!
```
**Characters: 230** | **Goal: Open door**

---

## 📋 Campaign 4: Re-Engagement (For Cold Connections)

### Purpose
Re-engage connections who didn't respond to initial sequence.

### Dux-Soup Settings

| Setting | Value |
|---------|-------|
| **Campaign Name** | `Chroma_Reengage` |
| **Trigger** | 30 days after last message, no response |
| **Action** | Send single message |

### Re-Engagement Messages

#### Message A: Content Share
```
{FirstName}, been a while! 

Just published something on [relevant topic] that made me think of you: [Link]

Hope {Company} is crushing it!
```

#### Message B: News Hook
```
{FirstName}, saw the news about {Company} [raising funding / launching feature / etc]. Congrats!

If embedding infrastructure ever becomes relevant, would love to chat.
```

#### Message C: Direct Ask
```
{FirstName}, circling back one more time.

Would you be open to a 15-min call to see if Chroma could help {Company} ship AI features faster?

If not the right time, no worries at all.
```

---

## ⚙️ Dux-Soup Configuration

### Account Safety Settings

| Setting | Recommended Value |
|---------|-------------------|
| **Daily Profile Visits** | 80-100 |
| **Daily Connection Requests** | 20-30 |
| **Daily Messages** | 50-80 |
| **Delay Between Actions** | 45-120 seconds (randomized) |
| **Working Hours** | 9 AM - 6 PM local |
| **Days Active** | Monday - Friday |
| **Weekend Activity** | OFF |

### Throttling Rules
```
If LinkedIn shows warning → Pause for 24 hours
If accept rate < 15% → Review targeting/messaging
If response rate < 5% → Review message content
```

### Tag System

Use Dux-Soup tags to track prospects:

| Tag | Meaning |
|-----|---------|
| `warmed` | Profile visited, ready for connection |
| `connected` | Connection accepted |
| `responded` | Replied to message |
| `interested` | Expressed interest |
| `meeting_booked` | Call scheduled |
| `not_interested` | Declined/uninterested |
| `competitor` | Works at competitor |

---

## 📊 Campaign Performance Tracking

### Weekly Dashboard

| Metric | Target | Week 1 | Week 2 | Week 3 | Week 4 |
|--------|--------|--------|--------|--------|--------|
| Profiles Visited | 400+ | | | | |
| Connection Requests Sent | 100+ | | | | |
| Connections Accepted | 30+ | | | | |
| Accept Rate | 30%+ | | | | |
| Messages Sent | 100+ | | | | |
| Responses Received | 20+ | | | | |
| Response Rate | 20%+ | | | | |
| Meetings Booked | 5+ | | | | |

### Segment Performance

| Segment | Requests | Accepts | Rate | Responses | Meetings |
|---------|----------|---------|------|-----------|----------|
| AI Engineers | | | | | |
| Tech Leaders | | | | | |
| Platform Eng | | | | | |

---

## 🚀 Launch Checklist

### Week 1: Setup

- [ ] **Install Dux-Soup** (Pro or Turbo edition)
- [ ] **Configure safety settings** (see above)
- [ ] **Create LinkedIn searches** for each segment
- [ ] **Set up tag system**
- [ ] **Create Campaign 1** (Warm-up) for Segment A
- [ ] **Test with 10 profiles** before scaling

### Week 2: Connection Phase

- [ ] **Launch Campaign 1** at full volume (80-100/day)
- [ ] **After 3 days**, move warmed profiles to Campaign 2
- [ ] **Launch Campaign 2** (20-30 requests/day)
- [ ] **Monitor accept rates** daily
- [ ] **A/B test** connection messages

### Week 3: Nurture Phase

- [ ] **Launch Campaign 3** for accepted connections
- [ ] **Monitor response rates**
- [ ] **Respond to replies** within 24 hours (manually)
- [ ] **Book meetings** from interested prospects
- [ ] **Tag all prospects** appropriately

### Week 4: Optimize

- [ ] **Review all metrics**
- [ ] **Kill underperforming segments**
- [ ] **Double down on winners**
- [ ] **Expand to new segments**
- [ ] **Launch re-engagement campaign**

---

## 🎯 Target Account Lists

### Tier 1: Highest Priority (Import to Dux-Soup First)

| Company | Category | Why Target |
|---------|----------|------------|
| Cursor | Developer Tools | AI coding assistant, needs RAG |
| Sierra AI | Customer Support | $10B valuation, AI support platform |
| Decagon | Customer Support | Building AI agents |
| Harvey AI | Legal Tech | Document retrieval |
| Clay | Sales Intelligence | Data enrichment with AI |
| n8n | AI Agents | Workflow automation |
| Guru | Knowledge Management | Enterprise knowledge base |
| Elicit | Research Tools | Academic paper search |
| AlphaSense | Financial Research | Market intelligence |
| Writer | Content AI | Enterprise writing assistant |

### Tier 2: High Priority

| Company | Category | Why Target |
|---------|----------|------------|
| Mintlify | Documentation | Developer docs |
| GitBook | Documentation | Technical documentation |
| Forethought | Customer Support | AI support |
| Abridge | Healthcare AI | Medical transcription |
| Semantic Scholar | Research | Paper search |
| Relevance AI | AI Agents | Agent platform |
| Tettra | Knowledge Management | Team wiki |
| Daloopa | Financial Research | Financial data |

### Search URLs for Dux-Soup

**Tier 1 Companies - AI Engineers:**
```
https://www.linkedin.com/search/results/people/?keywords=AI%20engineer&origin=GLOBAL_SEARCH_HEADER&currentCompany=[COMPANY_IDS]
```

**Tier 1 Companies - Technical Leaders:**
```
https://www.linkedin.com/search/results/people/?keywords=CTO%20OR%20VP%20Engineering&origin=GLOBAL_SEARCH_HEADER&currentCompany=[COMPANY_IDS]
```

---

## 💡 Pro Tips for Dux-Soup

### 1. Use Scan Mode First
Before running any campaign, use Dux-Soup's "Scan" feature to:
- Build a list of prospects
- Review profiles before outreach
- Remove competitors or bad fits

### 2. Leverage Profile Notes
Add notes to profiles as you go:
- What they're working on
- Potential use case for Chroma
- Any mutual connections

### 3. Export Regularly
Export your Dux-Soup data weekly:
- Backup your prospect list
- Analyze in spreadsheet
- Import to CRM

### 4. Combine with Manual Outreach
For high-value targets (VPs, CTOs at Tier 1 companies):
- Use Dux-Soup to warm up
- Send connection request manually
- Craft personalized first message

### 5. Monitor LinkedIn's Limits
LinkedIn's weekly limits (approximate):
- **Connection requests**: 100-200/week
- **Profile views**: 500-1000/week
- **Messages**: 150-300/week

Stay under these to avoid restrictions.

---

## 🚨 Troubleshooting

### "LinkedIn restricted my account"
1. **Stop all Dux-Soup activity immediately**
2. Wait 24-48 hours
3. Reduce daily limits by 50%
4. Gradually increase over 2 weeks

### "Accept rate is below 20%"
1. Review your profile - is it optimized?
2. Test different connection messages
3. Try sending with no note
4. Check if you're targeting the right people

### "No responses to messages"
1. Messages too long? Keep under 300 characters
2. Too salesy? Lead with value
3. Wrong timing? Check working hours
4. Wrong persona? Review targeting

### "Dux-Soup not finding profiles"
1. Check if LinkedIn search URL is correct
2. Ensure you're logged into LinkedIn
3. Clear browser cache
4. Try a different search

---

## 📅 Sample Weekly Schedule

| Day | Morning (1 hr) | Afternoon (30 min) |
|-----|----------------|-------------------|
| **Mon** | Review weekend accepts, respond to messages | Launch warm-up campaign |
| **Tue** | Check campaign metrics, adjust targeting | Send connection requests |
| **Wed** | Respond to new messages, book calls | Monitor campaigns |
| **Thu** | Export data, update CRM | Optimize messaging |
| **Fri** | Weekly review, plan next week | Pause campaigns for weekend |

---

## 📈 Expected Results (Month 1)

| Week | Visits | Requests | Accepts | Messages | Responses | Meetings |
|------|--------|----------|---------|----------|-----------|----------|
| 1 | 400 | 50 | 15 | 15 | 3 | 1 |
| 2 | 400 | 100 | 30 | 45 | 9 | 2 |
| 3 | 400 | 100 | 30 | 60 | 12 | 3 |
| 4 | 400 | 100 | 30 | 60 | 12 | 4 |
| **Total** | **1600** | **350** | **105** | **180** | **36** | **10** |

**Month 1 Targets:**
- 100+ new connections
- 30+ conversations started
- 10+ meetings booked

---

*Last Updated: December 2024*

