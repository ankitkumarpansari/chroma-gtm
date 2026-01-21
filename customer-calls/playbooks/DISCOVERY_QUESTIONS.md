# 🔍 Discovery Questions Playbook

> Questions that uncover pain, qualify opportunities, and move deals forward.

*Last updated: 2026-01-09*

---

## Philosophy

Good discovery is about **listening**, not interrogating. Use these questions as a framework, not a script. Follow the thread when you hear something interesting.

**The goal**: Understand their world so well that you can articulate their problem better than they can.

---

## Opening / Rapport

Start with context-setting, not selling.

- "Thanks for taking the time. Before I share about Chroma, I'd love to understand what you're working on. What's the project that brought you to us?"
- "I did some research before the call—saw you're working on [X]. Tell me more about that."
- "What's your role in this project?"

---

## Understanding Their World

### The Project

- "Walk me through what you're building."
- "Who's the end user? What are they trying to accomplish?"
- "What does success look like for this project?"
- "What's the timeline? When does this need to be in production?"

### The Team

- "Who's working on this? What's the team structure?"
- "Who else is involved in the decision?"
- "Is there a technical lead I should loop in for a deeper dive?"

### The Stack

- "What's your current tech stack for this?"
- "What LLM are you using? (OpenAI, Anthropic, Cohere, self-hosted?)"
- "Are you using any frameworks? (LangChain, LlamaIndex?)"
- "What cloud are you on?"

---

## Uncovering Pain

### Current State Problems

- "What's working well with your current approach?"
- "What's not working? What's frustrating?"
- "If you could wave a magic wand and fix one thing, what would it be?"
- "What happens if you don't solve this?"

### Specific Pain Probes

**For Elasticsearch users**:
- "How much time does your team spend managing Elastic?"
- "How's vector search performing vs. traditional search?"
- "What's your Elastic bill looking like?"

**For Pinecone users**:
- "How's Pinecone working for you at scale?"
- "Any concerns about cost as you grow?"
- "How do you feel about the vendor lock-in?"

**For build-your-own**:
- "What's the operational burden like?"
- "How much engineering time goes into maintenance?"
- "What would you do with that time if you got it back?"

---

## Qualification Questions

### Budget (B)

- "Is there budget allocated for this project?"
- "Where does the budget sit? (New line item vs. reallocation?)"
- "What's the expected investment range?"
- "Who controls the budget?"

### Authority (A)

- "Who makes the final decision on this?"
- "What's the approval process look like?"
- "Who else needs to be involved?"
- "Have you bought similar tools before? How did that process go?"

### Need (N)

- "How critical is this project to the business?"
- "What happens if you don't solve this in [timeframe]?"
- "Is this a 'nice to have' or a 'must have'?"

### Timeline (T)

- "When do you need this in production?"
- "What's driving that timeline?"
- "What happens if you miss that date?"
- "Are there any hard deadlines? (Compliance, launch, etc.)"

---

## Competitive Intelligence

### Who Else They're Talking To

- "Who else are you evaluating?"
- "Have you looked at Pinecone/Weaviate/Milvus?"
- "What do you like about [competitor]?"
- "What concerns do you have about [competitor]?"

### Decision Criteria

- "What are the top 3 things you're looking for?"
- "How will you make the final decision?"
- "What would make this an easy 'yes'?"
- "What would make you say 'no'?"

---

## Technical Deep-Dive Triggers

Use these when you need to go deeper technically:

### Scale & Performance

- "How many vectors are we talking about?"
- "What's your expected QPS?"
- "What latency do you need?"
- "How fast is your data growing?"

### Architecture

- "Walk me through your architecture."
- "Where does the vector DB fit in the flow?"
- "What are your availability requirements?"
- "Do you need multi-region?"

### Security & Compliance

- "What are your security requirements?"
- "Any compliance frameworks? (SOC 2, HIPAA, etc.)"
- "Do you need data to stay in a specific region?"
- "Is on-prem or BYOC a requirement?"

---

## Closing the Discovery Call

### Summarize Understanding

- "Let me make sure I understand... [summarize their situation]"
- "Did I miss anything?"

### Propose Next Steps

- "Based on what you've shared, I think the best next step is [demo/technical call/POC]. Does that make sense?"
- "Who else should be on that call?"
- "Can we get that scheduled before we hang up?"

### Leave the Door Open

- "What questions do you have for me?"
- "Is there anything else you'd like to know about Chroma?"

---

## Questions to Avoid

❌ "What's your budget?" (too direct, too early)
❌ "Are you the decision maker?" (puts them on the spot)
❌ "When are you going to buy?" (pushy)
❌ Leading questions that assume the sale

---

## Questions That Signal Strong Opportunities

When you hear these, lean in:

✅ "We're frustrated with [current solution]"
✅ "We need this live by [specific date]"
✅ "Our CTO is pushing for this"
✅ "We have budget allocated"
✅ "We're replacing Elasticsearch"
✅ "We tried building it ourselves and it's not working"

---

## Questions That Signal Weak Opportunities

When you hear these, qualify harder:

⚠️ "We're just exploring options"
⚠️ "No timeline yet"
⚠️ "I'm doing research for my team"
⚠️ "We're happy with our current solution"
⚠️ "Budget isn't approved yet"

---

## See Also

- [Objection Handling](OBJECTION_HANDLING.md)
- [Competitive Battle Cards](COMPETITIVE_BATTLES.md)



