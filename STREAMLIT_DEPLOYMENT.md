# Streamlit Deployment Guide - Mutual Funds Chatbot

## Quick Start

### 1. Install Dependencies
```bash
pip install -r src/requirements.txt
```

### 2. Run the Application
```bash
streamlit run streamlit_app.py --server.port 8501
```

### 3. Access the Chatbot
Open your browser and go to: `http://localhost:8501`

---

## Features

### Chat Interface
- 💬 Natural language chat interface
- 📚 Source citations with links to HDFC AMC & Groww
- 📊 Confidence scores for responses
- ⚡ Real-time query processing

### Sidebar Information
- ✅ System status indicator
- 📊 Document count in vector database
- 📋 Data sources (HDFC AMC, Groww)
- 🕐 Last updated timestamp
- 💡 Sample questions

### RAG Pipeline Integration
- Uses existing ChromaDB vector store
- Sentence Transformers embeddings (all-MiniLM-L6-v2)
- Query intent extraction
- Multi-source citation support

---

## Configuration

### Environment Variables
Create `.env` file:
```bash
GOOGLE_API_KEY=your_key_here  # Optional, for Gemini LLM
```

### Customization Options

**Port Number:**
```bash
streamlit run streamlit_app.py --server.port 8501
```

**Production Mode:**
```bash
streamlit run streamlit_app.py \
  --server.port 8501 \
  --server.headless true \
  --server.enableXsrfProtection true
```

---

## Architecture

```
┌─────────────────────────────────────┐
│     Streamlit Frontend              │
│  ┌──────────────────────────────┐   │
│  │  Chat Interface UI           │   │
│  │  • Message history           │   │
│  │  • Citation display          │   │
│  │  • Metadata sidebar          │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│     RAG Pipeline                    │
│  ┌──────────────────────────────┐   │
│  │  Query Processor             │   │
│  │  • Intent extraction         │   │
│  │  • Query enhancement         │   │
│  └──────────────────────────────┘   │
│                ↓                     │
│  ┌──────────────────────────────┐   │
│  │  Embedding Generator         │   │
│  │  • all-MiniLM-L6-v2          │   │
│  │  • 384 dimensions            │   │
│  └──────────────────────────────┘   │
│                ↓                     │
│  ┌──────────────────────────────┐   │
│  │  ChromaDB Vector Store       │   │
│  │  • Fund documents            │   │
│  │  • Metadata with URLs        │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## Deployment Options

### Local Development
```bash
streamlit run streamlit_app.py
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install -r src/requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py"]
```

Build and run:
```bash
docker build -t mutual-funds-chatbot .
docker run -p 8501:8501 mutual-funds-chatbot
```

### Cloud Deployment (Streamlit Cloud)
1. Push code to GitHub
2. Connect repository to [share.streamlit.io](https://share.streamlit.io)
3. Set main file path: `streamlit_app.py`
4. Add requirements: `src/requirements.txt`

---

## Data Sources

The chatbot uses information from:
- **HDFC AMC** (hdfcfund.com) - Primary source
- **Groww** (groww.in) - Alternative source

All citations link directly to these trusted sources.

---

## Troubleshooting

### Issue: RAG pipeline not initializing
**Solution:** Check if ChromaDB is properly initialized
```python
from src.vector_db.chroma_store import ChromaVectorStore
store = ChromaVectorStore()
print(f"Collection count: {store.collection.count()}")
```

### Issue: No responses showing
**Solution:** Verify data is loaded
```bash
python scripts/quick_load_data.py
```

### Issue: Port already in use
**Solution:** Use different port
```bash
streamlit run streamlit_app.py --server.port 8502
```

---

## Performance Optimization

1. **Enable Caching**: The app uses `@st.cache_resource` for RAG components
2. **Optimize Embeddings**: Pre-computed embeddings stored in ChromaDB
3. **Query Caching**: Similar queries can be cached for faster responses

---

## Security Considerations

For production deployment:
- Enable XSRF protection
- Use HTTPS
- Implement rate limiting if needed
- Secure API endpoints
- Monitor usage metrics

---

## Support

For issues or questions:
1. Check logs in terminal
2. Verify all dependencies installed
3. Ensure data files exist in `/data/processed/`
4. Test RAG pipeline independently first

---

**Last Updated:** March 6, 2026  
**Version:** 1.0.0
