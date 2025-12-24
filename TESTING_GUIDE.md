# 🧪 Testing Accuracy Guide

## Quick Start

### Option 1: Interactive Testing (Recommended)
Test on a few videos with manual verification:

```bash
# Test on 5 videos, compare pattern vs OpenAI
python3 test_accuracy.py --limit 5 --methods pattern openai
```

This will:
1. Show you each video's title and description
2. Ask you to identify actual customers (ground truth)
3. Run extraction methods
4. Compare results and show accuracy metrics

---

### Option 2: Use Pre-created Ground Truth
If you've already created a ground truth file:

```bash
# Create ground truth first (one time)
python3 test_accuracy.py --create-gt --limit 10

# Then test methods against it
python3 test_accuracy.py --limit 10 --methods pattern openai openai-gpt4 --no-manual
```

---

## Step-by-Step Testing Process

### Step 1: Create Ground Truth (One Time)

```bash
# Review 10 videos and mark actual customers
python3 test_accuracy.py --create-gt --limit 10
```

For each video, you'll see:
- Video title
- Description
- You enter the actual customer names

This creates `ground_truth.json` for future testing.

---

### Step 2: Test Different Methods

```bash
# Test pattern-based extraction
python3 test_accuracy.py --limit 10 --methods pattern --no-manual

# Test OpenAI GPT-4o-mini
export OPENAI_API_KEY="your-key"
python3 test_accuracy.py --limit 10 --methods openai --no-manual

# Test OpenAI GPT-4
python3 test_accuracy.py --limit 10 --methods openai-gpt4 --no-manual

# Compare all methods
python3 test_accuracy.py --limit 10 --methods pattern openai openai-gpt4 --no-manual
```

---

### Step 3: Review Results

The script outputs:
- **Precision**: How many extracted customers are correct
- **Recall**: How many actual customers were found
- **F1 Score**: Combined metric (higher is better)
- **False Positives**: Incorrectly identified customers
- **False Negatives**: Missed customers

Example output:
```
ACCURACY TEST RESULTS
================================================================================

PATTERN:
  Average Precision: 0.450
  Average Recall: 0.600
  Average F1 Score: 0.514
  Videos Tested: 10

OPENAI:
  Average Precision: 0.850
  Average Recall: 0.800
  Average F1 Score: 0.824
  Videos Tested: 10
```

---

## Understanding Metrics

### Precision
**What it means:** Of all customers extracted, how many are correct?

**Formula:** Correct Extractions / Total Extractions

**Example:**
- Extracted: ["Delphi", "Seam AI", "Fake Company"]
- Actual: ["Delphi", "Seam AI"]
- Precision: 2/3 = 0.667 (67%)

**Higher is better** - means fewer false positives

---

### Recall
**What it means:** Of all actual customers, how many were found?

**Formula:** Found Customers / Total Actual Customers

**Example:**
- Extracted: ["Delphi"]
- Actual: ["Delphi", "Seam AI", "APIsec"]
- Recall: 1/3 = 0.333 (33%)

**Higher is better** - means fewer false negatives

---

### F1 Score
**What it means:** Combined measure of precision and recall

**Formula:** 2 × (Precision × Recall) / (Precision + Recall)

**Range:** 0 to 1 (higher is better)

**Use:** Overall accuracy metric

---

## Testing Scenarios

### Scenario 1: Quick Comparison
Test 3-5 videos to quickly compare methods:

```bash
python3 test_accuracy.py --limit 3 --methods pattern openai
```

---

### Scenario 2: Comprehensive Testing
Test 20-30 videos for statistical significance:

```bash
# Create ground truth for 30 videos
python3 test_accuracy.py --create-gt --limit 30

# Test all methods
python3 test_accuracy.py --limit 30 --methods pattern openai openai-gpt4 --no-manual
```

---

### Scenario 3: Method Development
Test new extraction methods:

```bash
# Test your custom method
python3 test_accuracy.py --limit 10 --methods your-method --no-manual
```

---

## Expected Results

Based on typical performance:

| Method | Precision | Recall | F1 Score |
|--------|-----------|--------|----------|
| Pattern-based | 0.40-0.50 | 0.50-0.60 | 0.45-0.55 |
| GPT-4o-mini | 0.70-0.80 | 0.70-0.80 | 0.70-0.80 |
| GPT-4 | 0.85-0.90 | 0.80-0.85 | 0.82-0.87 |
| GPT-4 + Improved | 0.90-0.95 | 0.85-0.90 | 0.87-0.92 |

---

## Output Files

### `accuracy_test_results.json`
Complete test results with:
- Per-video metrics
- Overall averages
- False positives/negatives for each video

### `ground_truth.json`
Your manually verified customer list:
```json
{
  "video_id_1": ["Delphi", "Seam AI"],
  "video_id_2": ["APIsec", "TwelveLabs"]
}
```

---

## Tips for Accurate Testing

### 1. Use Representative Videos
- Mix of different video types
- Some with clear customer mentions
- Some with ambiguous mentions
- Some with no customers

### 2. Be Consistent
- Use same ground truth for all method comparisons
- Review videos in same order
- Use consistent naming (e.g., "Delphi" not "delphi" or "@withdelphi")

### 3. Test Enough Videos
- Minimum: 10 videos for rough estimate
- Recommended: 20-30 videos for reliable metrics
- Ideal: 50+ videos for statistical significance

### 4. Review Edge Cases
- Check false positives (why were they extracted?)
- Check false negatives (why were they missed?)
- Use insights to improve extraction

---

## Troubleshooting

**"No ground truth found"**
- Run `--create-gt` first to create ground truth file

**"API key not found"**
- Set `OPENAI_API_KEY` environment variable
- Or use `--api-key` argument

**"Method not found"**
- Make sure extraction scripts are in same directory
- Check method name spelling

---

## Next Steps After Testing

1. **Identify best method** - Use F1 score to choose
2. **Analyze errors** - Review false positives/negatives
3. **Improve extraction** - Update prompts/filters based on errors
4. **Re-test** - Verify improvements
5. **Scale up** - Process all 141 videos with best method

---

## Example Workflow

```bash
# 1. Create ground truth (10 videos)
python3 test_accuracy.py --create-gt --limit 10

# 2. Test pattern method
python3 test_accuracy.py --limit 10 --methods pattern --no-manual

# 3. Test OpenAI methods
export OPENAI_API_KEY="your-key"
python3 test_accuracy.py --limit 10 --methods openai openai-gpt4 --no-manual

# 4. Compare results
# Review accuracy_test_results.json

# 5. Choose best method and process all videos
python3 extract_customers_improved.py --provider openai --model gpt-4
```
