# 🛡️ Objection Handling Playbook

> How to handle the most common objections in Chroma sales conversations.

*Last updated: 2026-01-09*

---

## How to Use This Document

1. **Before calls**: Review objections likely to come up based on the prospect's situation
2. **During calls**: Don't read verbatim—internalize the logic and make it your own
3. **After calls**: Add new objections you encounter

---

## Pricing & Value Objections

### "Pinecone/Weaviate is cheaper"

**The reality**: Usually they're comparing starter tiers or not accounting for total cost.

**Response framework**:
1. Acknowledge: "I hear that. Price is important."
2. Probe: "Help me understand what you're comparing—is that their starter tier or at your expected scale?"
3. Reframe: "At production scale, our customers typically see [X]% lower total cost because..."
4. Proof: "Let me show you a comparison at your expected volume."

**Supporting data**:
- [ ] Add customer comparison data here

---

### "We don't have budget for a vector database"

**The reality**: Budget often exists elsewhere (Elasticsearch, cloud costs, engineering time).

**Response framework**:
1. Probe: "Where does your current search/retrieval budget sit today?"
2. Reframe: "Most of our customers don't have a 'vector DB budget'—they reallocate from Elasticsearch or reduce cloud compute costs."
3. Quantify: "What are you spending on [Elastic/search infrastructure] today?"

**Key insight**: The budget is in Elasticsearch/OpenSearch displacement, not new line items.

---

### "We'll just build it ourselves"

**The reality**: They underestimate operational complexity.

**Response framework**:
1. Acknowledge: "Totally valid—some teams do build in-house."
2. Probe: "What's your team's experience operating distributed databases at scale?"
3. Cost it out: "In our experience, teams spend 2-3 FTEs maintaining a production vector DB. At $200k/engineer fully loaded, that's $400-600k/year before infrastructure costs."
4. Opportunity cost: "What could those engineers build instead?"

---

## Competitive Objections

### "We're already using Pinecone" {#pinecone}

**Response framework**:
1. Acknowledge: "Pinecone's a solid product—good choice for getting started."
2. Probe for pain: "How's it working for you? Any challenges as you've scaled?"
3. Differentiate on:
   - **Performance**: "We consistently see 2x better latency at scale"
   - **Cost**: "Our pricing is typically 30-50% lower at production volumes"
   - **Flexibility**: "Unlike Pinecone, you can run Chroma anywhere—cloud, on-prem, edge"

**Common Pinecone pain points to probe**:
- Cold start latency
- Cost at scale
- Vendor lock-in concerns
- Limited filtering capabilities

---

### "We're evaluating Weaviate"

**Response framework**:
1. Acknowledge: "Weaviate's a capable option."
2. Differentiate on:
   - **Simplicity**: "Chroma is designed to be the simplest vector DB to operate"
   - **Performance**: "Our benchmarks show [X]% better throughput"
   - **Support**: "We offer enterprise support with [details]"

**Common Weaviate concerns to probe**:
- Operational complexity
- GraphQL learning curve
- Performance at scale

---

### "We're using Elasticsearch and it's fine"

**Response framework**:
1. Acknowledge: "Elastic is battle-tested for traditional search."
2. Probe: "How's it performing for vector/semantic search specifically?"
3. Differentiate:
   - **Purpose-built**: "Elastic bolted on vector search. Chroma was built for it from day one."
   - **Performance**: "2x faster for vector operations"
   - **Cost**: "10x cheaper—no need for the full Elastic stack"
   - **Simplicity**: "Zero operational burden vs. managing Elastic clusters"

**Key pitch**: "You can keep Elastic for what it's good at and use Chroma for vectors—or replace it entirely."

---

### "What about Milvus?"

**Response framework**:
1. Acknowledge: "Milvus is popular in the open-source community."
2. Differentiate on:
   - **Managed offering**: "We handle operations so you don't have to"
   - **Simplicity**: "Milvus has a steep operational learning curve"
   - **Support**: "Enterprise support and SLAs"

---

## Technical Objections

### "Is Chroma enterprise-ready?"

**Response framework**:
1. Direct answer: "Yes. Here's what that means specifically..."
2. Proof points:
   - SOC 2 Type 2 certified
   - BYOC (Bring Your Own Cloud)
   - CMEK (Customer-Managed Encryption Keys)
   - Multi-region, active-active
   - Zero RTO/RPO
3. Logos: "We're in production at [xAI, etc.]"
4. Offer: "Happy to do a security review with your team."

---

### "How does it scale?"

**Response framework**:
1. Probe: "What scale are you planning for? Vectors, QPS, latency requirements?"
2. Answer specifically for their scale
3. Proof: "We have customers running [X] vectors at [Y] QPS"
4. Architecture: Explain multi-region, sharding as relevant

---

### "We need on-prem / can't use cloud"

**Response framework**:
1. Good news: "Chroma supports BYOC—runs in your cloud, your VPC"
2. Probe: "Is it a compliance requirement? Data residency?"
3. Options:
   - BYOC (Bring Your Own Cloud)
   - Self-hosted open-source
   - Air-gapped deployment (enterprise)

---

### "What about data security / compliance?"

**Response framework**:
1. Lead with certs: "We're SOC 2 Type 2 certified"
2. Enumerate controls:
   - Encryption at rest and in transit
   - CMEK available
   - BYOC for full data control
   - RBAC and audit logging
3. Offer: "We can share our security documentation and do a review with your security team"

---

## Timing Objections

### "We're not ready yet / maybe next quarter"

**Response framework**:
1. Understand: "What needs to happen before you're ready?"
2. Identify blockers: Technical? Budget? Priorities?
3. Stay engaged: "Can we stay in touch? I'd love to share [relevant content] in the meantime."
4. Create urgency (if genuine): "I should mention [pricing change / capacity / relevant timeline]"

---

### "We need to evaluate more options first"

**Response framework**:
1. Support it: "Absolutely—you should evaluate thoroughly."
2. Probe: "Who else is on your list?"
3. Offer help: "Would a comparison guide be helpful? We've put together [competitive comparison]."
4. Stay in process: "Can we schedule a follow-up after you've seen the others?"

---

## Process Objections

### "I need to get buy-in from [stakeholder]"

**Response framework**:
1. Understand: "Tell me about [stakeholder]—what do they care about most?"
2. Offer help: "Would it help if I joined a call with them? Or I can prepare materials for you to share."
3. Arm your champion: "What would make this an easy yes for them?"

---

### "We need to do a POC first"

**Response framework**:
1. Agree: "Makes sense. Let's scope it properly."
2. Define success: "What would a successful POC look like? What are the criteria?"
3. Time-box: "Can we commit to a 2-week POC with a decision point at the end?"
4. Resources: "I'll make sure you have engineering support throughout."

---

## Adding New Objections

When you hear a new objection:

1. Add it to this document
2. Include:
   - The exact objection
   - Context (when does it come up?)
   - Your response framework
   - What worked / didn't work
3. Tag the call notes where you encountered it

---

## See Also

- [Competitive Battle Cards](COMPETITIVE_BATTLES.md)
- [Discovery Questions](DISCOVERY_QUESTIONS.md)
- [Use Case Library](USE_CASE_LIBRARY.md)

