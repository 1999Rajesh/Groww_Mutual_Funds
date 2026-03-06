"""
FAQ Assistant - Working Prototype
Answers factual queries about mutual funds with citations
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from src.config import DATA_RAW_DIR, DATA_PROCESSED_DIR
from src.models.fund_schema import FundScheme

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FAQAssistant:
    """
    FAQ Assistant for mutual fund queries
    Answers factual questions with citations
    """
    
    def __init__(self):
        """Initialize the FAQ Assistant"""
        self.funds_data = []
        self.knowledge_base = []
        self.load_data()
    
    def load_data(self):
        """Load scraped fund data"""
        raw_dir = Path(DATA_RAW_DIR) / "raw"
        
        # Load latest JSON file
        json_files = list(raw_dir.glob("mutual_funds_*.json"))
        
        if not json_files:
            logger.warning("No scraped data found. Please run scraper first.")
            return
        
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'data' in data:
            self.funds_data = data['data']
        else:
            self.funds_data = data
        
        logger.info(f"Loaded {len(self.funds_data)} funds from {latest_file.name}")
        
        # Build knowledge base
        self._build_knowledge_base()
    
    def _build_knowledge_base(self):
        """Build structured knowledge base from fund data"""
        self.knowledge_base = []
        
        for fund in self.funds_data:
            fund_name = fund.get('fund_name', 'Unknown')
            source_url = fund.get('source_url', '')
            
            # Add expense ratio info
            if fund.get('expense_ratio'):
                self.knowledge_base.append({
                    'fund_name': fund_name,
                    'topic': 'expense_ratio',
                    'question': f"What is the expense ratio of {fund_name}?",
                    'answer': f"The expense ratio of {fund_name} is {fund['expense_ratio']}%",
                    'source_url': source_url,
                    'data': fund
                })
            
            # Add minimum SIP info
            if fund.get('minimum_sip'):
                self.knowledge_base.append({
                    'fund_name': fund_name,
                    'topic': 'minimum_sip',
                    'question': f"What is the minimum SIP amount for {fund_name}?",
                    'answer': f"The minimum SIP amount for {fund_name} is ₹{fund['minimum_sip']}",
                    'source_url': source_url,
                    'data': fund
                })
            
            # Add lock-in period info
            if fund.get('lock_in_period'):
                self.knowledge_base.append({
                    'fund_name': fund_name,
                    'topic': 'lock_in',
                    'question': f"What is the lock-in period for {fund_name}?",
                    'answer': f"{fund_name} has a lock-in period of {fund['lock_in_period']}",
                    'source_url': source_url,
                    'data': fund
                })
            
            # Add exit load info
            if fund.get('exit_load'):
                self.knowledge_base.append({
                    'fund_name': fund_name,
                    'topic': 'exit_load',
                    'question': f"What is the exit load for {fund_name}?",
                    'answer': f"The exit load for {fund_name} is: {fund['exit_load']}",
                    'source_url': source_url,
                    'data': fund
                })
            
            # Add risk level info
            if fund.get('risk_level'):
                self.knowledge_base.append({
                    'fund_name': fund_name,
                    'topic': 'risk_level',
                    'question': f"What is the risk level of {fund_name}?",
                    'answer': f"{fund_name} has a {fund['risk_level']} risk level",
                    'source_url': source_url,
                    'data': fund
                })
            
            # Add benchmark info
            if fund.get('benchmark'):
                self.knowledge_base.append({
                    'fund_name': fund_name,
                    'topic': 'benchmark',
                    'question': f"What is the benchmark for {fund_name}?",
                    'answer': f"{fund_name} is benchmarked against {fund['benchmark']}",
                    'source_url': source_url,
                    'data': fund
                })
            
            # Add minimum lumpsum info
            if fund.get('minimum_lumpsum'):
                self.knowledge_base.append({
                    'fund_name': fund_name,
                    'topic': 'minimum_lumpsum',
                    'question': f"What is the minimum lumpsum investment for {fund_name}?",
                    'answer': f"The minimum lumpsum investment for {fund_name} is ₹{fund['minimum_lumpsum']}",
                    'source_url': source_url,
                    'data': fund
                })
        
        logger.info(f"Built knowledge base with {len(self.knowledge_base)} entries")
    
    def ask(self, query: str) -> Dict:
        """
        Ask a question and get an answer with citation
        
        Args:
            query: User's question
            
        Returns:
            Dictionary with answer, confidence, and citation
        """
        query_lower = query.lower()
        
        # Check for opinion/portfolio questions (should refuse)
        opinion_keywords = ['should i', 'should we', 'buy', 'sell', 'invest', 
                          'recommend', 'suggest', 'better', 'best', 'good']
        
        if any(keyword in query_lower for keyword in opinion_keywords):
            return {
                'answer': "I can only provide factual information about mutual funds. I cannot provide investment advice or recommendations. For personalized investment advice, please consult a SEBI-registered financial advisor.",
                'confidence': 1.0,
                'citation': "https://www.sebi.gov.in/investor-resources.html",
                'refused': True
            }
        
        # Find matching fund name in query
        matched_fund = None
        for fund in self.funds_data:
            if fund['fund_name'].lower() in query_lower:
                matched_fund = fund['fund_name']
                break
        
        # Find relevant knowledge base entry
        best_match = None
        best_score = 0
        
        for entry in self.knowledge_base:
            score = 0
            
            # Check if fund name matches
            if matched_fund and entry['fund_name'] == matched_fund:
                score += 50
            
            # Check if topic keywords match
            topic_keywords = entry['topic'].split('_')
            for keyword in topic_keywords:
                if keyword in query_lower:
                    score += 30
            
            # Check if question words match
            if entry['question'].lower() in query_lower or query_lower in entry['question'].lower():
                score += 100
            
            # Partial matching
            common_words = set(query_lower.split()) & set(entry['question'].lower().split())
            score += len(common_words) * 10
            
            if score > best_score:
                best_score = score
                best_match = entry
        
        # Return answer if confidence is high enough
        if best_match and best_score >= 40:
            return {
                'answer': best_match['answer'],
                'confidence': min(best_score / 100, 0.95),
                'citation': best_match['source_url'],
                'fund_name': best_match['fund_name'],
                'topic': best_match['topic'],
                'refused': False
            }
        
        # No match found
        return {
            'answer': f"I don't have specific information about that. You can check the official INDMoney page for detailed information.",
            'confidence': 0.0,
            'citation': "https://www.indmoney.com/mutual-funds",
            'refused': False
        }
    
    def get_example_questions(self) -> List[str]:
        """Get example questions for the UI"""
        examples = []
        
        # Get one example per primary scheme
        primary_schemes = [
            "HDFC ELSS Tax Saver Fund",
            "HDFC Large Cap Fund",
            "HDFC Small Cap Fund",
        ]
        
        for scheme in primary_schemes:
            # Find expense ratio question
            for entry in self.knowledge_base:
                if entry['fund_name'] == scheme and entry['topic'] == 'expense_ratio':
                    examples.append(entry['question'])
                    break
        
        # Add generic questions
        examples.extend([
            "What is the minimum SIP for HDFC Balanced Advantage Fund?",
            "ELSS lock-in period?",
        ])
        
        return examples[:5]  # Return max 5 examples
    
    def get_welcome_message(self) -> str:
        """Get welcome message for the UI"""
        return (
            "👋 Welcome to HDFC Mutual Funds FAQ Assistant!\n\n"
            "I can answer factual questions about HDFC Mutual Fund schemes.\n"
            "Ask me about expense ratios, SIP amounts, lock-in periods, exit loads, and more."
        )


def create_simple_ui():
    """Create a simple command-line UI"""
    assistant = FAQAssistant()
    
    print("\n" + "="*80)
    print(assistant.get_welcome_message())
    print("="*80)
    print("\n⚠️  Facts-only. No investment advice.")
    print("\nExample questions:")
    
    examples = assistant.get_example_questions()
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example}")
    
    print("\n" + "="*80)
    print("Type your question below (or 'quit' to exit):\n")
    
    while True:
        try:
            query = input("> ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\nThank you for using FAQ Assistant. Goodbye!")
                break
            
            if not query:
                continue
            
            print("\n🤔 Thinking...\n")
            
            response = assistant.ask(query)
            
            print(f"💡 Answer: {response['answer']}")
            
            if response.get('citation'):
                print(f"\n📚 Source: {response['citation']}")
            
            if response.get('refused'):
                print(f"\nℹ️  Note: This is an educational resource only.")
            
            print("\n" + "-"*80 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nThank you for using FAQ Assistant. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


if __name__ == "__main__":
    create_simple_ui()
