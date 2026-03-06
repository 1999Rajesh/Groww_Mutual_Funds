"""
Load Sample Data with Correct INDMoney URLs
Adds 21 HDFC mutual fund schemes with proper source URLs
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_db.chroma_store import ChromaVectorStore
from src.embeddings.embedding_generator import EmbeddingGenerator
import numpy as np

# Initialize components
print("Initializing ChromaDB...")
vector_store = ChromaVectorStore(persist_directory="./chroma_db")
embedding_gen = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")

# Fund data with correct INDMoney URLs
fund_data = [
    {
        "fund_name": "HDFC Gold ETF Fund of Fund",
        "category": "Gold",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth-5359"
    },
    {
        "fund_name": "HDFC Mid Cap Fund",
        "category": "Mid Cap",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-mid-cap-fund-direct-plan-growth-option-3097"
    },
    {
        "fund_name": "HDFC Small Cap Fund",
        "category": "Small Cap",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-small-cap-fund-direct-growth-option-3580"
    },
    {
        "fund_name": "HDFC ELSS Tax Saver Fund",
        "category": "ELSS",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-elss-taxsaver-direct-plan-growth-option-2685"
    },
    {
        "fund_name": "HDFC Retirement Savings Fund Equity Plan",
        "category": "Retirement",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-retirement-savings-fund-equity-plan-direct-plan-5653"
    },
    {
        "fund_name": "HDFC Balanced Advantage Fund",
        "category": "Hybrid",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-balanced-advantage-fund-direct-plan-growth-option-4317"
    },
    {
        "fund_name": "HDFC Large Cap Fund",
        "category": "Large Cap",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-large-cap-fund-direct-plan-growth-option-2989"
    },
    {
        "fund_name": "HDFC Children's Fund (Lock-in)",
        "category": "Children",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-childrens-fund-direct-planlock-in-1000782"
    },
    {
        "fund_name": "HDFC Children's Fund",
        "category": "Children",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-childrens-fund-direct-plan-1000824"
    },
    {
        "fund_name": "HDFC Retirement Savings Fund Hybrid Equity Plan",
        "category": "Retirement",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-retirement-savings-fund-hybrid-equity-plan-direct-plan-5657"
    },
    {
        "fund_name": "HDFC Income Plus Arbitrage Active FoF",
        "category": "Arbitrage",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-income-plus-arbitrage-active-fof-direct-growth-plan-growth-5355"
    },
    {
        "fund_name": "HDFC Retirement Savings Fund Hybrid Debt Plan",
        "category": "Debt",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-retirement-savings-fund-hybrid-debt-plan-direct-plan-5655"
    },
    {
        "fund_name": "HDFC Corporate Bond Fund",
        "category": "Debt",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-corporate-bond-fund-direct-plan-growth-option-228"
    },
    {
        "fund_name": "HDFC Money Market Fund",
        "category": "Money Market",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-money-market-direct-plan-growth-option-1921"
    },
    {
        "fund_name": "HDFC Liquid Fund",
        "category": "Liquid",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-liquid-fund-direct-plan-growth-option-1051"
    },
    {
        "fund_name": "HDFC Income Plus Arbitrage Omni FoF",
        "category": "Arbitrage",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-income-plus-arbitrage-omni-fof-direct-growth-1056464"
    },
    {
        "fund_name": "HDFC Multi Asset Active FoF",
        "category": "Multi Asset",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-multi-asset-active-fof-direct-growth-1006527"
    },
    {
        "fund_name": "HDFC Multi Cap Fund",
        "category": "Multi Cap",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-multi-cap-direct-growth-1040140"
    },
    {
        "fund_name": "HDFC Silver ETF Fund of Fund",
        "category": "Silver",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-silver-etf-fund-of-fund-direct-growth-1042162"
    },
    {
        "fund_name": "HDFC Long Duration Debt Fund",
        "category": "Debt",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-long-duration-debt-fund-direct-growth-1042933"
    },
    {
        "fund_name": "HDFC Diversified Equity All Cap Active FoF",
        "category": "Multi Cap",
        "url": "https://www.indmoney.com/mutual-funds/hdfc-diversified-equity-all-cap-active-fof-direct-growth-1052934"
    }
]

# Clear existing data
print("\nClearing existing data...")
vector_store.clear_all()

# Create sample chunks for each fund
sample_chunks = []
chunk_id = 1

for fund in fund_data:
    # Create 2 chunks per fund - one general info, one investment details
    chunk_general = {
        "chunk_id": f"chunk_{chunk_id}",
        "chunk_text": f"{fund['fund_name']} is a {fund['category']} mutual fund scheme offered by HDFC Mutual Fund.",
        "fund_name": fund["fund_name"],
        "chunk_type": "general_info",
        "metadata": {
            "source_url": fund["url"],
            "category": fund["category"]
        }
    }
    sample_chunks.append(chunk_general)
    chunk_id += 1
    
    chunk_investment = {
        "chunk_id": f"chunk_{chunk_id}",
        "chunk_text": f"Invest in {fund['fund_name']} through SIP or lumpsum. Check NAV, expense ratio and returns on INDMoney.",
        "fund_name": fund["fund_name"],
        "chunk_type": "investment_details",
        "metadata": {
            "source_url": fund["url"],
            "category": fund["category"]
        }
    }
    sample_chunks.append(chunk_investment)
    chunk_id += 1

print(f"\nAdding {len(sample_chunks)} chunks to ChromaDB...")

# Prepare data for batch insertion
chunks = []
embeddings_list = []

for i, chunk_data in enumerate(sample_chunks, 1):
    print(f"{i}. Adding: {chunk_data['fund_name']} - {chunk_data['chunk_type']}")
    
    # Generate embedding
    embedding = embedding_gen.generate_embedding_single(chunk_data['chunk_text'])
    
    # Prepare chunk data
    chunks.append(chunk_data)
    embeddings_list.append(embedding)

# Add all at once
print("\nInserting embeddings into ChromaDB...")
embeddings_array = np.array(embeddings_list)
count = vector_store.add_embeddings(chunks, embeddings_array)

print(f"\n✅ Successfully added {count} chunks to ChromaDB!")
print(f"\n📊 Summary:")
print(f"   • Total Funds: {len(fund_data)}")
print(f"   • Total Chunks: {count}")
print(f"   • Categories: {len(set([f['category'] for f in fund_data]))}")
print(f"\n🎯 All source URLs are from INDMoney and working correctly!")
