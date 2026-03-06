"""
Quick script to add sample mutual fund data to ChromaDB for testing
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.vector_db.chroma_store import ChromaVectorStore
from src.embeddings.embedding_generator import EmbeddingGenerator

# Initialize components
print("Initializing ChromaDB...")
vector_store = ChromaVectorStore(persist_directory="./chroma_db")
embedding_gen = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")

# Sample mutual fund data chunks
sample_chunks = [
    {
        "fund_name": "HDFC ELSS Tax Saver Fund",
        "chunk_type": "lock_in_exit",
        "chunk_text": "HDFC ELSS Tax Saver Fund has a lock-in period of 3 years from the date of investment. This is mandated by tax laws for Equity Linked Savings Schemes (ELSS). During this period, units cannot be redeemed or transferred.",
        "source_url": "https://www.indmoney.com/mutual-funds/hdfc-elss-tax-saver-fund"
    },
    {
        "fund_name": "HDFC ELSS Tax Saver Fund",
        "chunk_type": "investment_details",
        "chunk_text": "HDFC ELSS Tax Saver Fund Direct Plan has an expense ratio of 1.05% as of March 2024. Regular plans have a higher expense ratio of around 2.15%. Expense ratios are subject to change and are disclosed on the AMC website monthly.",
        "source_url": "https://www.indmoney.com/mutual-funds/hdfc-elss-tax-saver-fund"
    },
    {
        "fund_name": "HDFC Large Cap Fund",
        "chunk_type": "investment_details",
        "chunk_text": "HDFC Large Cap Fund Direct Plan Growth option has a total expense ratio (TER) of 0.95% as per latest disclosure. The regular plan expense ratio is approximately 1.85%. SEBI mandates all mutual funds to disclose their expense ratios daily on their websites.",
        "source_url": "https://www.indmoney.com/mutual-funds/hdfc-large-cap-fund"
    },
    {
        "fund_name": "HDFC Large Cap Fund",
        "chunk_type": "investment_details",
        "chunk_text": "HDFC Large Cap Fund allows SIP (Systematic Investment Plan) starting from a minimum amount of ₹500 per month. There is no maximum limit for SIP investments. Lumpsum investments start from ₹5,000 minimum.",
        "source_url": "https://www.indmoney.com/mutual-funds/hdfc-large-cap-fund"
    },
    {
        "fund_name": "HDFC Small Cap Fund",
        "chunk_type": "investment_details",
        "chunk_text": "HDFC Small Cap Fund offers flexible SIP options including monthly, quarterly, and semi-annual frequencies. Minimum SIP amount is ₹500 for monthly mode. Investors can also opt for STP (Systematic Transfer Plan) from debt funds starting from ₹250.",
        "source_url": "https://www.indmoney.com/mutual-funds/hdfc-small-cap-fund"
    },
    {
        "fund_name": "HDFC Flexi Cap Fund",
        "chunk_type": "investment_details",
        "chunk_text": "HDFC Flexi Cap Fund Direct Plan requires a minimum SIP amount of ₹500 per month. For lumpsum investment, the minimum amount is ₹5,000. Additional purchases can be made in multiples of ₹1 thereafter.",
        "source_url": "https://www.indmoney.com/mutual-funds/hdfc-flexi-cap-fund"
    },
    {
        "fund_name": "HDFC Mid Cap Fund",
        "chunk_type": "investment_details",
        "chunk_text": "HDFC Mid Cap Fund provides SIP facility with minimum monthly installment of ₹500. Investors can choose weekly, monthly, or quarterly SIP frequencies. The fund also supports perpetual SIPs with no fixed end date.",
        "source_url": "https://www.indmoney.com/mutual-funds/hdfc-mid-cap-fund"
    },
]

print(f"\nAdding {len(sample_chunks)} sample chunks to vector database...")

# Prepare data for batch insertion
chunks = []
embeddings_list = []

for i, chunk_data in enumerate(sample_chunks, 1):
    print(f"{i}. Adding: {chunk_data['fund_name']} - {chunk_data['chunk_type']}")
    
    # Generate embedding
    embedding = embedding_gen.generate_embedding_single(chunk_data['chunk_text'])
    
    # Prepare chunk data
    chunk = {
        'chunk_id': f"sample_{i}",
        'chunk_text': chunk_data['chunk_text'],
        'fund_name': chunk_data['fund_name'],
        'chunk_type': chunk_data['chunk_type'],
        'metadata': {
            'source_url': chunk_data['source_url']
        }
    }
    chunks.append(chunk)
    embeddings_list.append(embedding)

# Add all at once
import numpy as np
embeddings_array = np.array(embeddings_list)
count = vector_store.add_embeddings(chunks, embeddings_array)

print(f"\n✅ Successfully added {count} chunks to ChromaDB!")
print("\nYou can now test these questions:")
print("  • What is the expense ratio of HDFC Large Cap Fund?")
print("  • What is the minimum SIP amount for HDFC Flexi Cap Fund?")
print("  • Does HDFC ELSS have a lock-in period?")
print("  • Show SIP options for small cap funds")
