# 🤖 GitHub Automation for Chroma GTM

This folder contains GitHub Actions and templates for automating GTM workflows.

## Features

### 1. Claude GTM Assistant (`workflows/claude-helper.yml`)

Ask Claude questions directly in GitHub Issues! Claude has access to:
- `CLAUDE.md` - Project overview
- `context/GTM_CONTEXT.md` - Strategy & priorities
- `context/MEETING_INDEX.md` - Recent decisions
- `CHROMA_COMPETITORS.md` - Competitive intel

**How to use:**
1. Create a new issue using the "🤖 Ask Claude" template
2. Or add `@claude your question` to any issue/comment
3. Claude responds within 1-2 minutes

**Example questions:**
```
@claude What are our Q1 priorities?
@claude Draft an outreach email for Notion
@claude How should we position against Pinecone?
@claude Summarize the Sumble meeting from last week
```

### 2. Issue Templates (`ISSUE_TEMPLATE/`)

- **ask-claude.yml** - Structured form for asking Claude questions

## Setup Requirements

### Add Anthropic API Key

1. Go to repo **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `ANTHROPIC_API_KEY`
4. Value: Your Anthropic API key (starts with `sk-ant-`)

### Permissions

The workflow needs:
- `issues: write` - To post comments
- `contents: read` - To read context files

These are configured in the workflow file.

## Cost

- **GitHub Actions**: Free tier includes 2,000 minutes/month
- **Claude API**: ~$0.01-0.05 per question (Sonnet model)
- **Estimated monthly cost**: $1-5 for ~100 questions

## Troubleshooting

### "Error: Could not get response from Claude"
- Check that `ANTHROPIC_API_KEY` secret is set
- Verify the API key is valid and has credits

### Workflow not triggering
- Make sure the issue/comment contains `@claude`
- Check workflow permissions in repo settings

### Response is incomplete
- Context files may be too large (truncated at 100KB)
- Try asking a more specific question

## Files

```
.github/
├── README.md                    # This file
├── workflows/
│   └── claude-helper.yml        # Main Claude action
└── ISSUE_TEMPLATE/
    ├── ask-claude.yml           # Issue template
    └── config.yml               # Template config
```

