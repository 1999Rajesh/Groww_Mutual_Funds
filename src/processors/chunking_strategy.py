"""
Intelligent Chunking Strategy Module
Creates optimized chunks for RAG retrieval
"""
import hashlib
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.models.fund_schema import FundChunk

logger = logging.getLogger(__name__)


class ChunkingStrategy:
    """
    Implements intelligent chunking strategies for mutual fund data
    """
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize chunking strategy
        
        Args:
            chunk_size: Target token count per chunk
            chunk_overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_fund_data(self, fund_data: Dict[str, Any]) -> List[FundChunk]:
        """
        Create chunks from fund data using semantic chunking
        
        Args:
            fund_data: Cleaned fund data dictionary
            
        Returns:
            List of FundChunk objects
        """
        chunks = []
        
        # Strategy 1: Field-based semantic chunks
        field_chunks = self._create_field_chunks(fund_data)
        chunks.extend(field_chunks)
        
        # Strategy 2: Combined summary chunks
        summary_chunks = self._create_summary_chunks(fund_data)
        chunks.extend(summary_chunks)
        
        # Strategy 3: Q&A style chunks (for better retrieval)
        qa_chunks = self._create_qa_style_chunks(fund_data)
        chunks.extend(qa_chunks)
        
        logger.info(f"Created {len(chunks)} chunks for {fund_data.get('fund_name', 'Unknown')}")
        
        return chunks
    
    def _create_field_chunks(self, fund_data: Dict[str, Any]) -> List[FundChunk]:
        """
        Create chunks based on individual fields
        
        Args:
            fund_data: Fund data dictionary
            
        Returns:
            List of field-based chunks
        """
        chunks = []
        fund_name = fund_data.get('fund_name', 'Unknown Fund')
        source_url = fund_data.get('source_url', '')
        timestamp = datetime.now().isoformat()
        
        # Define field groups and their templates
        field_groups = {
            'basic_info': {
                'fields': ['fund_name', 'scheme_type', 'category'],
                'template': "{fund_name} - {scheme_type} in {category} category"
            },
            'investment_details': {
                'fields': ['expense_ratio', 'minimum_sip', 'minimum_lumpsum'],
                'template': self._create_investment_template(fund_data)
            },
            'lock_in_exit': {
                'fields': ['lock_in_period', 'exit_load'],
                'template': self._create_lockin_exit_template(fund_data)
            },
            'risk_benchmark': {
                'fields': ['risk_level', 'benchmark'],
                'template': "Risk Level: {risk_level}. Benchmark: {benchmark}"
            },
            'performance': {
                'fields': ['returns_1y', 'returns_3y', 'returns_5y', 'aum', 'nav'],
                'template': self._create_performance_template(fund_data)
            }
        }
        
        for group_name, config in field_groups.items():
            chunk_text = self._format_chunk_from_template(fund_data, config)
            
            if chunk_text:
                chunk_id = self._generate_chunk_id(fund_name, group_name)
                
                chunk = FundChunk(
                    fund_name=fund_name,
                    chunk_id=chunk_id,
                    chunk_text=chunk_text,
                    chunk_type=group_name,
                    metadata={
                        'source_url': source_url,
                        'scraped_at': timestamp,
                        'fields': config['fields']
                    },
                    token_count=self._estimate_tokens(chunk_text)
                )
                
                chunks.append(chunk)
        
        return chunks
    
    def _create_summary_chunks(self, fund_data: Dict[str, Any]) -> List[FundChunk]:
        """
        Create comprehensive summary chunks
        
        Args:
            fund_data: Fund data dictionary
            
        Returns:
            List of summary chunks
        """
        chunks = []
        fund_name = fund_data.get('fund_name', 'Unknown Fund')
        source_url = fund_data.get('source_url', '')
        timestamp = datetime.now().isoformat()
        
        # Create a comprehensive summary
        summary_parts = []
        
        # Basic info
        if fund_data.get('category'):
            summary_parts.append(f"{fund_name} is a {fund_data['category']} fund")
        
        # Key investment details
        key_details = []
        if fund_data.get('expense_ratio'):
            key_details.append(f"expense ratio {fund_data['expense_ratio']}%")
        if fund_data.get('minimum_sip'):
            key_details.append(f"minimum SIP ₹{fund_data['minimum_sip']}")
        if fund_data.get('lock_in_period'):
            key_details.append(f"lock-in period {fund_data['lock_in_period']}")
        
        if key_details:
            summary_parts.append(f"Key features: {', '.join(key_details)}")
        
        # Risk and performance
        if fund_data.get('risk_level'):
            summary_parts.append(f"Risk level: {fund_data['risk_level']}")
        if fund_data.get('benchmark'):
            summary_parts.append(f"Benchmark: {fund_data['benchmark']}")
        
        summary_text = ". ".join(summary_parts) + "."
        
        chunk_id = self._generate_chunk_id(fund_name, 'comprehensive_summary')
        
        chunk = FundChunk(
            fund_name=fund_name,
            chunk_id=chunk_id,
            chunk_text=summary_text,
            chunk_type='summary',
            metadata={
                'source_url': source_url,
                'scraped_at': timestamp,
                'is_summary': True
            },
            token_count=self._estimate_tokens(summary_text)
        )
        
        chunks.append(chunk)
        
        return chunks
    
    def _create_qa_style_chunks(self, fund_data: Dict[str, Any]) -> List[FundChunk]:
        """
        Create Q&A style chunks for better question matching
        
        Args:
            fund_data: Fund data dictionary
            
        Returns:
            List of Q&A style chunks
        """
        chunks = []
        fund_name = fund_data.get('fund_name', 'Unknown Fund')
        source_url = fund_data.get('source_url', '')
        timestamp = datetime.now().isoformat()
        
        # Common question patterns
        qa_pairs = []
        
        # Expense ratio
        if fund_data.get('expense_ratio'):
            qa_pairs.append({
                'question': f"What is the expense ratio of {fund_name}?",
                'answer': f"The expense ratio of {fund_name} is {fund_data['expense_ratio']}%"
            })
        
        # Minimum SIP
        if fund_data.get('minimum_sip'):
            qa_pairs.append({
                'question': f"What is the minimum SIP amount for {fund_name}?",
                'answer': f"The minimum SIP amount for {fund_name} is ₹{fund_data['minimum_sip']}"
            })
        
        # Lock-in period
        if fund_data.get('lock_in_period'):
            qa_pairs.append({
                'question': f"What is the lock-in period for {fund_name}?",
                'answer': f"{fund_name} has a lock-in period of {fund_data['lock_in_period']}"
            })
        
        # Exit load
        if fund_data.get('exit_load'):
            qa_pairs.append({
                'question': f"What is the exit load for {fund_name}?",
                'answer': f"The exit load for {fund_name} is: {fund_data['exit_load'] or 'Nil'}"
            })
        
        # Risk level
        if fund_data.get('risk_level'):
            qa_pairs.append({
                'question': f"What is the risk level of {fund_name}?",
                'answer': f"{fund_name} has a {fund_data['risk_level']} risk level"
            })
        
        # Benchmark
        if fund_data.get('benchmark'):
            qa_pairs.append({
                'question': f"What benchmark does {fund_name} track?",
                'answer': f"{fund_name} is benchmarked against {fund_data['benchmark']}"
            })
        
        # Create chunks from Q&A pairs
        for qa in qa_pairs:
            chunk_text = f"Q: {qa['question']}\nA: {qa['answer']}"
            chunk_id = self._generate_chunk_id(fund_name, f"qa_{hash(qa['question'])[:8]}")
            
            chunk = FundChunk(
                fund_name=fund_name,
                chunk_id=chunk_id,
                chunk_text=chunk_text,
                chunk_type='qa_pair',
                metadata={
                    'source_url': source_url,
                    'scraped_at': timestamp,
                    'question': qa['question'],
                    'answer': qa['answer']
                },
                token_count=self._estimate_tokens(chunk_text)
            )
            
            chunks.append(chunk)
        
        return chunks
    
    def _create_investment_template(self, fund_data: Dict[str, Any]) -> str:
        """Create investment details template"""
        parts = []
        
        if fund_data.get('expense_ratio'):
            parts.append("Expense Ratio: {expense_ratio}%")
        if fund_data.get('minimum_sip'):
            parts.append("Minimum SIP: ₹{minimum_sip}")
        if fund_data.get('minimum_lumpsum'):
            parts.append("Minimum Lumpsum: ₹{minimum_lumpsum}")
        
        return " | ".join(parts) if parts else ""
    
    def _create_lockin_exit_template(self, fund_data: Dict[str, Any]) -> str:
        """Create lock-in and exit load template"""
        parts = []
        
        if fund_data.get('lock_in_period'):
            parts.append("Lock-in: {lock_in_period}")
        if fund_data.get('exit_load'):
            parts.append("Exit Load: {exit_load}")
        
        return " | ".join(parts) if parts else ""
    
    def _create_performance_template(self, fund_data: Dict[str, Any]) -> str:
        """Create performance details template"""
        parts = []
        
        if fund_data.get('returns_1y'):
            parts.append("1Y Return: {returns_1y}%")
        if fund_data.get('returns_3y'):
            parts.append("3Y Return: {returns_3y}%")
        if fund_data.get('returns_5y'):
            parts.append("5Y Return: {returns_5y}%")
        if fund_data.get('aum'):
            parts.append("AUM: ₹{aum} Cr")
        if fund_data.get('nav'):
            parts.append("NAV: ₹{nav}")
        
        return " | ".join(parts) if parts else ""
    
    def _format_chunk_from_template(self, fund_data: Dict[str, Any], config: Dict) -> str:
        """Format chunk text from template"""
        template = config['template']
        
        if not template:
            return ""
        
        try:
            # Only include fields that exist in data
            available_data = {k: v for k, v in fund_data.items() if v is not None}
            return template.format(**available_data)
        except KeyError as e:
            logger.warning(f"Missing field for template: {e}")
            return ""
    
    def _generate_chunk_id(self, fund_name: str, chunk_type: str) -> str:
        """Generate unique chunk ID"""
        # Create hash from fund name and type
        unique_str = f"{fund_name}_{chunk_type}"
        hash_obj = hashlib.md5(unique_str.encode())
        hash_hex = hash_obj.hexdigest()[:8]
        
        # Clean fund name for ID
        clean_name = fund_name.lower().replace(' ', '_').replace('-', '_')[:30]
        
        return f"{clean_name}_{chunk_type}_{hash_hex}"
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Simple estimation: ~4 characters per token
        return len(text) // 4


def main():
    """Test chunking strategy"""
    from src.processors.data_cleaner import DataCleaner
    
    # Sample cleaned data
    test_data = {
        'fund_name': 'HDFC ELSS Tax Saver Fund',
        'scheme_type': 'Direct Plan - Growth Option',
        'category': 'ELSS',
        'expense_ratio': 0.68,
        'minimum_sip': 500.0,
        'minimum_lumpsum': 5000.0,
        'lock_in_period': '3 years',
        'exit_load': 'Nil',
        'risk_level': 'Very High',
        'benchmark': 'NIFTY 500 TRI',
        'fund_manager': 'Chirag Setalvad',
        'aum': 28500.5,
        'nav': 845.32,
        'returns_1y': 12.5,
        'returns_3y': 15.2,
        'returns_5y': 18.7,
        'source_url': 'https://www.indmoney.com/mutual-funds/hdfc-elss-taxsaver-direct-plan-growth-option-2685'
    }
    
    # Clean data first
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean_all_fields(test_data)
    
    # Create chunks
    chunker = ChunkingStrategy()
    chunks = chunker.chunk_fund_data(cleaned_data)
    
    print(f"\nCreated {len(chunks)} chunks:\n")
    
    for i, chunk in enumerate(chunks, 1):
        print(f"Chunk {i}:")
        print(f"  ID: {chunk.chunk_id}")
        print(f"  Type: {chunk.chunk_type}")
        print(f"  Text: {chunk.chunk_text[:100]}...")
        print(f"  Tokens: ~{chunk.token_count}")
        print()


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    main()
