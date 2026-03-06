"""
Phase 1 Implementation Runner
Scrapes data from INDMoney and launches FAQ Assistant
"""
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import LOG_LEVEL, LOG_FORMAT
from src.scrapers.indmoney_scraper import INDMoneyScraper
from src.storage.raw_data_storage import RawDataStorage
from src.scrapers.fund_list import PRIMARY_SCHEMES, HDFC_FUNDS
from src.faq_assistant import FAQAssistant, create_simple_ui

logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def scrape_primary_schemes():
    """Scrape primary schemes for MVP"""
    logger.info("="*80)
    logger.info("Starting Phase 1 Data Scraping")
    logger.info("="*80)
    
    scraper = INDMoneyScraper(use_selenium=False)
    storage = RawDataStorage()
    
    scraped_funds = []
    
    # Scrape primary schemes first (for MVP)
    logger.info(f"\nScraping {len(PRIMARY_SCHEMES)} primary schemes...")
    
    for fund_name in PRIMARY_SCHEMES:
        fund_info = next((f for f in HDFC_FUNDS if f["name"] == fund_name), None)
        
        if not fund_info:
            logger.warning(f"Fund info not found for {fund_name}")
            continue
        
        logger.info(f"Scraping {fund_name}...")
        
        fund_scheme = scraper.scrape_fund_scheme(
            fund_name=fund_name,
            fund_slug=fund_info["url_slug"]
        )
        
        if fund_scheme:
            scraped_funds.append(fund_scheme)
            logger.info(f"✓ Successfully scraped {fund_name}")
        else:
            logger.warning(f"✗ Failed to scrape {fund_name}")
    
    # Save results
    if scraped_funds:
        logger.info(f"\nSaving {len(scraped_funds)} funds...")
        saved_files = storage.save_scraped_data(scraped_funds, format="both")
        
        for fmt, filepath in saved_files.items():
            logger.info(f"Saved {fmt.upper()}: {filepath}")
        
        logger.info("\n" + "="*80)
        logger.info("Scraping completed successfully!")
        logger.info("="*80)
    else:
        logger.warning("No funds were scraped. Check logs for errors.")
    
    scraper.close()
    return len(scraped_funds)


def launch_cli_assistant():
    """Launch command-line FAQ assistant"""
    logger.info("\nLaunching CLI FAQ Assistant...")
    create_simple_ui()


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("HDFC Mutual Funds FAQ Assistant - Phase 1")
    print("="*80)
    print("\nOptions:")
    print("1. Scrape data from INDMoney")
    print("2. Launch FAQ Assistant (CLI)")
    print("3. Open Web UI (HTML file)")
    print("4. Exit")
    print("\nNote: Run option 1 first before using the assistant")
    print("="*80)
    
    while True:
        print("\nEnter your choice (1-4): ", end="")
        try:
            choice = input().strip()
            
            if choice == '1':
                count = scrape_primary_schemes()
                if count > 0:
                    print(f"\n✅ Successfully scraped {count} schemes!")
                    print("\nYou can now launch the FAQ Assistant (option 2 or 3)")
                else:
                    print("\n❌ Scraping failed. Check logs for details.")
            
            elif choice == '2':
                print("\n🤖 Launching CLI FAQ Assistant...")
                print("Type your questions about mutual funds!")
                launch_cli_assistant()
            
            elif choice == '3':
                import webbrowser
                html_path = Path(__file__).parent / "faq_ui.html"
                print(f"\n🌐 Opening Web UI: {html_path}")
                print("Opening in your default browser...")
                webbrowser.open(f"file://{html_path.absolute()}")
                print("\nTo reopen, run option 3 again or open faq_ui.html in your browser")
            
            elif choice == '4':
                print("\n👋 Goodbye!")
                break
            
            else:
                print("\n❌ Invalid choice. Please enter 1-4")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
