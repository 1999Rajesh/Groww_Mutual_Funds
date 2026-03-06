"""
Data Cleaning and Normalization Module
Cleans scraped fund data and standardizes formats
"""
import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Cleans and normalizes mutual fund data
    """
    
    def __init__(self):
        """Initialize data cleaner"""
        self.currency_symbol = '₹'
        self.percentage_symbol = '%'
    
    def clean_all_fields(self, fund_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean all fields in fund data
        
        Args:
            fund_data: Raw fund data dictionary
            
        Returns:
            Cleaned fund data
        """
        cleaned = fund_data.copy()
        
        # Clean text fields
        if 'fund_name' in cleaned:
            cleaned['fund_name'] = self.clean_text(cleaned['fund_name'])
        
        if 'scheme_type' in cleaned:
            cleaned['scheme_type'] = self.clean_text(cleaned['scheme_type'])
        
        if 'category' in cleaned:
            cleaned['category'] = self.clean_category(cleaned['category'])
        
        # Clean numeric fields
        if 'expense_ratio' in cleaned:
            cleaned['expense_ratio'] = self.clean_percentage(cleaned['expense_ratio'])
        
        if 'minimum_sip' in cleaned:
            cleaned['minimum_sip'] = self.clean_currency(cleaned['minimum_sip'])
        
        if 'minimum_lumpsum' in cleaned:
            cleaned['minimum_lumpsum'] = self.clean_currency(cleaned['minimum_lumpsum'])
        
        # Clean lock-in period
        if 'lock_in_period' in cleaned:
            cleaned['lock_in_period'] = self.clean_lock_in_period(cleaned['lock_in_period'])
        
        # Clean exit load
        if 'exit_load' in cleaned:
            cleaned['exit_load'] = self.clean_exit_load(cleaned['exit_load'])
        
        # Clean risk level
        if 'risk_level' in cleaned:
            cleaned['risk_level'] = self.clean_risk_level(cleaned['risk_level'])
        
        # Clean benchmark
        if 'benchmark' in cleaned:
            cleaned['benchmark'] = self.clean_benchmark(cleaned['benchmark'])
        
        # Clean AUM
        if 'aum' in cleaned:
            cleaned['aum'] = self.clean_aum(cleaned['aum'])
        
        # Clean NAV
        if 'nav' in cleaned:
            cleaned['nav'] = self.clean_nav(cleaned['nav'])
        
        # Clean returns
        for period in ['returns_1y', 'returns_3y', 'returns_5y']:
            if period in cleaned:
                cleaned[period] = self.clean_percentage(cleaned[period])
        
        # Add cleaning timestamp
        cleaned['cleaned_at'] = datetime.now().isoformat()
        
        return cleaned
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing extra spaces and special characters
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Trim whitespace
        text = text.strip()
        
        return text
    
    def clean_category(self, category: str) -> str:
        """
        Standardize category names
        
        Args:
            category: Raw category
            
        Returns:
            Standardized category
        """
        if not category:
            return "Unknown"
        
        category = self.clean_text(category)
        
        # Standardize common categories
        category_mapping = {
            'ELSS': 'ELSS',
            'Equity Linked Savings Scheme': 'ELSS',
            'Large Cap': 'Large Cap',
            'Large Cap Fund': 'Large Cap',
            'Mid Cap': 'Mid Cap',
            'Mid Cap Fund': 'Mid Cap',
            'Small Cap': 'Small Cap',
            'Small Cap Fund': 'Small Cap',
            'Hybrid': 'Hybrid',
            'Hybrid Fund': 'Hybrid',
            'Balanced Advantage': 'Hybrid',
            'Debt': 'Debt',
            'Debt Fund': 'Debt',
            'Liquid': 'Liquid',
            'Money Market': 'Money Market',
            'Gold ETF FoF': 'Gold ETF FoF',
            'Silver ETF FoF': 'Silver ETF FoF',
            'FoF': 'FoF',
            'Fund of Funds': 'FoF',
        }
        
        for key, value in category_mapping.items():
            if key.lower() in category.lower():
                return value
        
        return category
    
    def clean_percentage(self, value: Any) -> Optional[float]:
        """
        Clean percentage values
        
        Args:
            value: Raw percentage value (string or number)
            
        Returns:
            Cleaned float value or None
        """
        if value is None or value == '':
            return None
        
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove % symbol and spaces
            value = value.replace('%', '').strip()
            
            try:
                return float(value)
            except ValueError:
                logger.warning(f"Could not parse percentage: {value}")
                return None
        
        return None
    
    def clean_currency(self, value: Any) -> Optional[float]:
        """
        Clean currency values (INR)
        
        Args:
            value: Raw currency value
            
        Returns:
            Cleaned float value or None
        """
        if value is None or value == '':
            return None
        
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove currency symbols and commas
            value = value.replace('₹', '').replace('Rs', '').replace(',', '').strip()
            
            # Handle "Cr" or "Crore" suffixes
            multiplier = 1.0
            if 'Cr' in value or 'crore' in value.lower():
                multiplier = 10000000.0
                value = value.replace('Cr', '').replace('crore', '')
            elif 'Mn' in value or 'million' in value.lower():
                multiplier = 1000000.0
                value = value.replace('Mn', '').replace('million', '')
            
            value = value.strip()
            
            try:
                return float(value) * multiplier
            except ValueError:
                logger.warning(f"Could not parse currency: {value}")
                return None
        
        return None
    
    def clean_lock_in_period(self, value: str) -> str:
        """
        Standardize lock-in period format
        
        Args:
            value: Raw lock-in period
            
        Returns:
            Standardized lock-in period
        """
        if not value:
            return "Nil"
        
        value = self.clean_text(value)
        
        # Common patterns
        if 'nil' in value.lower() or 'none' in value.lower() or 'no' in value.lower():
            return "Nil"
        
        # Standardize years
        if 'year' in value.lower():
            # Extract number
            match = re.search(r'(\d+\.?\d*)\s*year', value.lower())
            if match:
                years = float(match.group(1))
                if years == 3:
                    return "3 years"
                elif years == 1:
                    return "1 year"
                else:
                    return f"{years} years"
        
        # For ELSS, default to 3 years
        if 'elss' in value.lower():
            return "3 years"
        
        return value
    
    def clean_exit_load(self, value: str) -> str:
        """
        Standardize exit load description
        
        Args:
            value: Raw exit load
            
        Returns:
            Standardized exit load
        """
        if not value:
            return "Nil"
        
        value = self.clean_text(value)
        
        # Common patterns
        if 'nil' in value.lower() or 'none' in value.lower() or 'no exit load' in value.lower():
            return "Nil"
        
        return value
    
    def clean_risk_level(self, value: str) -> str:
        """
        Standardize risk level
        
        Args:
            value: Raw risk level
            
        Returns:
            Standardized risk level (Low, Moderate, High, Very High)
        """
        if not value:
            return "Unknown"
        
        value = self.clean_text(value).lower()
        
        # Map to standard levels
        if 'very high' in value or 'veryhigh' in value:
            return "Very High"
        elif 'high' in value:
            return "High"
        elif 'moderate' in value or 'medium' in value:
            return "Moderate"
        elif 'low' in value:
            return "Low"
        
        return value.capitalize()
    
    def clean_benchmark(self, value: str) -> str:
        """
        Standardize benchmark name
        
        Args:
            value: Raw benchmark
            
        Returns:
            Standardized benchmark
        """
        if not value:
            return "Not specified"
        
        return self.clean_text(value)
    
    def clean_aum(self, value: Any) -> Optional[float]:
        """
        Clean AUM (Assets Under Management) in Crores
        
        Args:
            value: Raw AUM value
            
        Returns:
            Cleaned AUM in Crores or None
        """
        if value is None or value == '':
            return None
        
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove common suffixes
            value = value.lower().replace('cr', '').replace('crore', '').strip()
            
            try:
                return float(value)
            except ValueError:
                logger.warning(f"Could not parse AUM: {value}")
                return None
        
        return None
    
    def clean_nav(self, value: Any) -> Optional[float]:
        """
        Clean NAV value
        
        Args:
            value: Raw NAV value
            
        Returns:
            Cleaned NAV or None
        """
        if value is None or value == '':
            return None
        
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove currency symbols
            value = value.replace('₹', '').replace('Rs', '').replace(',', '').strip()
            
            try:
                return float(value)
            except ValueError:
                logger.warning(f"Could not parse NAV: {value}")
                return None
        
        return None
    
    def validate_fund_data(self, fund_data: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate cleaned fund data
        
        Args:
            fund_data: Cleaned fund data
            
        Returns:
            Dictionary with validation results
        """
        validation = {}
        
        # Required fields
        required_fields = ['fund_name', 'scheme_type', 'category']
        for field in required_fields:
            validation[f'{field}_present'] = field in fund_data and bool(fund_data.get(field))
        
        # Numeric field ranges
        if 'expense_ratio' in fund_data and fund_data['expense_ratio'] is not None:
            validation['expense_ratio_valid'] = 0 <= fund_data['expense_ratio'] <= 5.0
        else:
            validation['expense_ratio_valid'] = False
        
        if 'minimum_sip' in fund_data and fund_data['minimum_sip'] is not None:
            validation['minimum_sip_valid'] = fund_data['minimum_sip'] >= 100
        else:
            validation['minimum_sip_valid'] = False
        
        # Overall validity
        validation['is_valid'] = all([
            validation.get('fund_name_present', False),
            validation.get('scheme_type_present', False),
            validation.get('category_present', False)
        ])
        
        return validation


def main():
    """Test data cleaner"""
    cleaner = DataCleaner()
    
    # Test data
    test_data = {
        'fund_name': '  HDFC ELSS Tax Saver Fund  ',
        'scheme_type': 'Direct Plan - Growth Option',
        'category': 'Equity Linked Savings Scheme',
        'expense_ratio': '0.68%',
        'minimum_sip': '₹500',
        'minimum_lumpsum': '₹5,000',
        'lock_in_period': '3 years',
        'exit_load': 'Nil',
        'risk_level': 'Very High',
        'benchmark': 'NIFTY 500 TRI',
        'aum': '₹28,500 Cr',
        'nav': '₹845.32',
        'returns_1y': '12.5%'
    }
    
    print("Original Data:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    print("\nCleaned Data:")
    cleaned = cleaner.clean_all_fields(test_data)
    for key, value in cleaned.items():
        print(f"  {key}: {value}")
    
    print("\nValidation:")
    validation = cleaner.validate_fund_data(cleaned)
    for key, result in validation.items():
        print(f"  {key}: {result}")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    main()
