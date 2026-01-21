# 📚 Use Case Library

> Validated use cases with real customer examples and positioning guidance.

*Last updated: 2026-01-09*

---

## Use Case Overview

| Use Case | Frequency | Deal Size | Sales Cycle | Complexity |
|----------|-----------|-----------|-------------|------------|
| RAG / Retrieval | Very Common | $$ | Medium | Medium |
| AI Agents | Growing | $$$ | Long | High |
| Semantic Search | Common | $$ | Medium | Medium |
| Recommendations | Occasional | $$ | Medium | Medium |
| Elasticsearch Replacement | Common | $$$ | Long | Medium |

---

## RAG (Retrieval-Augmented Generation)

### What It Is
Using vector search to retrieve relevant context before generating LLM responses. The most common use case for vector databases today.

### Common Implementations
- **Customer support bots**: Retrieve relevant docs/tickets before answering
- **Internal knowledge bases**: Search company docs, wikis, Slack
- **Document Q&A**: Answer questions about PDFs, contracts, manuals
- **Code assistants**: Search codebases for relevant context

### Key Requirements
| Requirement | Typical Ask |
|-------------|-------------|
| Latency | <100ms p99 |
| Scale | 1M-100M vectors |
| Accuracy | High recall matters |
| Filtering | By document, user, date |

### Why Chroma Wins
- Fast retrieval at scale
- Flexible metadata filtering
- Easy integration with LangChain/LlamaIndex
- Cost-effective for large document sets

### Discovery Questions
- "What documents are you indexing?"
- "How many documents? How fast is it growing?"
- "What's your latency requirement?"
- "How are you chunking documents today?"

### Customer Examples
<!-- Add real examples as you close deals -->
- *[Company]* - [Brief description]

### Positioning
> "RAG is only as good as your retrieval. Chroma gives you the fastest, most accurate retrieval so your LLM has the best context to work with."

---

## AI Agents

### What It Is
Autonomous AI systems that use vector search for memory, tool selection, and context retrieval.

### Common Implementations
- **Long-term memory**: Store and retrieve conversation history
- **Tool/action selection**: Find the right tool for the task
- **Knowledge retrieval**: Access domain knowledge
- **Planning**: Retrieve relevant past plans/actions

### Key Requirements
| Requirement | Typical Ask |
|-------------|-------------|
| Latency | <50ms (in the loop) |
| Scale | Variable, often smaller |
| Updates | Real-time writes |
| Consistency | Strong consistency |

### Why Chroma Wins
- Low latency for real-time agent loops
- Fast writes for memory updates
- Flexible schema for different memory types
- Easy to embed in agent frameworks

### Discovery Questions
- "What kind of agent are you building?"
- "How are you handling memory today?"
- "What's the latency budget for retrieval in your agent loop?"
- "How often does the agent need to write to memory?"

### Customer Examples
<!-- Add real examples -->
- *[Company]* - [Brief description]

### Positioning
> "Agents need fast, reliable memory. Chroma is built for the real-time retrieval and updates that agents demand."

---

## Semantic Search

### What It Is
Search that understands meaning, not just keywords. Find relevant results even when the query doesn't match exact terms.

### Common Implementations
- **Product search**: Find products by description
- **Content discovery**: Surface relevant articles/content
- **Support ticket search**: Find similar past tickets
- **Legal/compliance search**: Find relevant clauses/precedents

### Key Requirements
| Requirement | Typical Ask |
|-------------|-------------|
| Latency | <200ms |
| Scale | 10M-1B vectors |
| Accuracy | Precision + recall |
| Hybrid | Often need keyword + semantic |

### Why Chroma Wins
- High-quality semantic search out of the box
- Hybrid search capabilities
- Scales to billions of vectors
- Lower cost than Elasticsearch for semantic

### Discovery Questions
- "What are users searching for?"
- "How does your current search perform on long-tail queries?"
- "Do you need exact match + semantic, or just semantic?"
- "What's your search volume?"

### Customer Examples
<!-- Add real examples -->
- *[Company]* - [Brief description]

### Positioning
> "Users expect search to understand what they mean, not just what they type. Chroma powers semantic search that actually works."

---

## Recommendations

### What It Is
Using vector similarity to recommend similar items—products, content, users, etc.

### Common Implementations
- **"More like this"**: Similar products/content
- **User matching**: Find similar users
- **Content personalization**: Personalized feeds
- **Collaborative filtering**: Based on behavior vectors

### Key Requirements
| Requirement | Typical Ask |
|-------------|-------------|
| Latency | <100ms |
| Scale | Often very large (all items) |
| Freshness | Near real-time updates |
| Diversity | Not just most similar |

### Why Chroma Wins
- Fast similarity search at scale
- Real-time updates for fresh recommendations
- Flexible filtering for business rules
- Cost-effective for large catalogs

### Discovery Questions
- "What are you recommending?"
- "How many items in your catalog?"
- "How fresh do recommendations need to be?"
- "What's driving recommendations today?"

### Customer Examples
<!-- Add real examples -->
- *[Company]* - [Brief description]

---

## Elasticsearch/OpenSearch Replacement

### What It Is
Migrating from Elasticsearch to a purpose-built vector database for semantic/vector search workloads.

### Why They Migrate
- **Cost**: Elastic is expensive for vector workloads
- **Performance**: Purpose-built is faster
- **Complexity**: Elastic is overkill for vectors
- **Focus**: Don't need full-text features

### Key Requirements
| Requirement | Typical Ask |
|-------------|-------------|
| Migration | Smooth transition |
| Feature parity | Match current capabilities |
| Performance | Better than Elastic |
| Cost | Significant savings |

### Why Chroma Wins
- 10x cost reduction
- 2x performance improvement
- Simpler operations
- Migration support available

### Discovery Questions
- "What's your Elastic bill today?"
- "What percentage is vector vs. full-text search?"
- "How much engineering time goes into Elastic?"
- "What would you do with 10x cost savings?"

### The Pitch
> "Elasticsearch is great for full-text search, but you're paying for a Swiss Army knife when you need a scalpel. Chroma gives you 10x cost savings and 2x performance for vector workloads."

### Migration Path
1. Run Chroma alongside Elastic
2. Migrate vector workloads first
3. Validate performance and accuracy
4. Cut over and decommission Elastic vector indices

### Customer Examples
<!-- Add real examples -->
- *[Company]* - [Brief description]

---

## Emerging Use Cases

### Multimodal Search
- Search across text, images, audio, video
- Growing as multimodal models improve
- Key requirement: support for different embedding types

### Anomaly Detection
- Find outliers in vector space
- Use cases: fraud, security, quality control
- Key requirement: fast nearest neighbor at scale

### Knowledge Graphs + Vectors
- Combine structured relationships with semantic similarity
- Growing interest in hybrid approaches
- Key requirement: integration flexibility

---

## Adding New Use Cases

When you encounter a new use case:

1. Add it to this document
2. Include:
   - What it is
   - Common implementations
   - Key requirements
   - Why Chroma wins
   - Discovery questions
3. Add customer examples as you close deals
4. Share in Slack for team learning

---

## See Also

- [Discovery Questions](DISCOVERY_QUESTIONS.md)
- [Competitive Battle Cards](COMPETITIVE_BATTLES.md)
- [Customer Insights Summary](../INSIGHTS_SUMMARY.md)



