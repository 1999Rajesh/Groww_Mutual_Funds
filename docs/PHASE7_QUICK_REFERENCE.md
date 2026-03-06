# Phase 7 Quick Start Guide

## 🚀 Running the CLI Chatbot

### Prerequisites Check

```bash
# 1. Install dependencies
pip install -r src/requirements.txt

# 2. Install Playwright browser
playwright install chromium

# 3. Set API key
export GOOGLE_API_KEY='your-gemini-api-key'

# 4. Verify ChromaDB installed
pip show chromadb
```

### Quick Start (3 Steps)

```bash
# Step 1: Navigate to project
cd c:\Users\Rajesh\Documents\RAG_Mutual_Funds

# Step 2: Run Phase 7
python run_phase7.py

# Step 3: Start chatting!
You: What is the expense ratio of HDFC ELSS Fund?
```

---

## 💬 Example Questions

Try these example queries:

```
✅ Factual Questions:
• What is the expense ratio of HDFC ELSS Tax Saver Fund?
• Minimum SIP amount for HDFC Large Cap Fund?
• What is the lock-in period for ELSS funds?
• Exit load for HDFC Small Cap Fund?
• Risk level of HDFC Balanced Advantage Fund?
• AUM of HDFC Mid Cap Fund?
• NAV of HDFC Flexi Cap Fund?
• Who manages HDFC Equity Fund?

❌ Opinion Questions (Will be refused):
• Should I invest in HDFC ELSS?
• Which fund is better - Large Cap or Small Cap?
• Is this a good time to buy mutual funds?
• Can you recommend a fund for tax saving?
```

---

## 🎮 Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `/help` | Show help message | `/help` |
| `/history` | Show conversation history | `/history` |
| `/clear` | Clear conversation | `/clear` |
| `/stats` | Show system statistics | `/stats` |
| `/export` | Export conversation | `/export` |
| `/quit` | Exit chatbot | `/quit` |

---

## ⚙️ Configuration Options

### Default Setup (Recommended)

```
Vector database type [chromadb]: chromadb
LLM model [gemini-1.5-flash]: gemini-1.5-flash
Vector DB path [./chroma_db]: ./chroma_db
```

### PostgreSQL Setup (Production)

```
Vector database type [chromadb]: postgresql
PostgreSQL connection string: postgresql://user:pass@localhost:5432/db
```

### Advanced LLM Models

```
LLM model [gemini-1.5-flash]: gemini-3.5-flash
```

---

## 📊 Understanding Output

### Response Format

```
--------------------------------------------------------------------------------

[Answer text with factual information]

📌 Source: https://www.indmoney.com/mutual-funds/...

Details:
  Confidence: 85%
  Fund: HDFC ELSS Tax Saver Fund
  Intent: expense_ratio
  Sources: 3 chunks

--------------------------------------------------------------------------------
```

**Components**:
- **Answer**: Main response text
- **Source**: Citation link with 📌 icon
- **Confidence**: AI confidence score (0-100%)
- **Fund**: Detected fund name from query
- **Intent**: Query intent classification
- **Sources**: Number of chunks retrieved

---

## 🔧 Troubleshooting

### "Module not found" errors

```bash
# Reinstall dependencies
pip uninstall playwright google-generativeai chromadb
pip install -r src/requirements.txt
playwright install chromium
```

### "GOOGLE_API_KEY not set"

```bash
# Windows PowerShell
$env:GOOGLE_API_KEY="your-api-key-here"

# Linux/Mac
export GOOGLE_API_KEY='your-api-key-here'
```

### "No data found" or "0 chunks retrieved"

Run previous phases first:
```bash
python run_phase1.py   # Scrape data
python run_phase2.py   # Process data
python run_phase3.py   # Generate embeddings
```

---

## 📈 Performance Expectations

| Metric | Expected Value |
|--------|----------------|
| Query Processing | <10ms |
| Vector Search | <15ms |
| LLM Generation | 1-2 seconds |
| Total Response Time | 2-3 seconds |

---

## 💾 Data Storage

### ChromaDB (Default)
- Location: `./chroma_db/`
- Format: SQLite-based vector storage
- Size: ~50-100MB for all funds

### Conversation History
- File: `cli_history.txt`
- Auto-saved between sessions
- Cleared with `/clear` command

### Exported Conversations
- File: `conversation_export.txt`
- Created with `/export` command
- Plain text format

---

## 🎯 Best Practices

1. **Start Simple**: Begin with basic factual questions
2. **Use Commands**: Leverage `/stats` to monitor system
3. **Export Important**: Save valuable conversations with `/export`
4. **Clear Regularly**: Use `/clear` for fresh sessions
5. **Check Sources**: Review citation links for verification

---

## 🔄 Session Flow

```
1. Run: python run_phase7.py
2. Configure: Select database and LLM
3. Initialize: Wait for components to load
4. Chat: Ask questions naturally
5. Explore: Use commands to manage session
6. Export: Save important conversations
7. Quit: Exit gracefully with /quit
```

---

## ✅ Success Indicators

You'll know it's working when you see:

```
✓ Query Processor ready
✓ ChromaDB loaded at ./chroma_db
✓ RAG Retriever ready
✓ gemini-1.5-flash ready

================================================================================
✅ All Components Initialized Successfully!
================================================================================
```

---

## 🆘 Getting Help

If issues persist:

1. Check logs in terminal output
2. Verify all prerequisites installed
3. Ensure API keys configured correctly
4. Confirm database path accessible
5. Review PHASE7_IMPLEMENTATION.md for details

---

**Quick Test**: If you can ask "What is the expense ratio of HDFC ELSS Fund?" and get an answer with citation, Phase 7 is working! ✅
