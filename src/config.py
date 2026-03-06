"""
Configuration settings for RAG Mutual Funds Chatbot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/rag_mutual_funds")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "rag_mutual_funds")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

# Web Scraping Configuration
BASE_URL = "https://www.indmoney.com"
SCRAPER_DELAY = float(os.getenv("SCRAPER_DELAY", "2.0"))  # Delay between requests in seconds
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
TIMEOUT = int(os.getenv("TIMEOUT", "30"))

# Embedding Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2")
EMBEDDING_DIMENSION = 768
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))

# Vector Store Configuration
VECTOR_TABLE_NAME = "fund_embeddings"
VECTOR_INDEX_METHOD = "ivfflat"  # or 'hnsw'
VECTOR_INDEX_PARAMS = {"lists": 100, "probes": 10}

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # openai, ollama, huggingface
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")

# RAG Configuration
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "5"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))  # For deterministic responses

# Data Paths
DATA_RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
DATA_PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
DATA_CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "cache")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Fund Categories
FUND_CATEGORIES = [
    "ELSS",
    "Large Cap",
    "Mid Cap", 
    "Small Cap",
    "Hybrid",
    "Debt",
    "Sectoral"
]

# Target Funds to Scrape
TARGET_FUNDS = [
    "HDFC ELSS Tax Saver Fund",
    "HDFC Small Cap Fund",
    "HDFC Large Cap Fund",
    "HDFC Mid Cap Fund",
    "HDFC Balanced Advantage Fund",
    "HDFC Top 100 Fund",
    "HDFC Focused 30 Fund",
    "HDFC Flexi Cap Fund",
]
