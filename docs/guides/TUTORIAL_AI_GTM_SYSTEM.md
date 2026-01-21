# How I Built an AI-Powered GTM System with Claude & GitHub Actions

> A step-by-step tutorial on building your own AI co-pilot for Go-To-Market work using Claude, Cursor, and GitHub Actions.

---

## The Problem

I run GTM for an open-source developer tools company. Traditional GTM work is:

- **Manual** - Research companies one by one, write emails from scratch
- **No memory** - Every task starts fresh, context is lost
- **Tool-hopping** - Jump between docs, CRM, email, LinkedIn

I wanted an AI system that:
- **Remembers everything** about my company, strategy, and style
- **Researches automatically** before drafting anything
- **Works anywhere** - from my IDE or even my phone via GitHub

Here's exactly how I built it.

---

## The Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI GTM OPERATING SYSTEM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐                                           │
│  │  CONTEXT LAYER  │  ← Claude's "memory"                      │
│  │                 │                                           │
│  │  • CLAUDE.md    │  Who I am, what we do                     │
│  │  • GTM_CONTEXT  │  Strategy, ICP, positioning               │
│  │  • COMPETITORS  │  Competitive intelligence                 │
│  │  • TEMPLATES    │  Outreach templates & style               │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      CLAUDE                              │   │
│  │                                                          │   │
│  │   Cursor (Desktop)  ←──OR──→  GitHub Actions (Mobile)   │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │     OUTPUTS     │                                           │
│  │                 │                                           │
│  │  • Email drafts │                                           │
│  │  • Research     │                                           │
│  │  • LinkedIn     │                                           │
│  │  • Competitor   │                                           │
│  └─────────────────┘                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## How All the Files Are Linked

This is the key insight: **every file feeds into Claude's context**, and **every output can become new context**. Here's how they connect:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE CONTEXT WEB                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                         ┌──────────────┐                                    │
│                         │  CLAUDE.md   │ ← Entry point                      │
│                         │  (The Brain) │   Claude reads this FIRST          │
│                         └──────┬───────┘                                    │
│                                │                                             │
│              ┌─────────────────┼─────────────────┐                          │
│              │                 │                 │                          │
│              ▼                 ▼                 ▼                          │
│     ┌────────────────┐ ┌────────────────┐ ┌────────────────┐               │
│     │ GTM_CONTEXT.md │ │ COMPETITORS.md │ │  TEMPLATES.md  │               │
│     │                │ │                │ │                │               │
│     │ • ICP          │ │ • Who they are │ │ • Email styles │               │
│     │ • Positioning  │ │ • Our counters │ │ • LinkedIn     │               │
│     │ • Value props  │ │ • Win/loss     │ │ • Objections   │               │
│     └───────┬────────┘ └───────┬────────┘ └───────┬────────┘               │
│             │                  │                  │                         │
│             └──────────────────┼──────────────────┘                         │
│                                │                                             │
│                                ▼                                             │
│                    ┌───────────────────────┐                                │
│                    │    MEETING_INDEX.md   │ ← Living document              │
│                    │                       │   Updated after every meeting  │
│                    │ • All meetings table  │                                │
│                    │ • Key insights        │                                │
│                    │ • Action items        │                                │
│                    │ • Decisions log       │                                │
│                    └───────────┬───────────┘                                │
│                                │                                             │
│                                │ Links to                                    │
│                                ▼                                             │
│                    ┌───────────────────────┐                                │
│                    │   meetings/notes/     │                                │
│                    │                       │                                │
│                    │ • 2026-01-09_call.md  │                                │
│                    │ • 2026-01-08_eval.md  │                                │
│                    │ • 2026-01-06_strat.md │                                │
│                    └───────────────────────┘                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Flow: How Context Gets Added

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONTEXT FLOW (The Feedback Loop)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║                         1. INPUT SOURCES                               ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                                                              │
│      Meetings          Emails           Research          Wins/Losses       │
│          │                │                 │                  │            │
│          ▼                ▼                 ▼                  ▼            │
│      ┌────────────────────────────────────────────────────────────┐        │
│      │              EXTRACT & STRUCTURE                           │        │
│      │                                                            │        │
│      │   Use Claude to turn raw input into structured notes:     │        │
│      │   "Extract key insights, decisions, and action items"     │        │
│      └────────────────────────────────────────────────────────────┘        │
│                                │                                            │
│                                ▼                                            │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║                    2. UPDATE CONTEXT FILES                             ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                                                              │
│      ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│      │ Meeting notes   │    │ MEETING_INDEX   │    │ GTM_CONTEXT     │     │
│      │ saved to        │───▶│ updated with    │───▶│ updated if      │     │
│      │ meetings/notes/ │    │ new row +       │    │ major learning  │     │
│      │                 │    │ key insights    │    │                 │     │
│      └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│                                                                              │
│                                │                                            │
│                                ▼                                            │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║                    3. CONTEXT NOW AVAILABLE                            ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                                                              │
│      Next time you ask Claude anything:                                     │
│                                                                              │
│      "@claude draft email to consulting partner"                            │
│                    │                                                        │
│                    ▼                                                        │
│      Claude reads: CLAUDE.md → GTM_CONTEXT → TEMPLATES → MEETING_INDEX     │
│                    │                                                        │
│                    ▼                                                        │
│      Claude knows: "In the Jan 9 partner meeting, we learned that          │
│                    consulting firms respond to 'extended credits for        │
│                    client POCs' - I'll include that in the email"          │
│                                                                              │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║                    4. OUTPUT BECOMES INPUT                             ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                                                              │
│      The email you send → Response you get → New meeting/insight            │
│                    │                                                        │
│                    └──────────────────────────────────────────────────┐     │
│                                                                       │     │
│                                                                       ▼     │
│                                                    Back to Step 1 ────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### What Each File Does (And How They Link)

| File | Purpose | Updated When | Links To |
|------|---------|--------------|----------|
| **CLAUDE.md** | Claude's "identity" - who you are, what you do, your style | Rarely (when fundamentals change) | Everything reads this first |
| **context/GTM_CONTEXT.md** | Strategy, ICP, positioning, value props | When strategy shifts or major learnings | Referenced by all prompts |
| **context/COMPETITORS.md** | Competitive intelligence | After competitive calls, when market shifts | Referenced for positioning questions |
| **context/OUTREACH_TEMPLATES.md** | Email/LinkedIn templates | When you find better approaches | Referenced for drafting |
| **context/MEETING_INDEX.md** | Master index of all meetings + key insights | After EVERY meeting | Links to individual meeting notes |
| **meetings/notes/*.md** | Individual meeting notes | After each meeting | Linked from MEETING_INDEX |

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
   └── Conversation history in GitHub issue
```

### Practical Example: The Full Loop

Let's trace how a single meeting becomes permanent context:

```
DAY 1: You have a partner call
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Meeting happens (recorded with Fathom/Otter)
   │
   ▼
2. You paste transcript into Claude:
   "Extract structured notes from this meeting..."
   │
   ▼
3. Claude outputs structured markdown
   │
   ▼
4. You save to: meetings/notes/2026-01-09_partner-call.md
   │
   ▼
5. You update MEETING_INDEX.md:
   - Add row to "All Meetings" table
   - Add key insight to "Key Insights by Theme"
   - Add action items to "Open Action Items"
   │
   ▼
6. (Optional) If major learning, update GTM_CONTEXT.md:
   "Partners respond well to 'extended credits for POCs'"


DAY 5: You need to email another partner
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. You ask: "@claude draft email to consulting partner"
   │
   ▼
2. Claude reads:
   - CLAUDE.md (your voice/style)
   - OUTREACH_TEMPLATES.md (partner template)
   - MEETING_INDEX.md (sees partner insights)
   │
   ▼
3. Claude's response includes:
   "...Happy to set you up with extended credits for client POCs..."
   (learned from the Jan 9 meeting!)
   │
   ▼
4. You send email, get response, have another meeting...
   │
   ▼
   └── Back to Step 1 (the loop continues)
```

### The Key Files in Action

**When you ask Claude to draft an email:**

```yaml
# GitHub Action loads these files:
cat CLAUDE.md >> context.txt                    # Your identity
cat context/GTM_CONTEXT.md >> context.txt       # Your strategy  
cat context/OUTREACH_TEMPLATES.md >> context.txt # Your templates
cat context/MEETING_INDEX.md >> context.txt     # Recent learnings

# Then sends to Claude with your request
```

**When you ask about a competitor:**

```yaml
# GitHub Action loads:
cat CLAUDE.md >> context.txt
cat context/COMPETITORS.md >> context.txt       # Competitor intel
cat context/MEETING_INDEX.md >> context.txt     # What came up in meetings
```

**When you ask about recent decisions:**

```yaml
# GitHub Action loads:
cat CLAUDE.md >> context.txt
cat context/MEETING_INDEX.md >> context.txt     # Has "Recent Decisions" table
# Claude can reference specific meetings if needed
```

### Why This Architecture Works

1. **Single source of truth**: Each type of information has ONE home
2. **Layered context**: General (CLAUDE.md) → Specific (templates) → Recent (meetings)
3. **Compounding knowledge**: Every meeting adds to the system
4. **Easy updates**: Change one file, all future responses improve
5. **Traceable**: You can see exactly where Claude got its information

---

## Step 1: Create the Folder Structure

Create a new repository with this structure:

```bash
mkdir ai-gtm-system
cd ai-gtm-system
git init
```

```
ai-gtm-system/
├── CLAUDE.md                    # AI context file (Claude reads this first)
├── context/
│   ├── GTM_CONTEXT.md          # Your GTM strategy
│   ├── COMPETITORS.md          # Competitive intelligence
│   └── OUTREACH_TEMPLATES.md   # Email/LinkedIn templates
├── .github/
│   ├── workflows/
│   │   └── claude-assistant.yml # GitHub Action
│   └── ISSUE_TEMPLATE/
│       └── ask-claude.yml       # Issue template
└── .gitignore
```

---

## Step 2: Create CLAUDE.md (The Brain)

This is the most important file. Claude reads this first to understand who you are.

```markdown
# CLAUDE.md

## Who I Am
- Name: [Your Name]
- Role: [Your Role] at [Company]
- Email: [your@email.com]

## About [Company]
[2-3 sentences about what your company does]

**Key facts:**
- [Fact 1 - e.g., "100M+ downloads"]
- [Fact 2 - e.g., "Series A, $20M raised"]
- [Fact 3 - e.g., "50+ enterprise customers"]

## Our Positioning
- We are: [What you are - e.g., "the leading platform for X"]
- We are NOT: [What you're not - e.g., "a legacy solution"]
- Key differentiator: [Your main advantage]

## My Communication Style
- Tone: [e.g., "Friendly, conversational, like talking to a smart friend"]
- Sign-off: [e.g., "Talk soon!"]
- Always include: [e.g., "CC the founder on important emails"]

## Key Links
- Website: [URL]
- Docs: [URL]
- Pricing: [URL]

## Current Priorities (Update Weekly)
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]
```

**Example:**

```markdown
# CLAUDE.md

## Who I Am
- Name: Alex Johnson
- Role: Head of Growth at Acme AI
- Email: alex@acme.ai

## About Acme AI
Acme AI is a developer platform that makes it easy to build production AI applications.
We're one of the fastest-growing open-source projects in the AI space.

**Key facts:**
- 50M+ downloads, 15k+ GitHub stars
- Used by Fortune 500 companies and thousands of startups
- Key product: Acme Cloud with Enterprise API

## Our Positioning
- We are: The developer-first AI platform
- We are NOT: An "enterprise AI suite" (we're built for developers)
- Key differentiator: Best DX, fastest time to production

## My Communication Style
- Tone: Friendly, conversational, never corporate
- Sign-off: "Talk soon!"
- Always: CC Sam (founder) on important emails
- Often: Include a PS with a gesture (credits, resources)

## Key Links
- Website: https://acme.ai
- Docs: https://docs.acme.ai
- API Reference: https://docs.acme.ai/api

## Current Priorities
1. Drive Cloud signups from AI builders
2. Partner with AI consulting firms
3. Create content around our new features
```

---

## Step 3: Create GTM_CONTEXT.md

```markdown
# GTM Context

## Ideal Customer Profile (ICP)

### Primary ICP: AI Application Builders
- Building AI-powered applications
- Team size: 2-50 engineers
- Stage: Seed to Series B
- Tech stack: Python, modern AI frameworks

### Secondary ICP: AI Consulting Firms
- Building AI solutions for enterprise clients
- Need reliable infrastructure for client projects
- Value: partner program, credits for POCs

## Value Propositions

### For Developers
- "Ship AI features in minutes, not weeks"
- "The platform that just works"

### For Enterprises
- "Production-ready from day one"
- "SOC2 compliant, enterprise support"

## Competitors

| Competitor | Their Pitch | Our Counter |
|------------|-------------|-------------|
| Competitor A | "Enterprise AI platform" | We're developer-first, not enterprise-first |
| Competitor B | "Open-source alternative" | Better DX, faster time to production |
| Competitor C | "High-performance solution" | Full-stack platform, not just one feature |

## Objection Handling

**"Why not just use [alternative]?"**
> [Alternative] is great for simple use cases. We're purpose-built for 
> production AI with better defaults, easier scaling, and more features.

**"We're already using [competitor]"**
> Happy to show you a side-by-side. Many teams switch for our DX and 
> API. We can run in parallel during evaluation.
```

---

## Step 4: Create Outreach Templates

```markdown
# Outreach Templates

## Template: New Signup (Product-Led)

**Use when:** Someone signs up for the product

**Format:**
```
Hey [FirstName],

I'm [YourName]. I lead growth at [Company].

Saw you're trying out [Product] - welcome! Let me know if you have 
any questions or need more credits to test.

[Personalized line about their company]

Happy to hop on a call or set up a shared Slack channel.

Talk soon!

PS: [Gesture - e.g., "Bumped your credits to $X"]
```

## Template: Consulting Partner

**Use when:** The lead is from a consulting/agency firm

**Format:**
```
Hey [FirstName],

I'm [YourName]. I lead growth at [Company].

Saw you're trying out [Product] - welcome! Looks like you're building 
[AI/software] solutions for clients at [TheirCompany].

We work with a lot of consulting partners who use [Product] for client 
projects. Happy to set you up with:
- Extended credits for client POCs
- Direct Slack channel for technical support
- Early access to new features

Let me know if helpful!

Talk soon!

PS: What company are you building for? I can provide relevant case studies.
```

## Template: Enterprise Lead

**Use when:** Large company (1000+ employees)

**Format:**
```
Hey [FirstName],

I'm [YourName]. I lead growth at [Company].

Saw you're trying out [Product] - welcome! [TheirCompany] is a big name 
in [their industry] - excited to see what you're building.

Happy to set you up with:
- Extended credits to test at scale
- Direct Slack channel for technical support
- Call to discuss your use case

[Link to relevant resource]

Let me know if helpful!

Talk soon!
```
```

---

## Step 5: Create the GitHub Action

This is where the magic happens. Create `.github/workflows/claude-assistant.yml`:

```yaml
name: Claude GTM Assistant

on:
  issues:
    types: [opened]
  issue_comment:
    types: [created]

jobs:
  claude-assistant:
    # Only run if message contains @claude
    if: >-
      contains(github.event.issue.body, '@claude') ||
      contains(github.event.issue.title, '@claude') ||
      contains(github.event.comment.body, '@claude')
    
    runs-on: ubuntu-latest
    permissions:
      issues: write
      contents: read
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Load conversation history
        id: history
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            
            // Get all comments for conversation context
            const comments = await github.rest.issues.listComments({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              per_page: 20
            });
            
            // Build conversation history
            let history = [];
            
            // Add original issue
            const issue = context.payload.issue;
            history.push(`USER: ${issue.title}\n${issue.body || ''}`);
            
            // Add all comments
            for (const comment of comments.data) {
              if (comment.user.login === 'github-actions[bot]') {
                history.push(`ASSISTANT: ${comment.body}`);
              } else if (comment.body && comment.body.toLowerCase().includes('@claude')) {
                history.push(`USER: ${comment.body}`);
              }
            }
            
            // Save to file
            fs.writeFileSync('/tmp/conversation.txt', history.join('\n\n---\n\n'));
            console.log(`Loaded ${history.length} messages`);
            return history.length;
      
      - name: Parse query and detect intent
        id: parse
        env:
          ISSUE_TITLE: ${{ github.event.issue.title }}
          ISSUE_BODY: ${{ github.event.issue.body }}
          COMMENT_BODY: ${{ github.event.comment.body }}
          EVENT_NAME: ${{ github.event_name }}
        run: |
          # Get the query
          if [ "$EVENT_NAME" == "issue_comment" ]; then
            QUERY="$COMMENT_BODY"
            IS_FOLLOWUP="true"
          else
            QUERY="$ISSUE_TITLE $ISSUE_BODY"
            IS_FOLLOWUP="false"
          fi
          
          # Remove @claude from query
          QUERY=$(echo "$QUERY" | sed 's/@[Cc]laude//g' | xargs)
          echo "$QUERY" > /tmp/query.txt
          
          echo "is_followup=$IS_FOLLOWUP" >> $GITHUB_OUTPUT
          
          # Detect intent from keywords
          QUERY_LOWER=$(echo "$QUERY" | tr '[:upper:]' '[:lower:]')
          
          if [ "$IS_FOLLOWUP" == "true" ]; then
            MODE="followup"
          elif echo "$QUERY_LOWER" | grep -qE '^email' && echo "$QUERY" | grep -qE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'; then
            MODE="email"
            EMAIL=$(echo "$QUERY" | grep -oE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' | head -1)
            echo "target=$EMAIL" >> $GITHUB_OUTPUT
          elif echo "$QUERY_LOWER" | grep -qE '^research'; then
            MODE="research"
            TARGET=$(echo "$QUERY" | sed -E 's/^[Rr]esearch[[:space:]]*//')
            echo "target=$TARGET" >> $GITHUB_OUTPUT
          elif echo "$QUERY_LOWER" | grep -qE '^linkedin'; then
            MODE="linkedin"
            TARGET=$(echo "$QUERY" | sed -E 's/^[Ll]inkedin[[:space:]]*//')
            echo "target=$TARGET" >> $GITHUB_OUTPUT
          elif echo "$QUERY_LOWER" | grep -qE '^competitor'; then
            MODE="competitor"
            TARGET=$(echo "$QUERY" | sed -E 's/^[Cc]ompetitor[s]?[[:space:]]*//')
            echo "target=$TARGET" >> $GITHUB_OUTPUT
          else
            MODE="general"
            echo "target=" >> $GITHUB_OUTPUT
          fi
          
          echo "mode=$MODE" >> $GITHUB_OUTPUT
          echo "Detected mode: $MODE"
      
      - name: Load context files
        run: |
          # Load all context into one file
          touch /tmp/context.txt
          
          # Core context
          cat CLAUDE.md >> /tmp/context.txt 2>/dev/null || true
          echo -e "\n---\n" >> /tmp/context.txt
          cat context/GTM_CONTEXT.md >> /tmp/context.txt 2>/dev/null || true
          echo -e "\n---\n" >> /tmp/context.txt
          cat context/COMPETITORS.md >> /tmp/context.txt 2>/dev/null || true
          echo -e "\n---\n" >> /tmp/context.txt
          cat context/OUTREACH_TEMPLATES.md >> /tmp/context.txt 2>/dev/null || true
          
          # Truncate to stay within limits
          head -c 50000 /tmp/context.txt > /tmp/context_final.txt
          echo "Context loaded: $(wc -c < /tmp/context_final.txt) bytes"
      
      - name: Build prompt
        env:
          MODE: ${{ steps.parse.outputs.mode }}
          TARGET: ${{ steps.parse.outputs.target }}
        run: |
          QUERY=$(cat /tmp/query.txt)
          CONVERSATION=$(cat /tmp/conversation.txt 2>/dev/null || echo "")
          
          case "$MODE" in
            followup)
              cat > /tmp/prompt.txt << EOF
          CONVERSATION HISTORY:
          $CONVERSATION

          ---

          NEW REQUEST: $QUERY

          Respond to the user's request. If they're asking to modify something 
          (like an email draft), provide the full updated version.
          EOF
              ;;
            
            email)
              NAME=$(echo "$TARGET" | sed 's/@.*//' | sed 's/[._]/ /g')
              DOMAIN=$(echo "$TARGET" | sed 's/.*@//')
              FIRST_NAME=$(echo "$NAME" | awk '{print $1}')
              
              cat > /tmp/prompt.txt << EOF
          Draft an outreach email to: $TARGET

          RECIPIENT INFO:
          - Email: $TARGET
          - First name: $FIRST_NAME  
          - Company domain: $DOMAIN

          INSTRUCTIONS:
          1. First, research what $DOMAIN company does (2-3 sentences)
          2. Determine if they're: startup, enterprise, or consulting/agency
          3. Use the appropriate template from OUTREACH_TEMPLATES
          4. Personalize with something specific about their company
          5. Keep it under 150 words

          FORMAT YOUR RESPONSE AS:

          ## About $DOMAIN
          [2-3 sentences about what they do]

          ## Email Draft
          \`\`\`
          Subject: [subject line]

          Hey $FIRST_NAME,

          [email body following the template]

          [sign off]

          PS: [optional gesture]
          \`\`\`
          EOF
              ;;
            
            research)
              cat > /tmp/prompt.txt << EOF
          Research "$TARGET" as a potential customer/partner.

          Provide:

          ## Company Overview
          What they do, size, funding stage, key products

          ## AI/Tech Relevance  
          Their AI products, use cases, tech stack if known

          ## Fit Score (1-5)
          How well they match our ICP, with reasoning

          ## Outreach Angle
          Best positioning, pain points to address, who to contact

          ## Risks
          Any concerns or red flags
          EOF
              ;;
            
            linkedin)
              cat > /tmp/prompt.txt << EOF
          Draft a LinkedIn post about: $TARGET

          STYLE:
          - Conversational, like talking to a smart friend
          - Share genuine insights, not corporate speak
          - Use short sentences and line breaks
          - Be specific with numbers and examples
          - End with a question that sparks discussion

          RULES:
          - Under 1300 characters
          - Strong hook in first line
          - Write in first person

          FORMAT:

          ## Post
          [ready to copy/paste]

          ## Alternative Hooks
          [3 alternatives]

          ## Hashtags
          [5-7 relevant hashtags]
          EOF
              ;;
            
            competitor)
              cat > /tmp/prompt.txt << EOF
          Competitor question: $TARGET

          Using the COMPETITORS context, provide:
          - Specific, actionable insights
          - Our positioning vs this competitor
          - Recommended talking points
          - What to avoid saying
          EOF
              ;;
            
            *)
              cat > /tmp/prompt.txt << EOF
          $QUERY

          Answer based on the GTM context provided. Be specific and actionable.
          Write like a helpful colleague, not a formal assistant.
          EOF
              ;;
          esac
      
      - name: Call Claude API
        id: api
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          # Check API key
          if [ -z "$ANTHROPIC_API_KEY" ]; then
            echo "Error: ANTHROPIC_API_KEY not set" > /tmp/response.txt
            exit 0
          fi
          
          # Prepare JSON-safe strings
          CONTEXT=$(cat /tmp/context_final.txt | jq -Rs .)
          PROMPT=$(cat /tmp/prompt.txt | jq -Rs .)
          
          # System message
          SYSTEM="You are a GTM assistant. You have access to context about the company, 
          strategy, competitors, and outreach templates. Use this context to provide 
          helpful, specific, actionable responses. Match the communication style described 
          in CLAUDE.md. Be concise and practical."
          SYSTEM_JSON=$(echo "$SYSTEM" | jq -Rs .)
          
          # Call Claude API
          HTTP_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST https://api.anthropic.com/v1/messages \
            -H "Content-Type: application/json" \
            -H "x-api-key: $ANTHROPIC_API_KEY" \
            -H "anthropic-version: 2023-06-01" \
            -d "{
              \"model\": \"claude-sonnet-4-20250514\",
              \"max_tokens\": 2048,
              \"system\": $SYSTEM_JSON,
              \"messages\": [{
                \"role\": \"user\", 
                \"content\": \"CONTEXT:\\n\" + $CONTEXT + \"\\n\\nREQUEST:\\n\" + $PROMPT
              }]
            }")
          
          # Parse response
          HTTP_BODY=$(echo "$HTTP_RESPONSE" | sed '$d')
          HTTP_STATUS=$(echo "$HTTP_RESPONSE" | tail -n1)
          
          if [ "$HTTP_STATUS" != "200" ]; then
            ERROR_MSG=$(echo "$HTTP_BODY" | jq -r '.error.message // "API error"')
            echo "Error: $ERROR_MSG (HTTP $HTTP_STATUS)" > /tmp/response.txt
          else
            echo "$HTTP_BODY" | jq -r '.content[0].text // "No response"' > /tmp/response.txt
          fi
      
      - name: Post response as comment
        uses: actions/github-script@v7
        env:
          MODE: ${{ steps.parse.outputs.mode }}
        with:
          script: |
            const fs = require('fs');
            const response = fs.readFileSync('/tmp/response.txt', 'utf8');
            const mode = process.env.MODE;
            
            const emoji = {
              email: '📧', research: '🔍', linkedin: '📱',
              competitor: '⚔️', general: '🤖', followup: '💬'
            }[mode] || '🤖';
            
            const label = {
              email: 'Email Draft', research: 'Company Research', 
              linkedin: 'LinkedIn Post', competitor: 'Competitor Intel',
              general: 'Response', followup: 'Updated'
            }[mode] || 'Response';
            
            const body = [
              `## ${emoji} ${label}`,
              '',
              response,
              '',
              '---',
              '<sub>💬 Reply with `@claude` to continue the conversation</sub>'
            ].join('\n');
            
            await github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
      
      - name: Handle errors
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '## ⚠️ Error\n\nSomething went wrong. Check the [workflow logs](' + 
                    context.serverUrl + '/' + context.repo.owner + '/' + context.repo.repo + 
                    '/actions) for details.'
            });
```

---

## Step 6: Create the Issue Template

Create `.github/ISSUE_TEMPLATE/ask-claude.yml`:

```yaml
name: Ask Claude
description: Ask Claude anything about GTM
title: "@claude "
labels: ["claude"]
body:
  - type: markdown
    attributes:
      value: |
        ## Ask Claude
        
        Just type your request after `@claude` in the title. Examples:
        
        - `@claude email john@company.com`
        - `@claude research Acme Corp`
        - `@claude linkedin post about AI trends`
        - `@claude how should I position against Competitor X?`
```

Create `.github/ISSUE_TEMPLATE/config.yml`:

```yaml
blank_issues_enabled: true
contact_links: []
```

---

## Step 7: Set Up the API Key

1. Go to your GitHub repository
2. Navigate to **Settings → Secrets and variables → Actions**
3. Click **New repository secret**
4. Name: `ANTHROPIC_API_KEY`
5. Value: Your Claude API key from [console.anthropic.com](https://console.anthropic.com)

---

## Step 8: Test It!

### Test 1: General Question

Create a new issue with title:
```
@claude what's our main differentiator vs Competitor A?
```

### Test 2: Email Draft

Create a new issue with title:
```
@claude email sarah@acme.ai
```

### Test 3: Research

Create a new issue with title:
```
@claude research OpenAI
```

### Test 4: Follow-up

Reply to any Claude response with:
```
@claude make it shorter
```

---

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                        WORKFLOW                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. You create GitHub Issue: "@claude email john@startup.ai"    │
│                           │                                      │
│                           ▼                                      │
│  2. GitHub Action triggers                                       │
│                           │                                      │
│                           ▼                                      │
│  3. Action loads context files (CLAUDE.md, GTM_CONTEXT, etc.)   │
│                           │                                      │
│                           ▼                                      │
│  4. Action detects intent: "email" mode                         │
│                           │                                      │
│                           ▼                                      │
│  5. Action builds prompt with context + template                │
│                           │                                      │
│                           ▼                                      │
│  6. Action calls Claude API                                      │
│                           │                                      │
│                           ▼                                      │
│  7. Claude researches company, drafts personalized email        │
│                           │                                      │
│                           ▼                                      │
│  8. Action posts response as issue comment                      │
│                           │                                      │
│                           ▼                                      │
│  9. You reply "@claude make it shorter" → conversation continues│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Advanced: Adding More Capabilities

### Add Meeting Summary Mode

Add to the intent detection:

```bash
elif echo "$QUERY_LOWER" | grep -qE '^meeting'; then
  MODE="meeting"
  TARGET=$(echo "$QUERY" | sed -E 's/^[Mm]eeting[[:space:]]*//')
  echo "target=$TARGET" >> $GITHUB_OUTPUT
```

Add to the prompt building:

```bash
meeting)
  cat > /tmp/prompt.txt << EOF
Summarize this meeting: $TARGET

$QUERY

Provide:
## Key Decisions
## Action Items  
## Follow-ups Needed
EOF
  ;;
```

### Add Web Search (via Firecrawl MCP)

If you have Firecrawl set up, Claude can research companies in real-time before drafting emails.

---

## Supercharging with External APIs

The GitHub Action is just the interface. The real power comes from connecting external APIs that do the heavy lifting. Here's how I integrate multiple APIs to create a complete GTM system.

### The API Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      API INTEGRATION LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │  PARALLEL API    │    │  FIRECRAWL API   │                   │
│  │  (Enrichment)    │    │  (Web Scraping)  │                   │
│  │                  │    │                  │                   │
│  │  • FindAll leads │    │  • Scrape sites  │                   │
│  │  • Company data  │    │  • Extract data  │                   │
│  │  • Market intel  │    │  • Search web    │                   │
│  └────────┬─────────┘    └────────┬─────────┘                   │
│           │                       │                              │
│           └───────────┬───────────┘                              │
│                       │                                          │
│                       ▼                                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    CLAUDE API                            │    │
│  │                                                          │    │
│  │   Orchestrates all APIs, generates content, makes        │    │
│  │   decisions based on enriched data                       │    │
│  │                                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                       │                                          │
│           ┌───────────┴───────────┐                              │
│           │                       │                              │
│           ▼                       ▼                              │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │  HUBSPOT API     │    │  SLACK API       │                   │
│  │  (CRM Sync)      │    │  (Notifications) │                   │
│  │                  │    │                  │                   │
│  │  • Sync contacts │    │  • Lead alerts   │                   │
│  │  • Update deals  │    │  • Daily digest  │                   │
│  │  • Track status  │    │  • Team updates  │                   │
│  └──────────────────┘    └──────────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Step 1: Set Up Your Environment File

Create a `.env` file to store all your API keys securely:

```bash
# .env - Store your API keys here (add to .gitignore!)

# ===========================================
# Core AI APIs
# ===========================================
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-openai-key-here

# ===========================================
# Lead Discovery & Enrichment
# ===========================================
# Parallel.ai - Web-scale entity discovery
PARALLEL_API_KEY=your-parallel-api-key

# Firecrawl - Web scraping and search
FIRECRAWL_API_KEY=fc-your-firecrawl-key

# ===========================================
# CRM & Notifications
# ===========================================
HUBSPOT_API_KEY=pat-your-hubspot-key
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/xxx/xxx
```

Add to `.gitignore`:
```
.env
*.pickle
credentials.json
```

### Step 2: Parallel API for Lead Discovery

[Parallel.ai](https://parallel.ai) is a game-changer for GTM. It turns natural language queries into structured databases of companies.

**What it does:**
- "FindAll AI startups in San Francisco" → Returns 100+ companies with URLs, descriptions, funding data
- "FindAll companies using vector databases" → Returns potential customers
- "FindAll consulting firms building AI solutions" → Returns partner leads

**Create `parallel_client.py`:**

```python
"""
Parallel FindAll API - Web-scale lead discovery
Docs: https://docs.parallel.ai/findall-api/findall-quickstart
"""

import os
import time
import requests
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.parallel.ai/v1beta/findall"

@dataclass
class Lead:
    """A discovered company/lead."""
    name: str
    url: str
    description: str
    match_status: str
    data: Dict[str, Any]

class ParallelClient:
    def __init__(self):
        self.api_key = os.getenv("PARALLEL_API_KEY")
        if not self.api_key:
            raise ValueError("PARALLEL_API_KEY not set in .env")
        
        self.headers = {
            "x-api-key": self.api_key,
            "parallel-beta": "findall-2025-09-15",
            "Content-Type": "application/json"
        }
    
    def find_leads(
        self, 
        query: str, 
        limit: int = 20,
        verbose: bool = True
    ) -> List[Lead]:
        """
        Find companies matching a natural language query.
        
        Examples:
            "FindAll AI startups that raised Series A in 2024"
            "FindAll companies building with LangChain or LlamaIndex"
            "FindAll consulting firms specializing in AI implementation"
        """
        # Step 1: Parse the query into structured schema
        schema = requests.post(
            f"{BASE_URL}/ingest",
            headers=self.headers,
            json={"objective": query}
        ).json()
        
        if verbose:
            print(f"🔍 Searching for: {schema['entity_type']}")
            for mc in schema['match_conditions']:
                print(f"   ✓ {mc['name']}")
        
        # Step 2: Start the search
        run_id = requests.post(
            f"{BASE_URL}/runs",
            headers=self.headers,
            json={
                "objective": schema["objective"],
                "entity_type": schema["entity_type"],
                "match_conditions": schema["match_conditions"],
                "generator": "core",
                "match_limit": limit
            }
        ).json()["findall_id"]
        
        if verbose:
            print(f"⏳ Running search: {run_id}")
        
        # Step 3: Wait for completion
        while True:
            status = requests.get(
                f"{BASE_URL}/runs/{run_id}",
                headers=self.headers
            ).json()
            
            if not status["status"]["is_active"]:
                break
            
            metrics = status["status"].get("metrics", {})
            if verbose:
                print(f"   Found: {metrics.get('matched_candidates_count', 0)} matches")
            time.sleep(5)
        
        # Step 4: Get results
        results = requests.get(
            f"{BASE_URL}/runs/{run_id}/result",
            headers=self.headers
        ).json()
        
        leads = [
            Lead(
                name=c["name"],
                url=c["url"],
                description=c["description"],
                match_status=c["match_status"],
                data=c.get("output", {})
            )
            for c in results.get("candidates", [])
        ]
        
        if verbose:
            print(f"✅ Found {len(leads)} leads")
        
        return leads


# Example usage
if __name__ == "__main__":
    client = ParallelClient()
    
    # Find potential customers
    leads = client.find_leads(
        "FindAll companies building AI applications with RAG or semantic search",
        limit=20
    )
    
    for lead in leads:
        print(f"\n{lead.name}")
        print(f"  URL: {lead.url}")
        print(f"  {lead.description[:100]}...")
```

### Step 3: Firecrawl for Web Research

[Firecrawl](https://firecrawl.dev) lets you scrape and search the web programmatically. I use it to research companies before drafting emails.

**What it does:**
- Scrape any website and get clean markdown
- Search the web and get results with content
- Extract structured data from pages

**Create `firecrawl_client.py`:**

```python
"""
Firecrawl API - Web scraping and search
Docs: https://docs.firecrawl.dev
"""

import os
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class FirecrawlClient:
    def __init__(self):
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise ValueError("FIRECRAWL_API_KEY not set in .env")
        
        self.base_url = "https://api.firecrawl.dev/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def scrape(self, url: str) -> Dict:
        """
        Scrape a URL and return clean markdown content.
        
        Perfect for:
        - Company websites before outreach
        - Product pages for competitive analysis
        - Blog posts for content research
        """
        response = requests.post(
            f"{self.base_url}/scrape",
            headers=self.headers,
            json={
                "url": url,
                "formats": ["markdown"],
                "onlyMainContent": True
            }
        )
        response.raise_for_status()
        return response.json()
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search the web and optionally scrape results.
        
        Perfect for:
        - "What does [company] do?"
        - "Who are [company]'s competitors?"
        - "[company] AI products"
        """
        response = requests.post(
            f"{self.base_url}/search",
            headers=self.headers,
            json={
                "query": query,
                "limit": limit
            }
        )
        response.raise_for_status()
        return response.json().get("data", [])
    
    def research_company(self, company_name: str) -> str:
        """
        Research a company and return a summary.
        Combines search + scrape for comprehensive info.
        """
        # Search for the company
        results = self.search(f"{company_name} company", limit=3)
        
        if not results:
            return f"No information found for {company_name}"
        
        # Get the main website content
        main_url = results[0].get("url", "")
        
        summary = f"## {company_name}\n\n"
        summary += f"**Website:** {main_url}\n\n"
        
        # Add search result snippets
        for result in results:
            if result.get("description"):
                summary += f"- {result['description']}\n"
        
        return summary


# Example usage
if __name__ == "__main__":
    client = FirecrawlClient()
    
    # Research a company before outreach
    info = client.research_company("Stripe")
    print(info)
    
    # Scrape a specific page
    page = client.scrape("https://stripe.com/about")
    print(page.get("data", {}).get("markdown", "")[:500])
```

### Step 4: Combining APIs in Your Workflow

Here's how I combine all APIs for a complete lead-to-outreach workflow:

**Create `gtm_workflow.py`:**

```python
"""
Complete GTM Workflow - From lead discovery to personalized outreach
"""

import os
import json
from anthropic import Anthropic
from parallel_client import ParallelClient
from firecrawl_client import FirecrawlClient
from dotenv import load_dotenv

load_dotenv()

class GTMWorkflow:
    def __init__(self):
        self.parallel = ParallelClient()
        self.firecrawl = FirecrawlClient()
        self.claude = Anthropic()
        
        # Load your context
        with open("CLAUDE.md", "r") as f:
            self.context = f.read()
    
    def discover_leads(self, query: str, limit: int = 20):
        """Step 1: Find companies matching your ICP."""
        print("🔍 Discovering leads...")
        return self.parallel.find_leads(query, limit=limit)
    
    def research_lead(self, lead):
        """Step 2: Deep research on a specific lead."""
        print(f"📚 Researching {lead.name}...")
        return self.firecrawl.research_company(lead.name)
    
    def draft_email(self, lead, research: str) -> str:
        """Step 3: Draft personalized outreach."""
        print(f"✍️  Drafting email for {lead.name}...")
        
        prompt = f"""
        Based on this context about my company:
        {self.context}
        
        And this research about the prospect:
        {research}
        
        Draft a personalized outreach email to {lead.name}.
        Keep it under 150 words, friendly, and offer specific value.
        """
        
        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def run_pipeline(self, query: str, limit: int = 5):
        """Run the complete pipeline."""
        
        # 1. Discover leads
        leads = self.discover_leads(query, limit=limit)
        
        results = []
        for lead in leads:
            # 2. Research each lead
            research = self.research_lead(lead)
            
            # 3. Draft personalized email
            email = self.draft_email(lead, research)
            
            results.append({
                "company": lead.name,
                "url": lead.url,
                "research": research,
                "email_draft": email
            })
            
            print(f"✅ Completed: {lead.name}")
        
        # Save results
        with open("outreach_drafts.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n🎉 Generated {len(results)} personalized outreach emails!")
        return results


# Example usage
if __name__ == "__main__":
    workflow = GTMWorkflow()
    
    # Find and reach out to AI startups
    results = workflow.run_pipeline(
        "FindAll AI startups building developer tools that raised seed funding",
        limit=5
    )
    
    # Preview first email
    if results:
        print("\n" + "="*60)
        print("SAMPLE EMAIL DRAFT")
        print("="*60)
        print(f"\nTo: {results[0]['company']}")
        print(results[0]['email_draft'])
```

### Step 5: Folder Structure for API Management

Keep your API integrations organized:

```
ai-gtm-system/
├── CLAUDE.md                    # AI context
├── .env                         # API keys (gitignored!)
├── .env.example                 # Template for team
├── context/
│   └── GTM_CONTEXT.md
├── clients/                     # API client wrappers
│   ├── __init__.py
│   ├── parallel_client.py       # Parallel FindAll
│   ├── firecrawl_client.py      # Web scraping
│   ├── hubspot_client.py        # CRM sync
│   └── slack_client.py          # Notifications
├── workflows/                   # Combined workflows
│   ├── lead_discovery.py        # Find new leads
│   ├── lead_enrichment.py       # Research leads
│   ├── outreach_generator.py    # Draft emails
│   └── crm_sync.py              # Sync to HubSpot
├── .github/
│   └── workflows/
│       └── claude-assistant.yml
└── outputs/                     # Generated content
    ├── leads/
    ├── emails/
    └── reports/
```

### The Power of API Composition

The magic happens when you compose these APIs:

| API | What It Does | GTM Use Case |
|-----|--------------|--------------|
| **Parallel** | Web-scale entity discovery | "Find 100 AI startups in SF" |
| **Firecrawl** | Scrape & search web | Research before outreach |
| **Claude** | Generate content | Draft personalized emails |
| **HubSpot** | CRM management | Track leads & deals |
| **Slack** | Notifications | Alert on hot leads |

**Example workflow:**

```
1. Parallel: "FindAll companies hiring AI engineers"
        ↓
2. Firecrawl: Scrape each company's careers page
        ↓
3. Claude: "Which of these are good fits for our product?"
        ↓
4. Claude: Draft personalized emails for top 10
        ↓
5. HubSpot: Create contacts & deals
        ↓
6. Slack: "🔥 10 new qualified leads ready for outreach"
```

This is how a single person can do the work of a 10-person SDR team.

---

## Building Institutional Memory with Meeting Notes

Most knowledge workers have the same problem: insights from meetings evaporate within days. You have a great call with a partner, learn exactly how to position your product, then six weeks later you're starting from scratch with a similar prospect.

This system fixes that. Every meeting becomes searchable context that compounds over time.

### The Problem It Solves

Think about how much gets lost:

- That positioning angle that resonated perfectly with the enterprise prospect
- The objection a customer raised that you handled well
- The competitive intel a partner shared about a rival's pricing
- The decision you made about targeting a new segment

Without a system, you're relying on memory. With this system, Claude has access to every insight from every meeting you've ever had.

### How It Works

**1. Record everything**

Use Fathom, Otter, Fireflies, or any transcription tool. The key is having a text transcript.

**2. Extract structured notes**

After each meeting, paste the transcript into Claude with a standard extraction prompt. Claude outputs clean, structured markdown.

**3. Index for retrieval**

Save notes to a consistent location. Update a master index with key insights organized by theme.

**4. Query across all meetings**

Now you can ask: "What positioning has resonated with enterprise prospects?" and get synthesized insights from dozens of conversations.

### The Folder Structure

```
meetings/
├── EXTRACTION_PROMPT.md        # The prompt you use to extract notes
└── notes/
    ├── _TEMPLATE.md            # Consistent structure for all notes
    ├── 2026-01-09_partner-call.md
    ├── 2026-01-08_vendor-eval.md
    └── 2026-01-06_strategy-session.md
```

### The Master Index

The magic is in `context/MEETING_INDEX.md` - a living document that grows with every meeting:

```markdown
# Meeting Index

## All Meetings

| Date | Title | Type | Participants | Link |
|------|-------|------|--------------|------|
| 2026-01-09 | Partner GTM Call | Partner | Alex, Sam | [notes](../meetings/notes/2026-01-09_partner.md) |
| 2026-01-08 | Vendor Evaluation | Vendor | Team | [notes](../meetings/notes/2026-01-08_vendor.md) |
| 2026-01-06 | Strategy Session | Internal | Team | [notes](../meetings/notes/2026-01-06_strategy.md) |

## Key Insights by Theme

### Positioning
- **Jan 9**: "Sell the architecture, not just the product" - resonated with partner
- **Jan 6**: "Better accuracy = lower costs = faster results" - use this framing

### Objections Heard
- **Jan 8**: "We're already using [Competitor]" - counter with migration support
- **Jan 6**: "Seems expensive" - emphasize ROI and free tier

### Competitive Intel
- **Jan 8**: Competitor X is strong in segment Y, weak in Z
- **Jan 6**: Competitor Y raised prices 40% - opportunity

### Decisions Made
| Date | Decision | Rationale |
|------|----------|-----------|
| Jan 9 | Hire fractional CMO | Need help with positioning |
| Jan 6 | Focus on enterprise | PLG caps at $1-2M ARR |

### Open Action Items
- [ ] Build Q1 revenue plan
- [ ] Launch outreach campaign
- [ ] Fix CRM tracking
```

### The Note Template

Every meeting note follows the same structure. Consistency is what makes retrieval work:

```markdown
# Meeting: [Title]

**Date**: YYYY-MM-DD  
**Type**: Customer / Partner / Internal / Vendor  
**Participants**: [Names]

## Summary
[2-3 sentences - what was this meeting about?]

## Key Points
1. **[Topic]**: [What was discussed, what was concluded]
2. **[Topic]**: [What was discussed, what was concluded]

## Decisions
- [Decision 1]
- [Decision 2]

## Action Items
- [ ] [Owner]: [Task] - Due: [Date]

## Insights

**What resonated**:
- [Messaging or positioning that worked]

**Objections raised**:
- [Concerns or pushback]

**Competitive mentions**:
- [What was said about competitors]

## Follow-up
- Next meeting: [Date]
- Open questions: [List]
```

### The Extraction Prompt

After every meeting, use this prompt with the transcript:

```
Extract structured meeting notes from this transcript.

[PASTE TRANSCRIPT]

Output:
1. Summary (2-3 sentences)
2. Key discussion points (top 3-5)
3. Decisions made
4. Action items (who, what, when)
5. Insights:
   - What messaging/positioning resonated
   - Objections or concerns raised
   - Competitive mentions
   - Market observations
6. Follow-up needed

Format as clean markdown.
```

### Why This Compounds

**Week 1**: You have notes from 3 meetings.

**Week 4**: You have notes from 12 meetings. Patterns emerge. You notice the same objection coming up repeatedly.

**Week 12**: You have notes from 40+ meetings. Claude can now synthesize:
- "Based on your meetings, enterprise prospects respond best to [X] positioning"
- "The most common objection is [Y] - here's how you've handled it successfully"
- "Competitor Z has been mentioned 8 times - here's what prospects say about them"

### Real Examples

**Before an important call:**
```
@claude I have a call with an enterprise prospect tomorrow. 
Based on my recent meetings, what positioning has worked best 
with similar companies? What objections should I prepare for?
```

**When drafting outreach:**
```
@claude Draft an email to a consulting partner. Use insights 
from my partner meetings about what resonates with agencies.
```

**During planning:**
```
@claude What are the open action items from the last month 
of meetings? Which ones are overdue?
```

### The 5-Minute Post-Meeting Workflow

```
1. Meeting ends
   ↓
2. Open transcript (Fathom/Otter auto-generates)
   ↓
3. Paste into Claude with extraction prompt
   ↓
4. Save output to meetings/notes/YYYY-MM-DD_topic.md
   ↓
5. Add row to MEETING_INDEX.md
   ↓
6. If major insight: add to "Key Insights by Theme"
```

Total time: 5 minutes. Value: permanent, searchable institutional memory.

### The Payoff

Six months in, you have:
- A searchable database of every conversation
- Patterns visible across dozens of meetings
- An AI that knows your positioning history, common objections, and competitive landscape
- Onboarding material for new team members (they can read the index and get up to speed in an hour)

**This is how individual knowledge becomes organizational knowledge.**

---

## The Key Insight

> **The magic isn't Claude's intelligence. It's the context you give it.**

Without context, Claude writes generic responses. With your CLAUDE.md, GTM_CONTEXT.md, and templates, Claude writes **in your voice** with **your strategy** for **your specific use case**.

Every time you update these context files, every future response gets better.

---

## What's Next?

1. **Start simple** - Create CLAUDE.md and test basic queries
2. **Add context** - Build out GTM_CONTEXT and templates
3. **Iterate** - Every good prompt becomes a recipe you can reuse
4. **Expand** - Add more modes, connect more tools

---

## Resources

- [Claude API Documentation](https://docs.anthropic.com)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Example Repository](https://github.com/your-repo/ai-gtm-system)

---

*Built by [Your Name] at [Company]. Questions? Reach out at [email].*
