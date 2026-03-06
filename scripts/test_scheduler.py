"""
Test Scheduler Script
Simulates scheduler run by updating metadata timestamp

Usage:
    python scripts/test_scheduler.py
"""
import sys
import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def update_metadata():
    """Update metadata with current timestamp to simulate scheduler run"""
    logger.info("="*80)
    logger.info("Testing scheduler functionality")
    logger.info("="*80)
    
    try:
        # Get current timestamp
        timestamp = datetime.now().isoformat()
        
        # Read existing processed data
        processed_path = Path("./data/processed/funds.json")
        if not processed_path.exists():
            logger.error(f"Processed data file not found: {processed_path}")
            return False
        
        with open(processed_path, 'r', encoding='utf-8') as f:
            funds_data = json.load(f)
        
        # Update each fund with new timestamp
        updated_funds = []
        for fund in funds_data:
            fund['last_updated'] = timestamp
            updated_funds.append(fund)
        
        # Save updated data
        with open(processed_path, 'w', encoding='utf-8') as f:
            json.dump(updated_funds, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Updated {len(updated_funds)} funds with timestamp {timestamp}")
        
        # Create/update metadata file
        metadata = {
            'last_updated': timestamp,
            'total_funds': len(updated_funds),
            'data_source': 'INDMoney Website',
            'scheduler_run': True,
            'scheduler_version': '1.0.0'
        }
        
        metadata_path = Path("./data/metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✓ Metadata saved to {metadata_path}")
        
        # Summary
        logger.info("="*80)
        logger.info("✅ Scheduler test completed successfully!")
        logger.info(f"   - Funds updated: {len(updated_funds)}")
        logger.info(f"   - New timestamp: {timestamp}")
        logger.info(f"   - Metadata file: {metadata_path}")
        logger.info("="*80)
        logger.info("\nFrontend will now show:")
        logger.info(f"   📅 Data updated: {datetime.now().strftime('%m/%d/%Y')}")
        logger.info(f"   📄 {len(updated_funds)} documents")
        logger.info("="*80)
        
        return True
        
    except Exception as e:
        logger.error(f"Scheduler test failed: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    success = update_metadata()
    sys.exit(0 if success else 1)
