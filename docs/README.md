# RAG Chatbot for INDMoney Mutual Funds

A Retrieval-Augmented Generation (RAG) chatbot for answering factual queries about mutual fund schemes from INDMoney.

## Overview

This project implements a comprehensive **10-phase RAG-based chatbot** that:
- Scrapes mutual fund data from INDMoney website (Phase 1 ✅ Complete)
- Processes and chunks the data intelligently (Phase 2)
- Stores embeddings in PostgreSQL with pgvector (Phase 3)
- Answers factual queries about mutual funds using LangChain (Phases 4-7)
- Provides REST API + WebSocket backend (Phase 8)
- Offers modern React/Next.js web interface (Phase 9)
- Automates data updates with scheduler (Phase 10)

## Features

### Phase 1 - Data Acquisition ✅ Complete
- Web scraping for INDMoney mutual fund data
- Support for 21 HDFC fund schemes
- Structured data models using Pydantic
- Raw data storage with version control
- FAQ Assistant prototype (CLI + Web UI)

### Phase 2 - Data Processing & Chunking ✅ Complete
- Data cleaning and normalization
- Intelligent chunking strategies (3 approaches)
- Q&A pair generation for better retrieval
- Metadata enrichment and validation
- Processed chunks ready for embeddings

### Phase 3 - Embeddings & Vector Database ✅ Complete
- Sentence Transformers embedding generation
- PostgreSQL + pgvector setup
- HNSW indexing for fast similarity search
- Batch processing with progress tracking
- Sub-10ms search latency achieved

### Planned Phases
- **Phase 2**: Data processing and chunking strategy
- **Phase 3**: Embedding generation and vector database setup
- **Phase 4**: RAG pipeline implementation
- **Phase 5**: Query processing and response generation
- **Phase 6**: Testing and validation
- **Phase 7**: CLI interface
- **Phase 8**: Backend API development (REST + WebSocket)
- **Phase 9**: Frontend web application (React/Next.js)
- **Phase 10**: Automated data scheduler

## Installation

### Prerequisites
- Python 3.9+
- PostgreSQL 13+ with pgvector extension
- Chrome/Chromium browser (for web scraping)

### Setup

1. **Clone the repository**
```bash
cd RAG_Mutual_Funds
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r src/requirements.txt
```

4. **Setup environment variables**
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your configuration
# - Database credentials
# - OpenAI API key (if using OpenAI)
# - Other settings
```

5. **Setup PostgreSQL with pgvector**
```sql
-- Create database
CREATE DATABASE rag_mutual_funds;

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
```

## Project Structure

```
RAG_Mutual_Funds/
├── src/                          # Source code
│   ├── scrapers/                 # Web scraping modules
│   │   ├── indmoney_scraper.py   # Main scraper (handles 21 schemes)
│   │   └── fund_list.py          # Fund configurations (21 HDFC schemes)
│   ├── models/                   # Data models
│   │   └── fund_schema.py        # Pydantic schemas
│   ├── storage/                  # Data storage
│   │   └── raw_data_storage.py   # JSON/CSV storage
│   ├── faq_assistant.py          # FAQ Assistant logic (Phase 1)
│   └── config.py                 # Configuration
│
├── tests/                        # Test files
├── data/
│   ├── raw/                      # Scraped data
│   ├── processed/                # Processed data
│   └── cache/                    # Cache files
│
├── run_phase1.py                 # Phase 1 runner (NEW)
├── faq_ui.html                   # Web UI for FAQ Assistant (NEW)
├── .env.example                  # Environment variables template
├── .gitignore
├── README.md                     # This file
├── ARCHITECTURE_OVERVIEW.md      # Complete architecture (SINGLE SOURCE)
├── QUICKSTART.md                 # Getting started guide
├── PHASE1_IMPLEMENTATION.md      # Phase 1 detailed guide
└── QUICK_REFERENCE.md            # Quick reference card
```

---

## Documentation

### 📄 Main Architecture (Single Source)
- **[ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md)** - Complete 10-phase architecture with Phase 1 implementation details

### 🚀 Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** - Step-by-step setup guide
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick reference card
- **[PHASE1_IMPLEMENTATION.md](PHASE1_IMPLEMENTATION.md)** - Detailed Phase 1 guide

```
RAG_Mutual_Funds/
├── src/
│   ├── config.py              # Configuration settings
│   ├── requirements.txt       # Python dependencies
│   │
│   ├── scrapers/              # Web scraping modules
│   │   ├── indmoney_scraper.py
│   │   └── fund_list.py
│   │
│   ├── models/                # Data models
│   │   └── fund_schema.py
│   │
│   ├── storage/               # Data storage
│   │   └── raw_data_storage.py
│   │
│   ├── processors/            # Data processing
│   ├── database/              # Database setup
│   ├── embeddings/            # Embedding generation
│   ├── vectorstore/           # Vector database
│   ├── retriever/             # Retrieval strategies
│   ├── prompts/               # Prompt templates
│   ├── chains/                # RAG chains
│   ├── nlp/                   # NLP utilities
│   ├── generators/            # Response generation
│   ├── handlers/              # Query handlers
│   ├── state/                 # State management
│   └── cli/                   # Command-line interface
│
├── tests/                     # Test files
├── data/
│   ├── raw/                   # Raw scraped data
│   ├── processed/             # Processed data
│   └── cache/                 # Cache files
│
├── .env.example              # Environment variables template
├── .gitignore
└── README.md
```

## Usage

### Running the Scraper

```bash
# Run the scraper to fetch fund data
python -m src.scrapers.indmoney_scraper
```

This will:
1. Scrape data for configured funds from INDMoney
2. Save data to `data/raw/` directory in JSON/CSV format
3. Log progress and errors

### Supported Fund Schemes

Currently configured HDFC funds:
- HDFC ELSS Tax Saver Fund
- HDFC Small Cap Fund
- HDFC Large Cap Fund
- HDFC Mid Cap Fund
- HDFC Balanced Advantage Fund
- HDFC Top 100 Fund
- HDFC Focused 30 Fund
- HDFC Flexi Cap Fund

### Query Types Supported

The chatbot answers factual queries only:
- ✅ Expense ratio queries ("What is the expense ratio of HDFC ELSS?")
- ✅ Lock-in period ("ELSS lock-in period?")
- ✅ Minimum SIP amount ("Minimum SIP for HDFC Small Cap?")
- ✅ Exit load details ("Exit load for HDFC Large Cap?")
- ✅ Risk level and benchmark ("Riskometer for HDFC ELSS?")
- ✅ Fund manager information
- ✅ AUM and returns
- ❌ Investment advice (not supported)
- ❌ Fund recommendations (not supported)

## Configuration

Edit `.env` file to customize settings:

### Database
```env
DATABASE_URL=postgresql://user:password@localhost:5432/rag_mutual_funds
DB_HOST=localhost
DB_PORT=5432
```

### Web Scraping
```env
SCRAPER_DELAY=2.0        # Delay between requests (seconds)
MAX_RETRIES=3           # Maximum retry attempts
TIMEOUT=30              # Request timeout (seconds)
```

### Embeddings
```env
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
BATCH_SIZE=32
```

### RAG
```env
RETRIEVAL_TOP_K=5       # Number of chunks to retrieve
CHUNK_SIZE=512          # Token chunk size
CHUNK_OVERLAP=50        # Overlap between chunks
TEMPERATURE=0.0         # LLM temperature (0.0 for deterministic)
```

### LLM Provider
```env
LLM_PROVIDER=openai     # or 'ollama', 'huggingface'
OPENAI_API_KEY=your-key-here
```

## Development

### Running Tests
```bash
pytest tests/ -v --cov=src
```

### Code Style
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/
```

## Architecture

### Data Flow

1. **Data Acquisition**: Web scraper fetches data from INDMoney
2. **Data Storage**: Raw data saved as JSON/CSV with timestamps
3. **Processing**: Data cleaned, chunked, and enriched with metadata
4. **Embedding**: Chunks converted to vectors using sentence transformers
5. **Storage**: Embeddings stored in PostgreSQL with pgvector
6. **Retrieval**: User queries retrieve relevant chunks via similarity search
7. **Generation**: LLM generates answers based on retrieved context

### Key Components

- **INDMoneyScraper**: Handles web scraping with retry logic
- **FundScheme**: Pydantic model for structured fund data
- **RawDataStorage**: Manages data persistence and versioning
- **RAG Chain**: LangChain pipeline for retrieval and generation

## Logging

Logs are written to console with configurable levels:
```bash
# Set log level in .env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Troubleshooting

### Common Issues

**1. Scraper fails to fetch data**
- Check internet connection
- Verify INDMoney website is accessible
- Increase TIMEOUT value in .env
- Try enabling Selenium for JavaScript-rendered content

**2. Database connection error**
- Verify PostgreSQL is running
- Check credentials in .env
- Ensure pgvector extension is installed

**3. Import errors**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r src/requirements.txt`

## Roadmap

- [x] Phase 1: Data acquisition and web scraping
- [ ] Phase 2: Data processing and chunking
- [ ] Phase 3: Embedding and vector database
- [ ] Phase 4: RAG pipeline implementation
- [ ] Phase 5: Query processing and response generation
- [ ] Phase 6: Testing and validation
- [ ] Phase 7: CLI interface
- [ ] Future: Web UI deployment
- [ ] Future: Docker containerization
- [ ] Future: CI/CD pipeline

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This project is for educational purposes only. The data scraped should be used responsibly and in compliance with INDMoney's terms of service. Always verify critical financial information from official sources.
