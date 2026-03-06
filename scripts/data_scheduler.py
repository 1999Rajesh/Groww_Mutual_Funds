"""
Simple Data Scheduler Script
Run this periodically to update mutual fund data from INDMoney

Usage:
    python scripts/data_scheduler.py
    
For automated scheduling, add to Windows Task Scheduler or cron
"""
import sys
import json
from pathlib import Path
from datetime import datetime
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.indmoney_scraper import INDMoneyScraper
from src.vector_db.chroma_store import ChromaVectorStore
from src.embeddings.embedding_generator import EmbeddingGenerator
from src.processors.data_cleaner import DataCleaner
from src.processors.chunking_strategy import ChunkingStrategy

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_data_update():
    """Execute data update process"""
    logger.info("="*80)
    logger.info("Starting scheduled data update")
    logger.info("="*80)
    
    timestamp = datetime.now().isoformat()
    
    try:
        # Step 1: Scrape latest data from INDMoney
        logger.info("Step 1: Scraping data from INDMoney...")
        scraper = INDMoneyScraper()
        
        # Scrape fund list
        funds_list = scraper.get_fund_list()
        logger.info(f"Found {len(funds_list)} funds in list")
        
        # Scrape details for each fund (limit to first 5 for demo)
        scraped_data = []
        for i, fund_info in enumerate(funds_list[:5]):  # Limit for demo
            logger.info(f"Scraping fund {i+1}/{min(5, len(funds_list))}: {fund_info['fund_name']}")
            try:
                fund_details = scraper.scrape_fund_details(fund_info['scheme_url'])
                if fund_details:
                    fund_details['last_updated'] = timestamp
                    scraped_data.append(fund_details)
            except Exception as e:
                logger.error(f"Failed to scrape {fund_info['fund_name']}: {str(e)}")
        
        scraper.close()
        
        if not scraped_data:
            logger.warning("No data scraped. Exiting.")
            return False
        
        # Step 2: Save raw data
        logger.info("Step 2: Saving raw data...")
        raw_data_path = Path("./data/raw/funds.json")
        raw_data_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(raw_data_path, 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Raw data saved to {raw_data_path}")
        
        # Step 3: Clean and process data
        logger.info("Step 3: Processing data...")
        cleaner = DataCleaner()
        processed_data = []
        
        for fund in scraped_data:
            cleaned = cleaner.clean(fund)
            if cleaned:
                processed_data.append(cleaned)
        
        # Step 4: Save processed data
        logger.info("Step 4: Saving processed data...")
        processed_path = Path("./data/processed/funds.json")
        
        with open(processed_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Processed data saved to {processed_path}")
        
        # Step 5: Update vector database
        logger.info("Step 5: Updating vector database...")
        
        # Initialize components
        vector_store = ChromaVectorStore(persist_directory="./chroma_db")
        embedding_gen = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
        chunking = ChunkingStrategy(strategy="sliding_window", chunk_size=512, chunk_overlap=50)
        
        # Create chunks from processed data
        all_chunks = []
        for fund in processed_data:
            fund_chunks = chunking.create_chunks(text=fund, doc_type="mutual_fund")
            all_chunks.extend(fund_chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks")
        
        # Generate embeddings
        chunk_texts = [chunk.text for chunk in all_chunks]
        embeddings = embedding_gen.generate_embeddings_batch(chunk_texts)
        
        # Prepare data for vector store
        chunks_data = []
        for i, (chunk, embedding) in enumerate(zip(all_chunks, embeddings)):
            chunk_data = {
                'chunk_id': f"update_{timestamp}_{i}",
                'chunk_text': chunk.text,
                'fund_name': chunk.metadata.get('fund_name', 'Unknown'),
                'chunk_type': chunk.metadata.get('chunk_type', 'general'),
                'metadata': {
                    'source_url': chunk.metadata.get('source_url', ''),
                    'last_updated': timestamp
                }
            }
            chunks_data.append(chunk_data)
        
        # Clear old data and add new
        vector_store.clear_all()
        import numpy as np
        embeddings_array = np.array(embeddings)
        count = vector_store.add_embeddings(chunks_data, embeddings_array)
        
        logger.info(f"Added {count} chunks to vector database")
        
        # Step 6: Update metadata file
        logger.info("Step 6: Updating metadata...")
        metadata = {
            'last_updated': timestamp,
            'total_funds': len(processed_data),
            'total_chunks': count,
            'data_source': 'INDMoney Website',
            'scheduler_version': '1.0.0'
        }
        
        metadata_path = Path("./data/metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Metadata saved to {metadata_path}")
        
        # Summary
        logger.info("="*80)
        logger.info("✅ Data update completed successfully!")
        logger.info(f"   - Funds scraped: {len(scraped_data)}")
        logger.info(f"   - Funds processed: {len(processed_data)}")
        logger.info(f"   - Chunks created: {count}")
        logger.info(f"   - Last updated: {timestamp}")
        logger.info("="*80)
        
        return True
        
    except Exception as e:
        logger.error(f"Data update failed: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    success = run_data_update()
    sys.exit(0 if success else 1)
