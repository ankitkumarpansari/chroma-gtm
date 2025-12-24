# Meeting Notes Extraction Prompt

> Copy this prompt and use it with your meeting recording/transcript to extract structured notes for the Chroma GTM project.

---

## 🎯 The Prompt

```
I just had a meeting and I need you to extract structured notes for my Chroma GTM project. Focus on what's actionable and relevant to go-to-market strategy.

Here's the meeting recording/transcript:
[PASTE YOUR CONTENT HERE]

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
- **LinkedIn/Outreach ideas**: Anything useful for our outreach campaigns

## 7. Open Questions
What questions came up that still need answers?

## 8. Follow-up Required
- Any follow-up meetings scheduled?
- Who needs to be looped in?

Format the output in clean markdown that I can save directly to a file.
```

---

## 📝 Quick Version (For Shorter Meetings)

```
Extract meeting notes from this recording for my Chroma GTM project:

[PASTE CONTENT]

Give me:
1. One-line summary
2. Key points (bullet list)
3. Action items with owners
4. Any GTM insights (customer feedback, competitive intel, messaging ideas)
5. Next steps

Keep it concise - only what's actionable.
```

---

## 🚀 After-Meeting Workflow

1. **During/After Meeting**: Use your recording tool (Fathom, Otter, etc.)
2. **Extract Notes**: Use the prompt above with Claude/ChatGPT
3. **Save Notes**: Copy output to `meetings/notes/YYYY-MM-DD_meeting-topic.md`
4. **Update Index**: Add a row to `context/MEETING_INDEX.md`
5. **Update Context**: If there are major learnings, add to `context/GTM_CONTEXT.md`

---

## 💡 Tips for Better Notes

### What to Include
✅ Customer pain points and feedback
✅ Competitive mentions
✅ Decisions and commitments
✅ Specific action items with owners
✅ Quotes that capture key insights
✅ Numbers and metrics discussed

### What to Skip
❌ Small talk and pleasantries
❌ Scheduling discussions
❌ Technical troubleshooting (unless relevant)
❌ Repeated information
❌ Context that's already documented elsewhere

---

## 🏷️ Suggested Tags for Notes

Use these tags at the bottom of your notes for easy searching:

| Tag | Use When |
|-----|----------|
| `#customer` | Customer-related meeting |
| `#prospect` | Potential customer |
| `#internal` | Team meeting |
| `#strategy` | Planning/strategy session |
| `#competitor` | Competitive intel discussed |
| `#linkedin` | LinkedIn/outreach related |
| `#chroma-signal` | Related to Chroma Signal list |
| `#partner` | SI/partner discussion |
| `#product` | Product feedback/roadmap |
| `#urgent` | Needs immediate attention |

