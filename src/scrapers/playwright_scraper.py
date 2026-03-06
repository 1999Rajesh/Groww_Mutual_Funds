"""
Playwright Web Scraper for INDMoney
Modern browser automation for dynamic content
"""
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Playwright not installed. Run: pip install playwright")

from src.models.fund_schema import FundScheme
from src.config import REQUEST_HEADERS

logger = logging.getLogger(__name__)


class PlaywrightScraper:
    """
    Modern web scraper using Playwright for JavaScript-heavy sites
    """
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        Initialize Playwright scraper
        
        Args:
            headless: Run browser in headless mode
            timeout: Page load timeout in milliseconds
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright is required. Install with: pip install playwright"
            )
        
        self.headless = headless
        self.timeout = timeout
        self.browser = None
        self.context = None
        
        logger.info(f"PlaywrightScraper initialized (headless={headless})")
    
    async def initialize(self):
        """Initialize browser"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            user_agent=REQUEST_HEADERS['User-Agent'],
            viewport={'width': 1920, 'height': 1080}
        )
        logger.info("Browser initialized successfully")
    
    async def close(self):
        """Close browser"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info("Browser closed")
    
    async def scrape_fund_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape fund information page using Playwright
        
        Args:
            url: Fund page URL
            
        Returns:
            Dictionary with scraped data
        """
        try:
            page = await self.context.new_page()
            await page.goto(url, wait_until='networkidle', timeout=self.timeout)
            
            # Wait for dynamic content to load
            await page.wait_for_timeout(2000)
            
            # Extract data using multiple selectors
            data = {
                'fund_name': await self._extract_text(page, [
                    'h1', '.fund-name', '[data-testid="fund-name"]',
                    '.scheme-name', 'div.title'
                ]),
                
                'scheme_type': await self._extract_text(page, [
                    '.scheme-type', '[data-testid="scheme-type"]',
                    '.plan-option', 'div.scheme-details'
                ]),
                
                'category': await self._extract_text(page, [
                    '.category', '[data-testid="category"]',
                    '.fund-category', 'span.category-label'
                ]),
                
                'expense_ratio': await self._extract_percentage(page, [
                    '.expense-ratio', '[data-testid="expense-ratio"]',
                    '.ter', 'span.er-value'
                ]),
                
                'minimum_sip': await self._extract_currency(page, [
                    '.min-sip', '[data-testid="min-sip"]',
                    '.minimum-sip', 'span.sip-amount'
                ]),
                
                'minimum_lumpsum': await self._extract_currency(page, [
                    '.min-lumpsum', '[data-testid="min-lumpsum"]',
                    '.minimum-lumpsum', 'span.lumpsum-amount'
                ]),
                
                'lock_in_period': await self._extract_text(page, [
                    '.lockin', '[data-testid="lockin-period"]',
                    '.lock-in-period', 'span.lockin-value'
                ]),
                
                'exit_load': await self._extract_text(page, [
                    '.exit-load', '[data-testid="exit-load"]',
                    '.exit-load-details', 'span.exit-value'
                ]),
                
                'risk_level': await self._extract_text(page, [
                    '.risk-level', '[data-testid="risk-level"]',
                    '.riskometer', 'span.risk-value', '.risk-indicator'
                ]),
                
                'benchmark': await self._extract_text(page, [
                    '.benchmark', '[data-testid="benchmark"]',
                    '.benchmark-index', 'span.benchmark-value'
                ]),
                
                'aum': await self._extract_aum(page, [
                    '.aum', '[data-testid="aum"]',
                    '.assets-under-management', 'span.aum-value'
                ]),
                
                'nav': await self._extract_nav(page, [
                    '.nav', '[data-testid="nav"]',
                    '.net-asset-value', 'span.nav-value'
                ]),
                
                'returns_1y': await self._extract_percentage(page, [
                    '.returns-1y', '[data-testid="returns-1y"]',
                    '.return-1year', 'span.return-1y'
                ]),
                
                'returns_3y': await self._extract_percentage(page, [
                    '.returns-3y', '[data-testid="returns-3y"]',
                    '.return-3year', 'span.return-3y'
                ]),
                
                'returns_5y': await self._extract_percentage(page, [
                    '.returns-5y', '[data-testid="returns-5y"]',
                    '.return-5year', 'span.return-5y'
                ]),
                
                'fund_manager': await self._extract_text(page, [
                    '.fund-manager', '[data-testid="fund-manager"]',
                    '.manager-name', 'span.manager'
                ])
            }
            
            # Add metadata
            data['source_url'] = url
            data['scraped_at'] = datetime.now().isoformat()
            
            await page.close()
            
            logger.info(f"Successfully scraped: {data.get('fund_name', 'Unknown')}")
            
            return data
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            if 'page' in locals():
                await page.close()
            return None
    
    async def _extract_text(self, page, selectors: list) -> Optional[str]:
        """Extract text using first matching selector"""
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text and text.strip():
                        return text.strip()
            except:
                continue
        return None
    
    async def _extract_percentage(self, page, selectors: list) -> Optional[float]:
        """Extract percentage value"""
        text = await self._extract_text(page, selectors)
        if text:
            try:
                # Remove % symbol and parse
                clean_text = text.replace('%', '').replace(',', '').strip()
                return float(clean_text)
            except ValueError:
                pass
        return None
    
    async def _extract_currency(self, page, selectors: list) -> Optional[float]:
        """Extract currency value (INR)"""
        text = await self._extract_text(page, selectors)
        if text:
            try:
                # Remove currency symbols and parse
                clean_text = text.replace('₹', '').replace('Rs', '').replace(',', '').strip()
                return float(clean_text)
            except ValueError:
                pass
        return None
    
    async def _extract_aum(self, page, selectors: list) -> Optional[float]:
        """Extract AUM value in Crores"""
        text = await self._extract_text(page, selectors)
        if text:
            try:
                # Handle Cr/Crore suffixes
                clean_text = text.lower().replace('cr', '').replace('crore', '').replace(',', '').strip()
                return float(clean_text)
            except ValueError:
                pass
        return None
    
    async def _extract_nav(self, page, selectors: list) -> Optional[float]:
        """Extract NAV value"""
        text = await self._extract_text(page, selectors)
        if text:
            try:
                # Remove currency symbols
                clean_text = text.replace('₹', '').replace('Rs', '').replace(',', '').strip()
                return float(clean_text)
            except ValueError:
                pass
        return None
    
    async def scrape_with_screenshot(self, url: str, screenshot_path: str = None) -> Optional[Dict]:
        """
        Scrape page with screenshot for debugging
        
        Args:
            url: Page URL
            screenshot_path: Path to save screenshot
            
        Returns:
            Scraped data dictionary
        """
        try:
            page = await self.context.new_page()
            await page.goto(url, wait_until='networkidle', timeout=self.timeout)
            
            # Take screenshot
            if screenshot_path:
                await page.screenshot(path=screenshot_path, full_page=True)
            
            # Wait for dynamic content
            await page.wait_for_timeout(2000)
            
            # Scrape data
            data = await self.scrape_fund_page(url)
            
            await page.close()
            return data
            
        except Exception as e:
            logger.error(f"Error in screenshot scrape: {str(e)}")
            return None


async def main():
    """Test Playwright scraper"""
    print("="*80)
    print("Testing Playwright Scraper")
    print("="*80)
    
    if not PLAYWRIGHT_AVAILABLE:
        print("\n❌ Playwright not installed")
        print("\nInstall with:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return
    
    # Test URL (example)
    test_url = "https://www.indmoney.com/mutual-funds/hdfc-elss-taxsaver-direct-plan-growth-option-2685"
    
    try:
        # Initialize scraper
        scraper = PlaywrightScraper(headless=True)
        await scraper.initialize()
        
        # Scrape fund page
        print(f"\nScraping: {test_url}")
        data = await scraper.scrape_fund_page(test_url)
        
        if data:
            print("\n✅ Successfully scraped data:")
            for key, value in data.items():
                if value:
                    print(f"  {key}: {value}")
        else:
            print("\n❌ Failed to scrape data")
        
        # Close scraper
        await scraper.close()
        
        print("\n✅ Playwright Scraper Test Complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Playwright installed: pip install playwright")
        print("2. Install browsers: playwright install chromium")
        print("3. Check internet connection")
        print("4. Verify URL is accessible")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Run async test
    asyncio.run(main())
