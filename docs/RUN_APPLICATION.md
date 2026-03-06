# 🚀 Running the RAG Mutual Funds Application

## ✅ **Quick Start Guide**

### Step 1: Start Backend API (Phase 8)

Open a terminal/PowerShell window:

```bash
cd c:\Users\Rajesh\Documents\RAG_Mutual_Funds

# Activate virtual environment (if using one)
.venv\Scripts\activate

# Start backend server
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output**:
```
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Starting up RAG Mutual Funds API...
INFO:     Initializing RAG pipeline...
✓ Query Processor loaded
✓ ChromaDB loaded
✓ Embedding Generator loaded
✓ gemini-1.5-flash loaded
✅ RAG Pipeline initialized successfully
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Backend is now running at**: http://localhost:8000  
**API Documentation**: http://localhost:8000/docs

---

### Step 2: Start Frontend Web App (Phase 9)

Open a **NEW** terminal/PowerShell window:

```bash
cd c:\Users\Rajesh\Documents\RAG_Mutual_Funds\frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**Expected Output**:
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
compiled successfully in 2.5s
✓ Ready in 3.1s
```

**Frontend is now running at**: http://localhost:3000

---

### Step 3: Open the Application

1. Open your web browser
2. Navigate to: **http://localhost:3000**
3. You'll see the RAG Mutual Funds chat interface!

---

## 🎨 What You'll See

### Welcome Screen

When you first open http://localhost:3000, you'll see:

```
┌─────────────────────────────────────────┐
│ 🤖 RAG Mutual Funds Assistant           │
│    AI-powered mutual fund information   │
│                              [Clear Chat]│
├─────────────────────────────────────────┤
│                                         │
│         Welcome to RAG Assistant        │
│                                         │
│  Ask me anything about mutual funds!    │
│                                         │
│  ┌──────────────────┬────────────────┐ │
│  │ What is expense  │ Minimum SIP    │ │
│  │ ratio of HDFC?   │ for large cap? │ │
│  └──────────────────┴────────────────┘ │
│                                         │
│  ┌──────────────────┬────────────────┐ │
│  │ Lock-in period   │ Exit load for  │ │
│  │ for tax saver?   │ HDFC Small Cap?│ │
│  └──────────────────┴────────────────┘ │
│                                         │
├─────────────────────────────────────────┤
│ [Ask about mutual funds...]  [Send ▶]  │
│ This assistant provides factual         │
│ information only, not investment advice.│
└─────────────────────────────────────────┘
```

### Chat Interface

After asking a question:

```
┌─────────────────────────────────────────┐
│ 🤖 RAG Mutual Funds Assistant     [🗑]  │
├─────────────────────────────────────────┤
│                                         │
│ You:                                    │
│ What is the expense ratio of HDFC ELSS? │
│                              [👤]       │
│                                         │
│          🤖                             │
│ HDFC ELSS Tax Saver Fund has an         │
│ expense ratio of 0.68%. This is a       │
│ direct plan growth option.              │
│                                         │
│ 📌 Source 🔗                            │
│ Confidence: 85% | Sources: 3            │
│                                         │
├─────────────────────────────────────────┤
│ [Type your question...]      [Send ▶]  │
└─────────────────────────────────────────┘
```

---

## 🧪 Test Questions to Try

Once the application is running, try these questions:

### Basic Queries
1. "What is the expense ratio of HDFC ELSS Fund?"
2. "Minimum SIP amount for large cap funds?"
3. "What is the lock-in period for ELSS funds?"
4. "Exit load for HDFC Small Cap Fund?"
5. "Risk level of balanced advantage funds?"

### Advanced Queries
6. "Compare expense ratios of large cap vs small cap funds"
7. "Which funds have the lowest minimum SIP?"
8. "What are the returns of HDFC mid cap fund?"
9. "Tell me about tax saver funds"
10. "NAV of HDFC flexi cap fund?"

### Opinion Queries (Will be Refused)
- "Should I invest in HDFC ELSS?" ❌
- "Which fund is better?" ❌
- "Is this a good time to buy?" ❌

---

## 🔧 Troubleshooting

### Backend Won't Start

**Error**: "ModuleNotFoundError: No module named 'fastapi'"

**Solution**:
```bash
pip install fastapi uvicorn pyjwt passlib python-jose[cryptography]
```

### Frontend Won't Start

**Error**: "Module not found"

**Solution**:
```bash
cd frontend
npm install
```

### Can't Access http://localhost:3000

**Check**:
1. Both terminals are running
2. No firewall blocking ports 8000 and 3000
3. Check terminal output for errors

### "GOOGLE_API_KEY not set" Warning

The application will still work but will use template-based responses instead of AI-generated ones.

To enable Gemini LLM:
```bash
export GOOGLE_API_KEY='your-api-key-here'
```

Or create a `.env` file:
```
GOOGLE_API_KEY=your-api-key-here
```

---

## 📊 System Status

### Check Backend Health

Open in browser: http://localhost:8000/health

**Expected Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-03-05T...",
  "components": {
    "api": true,
    "rag_pipeline": true,
    "vector_store": true,
    "llm": true
  }
}
```

### Check API Documentation

Visit: http://localhost:8000/docs

You'll see interactive Swagger UI where you can:
- View all available endpoints
- Test API calls directly
- See request/response schemas

---

## 🛑 Stopping the Application

### Stop Backend
In the terminal running the backend, press: **Ctrl+C**

### Stop Frontend
In the terminal running the frontend, press: **Ctrl+C**

---

## 📝 Quick Reference

| Component | URL | Port | Command |
|-----------|-----|------|---------|
| **Frontend** | http://localhost:3000 | 3000 | `npm run dev` |
| **Backend API** | http://localhost:8000 | 8000 | `uvicorn src.api.main:app` |
| **API Docs** | http://localhost:8000/docs | 8000 | Auto-generated |

---

## ✅ Success Indicators

You know everything is working when:

✅ Backend shows: "Uvicorn running on http://0.0.0.0:8000"  
✅ Frontend shows: "Ready in X.Xs"  
✅ Can access http://localhost:3000 without errors  
✅ Can type and send messages  
✅ Get responses to questions  
✅ Citations appear in responses  

---

## 🎯 Next Steps After Testing

1. **Explore the UI**: Click example queries, test different questions
2. **Check API Docs**: Visit http://localhost:8000/docs
3. **Review Code**: Look at the implementation files
4. **Customize**: Modify the UI colors, add features
5. **Deploy**: Prepare for production deployment

---

**Happy Testing!** 🚀

If you encounter any issues, check the terminal outputs for error messages and refer to the troubleshooting section above.
