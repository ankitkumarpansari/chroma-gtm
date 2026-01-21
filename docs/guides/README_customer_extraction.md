# Pinecone Customer Extraction Guide

This guide explains the best approaches to extract Pinecone customers from all 141 YouTube videos.

## 📋 Overview

You have 141 video URLs in `pinecone_ALL_video_urls_MASTER.txt`. To identify customers, you need to:
1. Get video metadata (titles, descriptions)
2. Analyze content to identify customer mentions
3. Extract and deduplicate company names

## 🎯 Best Approaches (Ranked)

### 1. **LLM API Approach (Recommended) ⭐**
**Best for:** Accuracy and understanding context

**Pros:**
- High accuracy in identifying customer mentions
- Understands context (e.g., "Delphi uses Pinecone" vs "Pinecone uses vector search")
- Can handle various mention patterns
- Extracts exact company names

**Cons:**
- Requires API key (OpenAI/Anthropic)
- Costs money (~$0.01-0.05 per video)
- Takes time (rate limits)

**Setup:**
```bash
# Install dependencies
pip install openai anthropic

# Set API key
export OPENAI_API_KEY="your-key-here"
# OR
export ANTHROPIC_API_KEY="your-key-here"

# Run extraction
python extract_customers_llm.py --provider openai --limit 10  # Test with 10 videos
python extract_customers_llm.py --provider openai  # Process all 141
```

**Cost Estimate:**
- OpenAI GPT-4o-mini: ~$0.01 per video = ~$1.41 for all 141 videos
- Anthropic Claude Sonnet: ~$0.02 per video = ~$2.82 for all 141 videos

### 2. **Pattern-Based Extraction (Free)**
**Best for:** Quick results, no API costs

**Pros:**
- Free
- Fast
- No API keys needed

**Cons:**
- Lower accuracy
- May miss context
- False positives

**Usage:**
```bash
python extract_customers_llm.py --provider pattern
```

### 3. **Hybrid Approach (Recommended for Production)**
**Best for:** Balance of cost and accuracy

1. Use pattern-based extraction first (fast, free)
2. Use LLM only on videos with potential matches
3. Manual review of top candidates

## 📊 Processing Strategy

### Option A: Process All Videos at Once
```bash
python extract_customers_llm.py --provider openai
```
- Processes all 141 videos
- Takes ~30-60 minutes
- Costs ~$1-3

### Option B: Batch Processing
```bash
# Process in batches of 50
python extract_customers_llm.py --provider openai --limit 50
# Then continue with next batch
```

### Option C: Test First, Then Scale
```bash
# Test with 10 videos
python extract_customers_llm.py --provider openai --limit 10

# Review results, then process all
python extract_customers_llm.py --provider openai
```

## 🔍 What Gets Extracted

The script identifies companies mentioned as:
- **Customers** ("Delphi uses Pinecone")
- **Partners** ("Pinecone partners with Seam AI")
- **Users** ("Built by TwelveLabs using Pinecone")
- **Case studies** ("APIsec uses Pinecone for...")

## 📁 Output Files

1. **`pinecone_customers_llm.json`** - Complete results with all video details
2. **`pinecone_customers_summary_llm.json`** - Summary with customer counts
3. **`pinecone_customers.csv`** - Easy-to-view spreadsheet format

## 🚀 Quick Start

```bash
# 1. Test with pattern matching (free, fast)
python extract_customers_llm.py --provider pattern --limit 10

# 2. If results look good, use LLM for accuracy
export OPENAI_API_KEY="your-key"
python extract_customers_llm.py --provider openai --limit 10

# 3. Process all videos
python extract_customers_llm.py --provider openai
```

## 💡 Tips for Best Results

1. **Use GPT-4o-mini or Claude Sonnet** - Good balance of cost/accuracy
2. **Process in batches** - Easier to monitor and debug
3. **Review top customers** - Manual verification of top mentions
4. **Check video descriptions** - Often contain customer names
5. **Look for @mentions** - Many videos mention customers with @username

## 📈 Expected Results

Based on the videos I've seen, you should find customers like:
- Delphi
- Seam AI
- APIsec
- TwelveLabs
- Cohere
- Databricks
- Fivetran
- Anthropic
- Unblocked
- Hyperleap
- Wipro
- Assembled
- And more...

## 🔧 Troubleshooting

**Issue: API rate limits**
- Solution: Add delays between batches (`--batch-size 5`)

**Issue: Missing customers**
- Solution: Try different LLM models (GPT-4 instead of GPT-4o-mini)

**Issue: False positives**
- Solution: Post-process results to filter common words

## 📝 Next Steps

After extraction:
1. Review `pinecone_customers.csv` for easy viewing
2. Manually verify top customers
3. Create a master customer list
4. Cross-reference with Pinecone's website/case studies
