# 🎯 LinkedIn Sales Navigator Company Adder

A Chrome extension to automatically add companies from your research pipeline to LinkedIn Sales Navigator.

## Features

- **140+ verified companies** from 15 categories pre-loaded
- **Priority filtering** - focus on HIGH priority targets first
- **Batch processing** - set how many companies to process at once
- **Auto-save** - automatically saves companies when found
- **Progress tracking** - resume where you left off
- **Export results** - download your results as JSON

## Installation

### Step 1: Open Chrome Extensions

1. Open Chrome browser
2. Go to `chrome://extensions/`
3. Enable **Developer mode** (toggle in top right)

### Step 2: Load the Extension

1. Click **"Load unpacked"**
2. Navigate to this folder: `linkedin-sales-nav-extension`
3. Click **"Select"**

### Step 3: Pin the Extension

1. Click the puzzle piece icon in Chrome toolbar
2. Find "LinkedIn Sales Nav Company Adder"
3. Click the pin icon to keep it visible

## Usage

### 1. Navigate to Sales Navigator

Go to [LinkedIn Sales Navigator](https://www.linkedin.com/sales/home) and make sure you're logged in.

### 2. Open the Extension

Click the extension icon in your Chrome toolbar.

### 3. Configure Settings

- **Priority Filter**: Choose which priority levels to include
- **Batch Size**: How many companies to process (default: 10)
- **Delay**: Seconds between each company (default: 5)

### 4. Start Adding Companies

Click **"▶️ Start Adding"** and watch the magic happen!

## Settings

| Setting | Description |
|---------|-------------|
| Auto-save companies | Automatically save when found |
| Skip already saved | Don't re-process saved companies |
| Random delay variation | Add ±2s randomness to delays |

## Company Categories

The extension includes companies from:

1. Documentation Platforms (Mintlify, GitBook, ReadMe...)
2. Developer Tools (Cursor, Cognition, Replit...)
3. Legal Tech (Harvey AI, Clio, Spellbook...)
4. Sales Intelligence (Clay, Apollo.io, Gong...)
5. Customer Support AI (Sierra AI, Decagon, Ada...)
6. Knowledge Management (Guru, Notion, Tettra...)
7. Enterprise Search (Glean, Coveo, Algolia...)
8. Financial Research (AlphaSense, Daloopa...)
9. Healthcare AI (Hippocratic AI, Abridge...)
10. Research Tools (Elicit, Semantic Scholar...)
11. AI Agents (n8n, Lindy.ai, Zapier...)
12. Content AI (Writer, Copy.ai, Jasper...)
13. Procurement (Zip, Ramp, Brex...)
14. Real Estate Tech (Placer.ai, Cherre...)
15. HR Tech (Eightfold AI, Paradox...)

## Priority Levels

| Priority | Description |
|----------|-------------|
| **HIGH** | Best fit, highest value targets |
| **MEDIUM-HIGH** | Strong fit, good opportunities |
| **MEDIUM** | Moderate fit |
| **MEDIUM-LOW** | Lower priority |
| **LOW** | Competitors or low fit |

## Tips

1. **Start with HIGH priority** - these are the best targets
2. **Use small batches** - 5-10 companies at a time
3. **Take breaks** - don't run continuously for hours
4. **Monitor the process** - watch for any issues
5. **Export results** - save your progress regularly

## Troubleshooting

### Extension not working?

1. Make sure you're on LinkedIn Sales Navigator
2. Check that you're logged in
3. Refresh the page and try again

### Companies not found?

Some companies may have different names on LinkedIn. Check the Results tab for failed companies.

### Rate limited?

If LinkedIn shows warnings:
1. Stop the automation immediately
2. Wait 24-48 hours before resuming
3. Use longer delays (10-15 seconds)

## Files

```
linkedin-sales-nav-extension/
├── manifest.json      # Extension configuration
├── popup.html         # Extension popup UI
├── popup.css          # Popup styles
├── popup.js           # Popup logic
├── companies.js       # Company data
├── content.js         # Page automation script
├── content.css        # Content script styles
├── background.js      # Service worker
└── icons/             # Extension icons
```

## Disclaimer

This extension is for personal use. Use responsibly and respect LinkedIn's terms of service. Add appropriate delays between actions to avoid rate limiting.

