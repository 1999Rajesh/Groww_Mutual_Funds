# Phase 1 - Quick Reference Card

## 🚀 Getting Started (3 Steps)

```bash
cd c:\Users\Rajesh\Documents\RAG_Mutual_Funds
pip install -r src\requirements.txt
python run_phase1.py
```

---

## 📋 Menu Options

```
1. Scrape data from INDMoney     ← Run this FIRST
2. Launch FAQ Assistant (CLI)    ← Command-line Q&A
3. Open Web UI (HTML file)       ← Browser interface
4. Exit                          ← Quit
```

---

## 💬 Example Queries to Try

### Expense Ratio
> "What is the expense ratio of HDFC ELSS Tax Saver Fund?"

### Minimum SIP
> "What is the minimum SIP for HDFC Large Cap Fund?"

### Lock-in Period
> "ELSS lock-in period?"

### Exit Load
> "Exit load for HDFC Small Cap Fund?"

### Risk Level
> "Risk level of HDFC Balanced Advantage Fund?"

### Opinion Question (Will be refused)
> "Should I invest in HDFC ELSS?"

---

## ✅ What Works

- ✅ Scrapes 6 primary HDFC schemes
- ✅ Answers factual questions
- ✅ Shows citation links
- ✅ Refuses opinion questions politely
- ✅ CLI and Web interfaces
- ✅ Example questions provided
- ✅ Facts-only messaging

---

## 🎯 Key Files

| File | Purpose |
|------|---------|
| `run_phase1.py` | Main launcher |
| `faq_ui.html` | Web interface |
| `src/faq_assistant.py` | FAQ logic |
| `src/scrapers/fund_list.py` | 21 schemes configured |

---

## ⚠️ Important Notes

1. **Run Option 1 first** before using assistant
2. **Internet required** for scraping
3. **Data saved locally** in `data/raw/`
4. **Facts-only** - no investment advice

---

## 🐛 Quick Troubleshooting

**No data scraped?**
- Check internet connection
- Increase delay: `SCRAPER_DELAY=3.0` in `.env`

**Assistant not finding answers?**
- Run "Option 1" to scrape data first
- Check `data/raw/` folder exists

**Web UI not opening?**
- Manually open `faq_ui.html` in browser

---

## 📞 Help Commands

```bash
# View logs with details
python run_phase1.py --verbose

# Test scraper only
python -c "from src.scrapers.indmoney_scraper import INDMoneyScraper; s = INDMoneyScraper(); print(s.scrape_fund_scheme('HDFC ELSS Tax Saver Fund', 'hdfc-elss-taxsaver-direct-plan-growth-option-2685'))"

# Check dependencies
pip list | grep -E "beautifulsoup4|requests|selenium"
```

---

## 🎨 UI Preview

```
┌────────────────────────────────────────────┐
│  💼 HDFC Mutual Funds FAQ Assistant        │
│  Your intelligent FAQ assistant            │
├────────────────────────────────────────────┤
│  ⚠️ Facts-only. No investment advice.      │
├────────────────────────────────────────────┤
│  📋 Example Questions:                     │
│  • What is the expense ratio of...?        │
│  • What is the minimum SIP for...?         │
│  • What is the lock-in period for...?      │
│  • Exit load for...?                       │
│  • Risk level of...?                       │
├────────────────────────────────────────────┤
│  Type your question here...                │
│  [_________________________________]       │
├────────────────────────────────────────────┤
│  💡 Answer: The expense ratio is 0.68%     │
│  📚 Source: https://www.indmoney.com/...   │
└────────────────────────────────────────────┘
```

---

## 📊 Coverage

**AMC**: HDFC Mutual Fund  
**Schemes**: 21 total (6 primary focus)  
**Categories**: ELSS, Large Cap, Small Cap, Mid Cap, Hybrid, Debt, FoF, etc.

---

## ✨ Success Indicators

✅ Data scraped successfully (check `data/raw/`)  
✅ Assistant answers with citations  
✅ Opinion questions refused politely  
✅ Both CLI and Web UI working  
✅ Example questions functional  

---

**Status**: ✅ Phase 1 Complete  
**Version**: 1.0  
**Date**: March 5, 2026
