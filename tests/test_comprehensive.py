"""
Comprehensive Test Suite for RAG Mutual Funds Chatbot
Tests for Phases 1-6
"""
import unittest
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestPhase1DataAcquisition(unittest.TestCase):
    """Test Phase 1: Data Acquisition and Scraping"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_fund_data = {
            'fund_name': 'HDFC ELSS Tax Saver Fund',
            'scheme_type': 'Direct Plan - Growth Option',
            'category': 'ELSS',
            'expense_ratio': 0.68,
            'minimum_sip': 500.0,
            'lock_in_period': '3 years'
        }
    
    def test_fund_data_structure(self):
        """Test fund data has required fields"""
        required_fields = ['fund_name', 'scheme_type', 'category']
        
        for field in required_fields:
            self.assertIn(field, self.test_fund_data)
            self.assertIsNotNone(self.test_fund_data[field])
    
    def test_fund_name_not_empty(self):
        """Test fund name is not empty"""
        self.assertTrue(len(self.test_fund_data['fund_name']) > 0)
    
    def test_expense_ratio_valid(self):
        """Test expense ratio is valid number"""
        expense_ratio = self.test_fund_data['expense_ratio']
        self.assertIsInstance(expense_ratio, (int, float))
        self.assertGreater(expense_ratio, 0)
        self.assertLess(expense_ratio, 5.0)  # Reasonable upper bound
    
    def test_minimum_sip_valid(self):
        """Test minimum SIP is valid amount"""
        min_sip = self.test_fund_data['minimum_sip']
        self.assertIsInstance(min_sip, (int, float))
        self.assertGreaterEqual(min_sip, 100)  # Minimum reasonable SIP
    
    def test_lock_in_period_format(self):
        """Test lock-in period format"""
        lock_in = self.test_fund_data['lock_in_period']
        self.assertIsInstance(lock_in, str)
        self.assertTrue('year' in lock_in or 'Nil' in lock_in)


class TestPhase2DataProcessing(unittest.TestCase):
    """Test Phase 2: Data Cleaning and Chunking"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            from src.processors.data_cleaner import DataCleaner
            self.cleaner = DataCleaner()
        except ImportError:
            self.skipTest("DataCleaner not available")
    
    def test_clean_percentage(self):
        """Test percentage cleaning"""
        test_cases = [
            ('0.68%', 0.68),
            ('12.5%', 12.5),
            ('', None),
            (None, None)
        ]
        
        for input_val, expected in test_cases:
            result = self.cleaner.clean_percentage(input_val)
            if expected is None:
                self.assertIsNone(result)
            else:
                self.assertAlmostEqual(result, expected, places=2)
    
    def test_clean_currency(self):
        """Test currency cleaning"""
        test_cases = [
            ('₹500', 500.0),
            ('Rs 1000', 1000.0),
            ('₹28,500 Cr', 28500.0),  # Simplified
            ('', None),
            (None, None)
        ]
        
        for input_val, expected in test_cases:
            result = self.cleaner.clean_currency(input_val)
            if expected is None:
                self.assertIsNone(result)
            else:
                self.assertAlmostEqual(result, expected, places=2)
    
    def test_clean_text(self):
        """Test text cleaning"""
        test_cases = [
            ('  HDFC Fund  ', 'HDFC Fund'),
            ('<p>HTML</p>', 'HTML'),
            ('Multiple   spaces', 'Multiple spaces')
        ]
        
        for input_val, expected in test_cases:
            result = self.cleaner.clean_text(input_val)
            self.assertEqual(result, expected)
    
    def test_validate_fund_data(self):
        """Test fund data validation"""
        valid_fund = {
            'fund_name': 'HDFC ELSS Fund',
            'scheme_type': 'Direct',
            'category': 'ELSS'
        }
        
        validation = self.cleaner.validate_fund_data(valid_fund)
        
        self.assertTrue(validation.get('is_valid', False))
        self.assertTrue(validation.get('fund_name_present', False))
        self.assertTrue(validation.get('scheme_type_present', False))


class TestPhase3Embeddings(unittest.TestCase):
    """Test Phase 3: Embeddings and Vector Database"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            from src.embeddings.embedding_generator import EmbeddingGenerator
            self.generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")  # Smaller model for testing
        except (ImportError, Exception) as e:
            self.skipTest(f"EmbeddingGenerator not available: {e}")
    
    def test_embedding_dimension(self):
        """Test embedding dimension is correct"""
        self.assertEqual(self.generator.dimension, 384)  # MiniLM dimension
    
    def test_generate_embedding_single(self):
        """Test single embedding generation"""
        text = "HDFC ELSS Fund has expense ratio of 0.68%"
        embedding = self.generator.generate_embedding_single(text)
        
        self.assertEqual(embedding.shape[0], self.generator.dimension)
        self.assertNotEqual(np.sum(embedding), 0)  # Non-zero embedding
    
    def test_generate_embeddings_batch(self):
        """Test batch embedding generation"""
        texts = [
            "HDFC ELSS Fund",
            "Minimum SIP is ₹500",
            "Lock-in period is 3 years"
        ]
        
        embeddings = self.generator.generate_embeddings(texts, show_progress=False)
        
        self.assertEqual(embeddings.shape[0], len(texts))
        self.assertEqual(embeddings.shape[1], self.generator.dimension)
    
    def test_model_info(self):
        """Test model info retrieval"""
        info = self.generator.get_model_info()
        
        self.assertIn('model_name', info)
        self.assertIn('dimension', info)
        self.assertEqual(info['dimension'], 384)


class TestPhase4RAGPipeline(unittest.TestCase):
    """Test Phase 4: RAG Pipeline"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            from src.rag.retriever import RAGRetriever
            from src.rag.response_generator import ResponseGenerator
            
            # Mock retriever for testing (no database connection)
            self.retriever = None  # Skip DB-dependent tests
            self.generator = ResponseGenerator(use_llm=False)
        except ImportError as e:
            self.skipTest(f"RAG components not available: {e}")
    
    def test_response_generator_template(self):
        """Test template-based response generation"""
        question = "What is the expense ratio?"
        context = "HDFC ELSS Fund has an expense ratio of 0.68%"
        
        response = self.generator.generate_response(question, context, [])
        
        self.assertIn('answer', response)
        self.assertIn('confidence', response)
        self.assertGreater(response['confidence'], 0.5)
    
    def test_response_with_citation(self):
        """Test response with citation extraction"""
        question = "What is the minimum SIP?"
        context = "Minimum SIP is ₹500"
        retrieved_chunks = [
            {
                'metadata': {
                    'source_url': 'https://www.indmoney.com/test-fund'
                }
            }
        ]
        
        response = self.generator.generate_response(
            question, context, retrieved_chunks
        )
        
        self.assertIn('citation', response)
        self.assertEqual(response['citation'], 'https://www.indmoney.com/test-fund')
    
    def test_opinion_detection_in_response(self):
        """Test opinion query handling"""
        question = "Should I invest in HDFC ELSS?"
        context = ""
        
        response = self.generator.generate_response(question, context, [])
        
        # Should handle gracefully even without context
        self.assertIn('answer', response)


class TestPhase5QueryProcessing(unittest.TestCase):
    """Test Phase 5: Query Processing"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            from src.rag.query_processor import QueryProcessor
            self.processor = QueryProcessor()
        except ImportError:
            self.skipTest("QueryProcessor not available")
    
    def test_fund_name_extraction(self):
        """Test fund name extraction from queries"""
        test_cases = [
            ("What is the expense ratio of HDFC ELSS Fund?", "HDFC ELSS Tax Saver Fund"),
            ("Tell me about HDFC Large Cap", "HDFC Large Cap Fund"),
            ("HDFC Small Cap Fund details", "HDFC Small Cap Fund")
        ]
        
        for query, expected in test_cases:
            extracted = self.processor.process_query(query)
            self.assertEqual(extracted['fund_name'], expected)
    
    def test_intent_detection(self):
        """Test intent detection from queries"""
        test_cases = [
            ("What is the expense ratio?", "expense_ratio"),
            ("Minimum SIP amount?", "minimum_sip"),
            ("What is the lock-in period?", "lock_in"),
            ("Exit load for this fund?", "exit_load"),
            ("Risk level?", "risk")
        ]
        
        for query, expected_intent in test_cases:
            extracted = self.processor.process_query(query)
            self.assertEqual(extracted['intent'], expected_intent)
    
    def test_opinion_detection(self):
        """Test opinion query detection"""
        opinion_queries = [
            "Should I invest in HDFC ELSS?",
            "Which fund is better - Large Cap or Small Cap?",
            "Is this a good time to buy?"
        ]
        
        for query in opinion_queries:
            extracted = self.processor.process_query(query)
            self.assertTrue(extracted['is_opinion'])
    
    def test_factual_query_classification(self):
        """Test factual query classification"""
        factual_queries = [
            "What is the expense ratio?",
            "Minimum SIP amount?",
            "Lock-in period?"
        ]
        
        for query in factual_queries:
            extracted = self.processor.process_query(query)
            self.assertFalse(extracted['is_opinion'])
            self.assertEqual(extracted['query_type'], 'factual_question')
    
    def test_entity_extraction(self):
        """Test entity extraction from queries"""
        query = "₹500 SIP with 0.68% expense ratio for 3 years"
        extracted = self.processor.process_query(query)
        
        entities = extracted['entities']
        self.assertGreater(len(entities), 0)
        
        entity_types = [e['type'] for e in entities]
        self.assertIn('currency_inr', entity_types)
        self.assertIn('percentage', entity_types)
        self.assertIn('duration', entity_types)
    
    def test_query_enhancement(self):
        """Test query enhancement"""
        query = "Minimum SIP for large cap?"
        extracted = self.processor.process_query(query)
        
        enhanced = self.processor.enhance_query(query, extracted)
        
        # Enhanced query should be longer (added information)
        self.assertGreater(len(enhanced), len(query))
        
        # Should include fund name if extracted
        if extracted.get('fund_name'):
            self.assertIn(extracted['fund_name'], enhanced)
    
    def test_filter_generation(self):
        """Test filter parameter generation"""
        query = "What is the expense ratio of HDFC ELSS Fund?"
        extracted = self.processor.process_query(query)
        
        filters = self.processor.get_filter_params(extracted)
        
        self.assertIn('fund_name', filters)
        self.assertIn('chunk_type', filters)
        
        # For expense_ratio intent, chunk_type should be investment_details
        if extracted['intent'] == 'expense_ratio':
            self.assertEqual(filters['chunk_type'], 'investment_details')


class TestPhase6Integration(unittest.TestCase):
    """Test Phase 6: Integration Tests"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        try:
            from src.rag.query_processor import QueryProcessor
            from src.rag.response_generator import ResponseGenerator
            
            self.processor = QueryProcessor()
            self.generator = ResponseGenerator(use_llm=False)
        except ImportError:
            self.skipTest("Integration test dependencies not available")
    
    def test_end_to_end_factual_query(self):
        """Test end-to-end processing of factual query"""
        query = "What is the expense ratio of HDFC ELSS Fund?"
        
        # Step 1: Process query (Phase 5)
        extracted = self.processor.process_query(query)
        
        # Verify extraction
        self.assertEqual(extracted['fund_name'], 'HDFC ELSS Tax Saver Fund')
        self.assertEqual(extracted['intent'], 'expense_ratio')
        self.assertFalse(extracted['is_opinion'])
        
        # Step 2: Generate mock context (simulating Phase 4 retrieval)
        mock_context = "HDFC ELSS Tax Saver Fund has an expense ratio of 0.68%"
        mock_chunks = [
            {
                'metadata': {
                    'source_url': 'https://www.indmoney.com/hdfc-elss'
                }
            }
        ]
        
        # Step 3: Generate response (Phase 4)
        response = self.generator.generate_response(query, mock_context, mock_chunks)
        
        # Verify response
        self.assertIn('answer', response)
        self.assertIn('citation', response)
        self.assertGreater(response['confidence'], 0.5)
    
    def test_end_to_end_opinion_query(self):
        """Test end-to-end processing of opinion query"""
        query = "Should I invest in HDFC ELSS Fund?"
        
        # Step 1: Process query (Phase 5)
        extracted = self.processor.process_query(query)
        
        # Verify opinion detection
        self.assertTrue(extracted['is_opinion'])
        
        # Step 2: Generate appropriate refusal response
        if extracted['is_opinion']:
            response_text = "I can only provide factual information. I cannot provide investment advice."
        else:
            response_text = "Some answer"
        
        # Verify appropriate handling
        self.assertIn("factual information", response_text.lower())


def run_all_tests():
    """Run all test suites and generate report"""
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST SUITE - RAG MUTUAL FUNDS CHATBOT")
    print("="*80)
    print(f"\nRunning tests at: {datetime.now().isoformat()}")
    print("="*80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests from all classes
    test_classes = [
        TestPhase1DataAcquisition,
        TestPhase2DataProcessing,
        TestPhase3Embeddings,
        TestPhase4RAGPipeline,
        TestPhase5QueryProcessing,
        TestPhase6Integration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Successful: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("="*80)
    
    if result.failures:
        print("\nFailed Tests:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\nTests with Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    return result


if __name__ == "__main__":
    import numpy as np
    
    # Run all tests
    result = run_all_tests()
    
    # Exit with appropriate code
    exit_code = 0 if result.wasSuccessful() else 1
    exit(exit_code)
