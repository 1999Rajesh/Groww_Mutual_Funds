"""
Web scraper for INDMoney mutual fund data
"""
import time
import logging
from datetime import datetime, date
from typing import Optional, Dict, Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from retrying import retry

from src.config import (
    BASE_URL,
    SCRAPER_DELAY,
    MAX_RETRIES,
    TIMEOUT,
)
from src.models.fund_schema import FundScheme, ScrapedData
from src.scrapers.fund_list import HDFC_FUNDS

logger = logging.getLogger(__name__)


class INDMoneyScraper:
    """
    Web scraper for extracting mutual fund data from INDMoney website
    """
    
    def __init__(self, use_selenium: bool = False):
        """
        Initialize the scraper
        
        Args:
            use_selenium: Whether to use Selenium for JavaScript-rendered content
        """
        self.base_url = BASE_URL
        self.use_selenium = use_selenium
        self.session = requests.Session()
        self.driver = None
        
        if use_selenium:
            self._setup_selenium()
    
    def _setup_selenium(self):
        """Setup Selenium WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # You may need to specify the path to chromedriver
        # service = Service('/path/to/chromedriver')
        self.driver = webdriver.Chrome(options=chrome_options)
        logger.info("Selenium WebDriver initialized")
    
    def _get_fund_url(self, fund_slug: str) -> str:
        """Construct full URL for a fund"""
        return urljoin(self.base_url, f"/mutual-funds/{fund_slug}")
    
    @retry(stop_max_attempt_number=MAX_RETRIES, wait_fixed=SCRAPER_DELAY * 1000)
    def _fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from URL with retry logic
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string or None if failed
        """
        try:
            if self.use_selenium and self.driver:
                self.driver.get(url)
                WebDriverWait(self.driver, TIMEOUT).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                return self.driver.page_source
            else:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                response = self.session.get(url, headers=headers, timeout=TIMEOUT)
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            raise
    
    def _parse_number(self, text: str) -> Optional[float]:
        """Parse numeric values from text"""
        if not text:
            return None
        
        # Remove common symbols and whitespace
        text = text.replace("%", "").replace("₹", "").replace(",", "").strip()
        
        try:
            return float(text)
        except ValueError:
            return None
    
    def _extract_text_by_class(self, soup: BeautifulSoup, class_name: str) -> Optional[str]:
        """Extract text from element by class name"""
        element = soup.find(class_=class_name)
        return element.get_text(strip=True) if element else None
    
    def _find_element_containing(self, soup: BeautifulSoup, text: str, tag: str = "div") -> Optional[str]:
        """Find element containing specific text"""
        for element in soup.find_all(tag):
            if text.lower() in element.get_text().lower():
                return element.get_text(strip=True)
        return None
    
    def scrape_fund_scheme(self, fund_name: str, fund_slug: str) -> Optional[FundScheme]:
        """
        Scrape complete fund scheme details
        
        Args:
            fund_name: Name of the fund
            fund_slug: URL slug for the fund
            
        Returns:
            FundScheme object with parsed data or None if failed
        """
        url = self._get_fund_url(fund_slug)
        logger.info(f"Scraping {fund_name} from {url}")
        
        try:
            html_content = self._fetch_page(url)
            if not html_content:
                return None
            
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Extract fund details
            fund_data = self._parse_fund_details(soup, url, fund_name)
            
            if fund_data:
                logger.info(f"Successfully scraped {fund_name}")
                return FundScheme(**fund_data)
            else:
                logger.warning(f"No data extracted for {fund_name}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to scrape {fund_name}: {str(e)}")
            return None
    
    def _parse_fund_details(self, soup: BeautifulSoup, url: str, fund_name: str) -> Optional[Dict[str, Any]]:
        """
        Parse fund details from HTML
        
        Args:
            soup: BeautifulSoup object
            url: Source URL
            fund_name: Name of the fund
            
        Returns:
            Dictionary with parsed fund data
        """
        try:
            # Find fund information sections
            # Note: These selectors need to be adjusted based on actual website structure
            
            fund_data = {
                "fund_name": fund_name,
                "scheme_type": self._extract_scheme_type(soup),
                "category": self._extract_category(soup),
                "expense_ratio": self._extract_expense_ratio(soup),
                "lock_in_period": self._extract_lock_in_period(soup),
                "minimum_sip": self._extract_minimum_sip(soup),
                "minimum_lumpsum": self._extract_minimum_lumpsum(soup),
                "exit_load": self._extract_exit_load(soup),
                "risk_level": self._extract_risk_level(soup),
                "benchmark": self._extract_benchmark(soup),
                "fund_manager": self._extract_fund_manager(soup),
                "aum": self._extract_aum(soup),
                "nav": self._extract_nav(soup),
                "returns_1y": self._extract_returns(soup, "1Y"),
                "returns_3y": self._extract_returns(soup, "3Y"),
                "returns_5y": self._extract_returns(soup, "5Y"),
                "source_url": url,
                "last_updated": date.today()
            }
            
            # Filter out None values for optional fields
            fund_data = {k: v for k, v in fund_data.items() if v is not None}
            
            return fund_data if fund_data else None
            
        except Exception as e:
            logger.error(f"Error parsing fund details: {str(e)}")
            return None
    
    def _extract_scheme_type(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract scheme type (Direct/Regular, Growth/Dividend)"""
        # Common patterns - adjust based on actual site structure
        patterns = ["Direct Plan", "Regular Plan", "Growth", "Dividend"]
        for pattern in patterns:
            if element := self._find_element_containing(soup, pattern, "span"):
                return element
        return None
    
    def _extract_category(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract fund category"""
        # Look for category labels
        categories = ["ELSS", "Large Cap", "Mid Cap", "Small Cap", "Hybrid", "Flexi Cap"]
        for category in categories:
            if element := self._find_element_containing(soup, category, "span"):
                return category
        return "Equity"  # Default
    
    def _extract_expense_ratio(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract expense ratio"""
        # Try multiple selectors
        selectors = [
            ".expense-ratio",
            "[data-testid='expense-ratio']",
            ".fund-details__expense-ratio"
        ]
        
        for selector in selectors:
            if element := soup.select_one(selector):
                text = element.get_text(strip=True)
                if ratio := self._parse_number(text):
                    return ratio
        
        # Fallback: search for text containing "expense ratio"
        if text := self._find_element_containing(soup, "expense ratio"):
            parts = text.split(":")
            if len(parts) > 1:
                return self._parse_number(parts[1])
        
        return None
    
    def _extract_lock_in_period(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract lock-in period (especially for ELSS)"""
        # For ELSS funds, default is 3 years
        if element := self._find_element_containing(soup, "lock-in", "div"):
            return element
        
        # Check if it's an ELSS fund
        if self._find_element_containing(soup, "ELSS"):
            return "3 years"
        
        return "Nil"  # Most equity funds have no lock-in
    
    def _extract_minimum_sip(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract minimum SIP amount"""
        selectors = [
            ".minimum-sip",
            "[data-testid='min-sip']",
            ".sip-amount"
        ]
        
        for selector in selectors:
            if element := soup.select_one(selector):
                text = element.get_text(strip=True)
                if amount := self._parse_number(text):
                    return amount
        
        # Fallback: search for text
        if text := self._find_element_containing(soup, "minimum sip"):
            parts = text.split(":")
            if len(parts) > 1:
                return self._parse_number(parts[1])
        
        return 500.0  # Common default
    
    def _extract_minimum_lumpsum(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract minimum lumpsum investment"""
        selectors = [
            ".minimum-lumpsum",
            "[data-testid='min-lumpsum']",
            ".lumpsum-amount"
        ]
        
        for selector in selectors:
            if element := soup.select_one(selector):
                text = element.get_text(strip=True)
                if amount := self._parse_number(text):
                    return amount
        
        return 5000.0  # Common default
    
    def _extract_exit_load(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract exit load details"""
        if element := self._find_element_containing(soup, "exit load", "div"):
            return element
        
        if element := self._find_element_containing(soup, "exitload", "div"):
            return element
        
        return "Nil"
    
    def _extract_risk_level(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract risk level (Riskometer)"""
        risk_levels = ["Low", "Moderate", "High", "Very High"]
        
        for level in risk_levels:
            if self._find_element_containing(soup, level.lower(), "span"):
                return level
        
        # Default based on category
        return "Very High"  # Most equity funds
    
    def _extract_benchmark(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract benchmark index"""
        benchmarks = ["NIFTY 50", "NIFTY 500", "BSE Sensex", "Nifty Midcap 150"]
        
        for benchmark in benchmarks:
            if self._find_element_containing(soup, benchmark, "span"):
                return benchmark
        
        return None
    
    def _extract_fund_manager(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract fund manager name"""
        if element := self._find_element_containing(soup, "fund manager", "div"):
            return element
        
        if element := self._find_element_containing(soup, "managed by", "div"):
            return element
        
        return None
    
    def _extract_aum(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract Assets Under Management"""
        selectors = [
            ".aum",
            "[data-testid='aum']",
            ".assets-under-management"
        ]
        
        for selector in selectors:
            if element := soup.select_one(selector):
                text = element.get_text(strip=True)
                # Handle Cr/Mn conversions
                if "Cr" in text or "crore" in text.lower():
                    return self._parse_number(text)
                elif "Mn" in text:
                    return self._parse_number(text) * 0.01  # Convert to Crores
        
        return None
    
    def _extract_nav(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract current NAV"""
        selectors = [
            ".nav",
            "[data-testid='nav']",
            ".current-nav"
        ]
        
        for selector in selectors:
            if element := soup.select_one(selector):
                text = element.get_text(strip=True)
                if nav := self._parse_number(text):
                    return nav
        
        return None
    
    def _extract_returns(self, soup: BeautifulSoup, period: str) -> Optional[float]:
        """Extract returns for specific period (1Y, 3Y, 5Y)"""
        # Look for return percentages
        patterns = [
            f"{period} Return",
            f"{period} Returns",
            f"Returns ({period})"
        ]
        
        for pattern in patterns:
            if element := self._find_element_containing(soup, pattern, "div"):
                # Extract percentage value
                if "%" in element:
                    parts = element.split("%")[0]
                    return self._parse_number(parts)
        
        return None
    
    def scrape_all_funds(self, fund_list: list = None) -> list:
        """
        Scrape all funds from the list
        
        Args:
            fund_list: List of fund dictionaries to scrape
            
        Returns:
            List of FundScheme objects
        """
        if fund_list is None:
            fund_list = HDFC_FUNDS
        
        results = []
        
        for fund in fund_list:
            logger.info(f"Scraping {fund['name']}...")
            
            fund_scheme = self.scrape_fund_scheme(
                fund_name=fund["name"],
                fund_slug=fund["url_slug"]
            )
            
            if fund_scheme:
                results.append(fund_scheme)
            
            # Rate limiting
            time.sleep(SCRAPER_DELAY)
        
        logger.info(f"Completed scraping {len(results)} funds")
        return results
    
    def close(self):
        """Close browser and sessions"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")
        
        if self.session:
            self.session.close()
            logger.info("Request session closed")
    
    def __del__(self):
        """Destructor to clean up resources"""
        self.close()


def main():
    """Example usage"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize scraper
    scraper = INDMoneyScraper(use_selenium=False)
    
    try:
        # Scrape a single fund
        fund = scraper.scrape_fund_scheme(
            fund_name="HDFC ELSS Tax Saver Fund",
            fund_slug="hdfc-elss-taxsaver-direct-plan-growth-option-2685"
        )
        
        if fund:
            print(f"\nFund: {fund.fund_name}")
            print(f"Category: {fund.category}")
            print(f"Expense Ratio: {fund.expense_ratio}%")
            print(f"Minimum SIP: ₹{fund.minimum_sip}")
            print(f"Lock-in: {fund.lock_in_period}")
        
        # Scrape all HDFC funds
        # all_funds = scraper.scrape_all_funds()
        # print(f"\nScraped {len(all_funds)} funds")
        
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
