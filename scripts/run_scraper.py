"""
Main entry point for running the mutual fund scraper
"""
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import LOG_LEVEL, LOG_FORMAT, TARGET_FUNDS
from src.scrapers.indmoney_scraper import INDMoneyScraper
from src.storage.raw_data_storage import RawDataStorage
from src.models.fund_schema import FundScheme


def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT
    )


def scrape_funds(use_selenium: bool = False):
    """
    Main function to scrape mutual fund data
    
    Args:
        use_selenium: Whether to use Selenium for JavaScript content
    """
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 80)
    logger.info("Starting Mutual Fund Data Scraper")
    logger.info("=" * 80)
    
    # Initialize scraper
    scraper = INDMoneyScraper(use_selenium=use_selenium)
    
    # Initialize storage
    storage = RawDataStorage()
    
    try:
        # Scrape all target funds
        scraped_funds = []
        
        for fund in TARGET_FUNDS:
            logger.info(f"\nScraping {fund}...")
            
            # Find fund slug from fund_list
            from src.scrapers.fund_list import HDFC_FUNDS, OTHER_FUNDS
            
            all_funds = HDFC_FUNDS + OTHER_FUNDS
            fund_info = next((f for f in all_funds if f["name"] == fund), None)
            
            if not fund_info:
                logger.warning(f"Fund info not found for {fund}, skipping...")
                continue
            
            # Scrape fund
            fund_scheme = scraper.scrape_fund_scheme(
                fund_name=fund["name"],
                fund_slug=fund["url_slug"]
            )
            
            if fund_scheme:
                scraped_funds.append(fund_scheme)
                logger.info(f"✓ Successfully scraped {fund}")
            else:
                logger.warning(f"✗ Failed to scrape {fund}")
        
        # Save results
        if scraped_funds:
            logger.info(f"\n{'='*80}")
            logger.info(f"Saving {len(scraped_funds)} funds to storage...")
            
            saved_files = storage.save_scraped_data(
                scraped_funds,
                format="both"  # Save as both JSON and CSV
            )
            
            for format_type, filepath in saved_files.items():
                logger.info(f"Saved {format_type.upper()}: {filepath}")
            
            # Print summary
            print_summary(scraped_funds)
            
            logger.info(f"\n{'='*80}")
            logger.info("Scraping completed successfully!")
            logger.info(f"{'='*80}")
        else:
            logger.warning("No funds were scraped. Check logs for errors.")
    
    except KeyboardInterrupt:
        logger.warning("\nScraping interrupted by user")
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}", exc_info=True)
    finally:
        # Cleanup
        scraper.close()
        logger.info("Resources cleaned up")


def print_summary(funds: list):
    """Print summary of scraped funds"""
    logger = logging.getLogger(__name__)
    
    print("\n" + "=" * 80)
    print("SCRAPING SUMMARY")
    print("=" * 80)
    
    for i, fund in enumerate(funds, 1):
        print(f"\n{i}. {fund.fund_name}")
        print(f"   Category: {fund.category}")
        
        if hasattr(fund, 'expense_ratio') and fund.expense_ratio:
            print(f"   Expense Ratio: {fund.expense_ratio}%")
        
        if hasattr(fund, 'minimum_sip') and fund.minimum_sip:
            print(f"   Min SIP: ₹{fund.minimum_sip}")
        
        if hasattr(fund, 'lock_in_period'):
            print(f"   Lock-in: {fund.lock_in_period}")
        
        if hasattr(fund, 'risk_level'):
            print(f"   Risk Level: {fund.risk_level}")
    
    print("\n" + "=" * 80)


def scrape_single_fund(fund_name: str):
    """
    Scrape a single fund by name
    
    Args:
        fund_name: Name of the fund to scrape
    """
    from src.scrapers.fund_list import HDFC_FUNDS, OTHER_FUNDS
    
    all_funds = HDFC_FUNDS + OTHER_FUNDS
    fund_info = next((f for f in all_funds if f["name"] == fund_name), None)
    
    if not fund_info:
        print(f"Fund '{fund_name}' not found in configuration")
        print(f"Available funds: {[f['name'] for f in all_funds]}")
        return
    
    scraper = INDMoneyScraper(use_selenium=False)
    
    try:
        fund_scheme = scraper.scrape_fund_scheme(
            fund_name=fund_name,
            fund_slug=fund_info["url_slug"]
        )
        
        if fund_scheme:
            print(f"\nSuccessfully scraped {fund_name}")
            print(fund_scheme.dict(exclude_none=True, indent=2))
        else:
            print(f"Failed to scrape {fund_name}")
    finally:
        scraper.close()


if __name__ == "__main__":
    setup_logging()
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Mutual Fund Data Scraper")
    parser.add_argument(
        "--selenium",
        action="store_true",
        help="Use Selenium for JavaScript-rendered content"
    )
    parser.add_argument(
        "--fund",
        type=str,
        help="Scrape a single fund (e.g., 'HDFC ELSS Tax Saver Fund')"
    )
    
    args = parser.parse_args()
    
    if args.fund:
        scrape_single_fund(args.fund)
    else:
        scrape_funds(use_selenium=args.selenium)
