# Using Claude Code to run any Ops (in this case GTM Engineering) 
Ankit Pansari
--- 
For the past six years, I have focused on knowledge management and productivity. This journey led me to start OSlash and spend a significant amount of time (and money 🙃) working with LLMs.

Everything I write below is based on empirical evidence, prompt experimentation, and guesswork. As the Manus team says, “It’s not elegant, but it works” - [Context Engineering for AI Agents: Lessons from Building Manus](￼).  
Note: I have drawn inspiration from Manus and discussions with engineering teams at Anthropic regarding their internal guidelines for Claude Projects and Code. 
___
This is a semi-automated attempt to build a personal OS for work - in this case being a GTM engineer for a fast growing dev tool company. 

My goal is to design a OS that : 
- **Remembers everything** about my company, strategy, and style
- **Researches automatically** before drafting anything
- **Works anywhere** - from my IDE or even my phone via GitHub

I want to run multiple instances of Claude Code in parallel, so I use a tool called [Conductor](https://www.conductor.build/) (similar to [Cursor Agent](https://cursor.sh) )

### How to start 
Start with Claude Code in a single Github repo and provide guidelines to create the following files with context about your company, yourself, and your role.

1. Start with **CLAUDE.md** - Tell Claude who you are
2. **Add context files** -ex companies.md, prospects.md, competitors.md, tools.md 
3. Large Data files - **CSV, JSON** (leads, compeitors, companies)
4. **Documentation** (Markdown) for playbooks, templates, and meeting notes
   
### **Claude.md** 
This is the most important file. Claude reads this first to understand who you are, what your role is, and what actions you need to take. You can ask Claude for code directly to configure the md file and keep it updated.  

For reference, this is how my Claude.md file looks.  
![](Using%20Claude%20Code%20to%20run%20any%20Ops%20%28in%20this%20case%20GTM%20Engineering%29/CleanShot%202026-01-10%20at%2022.05.34@2x.png)

### What Each File Does (And How They Link)  
Here I am talking in GTM perspective your file structure might be different and will evolve with time. You can create as many files as possible, just make sure they are linked to Claude.md 

* **CLAUDE.md** - Claude's identity and style guide
* **GTM_CONTEXT.md** - Strategy, ICP, and positioning
* **COMPETITORS.md** - Competitive intelligence
* **OUTREACH_TEMPLATES.md** - Email/LinkedIn templates
* **MEETING_INDEX.md** - Master meeting index
* **meetings/notes/*.md** - Individual meeting notes
* **env folder** - API keys (for using external tools) 

### The Hierarchy of Context

Claude reads files in this order of priority:
```
1. CLAUDE.md (ALWAYS read first)
   └── "This is who I am and how I communicate"

2. Task-specific context (based on what you're asking)
   ├── Email? → OUTREACH_TEMPLATES.md
   ├── Competitor question? → COMPETITORS.md
   ├── Strategy question? → GTM_CONTEXT.md
   └── Meeting reference? → MEETING_INDEX.md → specific notes

3. Recent context (for follow-ups)
   └── Conversation history based on your query box
```

### **Make the entire setup Mobile** 
1. I want to ensure that I can use everything on the go (on my mobile). The best interface and workflow I found is [GitHub Actions](https://github.com/features/actions). 
2. Claude Code now has a native integration. You can push all your code to a GitHub repository, including large files like CSV and JSON, using [GitHub LFS](https://git-lfs.com). 
3. I can simply ask Claude for my top three priorities as an issue, and I will receive the results. (You can see the sloppiness with January 2025 🙄) 
![](Using%20Claude%20Code%20to%20run%20any%20Ops%20%28in%20this%20case%20GTM%20Engineering%29/CleanShot%202026-01-10%20at%2022.16.25.png)


**When you ask Claude to draft an email:**

```yaml
*# GitHub Action loads these files:*
cat CLAUDE.md >> context.txt                    *# Your identity*
cat context/GTM_CONTEXT.md >> context.txt       *# Your strategy*  
cat context/OUTREACH_TEMPLATES.md >> context.txt *# Your templates*
cat context/MEETING_INDEX.md >> context.txt     *# Recent learnings*

*# Then sends to Claude with your request*
```
![](Using%20Claude%20Code%20to%20run%20any%20Ops%20%28in%20this%20case%20GTM%20Engineering%29/CleanShot%202026-01-10%20at%2022.35.29@2x.png)

**When you ask about a competitor:**

```yaml
*# GitHub Action loads:*
cat CLAUDE.md >> context.txt
cat context/COMPETITORS.md >> context.txt       *# Competitor intel*
cat context/MEETING_INDEX.md >> context.txt     *# What came up in meetings*
```

**When you ask about recent decisions:**

```yaml
*# GitHub Action loads:*
cat CLAUDE.md >> context.txt
cat context/MEETING_INDEX.md >> context.txt     *# Has "Recent Decisions" table*
*# Claude can reference specific meetings if needed*
```

### Why This Architecture Works

1\. **Single source of truth**: Each type of information has ONE home (single folder structure) 
2\. **Layered context**: General (CLAUDE.md) → Specific (templates) → Recent (meetings)
3\. **Compounding knowledge**: Every meeting adds to the system
4\. **Easy updates**: Change one file, all future responses improve
5\. **Traceable**: You can see exactly where Claude got its information 

### External APIs 
The GitHub Action is just the interface. The real power comes from connecting external APIs that do the heavy lifting. Here's how I integrate multiple APIs to create a complete GTM system.
- If you're creating a list of prospects for your company, use [Parallel AI](￼) ==🟡to generate a list of look-alike companies based on your competitors' customer case studies.== 
- Use Selenium or a headless browser to run automation directly in Chrome. This is easier if you are using Cursor Agent. For example, ==🟡you can automate Sales Navigator requests for all ICPs on LinkedIn.== 
- In my  case - I used [Coresignal](https://coresignal.com) ==🟡API to make a list of all the companies who are hiring AI engineers.==  
- ￼And then [Firecrawl](https://firecrawl.dev) ==🟡to visit company website before drafting emails, verification of ICP etc.== 
- You can also add multiple webhooks to connect with GTM tools and enrich them directly in HubSpot, Slack, and draft Gmail responses. You can even get creative and use a terminal-based mail client like Mutt. 

**Note**: it helps to create a `.env` file to store all your API keys securely in one folder (both for models and external tools)

```bash
*# .env - Store your API keys here (add to .gitignore!)*

*# ===========================================*
*# Core AI APIs*
*# ===========================================*
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-openai-key-here

*# ===========================================*
*# Lead Discovery & Enrichment*
*# ===========================================*
*# Parallel.ai - Web-scale entity discovery*
PARALLEL_API_KEY=your-parallel-api-key

*# Firecrawl - Web scraping and search*
FIRECRAWL_API_KEY=fc-your-firecrawl-key

*# ===========================================*
*# CRM & Notifications*
*# ===========================================*
HUBSPOT_API_KEY=pat-your-hubspot-key
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/xxx/xxx
```

### Building Institutional Memory with Meeting Notes
One of the most powerful parts of this system is how it captures and compounds knowledge from every meeting. Instead of insights disappearing after calls, they become permanent context that Claude can reference.

Every meeting gets recorded, transcribed, and structured into searchable context.

**Folder structure**
```
meetings/
├── MEETING_NOTES_PROMPT.md     # Prompt template for extraction
├── README.md                   # How to use the system
└── notes/
    ├── _TEMPLATE.md            # Template for new notes
    ├── 2026-01-09_partner-call.md
    ├── 2026-01-08_vendor-eval.md
    ├── 2026-01-06_strategy-ceo.md
    └── 
```

Every meeting gets recorded, transcribed, and structured into searchable context. I have written custom recipe in Granola to make transcripts more actionable. 

```
| Date | Meeting Title | Type | Participants | Notes | Key Topics |
|------|---------------|------|--------------|-------|------------|
| 2026-01-09 | Partner GTM Call | Partner | Team, Partner | [📋](../meetings/notes/2026-01-09_partner-call.md) | Positioning, Packaging |
| 2026-01-08 | Vendor Evaluation | Vendor | Team, Vendor | [📋](../meetings/notes/2026-01-08_vendor-eval.md) | Signals, HubSpot |
| 2026-01-06 | Strategy Session | Internal | Team | [📋](../meetings/notes/2026-01-06_strategy.md) | SEO, Content |

## Key Insights by Theme

### 🎯 GTM Strategy
- **2026-01-06**: PLG caps at $1-2M; enterprise must cover the rest
- **2026-01-05**: ICP is only 2-5k accounts; need high-touch

### 💰 Positioning
- **2026-01-09**: "Sell the architecture, not just the product"
- **2026-01-06**: "Better accuracy → lower costs → better agents"

### 🏢 Competitive Intel
- **2026-01-08**: Competitor X = strong in segment Y
- **2026-01-06**: We're losing SEO on "keyword Z"

## Open Action Items
- [ ] Build quarter plan for revenue target
- [ ] Start outreach campaign (700 emails)
- [ ] Fix CRM tracking

## Recent Decisions
| Date | Decision | Context |
|------|----------|---------|
| 2026-01-09 | Evaluate new partner | Fractional CMO for positioning |
| 2026-01-06 | Programmatic SEO experiment | "Build X with Y" content |
```

```
# Meeting Notes: [MEETING TITLE]

## Metadata
- **Date**: YYYY-MM-DD
- **Participants**: [Names and roles]
- **Meeting Type**: [Customer / Internal / Strategy / Partner]

## Summary
<!-- 2-3 sentences: What was this meeting about? -->

## Key Discussion Points

### 1. [Topic]
- Point 1
- Point 2

### 2. [Topic]
- Point 1
- Point 2---

## Decisions Made
- Decision 1
- Decision 2

---

## Action Items
- [ ] **[Owner]**: [Task] - Due: [Date]
- [ ] **[Owner]**: [Task] - Due: [Date]

---

## GTM Insights

**Customer Signals**:
- Pain point mentioned
- Feature request

**Competitive Intel**:
- Competitor mentioned
- How we compare

**Messaging/Positioning**:
- What resonated
- What to emphasize

---

## Follow-up
- Next meeting: [Date]
- Questions to answer: [List]
```

My **Granola Recipe**  
```
I just had a meeting. Extract structured notes for my GTM project.

Here's the transcript:
[PASTE TRANSCRIPT]

Extract:
1. **Meeting Metadata** - Date, participants, type

2. **Summary** - 2-3 sentences max

3. **Key Discussion Points** - Top 3-5 topics with conclusions

4. **Decisions Made** - What was agreed upon

5. **Action Items** - Who, what, when

6. **GTM Insights**:
   - Customer signals (pain points, needs, objections)
   - Competitive intel (mentions of competitors)
   - Positioning (what resonated, messaging ideas)
   - Market insights (trends, opportunities)

7. **Open Questions** - What still needs answers

8. **Follow-up** - Next meetings, who to loop in

Format as clean markdown I can save directly.
```

I manually then paste all the notes to Meetings Index folder. 

After a few weeks of meetings, you can ask Claude: @claude Based on our recent meetings, what positioning is resonating  with prospects? What objections keep coming up?
```

Claude reads the meeting index and responds with synthesized insights from all your conversations.

Or when drafting outreach: 
```
@claude Draft an email to a consulting partner. Reference what we 
learned from the Reify meeting about how to position for agencies.

Claude pulls specific insights from that meeting into your email.
**This is how you build institutional memory that compounds over time.**

--- 
### Issues in the current system
1. Context still gets lost. Even with all the context files, Claude doesn't automatically know which file to reference. You have to:
   * Remember which files exist
   * Explicitly mention them or hope Claude reads them
   * Re-reference files as the conversation gets long
 **The workaround today**: Periodically say "read CLAUDE.md and GTM_CONTEXT.md" to refresh context.
![](Using%20Claude%20Code%20to%20run%20any%20Ops%20%28in%20this%20case%20GTM%20Engineering%29/image.png)
3. Working with large files in JSON/CSV takes time and the workflow  is not suitable for Github action 
   - Can't fit in context window
   - GitHub Actions has output limits
   - Processing is slow and expensive
   - No way to query subsets
4. As chat window gets longer, context rotting occurs leading to loss of relevant information. 
5. I have more than 40 guideline files , I often forget what to invoke. A better retrieval system linked to a vector database and creating separate collection for every data request might solve this issue. 
6. Each conversation starts fresh - Claude doesn't remember: 
   * The email style you preferred yesterday
   * The decision you made last week
   * The leads you already contacted 
   (I am experimenting with knowledge graph solution here)
   