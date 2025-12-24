# 🚀 LinkedIn Sales Navigator Company Automation Guide

## Overview

This automation helps you add **140+ verified companies** from your research pipeline to LinkedIn Sales Navigator. Since Sales Navigator solo accounts don't support bulk import, this script automates the process through browser automation.

---

## Quick Start

### Step 1: Install Dependencies

```bash
cd "/Users/ankitpansari/Desktop/Chroma GTM"

# Install Playwright
pip install playwright

# Install browser (Chromium)
playwright install chromium
```

### Step 2: View Companies to Add

```bash
python linkedin_sales_nav_automation.py --list-companies
```

This shows all 140+ companies organized by category with their priority levels.

### Step 3: Run the Automation

```bash
# Start with HIGH priority companies only (recommended first run)
python linkedin_sales_nav_automation.py --priority HIGH --limit 10

# Or run all HIGH priority companies
python linkedin_sales_nav_automation.py --priority HIGH

# Or run all companies
python linkedin_sales_nav_automation.py
```

### Step 4: Login When Prompted

1. A browser window will open
2. Navigate to LinkedIn and log in to Sales Navigator manually
3. The script will detect your login and continue automatically

---

## Command Options

| Option | Description | Example |
|--------|-------------|---------|
| `--limit N` | Process only N companies | `--limit 10` |
| `--priority` | Filter by priority level | `--priority HIGH MEDIUM-HIGH` |
| `--headless` | Run without visible browser (not recommended) | `--headless` |
| `--no-resume` | Start fresh, ignore previous progress | `--no-resume` |
| `--list-companies` | List all companies and exit | `--list-companies` |

---

## Priority Levels

Companies are categorized by priority based on:
- Funding activity and growth signals
- Explicit research needs
- Buy propensity

| Priority | Count | Description |
|----------|-------|-------------|
| **HIGH** | ~50 | Best fit, highest value targets |
| **MEDIUM-HIGH** | ~25 | Strong fit, good opportunities |
| **MEDIUM** | ~45 | Moderate fit |
| **MEDIUM-LOW** | ~15 | Lower priority |
| **LOW** | ~10 | Competitors or low fit |

---

## Company Categories

The 140+ companies span 15 categories:

1. **Documentation Platforms** (9 companies) - Mintlify, GitBook, ReadMe...
2. **Developer Tools** (12 companies) - Cursor, Cognition, Replit...
3. **Legal Tech** (13 companies) - Harvey AI, Clio, Spellbook...
4. **Sales Intelligence** (18 companies) - Clay, Apollo.io, Gong...
5. **Customer Support AI** (12 companies) - Sierra AI, Decagon, Ada...
6. **Knowledge Management** (12 companies) - Guru, Notion, Tettra...
7. **Enterprise Search** (7 companies) - Glean, Coveo, Algolia...
8. **Financial Research** (11 companies) - AlphaSense, Daloopa, YipitData...
9. **Healthcare AI** (12 companies) - Hippocratic AI, Abridge, Viz.ai...
10. **Research Tools** (9 companies) - Elicit, Semantic Scholar, Scite...
11. **AI Agents** (13 companies) - n8n, Lindy.ai, Zapier...
12. **Content AI** (12 companies) - Writer, Copy.ai, Jasper...
13. **Procurement** (5 companies) - Zip, Ramp, Brex...
14. **Real Estate Tech** (4 companies) - Placer.ai, Cherre, Crexi...
15. **HR Tech** (11 companies) - Eightfold AI, Paradox, Beamery...

---

## How It Works

1. **Search**: For each company, searches Sales Navigator's company search
2. **Match**: Finds the company profile from search results
3. **Save**: Clicks the "Save" button to add to your saved accounts
4. **Track**: Logs progress and saves results to JSON

### Files Created

| File | Purpose |
|------|---------|
| `linkedin_automation_results.json` | Results with LinkedIn URLs and status |
| `linkedin_automation_state.json` | Progress state for resume capability |
| `linkedin_automation.log` | Detailed execution log |

---

## Resume Capability

The script automatically saves progress. If interrupted:

```bash
# Resume from where you left off
python linkedin_sales_nav_automation.py --priority HIGH

# Or start fresh
python linkedin_sales_nav_automation.py --priority HIGH --no-resume
```

---

## Rate Limiting & Safety

The automation includes several safety features:

- **Random delays** between actions (1-7 seconds)
- **Human-like behavior** with variable timing
- **Persistent browser profile** to maintain login state
- **Progress saving** to handle interruptions

### Recommended Approach

1. **Start slow**: Process 10-20 companies per session
2. **Take breaks**: Don't run continuously for hours
3. **Monitor**: Watch the browser to ensure it's working correctly
4. **Review results**: Check `linkedin_automation_results.json` after each run

---

## Troubleshooting

### "Playwright not installed"
```bash
pip install playwright
playwright install chromium
```

### "Login not detected"
- Make sure you're fully logged into Sales Navigator
- The script looks for the Sales Navigator navigation bar
- Try refreshing the page after login

### "Company not found"
Some companies may have different LinkedIn names. Check `linkedin_automation_results.json` for companies with `"status": "not_found"`.

### "Rate limited by LinkedIn"
- Stop the script immediately
- Wait 24-48 hours before resuming
- Consider processing fewer companies per session

---

## Top 25 Priority Targets

Based on the research, these are the highest-value companies to add first:

| Rank | Company | Category | Valuation |
|------|---------|----------|-----------|
| 1 | Sierra AI | Customer Support | $10B |
| 2 | Clay | Sales Intelligence | $3.1B |
| 3 | Cursor | Developer Tools | $29.3B |
| 4 | n8n | AI Agents | $2.5B |
| 5 | Abridge | Healthcare | $5.3B |
| 6 | Decagon | Customer Support | $1.5B |
| 7 | Harvey AI | Legal Tech | $8B |
| 8 | Ramp | Procurement | $22.5B |
| 9 | Zip | Procurement | $2.2B |
| 10 | Writer | Content AI | $1.9B |
| 11 | Hippocratic AI | Healthcare | $3.5B |
| 12 | Mintlify | Documentation | ~$100M |
| 13 | AlphaSense | Financial | $4B |
| 14 | Apollo.io | Sales Intelligence | $1.6B |
| 15 | Relevance AI | AI Agents | ~$150M |

---

## Alternative: Manual Process

If you prefer not to use automation:

1. Open `linkedin_automation_results.json` or run `--list-companies`
2. Search each company manually in Sales Navigator
3. Click "Save" to add to your saved accounts

The company list is also available in the Python script under `COMPANIES_DATA`.

---

## Support

Check the log file for detailed error messages:
```bash
tail -f linkedin_automation.log
```

Review results:
```bash
cat linkedin_automation_results.json | python -m json.tool
```

