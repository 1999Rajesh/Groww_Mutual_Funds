"""
Query Processor Module - Phase 5
Processes and understands user queries for RAG system
"""
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class QueryProcessor:
    """
    Processes and extracts information from user queries
    """
    
    def __init__(self):
        """Initialize query processor"""
        
        # Fund name patterns
        self.fund_patterns = {
            'elss': [r'elss', r'tax saver', r'tax saving', r'80c'],
            'large_cap': [r'large cap', r'large-cap', r'bluechip', r'blue chip'],
            'mid_cap': [r'mid cap', r'mid-cap', r'midcap'],
            'small_cap': [r'small cap', r'small-cap', r'smallcap'],
            'balanced': [r'balanced', r'hybrid', r'conservative', r'aggressive'],
            'liquid': [r'liquid', r'overnight', r'money market'],
            'debt': [r'debt', r'bond', r'fixed income', r'corporate bond'],
            'gold': [r'gold', r'precious metal', r'etf gold'],
            'children': [r"children's", r"kids", r'child']
        }
        
        # Query intent patterns
        self.intent_patterns = {
            'expense_ratio': [r'expense ratio', r'expense', r'total expense ratio', r'ter', r'管理费'],
            'minimum_sip': [r'minimum sip', r'min sip', r'sip amount', r'monthly investment'],
            'minimum_lumpsum': [r'minimum lumpsum', r'min lumpsum', r'one time investment', r'lumpsum'],
            'lock_in': [r'lock in', r'lock-in', r'lock period', r'maturity period'],
            'exit_load': [r'exit load', r'exit fee', r'redemption fee', r'penalty'],
            'risk': [r'risk', r'riskometer', r'risk level', r'volatility'],
            'benchmark': [r'benchmark', r'index', r'comparison index'],
            'returns': [r'return', r'yield', r'performance', r'cagr', r'growth'],
            'nav': [r'nav', r'net asset value', r'price per unit'],
            'aum': [r'aum', r'asset size', r'fund size', r'assets under management']
        }
        
        # Fund house names
        self.amc_names = [
            'HDFC', 'ICICI', 'SBI', 'Axis', 'Kotak', 'Aditya Birla',
            'Nippon', 'UTI', 'DSP', 'Franklin', 'IDFC', 'Invesco'
        ]
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query and extract structured information
        
        Args:
            query: User's question
            
        Returns:
            Dictionary with extracted information
        """
        logger.info(f"Processing query: '{query}'")
        
        query_lower = query.lower()
        
        # Extract components
        extracted = {
            'original_query': query,
            'processed_at': datetime.now().isoformat(),
            'fund_name': self._extract_fund_name(query_lower),
            'fund_category': self._extract_fund_category(query_lower),
            'intent': self._extract_intent(query_lower),
            'amc': self._extract_amc(query_lower),
            'query_type': self._classify_query_type(query_lower),
            'entities': self._extract_entities(query_lower),
            'is_comparison': self._is_comparison_query(query_lower),
            'is_opinion': self._is_opinion_query(query_lower)
        }
        
        logger.info(f"Extracted: fund={extracted['fund_name']}, intent={extracted['intent']}, category={extracted['fund_category']}")
        
        return extracted
    
    def _extract_fund_name(self, query: str) -> Optional[str]:
        """Extract specific fund name from query"""
        
        # Full fund name patterns
        fund_names = [
            r'hdfc elss tax saver',
            r'hdfc large cap',
            r'hdfc mid cap',
            r'hdfc small cap',
            r'hdfc balanced advantage',
            r'hdfc liquid',
            r'hdfc children',
            r'hdfc retirement savings',
            r'hdfc multi cap',
            r'hdfc diversified equity'
        ]
        
        for pattern in fund_names:
            if re.search(pattern, query, re.IGNORECASE):
                # Return standardized name
                return self._standardize_fund_name(pattern)
        
        return None
    
    def _standardize_fund_name(self, pattern: str) -> str:
        """Convert pattern to standardized fund name"""
        mapping = {
            r'hdfc elss tax saver': 'HDFC ELSS Tax Saver Fund',
            r'hdfc large cap': 'HDFC Large Cap Fund',
            r'hdfc mid cap': 'HDFC Mid Cap Fund',
            r'hdfc small cap': 'HDFC Small Cap Fund',
            r'hdfc balanced advantage': 'HDFC Balanced Advantage Fund',
            r'hdfc liquid': 'HDFC Liquid Fund',
            r'hdfc children': "HDFC Children's Fund",
            r'hdfc retirement savings': 'HDFC Retirement Savings Fund',
            r'hdfc multi cap': 'HDFC Multi Cap Fund',
            r'hdfc diversified equity': 'HDFC Diversified Equity Fund'
        }
        return mapping.get(pattern, 'Unknown Fund')
    
    def _extract_fund_category(self, query: str) -> Optional[str]:
        """Extract fund category from query"""
        
        for category, patterns in self.fund_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return category
        
        return None
    
    def _extract_intent(self, query: str) -> Optional[str]:
        """Extract user intent from query"""
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return intent
        
        # Default intent
        return 'general_inquiry'
    
    def _extract_amc(self, query: str) -> Optional[str]:
        """Extract AMC/Asset Management Company name"""
        
        for amc in self.amc_names:
            if amc.lower() in query:
                return amc
        
        return None
    
    def _classify_query_type(self, query: str) -> str:
        """Classify the type of query"""
        
        if '?' in query or query.startswith('what') or query.startswith('how'):
            return 'factual_question'
        elif any(word in query for word in ['compare', 'vs', 'versus', 'better']):
            return 'comparison'
        elif any(word in query for word in ['should', 'recommend', 'suggest', 'advice']):
            return 'opinion'
        else:
            return 'statement'
    
    def _extract_entities(self, query: str) -> List[Dict[str, str]]:
        """Extract named entities from query"""
        
        entities = []
        
        # Extract numbers (amounts, percentages, years)
        number_patterns = [
            (r'₹\s*(\d+(?:,\d{3})*(?:\.\d+)?)', 'currency_inr'),
            (r'rs\s*(\d+(?:,\d{3})*(?:\.\d+)?)', 'currency_inr'),
            (r'(\d+(?:\.\d+)?)\s*%', 'percentage'),
            (r'(\d+(?:\.\d+)?)\s*(years?|yrs?|months?|mos?)', 'duration')
        ]
        
        for pattern, entity_type in number_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                entities.append({
                    'type': entity_type,
                    'value': match if isinstance(match, str) else match[0],
                    'text': match
                })
        
        return entities
    
    def _is_comparison_query(self, query: str) -> bool:
        """Check if query is comparing multiple funds"""
        
        comparison_keywords = ['compare', 'vs', 'versus', 'better', 'difference between']
        
        return any(keyword in query for keyword in comparison_keywords)
    
    def _is_opinion_query(self, query: str) -> bool:
        """Check if query is asking for opinion/advice"""
        
        opinion_keywords = [
            'should i', 'should we', 'should my',
            'recommend', 'suggestion', 'advise',
            'good to buy', 'worth investing',
            'best fund', 'top fund'
        ]
        
        return any(keyword in query.lower() for keyword in opinion_keywords)
    
    def enhance_query(
        self,
        query: str,
        extracted_info: Dict[str, Any]
    ) -> str:
        """
        Enhance query with extracted information for better retrieval
        
        Args:
            query: Original query
            extracted_info: Extracted information dictionary
            
        Returns:
            Enhanced query string
        """
        enhanced_parts = [query]
        
        # Add fund name if extracted
        if extracted_info.get('fund_name'):
            fund_name = extracted_info['fund_name']
            if fund_name not in query:
                enhanced_parts.append(fund_name)
        
        # Add intent keywords
        intent = extracted_info.get('intent')
        if intent:
            intent_keywords = {
                'expense_ratio': 'expense ratio ter',
                'minimum_sip': 'minimum sip amount',
                'lock_in': 'lock in period years',
                'exit_load': 'exit load penalty fee',
                'risk': 'risk level riskometer',
                'benchmark': 'benchmark index'
            }
            
            keyword = intent_keywords.get(intent)
            if keyword and keyword not in query:
                enhanced_parts.append(keyword)
        
        enhanced_query = ' '.join(enhanced_parts)
        
        logger.info(f"Enhanced query: '{enhanced_query}'")
        
        return enhanced_query
    
    def get_filter_params(
        self,
        extracted_info: Dict[str, Any]
    ) -> Dict[str, Optional[str]]:
        """
        Get filter parameters for vector search
        
        Args:
            extracted_info: Extracted information
            
        Returns:
            Dictionary with filter parameters
        """
        filters = {
            'fund_name': extracted_info.get('fund_name'),
            'fund_category': extracted_info.get('fund_category'),
            'chunk_type': None
        }
        
        # Map intent to chunk type
        intent = extracted_info.get('intent')
        if intent:
            chunk_type_mapping = {
                'expense_ratio': 'investment_details',
                'minimum_sip': 'investment_details',
                'lock_in': 'lock_in_exit',
                'exit_load': 'lock_in_exit',
                'risk': 'risk_benchmark',
                'benchmark': 'risk_benchmark'
            }
            filters['chunk_type'] = chunk_type_mapping.get(intent)
        
        return filters


def main():
    """Test query processor"""
    print("="*80)
    print("Testing Query Processor")
    print("="*80)
    
    processor = QueryProcessor()
    
    # Test queries
    test_queries = [
        "What is the expense ratio of HDFC ELSS Tax Saver Fund?",
        "Minimum SIP amount for large cap fund?",
        "What is the lock-in period for ELSS?",
        "Exit load for HDFC Small Cap Fund?",
        "Risk level of balanced advantage fund?",
        "Should I invest in HDFC ELSS?",
        "Compare HDFC Large Cap vs Small Cap Fund"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print(f"{'='*80}")
        
        # Process query
        extracted = processor.process_query(query)
        
        print(f"\nExtracted Information:")
        print(f"  Fund Name: {extracted.get('fund_name')}")
        print(f"  Fund Category: {extracted.get('fund_category')}")
        print(f"  Intent: {extracted.get('intent')}")
        print(f"  AMC: {extracted.get('amc')}")
        print(f"  Query Type: {extracted.get('query_type')}")
        print(f"  Is Comparison: {extracted.get('is_comparison')}")
        print(f"  Is Opinion: {extracted.get('is_opinion')}")
        
        if extracted.get('entities'):
            print(f"  Entities: {extracted['entities']}")
        
        # Enhance query
        enhanced = processor.enhance_query(query, extracted)
        print(f"\nEnhanced Query: {enhanced}")
        
        # Get filters
        filters = processor.get_filter_params(extracted)
        print(f"Filters: {filters}")
    
    print("\n✅ Query Processor Test Complete!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
