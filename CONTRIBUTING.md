# Contributing to Chroma Signal

Guidelines for keeping this repository organized and synced.

---

## 📁 File Organization

### Where to Put Things

| Type | Location | Example |
|------|----------|---------|
| **Strategy docs** | `context/` | `GTM_CONTEXT.md`, `GTM_TASKS.md` |
| **Scripts** | Root or `src/` | `chroma_signal_list.py` |
| **Diagrams/SVGs** | `diagrams/` | `chroma-solution-architectures.svg` |
| **Company data** | Root (with LFS) | `*_COMPANIES_FINAL.json` |
| **LinkedIn docs** | Root | `LINKEDIN_*.md` |
| **HubSpot scripts** | Root | `hubspot_*.py`, `sync_*_to_hubspot.py` |
| **Customer call templates** | `customer-calls/templates/` | `_CALL_TEMPLATE.md` |
| **Customer call playbooks** | `customer-calls/playbooks/` | `DISCOVERY_QUESTIONS.md` |

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| **Scripts** | `snake_case.py` | `sync_companies_to_hubspot.py` |
| **Docs** | `UPPER_SNAKE_CASE.md` | `EXECUTIVE_SUMMARY_GTM.md` |
| **Data files** | `snake_case.json/csv` | `chroma_signal_companies.json` |
| **Diagrams** | `YYYY-MM-DD_description.svg` or `snake_case.svg` | `2026-01-09_chroma-solution-architectures.svg` |

---

## 🔄 Syncing with GitHub

### Quick Sync (Daily)

Run this command to sync your changes:

```bash
# From the project root
./sync.sh "Your commit message"

# Or manually:
git add -A
git commit -m "Your message"
git push chroma-signal main
```

### What Gets Synced

✅ **Automatically included:**
- All `.py` scripts
- All `.md` documentation
- All `.json` and `.csv` data files (via Git LFS)
- All `.svg` diagrams
- `customer-calls/` templates and playbooks

❌ **Automatically excluded (via .gitignore):**
- `meetings/` - Personal meeting notes
- `customer-calls/calls/` - Actual call notes (sensitive)
- `*_progress.json`, `*_results.json` - Temp files
- `*.log`, `automation_log.txt` - Logs
- Debug screenshots
- Personal files (`ANKIT_*.md`, `AI_LEADERS_DINNER_LIST.*`)

### Before Pushing

1. **Check what's staged:** `git status`
2. **Review changes:** `git diff --staged`
3. **Ensure no sensitive data** is included

---

## 📦 Git LFS (Large Files)

Large files are tracked with Git LFS. After cloning:

```bash
git lfs install
git lfs pull
```

### Files tracked by LFS:
- `*.csv` - All CSV files
- `*.ipynb` - Jupyter notebooks
- `*_COMPANIES*.json` - Company data
- `*_companies*.json` - Company data (lowercase)
- `*_leads*.json` - Lead data
- `*.png` - Images

### Adding new large file types:

```bash
git lfs track "*.newextension"
git add .gitattributes
```

---

## 📝 Commit Message Guidelines

Use clear, descriptive commit messages:

```
# Good examples:
"Add HubSpot integration scripts for company sync"
"Update GTM context with Q1 2026 priorities"
"Add LinkedIn parallel search automation"
"Fix customer extraction script for edge cases"

# Bad examples:
"update"
"fix"
"wip"
```

### Commit Message Format

```
<type>: <short description>

<optional longer description>
```

Types:
- `Add` - New feature/file
- `Update` - Changes to existing
- `Fix` - Bug fixes
- `Remove` - Deletions
- `Refactor` - Code restructuring

---

## 🚨 What NOT to Commit

Never commit:
- API keys or secrets (use `.env`)
- Personal contact lists
- Meeting notes with sensitive info
- Customer call recordings/transcripts
- Large binary files (use LFS or exclude)

---

## 🔧 Setting Up a New Machine

```bash
# 1. Clone the repo
git clone https://github.com/chroma-core/chroma-signal.git
cd chroma-signal

# 2. Install Git LFS and pull large files
git lfs install
git lfs pull

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Copy environment template
cp env.example .env
# Then edit .env with your API keys

# 5. Set up remotes (if needed)
git remote add chroma-signal https://github.com/chroma-core/chroma-signal.git
```

---

## 📊 Repository Structure

```
chroma-signal/
├── 📄 README.md                    # Main documentation
├── 📄 CONTRIBUTING.md              # This file
├── 📄 CLAUDE.md                    # AI assistant context
├── 📄 env.example                  # Environment template
│
├── 📂 context/                     # Strategy & Planning
│   ├── GTM_CONTEXT.md              # Master GTM strategy
│   ├── GTM_TASKS.md                # Current tasks
│   └── MEETING_INDEX.md            # Meeting index
│
├── 📂 diagrams/                    # All SVG diagrams
│   ├── chroma_seo_*.svg
│   └── 2026-*_*.svg
│
├── 📂 customer-calls/              # Customer call system
│   ├── templates/                  # Call templates
│   ├── playbooks/                  # Sales playbooks
│   ├── README.md
│   └── CALL_INDEX.md
│
├── 📂 linkedin-sales-nav-extension/ # Chrome extension
├── 📂 seo_strategy/                # SEO diagrams
├── 📂 src/                         # Core modules
├── 📂 tests/                       # Tests
│
├── 📄 *.py                         # Automation scripts
├── 📄 *.md                         # Documentation
├── 📄 *.json/*.csv                 # Data files (LFS)
│
├── 📄 .gitignore                   # Excluded files
├── 📄 .gitattributes               # LFS configuration
└── 📄 requirements.txt             # Dependencies
```

---

## ❓ Questions?

Reach out in Slack: `#gtm-signal`



