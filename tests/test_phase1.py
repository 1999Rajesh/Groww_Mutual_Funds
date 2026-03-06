"""
Test cases for Phase 1 - Data Acquisition
Tests for web scrapers, data models, and storage
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.models.fund_schema import FundScheme, FundChunk, ScrapedData
from src.scrapers.fund_list import HDFC_FUNDS, ALL_FUNDS


class TestFundModels:
    """Test Pydantic data models"""
    
    def test_fund_scheme_creation(self):
        """Test creating a FundScheme object"""
        fund = FundScheme(
            fund_name="HDFC ELSS Tax Saver Fund",
            scheme_type="Direct Plan - Growth Option",
            category="ELSS",
            expense_ratio=0.68,
            minimum_sip=500.0,
            minimum_lumpsum=5000.0,
            lock_in_period="3 years",
            exit_load="Nil",
            risk_level="Very High"
        )
        
        assert fund.fund_name == "HDFC ELSS Tax Saver Fund"
        assert fund.category == "ELSS"
        assert fund.expense_ratio == 0.68
        assert fund.minimum_sip == 500.0
    
    def test_fund_scheme_optional_fields(self):
        """Test FundScheme with optional fields"""
        fund = FundScheme(
            fund_name="HDFC Large Cap Fund",
            scheme_type="Regular Plan - Dividend",
            category="Large Cap"
            # Other fields are optional
        )
        
        assert fund.fund_name == "HDFC Large Cap Fund"
        assert fund.expense_ratio is None
        assert fund.minimum_sip is None
    
    def test_fund_scheme_validation(self):
        """Test field validation"""
        # Valid expense ratio (must be >= 0)
        fund = FundScheme(
            fund_name="Test Fund",
            scheme_type="Direct",
            category="ELSS",
            expense_ratio=1.5
        )
        assert fund.expense_ratio == 1.5
        
        # Negative expense ratio should fail
        with pytest.raises(ValueError):
            FundScheme(
                fund_name="Test Fund",
                scheme_type="Direct",
                category="ELSS",
                expense_ratio=-0.5
            )
    
    def test_fund_chunk_creation(self):
        """Test creating FundChunk object"""
        chunk = FundChunk(
            fund_name="HDFC ELSS Tax Saver Fund",
            chunk_id="test_001",
            chunk_text="Expense ratio is 0.68%",
            chunk_type="expense_ratio",
            metadata={"source": "indmoney"},
            token_count=10
        )
        
        assert chunk.chunk_id == "test_001"
        assert chunk.chunk_type == "expense_ratio"
        assert chunk.token_count == 10
    
    def test_qa_pair_creation(self):
        """Test creating QAPair object"""
        from src.models.fund_schema import QAPair
        
        qa = QAPair(
            question="What is the expense ratio?",
            answer="The expense ratio is 0.68%",
            fund_name="HDFC ELSS Tax Saver Fund",
            chunk_type="expense_ratio",
            confidence_score=0.95
        )
        
        assert qa.confidence_score == 0.95
        assert qa.question.startswith("What")


class TestFundList:
    """Test fund list configuration"""
    
    def test_hdfc_funds_configured(self):
        """Test that HDFC funds are configured"""
        assert len(HDFC_FUNDS) > 0
        assert any(f["name"] == "HDFC ELSS Tax Saver Fund" for f in HDFC_FUNDS)
        assert any(f["name"] == "HDFC Small Cap Fund" for f in HDFC_FUNDS)
    
    def test_fund_structure(self):
        """Test fund dictionary structure"""
        for fund in HDFC_FUNDS:
            assert "name" in fund
            assert "category" in fund
            assert "url_slug" in fund
            
            # Verify slug format
            assert isinstance(fund["url_slug"], str)
            assert " " not in fund["url_slug"]  # No spaces in slug
    
    def test_all_funds_combined(self):
        """Test combined fund list"""
        assert len(ALL_FUNDS) >= len(HDFC_FUNDS)


class TestScraperStructure:
    """Test scraper module structure"""
    
    def test_scraper_imports(self):
        """Test that scraper can be imported"""
        try:
            from src.scrapers.indmoney_scraper import INDMoneyScraper
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import scraper: {e}")
    
    def test_scraper_initialization(self):
        """Test scraper initialization"""
        from src.scrapers.indmoney_scraper import INDMoneyScraper
        
        # Test without Selenium
        scraper = INDMoneyScraper(use_selenium=False)
        assert scraper is not None
        assert scraper.base_url is not None
    
    def test_scraper_methods_exist(self):
        """Test that required methods exist"""
        from src.scrapers.indmoney_scraper import INDMoneyScraper
        
        scraper = INDMoneyScraper(use_selenium=False)
        
        assert hasattr(scraper, 'scrape_fund_scheme')
        assert hasattr(scraper, 'scrape_all_funds')
        assert hasattr(scraper, 'close')


class TestStorageStructure:
    """Test storage module structure"""
    
    def test_storage_imports(self):
        """Test that storage can be imported"""
        try:
            from src.storage.raw_data_storage import RawDataStorage
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import storage: {e}")
    
    def test_storage_initialization(self):
        """Test storage initialization"""
        from src.storage.raw_data_storage import RawDataStorage
        
        storage = RawDataStorage()
        assert storage is not None
        assert storage.raw_dir is not None
    
    def test_storage_methods_exist(self):
        """Test that required storage methods exist"""
        from src.storage.raw_data_storage import RawDataStorage
        
        storage = RawDataStorage()
        
        assert hasattr(storage, 'save_to_json')
        assert hasattr(storage, 'save_to_csv')
        assert hasattr(storage, 'load_from_json')
        assert hasattr(storage, 'get_storage_stats')


class TestDataValidation:
    """Test data validation and constraints"""
    
    def test_expense_ratio_range(self):
        """Test expense ratio is reasonable"""
        # Typical range is 0-3%
        fund = FundScheme(
            fund_name="Test Fund",
            scheme_type="Direct",
            category="ELSS",
            expense_ratio=2.5
        )
        assert 0 <= fund.expense_ratio <= 3.0
    
    def test_minimum_sip_reasonable(self):
        """Test minimum SIP amount is reasonable"""
        # Typical minimum SIP is ₹100-₹5000
        fund = FundScheme(
            fund_name="Test Fund",
            scheme_type="Direct",
            category="ELSS",
            minimum_sip=500.0
        )
        assert fund.minimum_sip >= 100.0
    
    def test_lock_in_period_format(self):
        """Test lock-in period string format"""
        fund = FundScheme(
            fund_name="HDFC ELSS Tax Saver Fund",
            scheme_type="Direct",
            category="ELSS",
            lock_in_period="3 years"
        )
        assert isinstance(fund.lock_in_period, str)
        assert "year" in fund.lock_in_period.lower() or "nil" in fund.lock_in_period.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
