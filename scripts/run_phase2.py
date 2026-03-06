"""
Phase 2 Runner - Data Processing Pipeline
Cleans data, creates chunks, and prepares for embeddings
"""
import json
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from src.config import DATA_RAW_DIR, DATA_PROCESSED_DIR
from src.processors.data_cleaner import DataCleaner
from src.processors.chunking_strategy import ChunkingStrategy
from src.storage.raw_data_storage import RawDataStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase2Processor:
    """
    Phase 2 Data Processing Pipeline
    """
    
    def __init__(self):
        """Initialize Phase 2 processor"""
        self.cleaner = DataCleaner()
        self.chunker = ChunkingStrategy(chunk_size=512, chunk_overlap=50)
        self.storage = RawDataStorage()
    
    def process_all_funds(self) -> Dict:
        """
        Process all scraped funds
        
        Returns:
            Processing statistics
        """
        logger.info("="*80)
        logger.info("Starting Phase 2 Data Processing")
        logger.info("="*80)
        
        # Load raw data
        raw_dir = Path(DATA_RAW_DIR) / "raw"
        json_files = list(raw_dir.glob("mutual_funds_*.json"))
        
        if not json_files:
            logger.error("No scraped data found. Please run Phase 1 first.")
            return {'error': 'No data found'}
        
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        logger.info(f"Loading data from {latest_file.name}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        funds_data = data.get('data', data) if isinstance(data, dict) else data
        logger.info(f"Found {len(funds_data)} funds to process")
        
        # Process each fund
        all_chunks = []
        processing_stats = {
            'total_funds': len(funds_data),
            'successful': 0,
            'failed': 0,
            'total_chunks': 0,
            'chunk_types': {}
        }
        
        for i, fund in enumerate(funds_data, 1):
            logger.info(f"\nProcessing fund {i}/{len(funds_data)}: {fund.get('fund_name', 'Unknown')}")
            
            try:
                # Step 1: Clean data
                cleaned_fund = self.cleaner.clean_all_fields(fund)
                
                # Validate
                validation = self.cleaner.validate_fund_data(cleaned_fund)
                if not validation.get('is_valid', False):
                    logger.warning(f"Validation failed for {fund.get('fund_name')}")
                    processing_stats['failed'] += 1
                    continue
                
                # Step 2: Create chunks
                chunks = self.chunker.chunk_fund_data(cleaned_fund)
                
                # Track statistics
                processing_stats['successful'] += 1
                processing_stats['total_chunks'] += len(chunks)
                
                for chunk in chunks:
                    chunk_type = chunk.chunk_type
                    if chunk_type not in processing_stats['chunk_types']:
                        processing_stats['chunk_types'][chunk_type] = 0
                    processing_stats['chunk_types'][chunk_type] += 1
                
                all_chunks.extend([c.dict() for c in chunks])
                
                logger.info(f"✓ Created {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Error processing {fund.get('fund_name')}: {str(e)}")
                processing_stats['failed'] += 1
        
        # Save processed chunks
        if all_chunks:
            output_file = self._save_processed_chunks(all_chunks)
            logger.info(f"\nSaved {len(all_chunks)} chunks to {output_file}")
        
        # Print summary
        self._print_summary(processing_stats)
        
        return processing_stats
    
    def _save_processed_chunks(self, chunks: List[Dict]) -> str:
        """Save processed chunks to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(DATA_PROCESSED_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"processed_chunks_{timestamp}.json"
        
        output_data = {
            'metadata': {
                'processed_at': datetime.now().isoformat(),
                'total_chunks': len(chunks),
                'pipeline': 'Phase 2 - Data Processing'
            },
            'chunks': chunks
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        return str(output_file)
    
    def _print_summary(self, stats: Dict):
        """Print processing summary"""
        logger.info("\n" + "="*80)
        logger.info("PHASE 2 PROCESSING SUMMARY")
        logger.info("="*80)
        logger.info(f"Total Funds Processed: {stats['total_funds']}")
        logger.info(f"Successful: {stats['successful']}")
        logger.info(f"Failed: {stats['failed']}")
        logger.info(f"Total Chunks Created: {stats['total_chunks']}")
        
        logger.info("\nChunks by Type:")
        for chunk_type, count in stats['chunk_types'].items():
            logger.info(f"  - {chunk_type}: {count} chunks")
        
        success_rate = (stats['successful'] / stats['total_funds'] * 100) if stats['total_funds'] > 0 else 0
        logger.info(f"\nSuccess Rate: {success_rate:.1f}%")
        logger.info("="*80)


def main():
    """Main entry point for Phase 2"""
    print("\n" + "="*80)
    print("Phase 2: Data Processing Pipeline")
    print("="*80)
    print("\nThis will:")
    print("1. Clean and normalize scraped data")
    print("2. Create intelligent chunks (field-based, summary, Q&A)")
    print("3. Save processed chunks for Phase 3 (embeddings)")
    print("\nNote: Make sure you've run Phase 1 first!")
    print("="*80)
    
    input("\nPress Enter to start Phase 2 processing...")
    
    processor = Phase2Processor()
    stats = processor.process_all_funds()
    
    if stats.get('error'):
        print(f"\n❌ Error: {stats['error']}")
        print("Please run Phase 1 first to scrape data.")
    else:
        print(f"\n✅ Phase 2 Complete!")
        print(f"   - Processed {stats['successful']} funds")
        print(f"   - Created {stats['total_chunks']} chunks")
        print(f"   - Success rate: {(stats['successful']/stats['total_funds']*100):.1f}%")
        print("\nNext step: Run Phase 3 to generate embeddings")


if __name__ == "__main__":
    main()
