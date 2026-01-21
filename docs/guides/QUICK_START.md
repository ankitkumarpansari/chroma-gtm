# 🚀 Quick Start: Extract Pinecone Customers

## Recommended Approach: LLM-Based Extraction

For the **best accuracy**, use an LLM API (OpenAI or Anthropic) to analyze video descriptions and identify customers.

### Step 1: Set Up API Key

```bash
# Option A: OpenAI (cheaper, ~$1.41 for all videos)
export OPENAI_API_KEY="sk-your-key-here"

# Option B: Anthropic Claude (more accurate, ~$2.82 for all videos)
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### Step 2: Test with 10 Videos

```bash
python3 extract_customers_llm.py --provider openai --limit 10
```

### Step 3: Process All 141 Videos

```bash
python3 extract_customers_llm.py --provider openai
```

**Expected time:** 30-60 minutes  
**Expected cost:** $1-3  
**Output:** `pinecone_customers.csv` with all customers

---

## Alternative: Free Pattern-Based (Less Accurate)

If you don't want to use an API:

```bash
python3 extract_customers_llm.py --provider pattern
```

**Pros:** Free, fast  
**Cons:** Many false positives, lower accuracy

---

## What You'll Get

After running, you'll have:

1. **`pinecone_customers.csv`** - Spreadsheet with:
   - Customer name
   - Number of videos mentioning them
   - Video IDs where mentioned

2. **`pinecone_customers_llm.json`** - Complete data with:
   - All video metadata
   - Customer mentions per video
   - Full context

3. **`pinecone_customers_summary_llm.json`** - Summary statistics

---

## Expected Customers (Based on Video Titles)

From the video titles, you should find:
- **Delphi** (@withdelphi)
- **Seam AI**
- **APIsec**
- **TwelveLabs**
- **Cohere**
- **Databricks**
- **Fivetran**
- **Anthropic**
- **Unblocked**
- **Hyperleap**
- **Wipro**
- **Assembled**
- **Zapier**
- **Groq**
- **Neo4j**
- **SpiceDB** (AuthZed)
- **LangChain**
- **OpenAI**
- And more...

---

## Installation

```bash
# Install required packages
pip install openai anthropic

# Or if using pattern-only (no install needed)
# Python standard library is sufficient
```

---

## Troubleshooting

**"No module named 'openai'"**
```bash
pip install openai
```

**"API rate limit exceeded"**
- Add delays: `--batch-size 5`
- Or process in smaller batches

**"No customers found"**
- Check video descriptions are accessible
- Try different provider (anthropic vs openai)
- Review sample videos manually

---

## Next Steps After Extraction

1. **Review CSV file** - Open `pinecone_customers.csv` in Excel/Sheets
2. **Verify top customers** - Check top 20-30 mentions
3. **Deduplicate** - Some companies may be mentioned with variations
4. **Cross-reference** - Check Pinecone's website for official customer list
5. **Build master list** - Create final customer database

---

## Cost Breakdown

| Provider | Model | Cost per Video | Total (141 videos) |
|----------|-------|----------------|-------------------|
| OpenAI | gpt-4o-mini | ~$0.01 | ~$1.41 |
| OpenAI | gpt-4 | ~$0.05 | ~$7.05 |
| Anthropic | claude-3-5-sonnet | ~$0.02 | ~$2.82 |
| Anthropic | claude-3-opus | ~$0.10 | ~$14.10 |
| Pattern | N/A | $0.00 | $0.00 |

**Recommendation:** Start with `gpt-4o-mini` for best cost/accuracy balance.
