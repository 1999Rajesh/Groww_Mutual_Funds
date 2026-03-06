# Phase 1 Implementation - FAQ Assistant

## 🎯 Overview

This implementation delivers a **working FAQ assistant prototype** that answers factual queries about HDFC Mutual Fund schemes with proper citations.

### Scope
- **AMC**: HDFC Mutual Fund
- **Schemes**: 21 schemes across diverse categories (Large Cap, Small Cap, ELSS, Hybrid, Debt, etc.)
- **Primary Focus**: 6 key schemes for MVP

---

## 📊 Data Coverage

### Primary Schemes (MVP)
1. **HDFC ELSS Tax Saver Fund** - ELSS (Tax Saving)
2. **HDFC Large Cap Fund** - Large Cap Equity
3. **HDFC Small Cap Fund** - Small Cap Equity
4. **HDFC Mid Cap Fund** - Mid Cap Equity
5. **HDFC Balanced Advantage Fund** - Hybrid
6. **HDFC Liquid Fund** - Debt/Liquid

### All 21 Schemes Configured
- Gold ETF FoF, Silver ETF FoF
- Children's Fund (2 variants)
- Retirement Savings Fund (3 variants)
- Multi Asset FoF, Multi Cap Fund
- Corporate Bond, Money Market, Long Duration Debt
- And more...

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd c:\Users\Rajesh\Documents\RAG_Mutual_Funds
pip install -r src\requirements.txt
```

### Step 2: Run Phase 1

```bash
python run_phase1.py
```

### Step 3: Follow the Menu

```
================================================================================
HDFC Mutual Funds FAQ Assistant - Phase 1
================================================================================

Options:
1. Scrape data from INDMoney
2. Launch FAQ Assistant (CLI)
3. Open Web UI (HTML file)
4. Exit

Note: Run option 1 first before using the assistant
================================================================================

Enter your choice (1-4): 
```

---

## 📋 Features Implemented

### ✅ 1. Web Scraping
- Scrapes data from 21 INDMoney fund pages
- Extracts: Expense ratio, SIP amount, lock-in, exit load, risk level, benchmark, etc.
- Saves to JSON and CSV formats with timestamps

### ✅ 2. FAQ Assistant (CLI)
- Answers factual queries only
- Shows citation links in every answer
- Refuses opinionated questions politely
- Provides example questions

### ✅ 3. Web UI (HTML)
- Clean, modern interface
- Example questions (clickable)
- Real-time response display
- Citation links
- Mobile responsive

### ✅ 4. Knowledge Base
- Built from scraped data
- Topic-based organization
- Question-answer pairs
- Source tracking

---

## 💬 Example Queries

### Supported (Factual)
✅ "What is the expense ratio of HDFC ELSS Tax Saver Fund?"
✅ "What is the minimum SIP for HDFC Large Cap Fund?"
✅ "ELSS lock-in period?"
✅ "Exit load for HDFC Small Cap Fund?"
✅ "Risk level of HDFC Balanced Advantage Fund?"
✅ "Benchmark for HDFC Multi Cap Fund?"

### Refused (Opinionated)
❌ "Should I invest in HDFC ELSS?"
❌ "Which fund is better - Large Cap or Small Cap?"
❌ "Is this a good time to buy?"
❌ "Recommend me a tax-saving fund"

**Response for refused queries:**
> "I can only provide factual information about mutual funds. I cannot provide investment advice or recommendations. For personalized investment advice, please consult a SEBI-registered financial advisor."

---

## 🗂️ File Structure

```
RAG_Mutual_Funds/
├── src/
│   ├── scrapers/
│   │   ├── indmoney_scraper.py      # Web scraper
│   │   └── fund_list.py             # 21 schemes configured
│   ├── models/
│   │   └── fund_schema.py           # Data models
│   ├── storage/
│   │   └── raw_data_storage.py      # JSON/CSV storage
│   ├── config.py                     # Configuration
│   └── faq_assistant.py              # FAQ Assistant logic
├── faq_ui.html                       # Web UI
├── run_phase1.py                     # Main runner
└── data/
    └── raw/                          # Scraped data
```

---

## 🔧 How It Works

### Data Flow

```
INDMoney Website
    ↓
Web Scraper (INDMoneyScraper)
    ↓
Fund Data (21 schemes)
    ↓
RawDataStorage (JSON/CSV)
    ↓
Knowledge Base Builder
    ↓
FAQ Assistant
    ↓
User Query → Answer + Citation
```

### Query Processing

1. **User asks question**
2. **Match fund name** in query
3. **Identify topic** (expense_ratio, sip, lock_in, etc.)
4. **Search knowledge base** for best match
5. **Return answer** with confidence score
6. **Include citation** link

### Opinion Detection

Queries containing keywords like:
- "should i", "should we"
- "buy", "sell", "invest"
- "recommend", "suggest"
- "better", "best", "good"

→ Trigger polite refusal with educational resource link

---

## 📖 Usage Examples

### Command-Line Interface

```bash
$ python run_phase1.py

# Choose option 2

👋 Welcome to HDFC Mutual Funds FAQ Assistant!

I can answer factual questions about HDFC Mutual Fund schemes.
Ask me about expense ratios, SIP amounts, lock-in periods, exit loads, and more.

⚠️  Facts-only. No investment advice.

Example questions:
  1. What is the expense ratio of HDFC ELSS Tax Saver Fund?
  2. What is the minimum SIP for HDFC Large Cap Fund?
  3. What is the lock-in period for ELSS funds?
  4. Exit load for HDFC Small Cap Fund?
  5. Risk level of HDFC Balanced Advantage Fund?

================================================================================
Type your question below (or 'quit' to exit):

> What is the expense ratio of HDFC ELSS?

🤔 Thinking...

💡 Answer: The expense ratio of HDFC ELSS Tax Saver Fund is 0.68%

📚 Source: https://www.indmoney.com/mutual-funds/hdfc-elss-taxsaver-direct-plan-growth-option-2685

--------------------------------------------------------------------------------
```

### Web Interface

1. Run `python run_phase1.py`
2. Choose option 3
3. Opens in browser automatically
4. Click example questions or type your own

---

## 🎨 UI Features

### Web Interface Highlights

- **Welcome Message**: Clear introduction
- **Disclaimer Banner**: "Facts-only. No investment advice."
- **Example Questions**: 5 clickable examples
- **Input Field**: Type custom questions
- **Response Card**: Beautiful answer display
- **Citation Link**: Source URL shown
- **Loading Indicator**: "Thinking..." animation
- **Mobile Responsive**: Works on all devices

---

## 📊 Data Extraction Fields

For each scheme, the scraper extracts:

| Field | Description | Example |
|-------|-------------|---------|
| fund_name | Scheme name | HDFC ELSS Tax Saver Fund |
| scheme_type | Plan type | Direct Growth |
| category | Fund category | ELSS |
| expense_ratio | Annual fee (%) | 0.68 |
| minimum_sip | Min SIP amount (₹) | 500 |
| minimum_lumpsum | Min lumpsum (₹) | 5000 |
| lock_in_period | Lock-in duration | 3 years |
| exit_load | Exit load details | 1% within 1 year |
| risk_level | Risk category | Very High |
| benchmark | Benchmark index | NIFTY 500 TRI |
| fund_manager | Fund manager name | Chirag Setalvad |
| aum | Assets Under Management | ₹28,500 Cr |
| nav | Current NAV | ₹845.32 |
| returns_1y | 1-year return (%) | 12.5 |
| returns_3y | 3-year return (%) | 15.2 |
| returns_5y | 5-year return (%) | 18.7 |
| source_url | INDMoney URL | Full URL |

---

## 🔍 Testing

### Test Queries

Try these to verify functionality:

1. **Expense Ratio Query**
   - Input: "What is the expense ratio of HDFC ELSS Tax Saver Fund?"
   - Expected: Answer with percentage + citation

2. **SIP Query**
   - Input: "Minimum SIP for HDFC Large Cap?"
   - Expected: Answer with amount + citation

3. **Lock-in Query**
   - Input: "ELSS lock-in period?"
   - Expected: "3 years" + explanation + citation

4. **Exit Load Query**
   - Input: "Exit load for HDFC Small Cap Fund?"
   - Expected: Exit load details + citation

5. **Risk Query**
   - Input: "Risk level of HDFC Balanced Advantage?"
   - Expected: Risk category + citation

6. **Opinion Query (Should Refuse)**
   - Input: "Should I invest in HDFC ELSS?"
   - Expected: Polite refusal + SEBI resource link

---

## ⚙️ Configuration

### Environment Variables (.env)

```env
# No special configuration needed for Phase 1
# Default settings work out of the box

SCRAPER_DELAY=2.0        # Delay between requests (seconds)
MAX_RETRIES=3           # Retry attempts
TIMEOUT=30              # Request timeout (seconds)
LOG_LEVEL=INFO          # Logging level
```

### Customization

Edit `src/scrapers/fund_list.py` to:
- Add/remove schemes
- Change primary schemes for MVP
- Update categories

---

## 🐛 Troubleshooting

### Issue: No data scraped

**Solution:**
1. Check internet connection
2. Verify INDMoney website is accessible
3. Increase delay in `.env`: `SCRAPER_DELAY=3.0`
4. Try with Selenium: Modify scraper to use `use_selenium=True`

### Issue: FAQ Assistant not finding answers

**Solution:**
1. Ensure you've run "Option 1" (Scrape data) first
2. Check if data files exist in `data/raw/`
3. Verify JSON format is correct
4. Re-run scraper to refresh data

### Issue: Web UI not loading

**Solution:**
1. Check if `faq_ui.html` exists
2. Open file directly in browser
3. Check browser console for errors
4. Try different browser

---

## 📈 Performance Metrics

### Scraping Performance
- **Time per scheme**: ~3-5 seconds
- **Total time (6 primary schemes)**: ~30 seconds
- **Success rate**: Target >80%
- **Data accuracy**: Manual verification recommended

### Query Response Time
- **CLI**: <1 second
- **Web UI**: <1 second (simulated API call)
- **Confidence threshold**: 40% minimum for matches

---

## 🎯 Success Criteria

Phase 1 is successful if:

- ✅ All 6 primary schemes scraped successfully
- ✅ Data saved in JSON and CSV formats
- ✅ FAQ Assistant answers factual queries correctly
- ✅ Citations shown in every answer
- ✅ Opinionated questions refused politely
- ✅ Web UI functional with example questions
- ✅ CLI interface working smoothly

---

## 🔄 Next Steps

### Before Phase 2

1. **Test thoroughly** with all 21 schemes
2. **Verify data accuracy** manually
3. **Add more example queries** to UI
4. **Improve matching algorithm** if needed
5. **Enhance error messages**

### Phase 2 Preview

- Data cleaning and normalization
- Intelligent chunking strategies
- Q&A pair generation
- Embedding preparation

---

## 📝 Notes

### Important

1. **Data Freshness**: Run scraper periodically to update data
2. **Manual Verification**: Always verify critical financial data
3. **Rate Limiting**: Built-in delays respect website policies
4. **Educational Use**: This is a prototype, not production-ready

### Future Enhancements

- Real RAG pipeline with embeddings
- Better semantic search
- Multiple AMC support
- Historical data tracking
- Performance charts
- Comparison features

---

## 📞 Support

For issues or questions:
1. Check logs in console output
2. Review `src/config.py` for settings
3. Inspect `data/raw/` for scraped files
4. Verify dependencies installed correctly

---

**Status**: ✅ Phase 1 Complete  
**Version**: 1.0  
**Last Updated**: March 5, 2026  
**Data Source**: INDMoney (https://www.indmoney.com/)
