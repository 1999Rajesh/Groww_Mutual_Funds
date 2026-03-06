"""Simple script to add sample data with HDFC AMC and Groww URLs
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Sample data with HDFC AMC and Groww URLs
sample_chunks = [
    {
        "fund_name": "HDFC ELSS Tax Saver Fund",
        "chunk_type": "lock_in_exit",
        "chunk_text": "HDFC ELSS Tax Saver Fund has a lock-in period of 3 years from the date of investment.",
        "source_url": "https://www.hdfcfund.com/product-solutions/overview/hdfc-elss-tax-saver/direct",
        "alt_url": "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth"
    },
    {
        "fund_name": "HDFC ELSS Tax Saver Fund",
        "chunk_type": "investment_details",
        "chunk_text": "HDFC ELSS Tax Saver Fund Direct Plan has an expense ratio of 1.05% as of March 2024.",
        "source_url": "https://www.hdfcfund.com/product-solutions/overview/hdfc-elss-tax-saver/direct",
        "alt_url": "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth"
    },
    {
        "fund_name": "HDFC Top 100 Fund",
        "chunk_type": "investment_details",
        "chunk_text": "HDFC Top 100 Fund Direct Plan has a total expense ratio (TER) of 0.95%.",
        "source_url": "https://www.hdfcfund.com/product-solutions/overview/hdfc-top-100-fund/direct",
        "alt_url": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-plan-growth"
    },
    {
        "fund_name": "HDFC Top 100 Fund",
        "chunk_type": "investment_details",
        "chunk_text": "HDFC Top 100 Fund allows SIP starting from ₹500 per month.",
        "source_url": "https://www.hdfcfund.com/product-solutions/overview/hdfc-top-100-fund/direct",
        "alt_url": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-plan-growth"
    },
    {
        "fund_name": "HDFC Mid-Cap Opportunities Fund",
        "chunk_type": "investment_details",
        "chunk_text": "HDFC Mid-Cap Opportunities Fund invests in mid-cap companies with high growth potential.",
        "source_url": "https://www.hdfcfund.com/product-solutions/overview/hdfc-mid-cap-opportunities-fund/direct",
        "alt_url": "https://groww.in/mutual-funds/hdfc-mid-cap-opportunities-fund-direct-growth"
    },
    {
        "fund_name": "HDFC Flexi Cap Fund",
        "chunk_type": "investment_details",
        "chunk_text": "HDFC Flexi Cap Fund can invest across large, mid, and small cap stocks.",
        "source_url": "https://www.hdfcfund.com/product-solutions/overview/hdfc-flexi-cap-fund/direct",
        "alt_url": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth"
    },
]

print(f"Sample chunks prepared: {len(sample_chunks)}")
print("\nSource URLs:")
for chunk in sample_chunks:
    print(f"  • {chunk['fund_name']}: {chunk['source_url']}")

# Load into ChromaDB
print("\nLoading into ChromaDB...")
from src.vector_db.chroma_store import ChromaVectorStore
from src.embeddings.embedding_generator import EmbeddingGenerator

# Initialize with same model as API (all-MiniLM-L6-v2 - 384 dimensions)
embedding_gen = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
chroma_store = ChromaVectorStore()

# Clear existing data and add new data
print(f"Current collection count: {chroma_store.collection.count()}")

# Delete old data
old_ids = chroma_store.collection.get()['ids']
if old_ids:
    chroma_store.collection.delete(ids=old_ids)
    print(f"Deleted {len(old_ids)} old documents")

# Add new documents
for i, chunk in enumerate(sample_chunks):
    chunk_id = f"chunk_{i}"
    text = chunk['chunk_text']
    
    # Generate embedding
    embedding = embedding_gen.generate_embeddings([text])[0]
    
    # Add to ChromaDB
    chroma_store.collection.add(
        ids=[chunk_id],
        embeddings=[embedding.tolist()],
        documents=[text],
        metadatas=[{
            'fund_name': chunk['fund_name'],
            'chunk_type': chunk['chunk_type'],
            'source_url': chunk['source_url'],
            'alt_url': chunk.get('alt_url', '')
        }]
    )
    print(f"  Added: {chunk_id} - {chunk['fund_name']}")

print(f"\n✅ Loaded {len(sample_chunks)} chunks into ChromaDB")
print(f"New collection count: {chroma_store.collection.count()}")
