# Quick Start Guide - RAG Mutual Funds Chatbot

## Phase 1: Data Acquisition (Current Phase)

### Setup Instructions

#### 1. Install Python Dependencies

```bash
# Navigate to project directory
cd C:\Users\Rajesh\Documents\RAG_Mutual_Funds

# Create virtual environment (if not already done)
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install required packages
pip install -r src\requirements.txt
```

#### 2. Configure Environment

```bash
# Copy example environment file
copy .env.example .env

# Edit .env file with your settings
notepad .env
```

**Important settings to configure:**
- Database credentials (if you have PostgreSQL installed)
- LLM API keys (OpenAI or use local Ollama)
- Scraper delay and timeout settings

#### 3. Run the Scraper

```bash
# Scrape all configured funds
python run_scraper.py

# Or scrape a single fund
python run_scraper.py --fund "HDFC ELSS Tax Saver Fund"

# Use Selenium for JavaScript-heavy pages
python run_scraper.py --selenium
```

### Expected Output

The scraper will:
1. Connect to INDMoney website
2. Extract fund details for each configured scheme
3. Save data to `data/raw/` directory in JSON and CSV formats
4. Display progress and summary in console

**Sample Console Output:**
```
================================================================================
Starting Mutual Fund Data Scraper
================================================================================

Scraping HDFC ELSS Tax Saver Fund...
✓ Successfully scraped HDFC ELSS Tax Saver Fund

Scraping HDFC Small Cap Fund...
✓ Successfully scraped HDFC Small Cap Fund

...

================================================================================
Saving 8 funds to storage...
Saved JSON: data\raw\mutual_funds_20240305_010630.json
Saved CSV: data\raw\mutual_funds_20240305_010630.csv

================================================================================
SCRAPING SUMMARY
================================================================================

1. HDFC ELSS Tax Saver Fund
   Category: ELSS
   Expense Ratio: 0.68%
   Min SIP: ₹500
   Lock-in: 3 years
   Risk Level: Very High

...

================================================================================
Scraping completed successfully!
================================================================================
```

### Data Files Created

After running the scraper, you'll find:

- `data/raw/mutual_funds_YYYYMMDD_HHMMSS.json` - Complete fund data in JSON format
- `data/raw/mutual_funds_YYYYMMDD_HHMMSS.csv` - Fund data in CSV format
- Logs with detailed scraping information

### Viewing Scraped Data

**JSON Format:**
```json
{
  "metadata": {
    "scraped_at": "2024-03-05T01:06:30",
    "total_funds": 8,
    "fund_names": ["HDFC ELSS Tax Saver Fund", ...]
  },
  "data": [
    {
      "fund_name": "HDFC ELSS Tax Saver Fund",
      "category": "ELSS",
      "expense_ratio": 0.68,
      "minimum_sip": 500.0,
      "lock_in_period": "3 years",
      ...
    }
  ]
}
```

**CSV Format:**
| fund_name | category | expense_ratio | minimum_sip | lock_in_period | ... |
|-----------|----------|---------------|-------------|----------------|-----|
| HDFC ELSS Tax Saver Fund | ELSS | 0.68 | 500.0 | 3 years | ... |

### Troubleshooting

#### Issue: Scraper fails to fetch data

**Solution 1:** Check internet connection
```bash
ping www.indmoney.com
```

**Solution 2:** Increase timeout in `.env`
```env
TIMEOUT=60
SCRAPER_DELAY=3.0
```

**Solution 3:** Use Selenium for JavaScript content
```bash
python run_scraper.py --selenium
```

#### Issue: Import errors

**Solution:** Reinstall dependencies
```bash
pip uninstall -y beautifulsoup4 selenium requests
pip install beautifulsoup4==4.12.2 selenium==4.15.2 requests==2.31.0
```

#### Issue: No data extracted

This could mean:
1. Website structure changed - update selectors in `src/scrapers/indmoney_scraper.py`
2. Rate limiting - increase delay between requests
3. Temporary website issue - try again later

### Next Steps

Once you have successfully scraped the data:

1. **Verify Data Quality**
   - Check JSON/CSV files for completeness
   - Ensure all expected fields are populated
   - Look for any error messages in logs

2. **Review Scraped Fields**
   - Fund name and category
   - Expense ratio
   - Minimum SIP amount
   - Lock-in period
   - Exit load
   - Risk level
   - Benchmark
   - Returns (1Y, 3Y, 5Y)

3. **Prepare for Phase 2**
   - Data cleaning and normalization
   - Chunking strategy implementation
   - Metadata enrichment

### Current Limitations

**Phase 1 (Current):**
- ✅ Web scraping from INDMoney
- ✅ Structured data models
- ✅ Raw data storage
- ❌ No data processing yet
- ❌ No embeddings/vector database
- ❌ No RAG pipeline
- ❌ No chatbot interface

**Coming in Phase 2:**
- Data cleaning and standardization
- Intelligent chunking strategies
- Q&A pair generation
- Preparation for embedding generation

### Supported Query Types (Future)

Once the full RAG pipeline is implemented, users will be able to ask:

**Factual Questions:**
- "What is the expense ratio of HDFC ELSS Tax Saver Fund?"
- "What is the lock-in period for ELSS funds?"
- "Minimum SIP amount for HDFC Small Cap Fund?"
- "Exit load for HDFC Large Cap Fund?"
- "Risk level of HDFC Mid Cap Fund?"
- "Fund manager for HDFC Focused 30 Fund?"

**Not Supported (Investment Advice):**
- "Which fund should I invest in?"
- "Is HDFC Small Cap better than HDFC Large Cap?"
- "Should I start a SIP now?"

### Project Structure Overview

```
RAG_Mutual_Funds/
├── src/                          # Source code
│   ├── scrapers/                 # Web scraping modules
│   │   ├── indmoney_scraper.py   # Main scraper
│   │   └── fund_list.py          # Fund configurations
│   ├── models/                   # Data models
│   │   └── fund_schema.py        # Pydantic schemas
│   ├── storage/                  # Data storage
│   │   └── raw_data_storage.py   # JSON/CSV storage
│   └── config.py                 # Configuration
├── data/                         # Data directories
│   ├── raw/                      # Scraped data
│   └── processed/                # Processed data
├── run_scraper.py               # Main scraper runner
└── README.md                     # Documentation
```

### Getting Help

If you encounter issues:

1. Check the logs in console output
2. Review `README.md` for detailed documentation
3. Inspect `src/config.py` for configuration options
4. Verify `.env` settings are correct

### Testing the Setup

Run a simple test to verify everything is working:

```bash
# Test imports
python -c "from src.scrapers.indmoney_scraper import INDMoneyScraper; print('Imports OK')"

# Test configuration
python -c "from src.config import TARGET_FUNDS; print(f'Configured funds: {len(TARGET_FUNDS)}')"

# Test scraper initialization
python -c "from src.scrapers.indmoney_scraper import INDMoneyScraper; s = INDMoneyScraper(); print('Scraper initialized')"
```

All commands should execute without errors if setup is correct.

---

**Note:** This is Phase 1 implementation only. Full RAG pipeline with chatbot interface will be available in subsequent phases.
