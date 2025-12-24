# Chroma GTM Meeting Notes

This folder captures meeting notes and insights to build context for the Chroma GTM function.

## Folder Structure

```
meetings/
├── README.md                    # This file
├── MEETING_NOTES_PROMPT.md      # Prompt to extract notes from recordings
└── notes/                       # All meeting notes
    ├── _TEMPLATE.md             # Template for new notes
    └── YYYY-MM-DD_topic.md      # Individual meeting notes
```

## Quick Workflow

1. **Record your meeting** (Fathom, Otter, Zoom, etc.)
2. **Use the prompt** in `MEETING_NOTES_PROMPT.md` to extract structured notes
3. **Save to** `notes/YYYY-MM-DD_meeting-topic.md`
4. **Update** `../context/MEETING_INDEX.md` with a new row

---

## File Naming Convention

Format: `YYYY-MM-DD_brief-description.md`

Examples:
- `2024-12-22_customer-call-acme.md`
- `2024-12-20_weekly-gtm-sync.md`
- `2024-12-18_linkedin-strategy-review.md`

---

## Meeting Types to Track

| Type | Priority | What to Capture |
|------|----------|-----------------|
| Customer Calls | 🔴 High | Pain points, feedback, objections, use cases |
| Strategy Sessions | 🔴 High | Decisions, priorities, OKRs |
| Internal Syncs | 🟡 Medium | Action items, blockers, updates |
| Partner Meetings | 🟡 Medium | Partnership opportunities, integrations |
| Competitor Intel | 🟢 Low | What we learned about competition |

---

## What Makes Good Meeting Notes

### ✅ Include
- Customer quotes and pain points
- Decisions made
- Action items with owners
- Competitive mentions
- GTM-relevant insights

### ❌ Skip
- Small talk
- Scheduling logistics
- Already-documented context
- Technical troubleshooting (unless relevant)

