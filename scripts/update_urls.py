"""
Update source URLs in existing ChromaDB data
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_db.chroma_store import ChromaVectorStore

# Initialize
print("Initializing ChromaDB...")
vector_store = ChromaVectorStore(persist_directory="./chroma_db")

# Get all current data
collection = vector_store.collection
count = collection.count()
print(f"Current documents: {count}")

if count == 0:
    print("No documents to update!")
    sys.exit(0)

# Get all documents
results = collection.get(include=['documents', 'metadatas'])

# Prepare updates with corrected URLs
url_mapping = {
    "https://www.hdfcfund.com/scheme/elss-tax-saver": "https://www.indmoney.com/mutual-funds/hdfc-elss-tax-saver-fund",
    "https://www.hdfcfund.com/scheme/large-cap-fund": "https://www.indmoney.com/mutual-funds/hdfc-large-cap-fund",
    "https://www.hdfcfund.com/scheme/small-cap-fund": "https://www.indmoney.com/mutual-funds/hdfc-small-cap-fund",
    "https://www.hdfcfund.com/scheme/flexi-cap-fund": "https://www.indmoney.com/mutual-funds/hdfc-flexi-cap-fund",
    "https://www.hdfcfund.com/scheme/mid-cap-fund": "https://www.indmoney.com/mutual-funds/hdfc-mid-cap-fund",
}

updated_count = 0
ids_to_update = []
new_metadatas = []

for i, metadata in enumerate(results['metadatas']):
    old_url = metadata.get('source_url', '')
    if old_url in url_mapping:
        new_url = url_mapping[old_url]
        print(f"Updating: {old_url} -> {new_url}")
        
        ids_to_update.append(results['ids'][i])
        new_metadata = metadata.copy()
        new_metadata['source_url'] = new_url
        new_metadatas.append(new_metadata)
        updated_count += 1

if updated_count > 0:
    # Update the documents
    collection.update(
        ids=ids_to_update,
        metadatas=new_metadatas
    )
    print(f"\n✅ Updated {updated_count} documents with correct INDMoney URLs!")
else:
    print("\nNo updates needed.")

print("\nVerification:")
test_results = collection.get(include=['metadatas'], limit=3)
for meta in test_results['metadatas'][:3]:
    print(f"  - {meta.get('source_url', 'N/A')}")
