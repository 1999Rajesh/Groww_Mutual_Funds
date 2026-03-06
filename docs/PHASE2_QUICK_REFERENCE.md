# Phase 2 - Quick Reference Guide

## ✅ **Phase 2 Complete: Data Processing & Chunking**

---

## 🚀 Quick Start

### Prerequisites
✅ Phase 1 complete (scraped data in `data/raw/`)

### Running Phase 2
```bash
cd c:\Users\Rajesh\Documents\RAG_Mutual_Funds
python run_phase2.py
```

---

## 📊 What Phase 2 Does

```
Raw Data (Phase 1) → Clean → Chunk → Processed Data (Ready for Embeddings)
```

**3 Main Steps:**
1. **Clean** - Normalize formats, parse numbers, validate
2. **Chunk** - Create 3 types of chunks (field-based, summary, Q&A)
3. **Save** - Store processed chunks with metadata

---

## 📁 Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `src/processors/data_cleaner.py` | Data cleaning module | 459 |
| `src/processors/chunking_strategy.py` | Chunking strategies | 387 |
| `run_phase2.py` | Processing pipeline | 185 |

**Total**: 1,031 lines of code

---

## 🔍 Cleaning Functions

| Function | Cleans | Example |
|----------|--------|---------|
| `clean_text()` | HTML, whitespace | `"  HDFC Fund  "` → `"HDFC Fund"` |
| `clean_category()` | Fund categories | `"Equity Linked Savings Scheme"` → `"ELSS"` |
| `clean_percentage()` | %, returns | `"0.68%"` → `0.68` |
| `clean_currency()` | ₹, Cr, Mn | `"₹500"` → `500.0`, `"₹28,500 Cr"` → `28500.0` |
| `clean_lock_in_period()` | Lock-in formats | `"3 years"` → `"3 years"` |
| `clean_risk_level()` | Risk levels | `"very high"` → `"Very High"` |

---

## 📦 Chunk Types

### 3 Complementary Strategies

#### 1. Field-Based Chunks (5 per fund)
Groups related fields:
- `basic_info`: Name, type, category
- `investment_details`: Expense ratio, SIP, lumpsum
- `lock_in_exit`: Lock-in, exit load
- `risk_benchmark`: Risk level, benchmark
- `performance`: Returns, AUM, NAV

#### 2. Summary Chunks (1 per fund)
Comprehensive overview combining key info

#### 3. Q&A Chunks (~5-6 per fund)
Question-answer pairs for better matching:
```
Q: What is the expense ratio of HDFC ELSS Tax Saver Fund?
A: The expense ratio of HDFC ELSS Tax Saver Fund is 0.68%
```

---

## 📈 Typical Output (6 funds)

| Metric | Value |
|--------|-------|
| Funds Processed | 6 |
| Success Rate | 100% |
| Total Chunks | 48-60 |
| Chunks per Fund | 8-10 |

**Chunk Distribution:**
- basic_info: 6 chunks
- investment_details: 6 chunks
- lock_in_exit: 6 chunks
- risk_benchmark: 6 chunks
- performance: 6 chunks
- summary: 6 chunks
- qa_pair: 30 chunks

---

## 💡 Example Usage

### Test Data Cleaning
```python
from src.processors.data_cleaner import DataCleaner

cleaner = DataCleaner()

test_data = {
    'expense_ratio': '0.68%',
    'minimum_sip': '₹500',
    'aum': '₹28,500 Cr'
}

cleaned = cleaner.clean_all_fields(test_data)
# Result: {'expense_ratio': 0.68, 'minimum_sip': 500.0, 'aum': 28500.0}
```

### Test Chunking
```python
from src.processors.chunking_strategy import ChunkingStrategy

chunker = ChunkingStrategy()
chunks = chunker.chunk_fund_data(cleaned_fund)

for chunk in chunks:
    print(f"Type: {chunk.chunk_type}")
    print(f"Text: {chunk.chunk_text[:100]}...")
```

---

## 🎯 Key Features

✅ **Data Quality Assurance**
- Automatic validation
- Numeric range checking
- Format standardization
- Error handling

✅ **Intelligent Chunking**
- Semantic grouping
- Multiple chunk types
- Q&A format for better matching
- Unique IDs (hash-based)

✅ **Metadata Enrichment**
- Source URLs preserved
- Timestamps tracked
- Field mappings included
- Chunk type classification

✅ **Scalability**
- Batch processing
- Progress logging
- Error recovery
- Statistics tracking

---

## 📝 Output Location

Processed chunks saved to:
```
data/processed/processed_chunks_YYYYMMDD_HHMMSS.json
```

**File Structure:**
```json
{
  "metadata": {
    "processed_at": "2024-03-05T14:30:22",
    "total_chunks": 48,
    "pipeline": "Phase 2 - Data Processing"
  },
  "chunks": [
    {
      "chunk_id": "hdfc_elss_tax_saver_fund_qa_1a2b3c4d",
      "fund_name": "HDFC ELSS Tax Saver Fund",
      "chunk_type": "qa_pair",
      "chunk_text": "Q: What is the expense ratio...",
      "metadata": {
        "source_url": "https://www.indmoney.com/...",
        "question": "...",
        "answer": "..."
      }
    }
  ]
}
```

---

## ⚙️ Troubleshooting

### Issue: "No scraped data found"
**Solution**: Run Phase 1 first or check `data/raw/` folder

### Issue: Validation failures
**Solution**: Ensure required fields present (fund_name, scheme_type, category)

### Issue: Low chunk count
**Solution**: Verify data has sufficient fields populated

---

## 🔄 Next Steps

After Phase 2 completes:

1. ✅ Verify output in `data/processed/`
2. ✅ Review chunk JSON structure
3. ✅ Validate metadata completeness
4. ⏭️ **Next**: Run Phase 3 (Embeddings & Vector DB)

---

## 📞 Quick Links

- **Full Guide**: [PHASE2_IMPLEMENTATION.md](./PHASE2_IMPLEMENTATION.md)
- **Architecture**: [ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md)
- **Getting Started**: [QUICKSTART.md](./QUICKSTART.md)

---

**Status**: ✅ **Phase 2 Complete**  
**Ready for**: Phase 3 (Embeddings & Vector Database)  
**Last Updated**: March 5, 2026
