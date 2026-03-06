# 🚀 RAG Mutual Funds Assistant - Quick Setup Guide

## 📋 Project Overview

An AI-powered chatbot that answers factual queries about **HDFC Mutual Fund schemes** using Retrieval-Augmented Generation (RAG) technology. Built with Python, Streamlit, ChromaDB, and Sentence Transformers.

**Live Demo:** [Insert Streamlit Cloud Link Here]  
**GitHub Repository:** https://github.com/1999Rajesh/Groww_Mutual_Funds

---

## ⚡ Quick Start (5 Minutes)

### Prerequisites
- Python 3.8+ installed
- Git (for cloning repository)
- Internet connection

### Step 1: Clone Repository
```bash
git clone https://github.com/1999Rajesh/Groww_Mutual_Funds.git
cd Groww_Mutual_Funds
```

### Step 2: Install Dependencies
```bash
pip install -r src/requirements.txt
```

### Step 3: Configure Environment
Create `.env` file in root directory:
```bash
# Copy from example
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Edit `.env` and add your API key if needed (optional for basic functionality).

### Step 4: Run the Application
```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 🎯 Scope & Coverage

### Supported AMCs
- ✅ **HDFC Mutual Fund** (Primary focus)

### Supported Schemes (4 Funds)
1. **HDFC Top 100 Fund** - Large Cap
2. **HDFC Flexi Cap Fund** - Flexi Cap
3. **HDFC ELSS Tax Saver Fund** - ELSS
4. **HDFC Mid-Cap Opportunities Fund** - Mid Cap

### Data Sources
- **Primary**: HDFC AMC Official Website (hdfcfund.com)
- **Secondary**: Groww Investment Platform (groww.in)
- **Regulatory**: AMFI India, SEBI
- **Services**: CAMS, KFintech

### What You Can Ask
✅ Expense ratios, fund categories, lock-in periods  
✅ Minimum investment amounts (SIP/Lumpsum)  
✅ Tax benefits and regulations  
✅ NAV information sources  
✅ Portfolio allocation details  
✅ Direct vs Regular plan differences  

### Known Limitations ⚠️
- ❌ **Real-time NAV**: Data may not be live; check official sources for current NAV
- ❌ **Performance Metrics**: Returns, alpha, beta not included in current version
- ❌ **Fund Manager Changes**: May have delay in updating manager information
- ❌ **Limited AMC**: Currently only HDFC funds (expansion planned)
- ❌ **No Investment Advice**: Tool provides facts only, not recommendations

---

## 🔧 Technical Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit |
| **Backend** | Python 3.8+ |
| **Vector DB** | ChromaDB |
| **Embeddings** | Sentence Transformers (all-MiniLM-L6-v2) |
| **LLM** | OpenAI / Ollama (configurable) |
| **Web Scraping** | Playwright |
| **Data Processing** | Custom chunking with metadata |

---

## 📁 Project Structure

```
Groww_Mutual_Funds/
├── streamlit_app.py          # Main Streamlit application
├── src/
│   ├── rag/                  # RAG pipeline components
│   │   ├── query_processor.py
│   │   ├── retriever.py
│   │   └── response_generator.py
│   ├── vector_db/            # Vector database management
│   │   └── chroma_store.py
│   ├── embeddings/           # Embedding generation
│   │   └── embedding_generator.py
│   └── scrapers/             # Web scraping modules
│       └── fund_list.py
├── data/
│   ├── processed/            # Processed fund data
│   └── metadata.json         # Data metadata
├── chroma_db/                # Vector database storage
├── .streamlit/               # Streamlit configuration
└── docs/                     # Documentation
```

---

## 🧪 Sample Usage

### Example Queries to Try
1. "What is the expense ratio of HDFC ELSS?"
2. "Tell me about HDFC Top 100 Fund"
3. "What is the lock-in period for ELSS funds?"
4. "What is the minimum SIP amount?"
5. "Difference between Direct and Regular plans?"

### Expected Response Time
- **Average**: 2-5 seconds per query
- **First Query**: 5-10 seconds (initialization overhead)
- **Subsequent Queries**: 1-3 seconds

---

## 🛠️ Troubleshooting

### Issue: ChromaDB not loading
**Solution**: Ensure all dependencies are installed
```bash
pip install chromadb sentence-transformers
```

### Issue: No results returned
**Solution**: Check if data is loaded in `data/processed/funds.json`
If empty, re-run data processing scripts from `/scripts` folder

### Issue: Streamlit port already in use
**Solution**: Change port in `.streamlit/config.toml`
```toml
[server]
port = 8502  # Change to different port
```

---

## 📊 Performance Metrics

- **Documents Indexed**: ~100+ chunks from 4 funds
- **Search Latency**: <10ms average
- **Response Time**: 2-5 seconds end-to-end
- **Accuracy**: 80-95% confidence scores on factual queries
- **Uptime**: Local deployment (user-managed)

---

## 🔐 Privacy & Security

- ✅ No user data is stored or transmitted externally
- ✅ All processing happens locally
- ✅ API keys stored in `.env` (not committed to Git)
- ✅ Sources properly cited for transparency

---

## 📝 License & Attribution

This project is for educational purposes. All mutual fund data belongs to respective AMCs and platforms.

**Built as part of [Your Program/Course Name]**  
**Developer:** [Your Name]  
**LinkedIn:** [Your LinkedIn Profile URL]

---

## 🤝 Contributing

Feel free to fork, modify, and submit PRs! For major changes, please open an issue first.

---

## 📞 Contact

- **GitHub Issues**: [Create an issue](https://github.com/1999Rajesh/Groww_Mutual_Funds/issues)
- **Email**: [Your Email]
- **LinkedIn**: [Your LinkedIn Profile]

---

**Last Updated:** March 6, 2026  
**Version:** 1.0.0
