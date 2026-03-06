"""
Phase 4 & 5 Combined Runner - RAG Pipeline with Query Processing
Complete implementation of Phases 4 and 5
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from src.rag.retriever import RAGRetriever
from src.rag.response_generator import ResponseGenerator
from src.rag.query_processor import QueryProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase45Pipeline:
    """
    Combined Phase 4 & 5 Pipeline
    RAG Pipeline with Advanced Query Processing
    """
    
    def __init__(self, db_connection_string: str):
        """
        Initialize combined pipeline
        
        Args:
            db_connection_string: PostgreSQL connection string
        """
        self.db_connection_string = db_connection_string
        self.query_processor = None
        self.retriever = None
        self.generator = None
    
    def initialize(self, use_llm: bool = False):
        """Initialize all components"""
        logger.info("="*80)
        logger.info("Initializing Phase 4 & 5 Pipeline")
        logger.info("="*80)
        
        # Initialize query processor (Phase 5)
        logger.info("Initializing Query Processor (Phase 5)...")
        self.query_processor = QueryProcessor()
        logger.info("✓ Query Processor ready")
        
        # Initialize retriever (Phase 4)
        logger.info("Initializing RAG Retriever (Phase 4)...")
        self.retriever = RAGRetriever(self.db_connection_string)
        logger.info("✓ RAG Retriever ready")
        
        # Initialize response generator (Phase 4)
        logger.info(f"Initializing Response Generator (use_llm={use_llm})...")
        self.generator = ResponseGenerator(use_llm=use_llm)
        logger.info("✓ Response Generator ready")
        
        logger.info("✓ All Phase 4 & 5 components initialized successfully")
    
    def answer_question_advanced(
        self,
        question: str,
        top_k: int = 5,
        use_enhanced_retrieval: bool = True
    ) -> Dict[str, Any]:
        """
        Answer question using advanced query processing + RAG
        
        Args:
            question: User's question
            top_k: Number of chunks to retrieve
            use_enhanced_retrieval: Use query enhancement for better retrieval
            
        Returns:
            Dictionary with answer and metadata
        """
        logger.info(f"\nProcessing question: '{question}'")
        
        # Step 1: Process query (Phase 5)
        logger.info("Step 1: Processing query (Phase 5)...")
        extracted_info = self.query_processor.process_query(question)
        
        # Check for opinion/advice queries
        if extracted_info.get('is_opinion'):
            logger.info("Opinion query detected - returning standard refusal")
            return {
                'question': question,
                'answer': "I can only provide factual information about mutual funds. I cannot provide investment advice or recommendations. For personalized investment advice, please consult a SEBI-registered financial advisor.",
                'confidence': 1.0,
                'citation': "https://www.sebi.gov.in/investor-resources.html",
                'refused': True,
                'query_type': 'opinion'
            }
        
        # Step 2: Enhance query if needed (Phase 5)
        if use_enhanced_retrieval:
            enhanced_query = self.query_processor.enhance_query(question, extracted_info)
            filters = self.query_processor.get_filter_params(extracted_info)
        else:
            enhanced_query = question
            filters = {'fund_name': None, 'chunk_type': None}
        
        logger.info(f"Enhanced query: '{enhanced_query}'")
        logger.info(f"Filters: fund={filters['fund_name']}, type={filters['chunk_type']}")
        
        # Step 3: Retrieve relevant chunks (Phase 4)
        logger.info("Step 2: Retrieving relevant context (Phase 4)...")
        retrieved_chunks = self.retriever.retrieve_with_reranking(
            query=enhanced_query,
            top_k=top_k,
            use_diversity=True
        )
        
        if not retrieved_chunks:
            logger.warning("No relevant chunks found")
            return {
                'question': question,
                'answer': "I don't have enough information to answer that question from my knowledge base. Please try rephrasing your question.",
                'confidence': 0.0,
                'citation': None,
                'chunks_retrieved': 0,
                'refused': False
            }
        
        logger.info(f"Retrieved {len(retrieved_chunks)} relevant chunks")
        
        # Step 4: Format context
        logger.info("Step 3: Formatting context...")
        context = self.retriever.get_context_text(
            retrieved_chunks,
            format_type="structured"
        )
        
        # Step 5: Generate response (Phase 4)
        logger.info("Step 4: Generating response (Phase 4)...")
        response_data = self.generator.generate_response(
            question=question,  # Use original question
            context=context,
            retrieved_chunks=retrieved_chunks
        )
        
        # Add comprehensive metadata
        response_data.update({
            'chunks_retrieved': len(retrieved_chunks),
            'retrieved_chunks': [
                {
                    'chunk_id': chunk.get('chunk_id'),
                    'fund_name': chunk.get('fund_name'),
                    'chunk_type': chunk.get('chunk_type'),
                    'similarity_score': chunk.get('similarity_score')
                }
                for chunk in retrieved_chunks
            ],
            'query_analysis': {
                'fund_name': extracted_info.get('fund_name'),
                'fund_category': extracted_info.get('fund_category'),
                'intent': extracted_info.get('intent'),
                'amc': extracted_info.get('amc'),
                'entities': extracted_info.get('entities', [])
            },
            'refused': False
        })
        
        logger.info(f"Response generated (confidence: {response_data['confidence']:.2f})")
        
        return response_data
    
    def test_complete_pipeline(self):
        """Test complete Phase 4 & 5 pipeline"""
        logger.info("\n" + "="*80)
        logger.info("Testing Complete Phase 4 & 5 Pipeline")
        logger.info("="*80)
        
        # Comprehensive test questions
        test_questions = [
            # Factual questions (should be answered)
            "What is the expense ratio of HDFC ELSS Tax Saver Fund?",
            "What is the minimum SIP amount for HDFC Large Cap Fund?",
            "What is the lock-in period for ELSS funds?",
            "What is the exit load for HDFC Small Cap Fund?",
            "What is the risk level of HDFC Balanced Advantage Fund?",
            "How to download capital gains statement?",
            
            # Opinion questions (should be refused)
            "Should I invest in HDFC ELSS Fund?",
            "Which fund is better - Large Cap or Small Cap?",
            "Is this a good time to buy HDFC Mid Cap Fund?",
            
            # Comparison questions
            "Compare HDFC Large Cap vs Small Cap Fund"
        ]
        
        results = []
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{'='*80}")
            print(f"Question {i}/{len(test_questions)}: {question}")
            print(f"{'='*80}")
            
            # Get answer
            answer_data = self.answer_question_advanced(question, top_k=3)
            
            print(f"\nAnswer:")
            print(f"{answer_data['answer']}")
            
            if answer_data.get('citation'):
                print(f"\n📌 Source: {answer_data['citation']}")
            
            print(f"\nMetadata:")
            print(f"  Confidence: {answer_data['confidence']:.0%}")
            print(f"  Chunks Retrieved: {answer_data.get('chunks_retrieved', 0)}")
            print(f"  Refused: {answer_data.get('refused', False)}")
            
            if answer_data.get('query_analysis'):
                analysis = answer_data['query_analysis']
                print(f"  Query Analysis:")
                print(f"    Fund: {analysis.get('fund_name', 'N/A')}")
                print(f"    Intent: {analysis.get('intent', 'N/A')}")
                print(f"    Category: {analysis.get('fund_category', 'N/A')}")
            
            results.append(answer_data)
        
        # Print summary statistics
        print(f"\n{'='*80}")
        print("Pipeline Test Summary")
        print(f"{'='*80}")
        total = len(results)
        refused = sum(1 for r in results if r.get('refused'))
        high_confidence = sum(1 for r in results if r['confidence'] >= 0.7)
        
        print(f"Total Questions: {total}")
        print(f"Answered: {total - refused}")
        print(f"Refused (Opinion): {refused}")
        print(f"High Confidence (>70%): {high_confidence}")
        
        return results
    
    def run_interactive_session(self):
        """Run interactive Q&A session with advanced features"""
        print("\n" + "="*80)
        print("Advanced RAG Interactive Q&A Session (Phase 4 & 5)")
        print("="*80)
        print("\nAsk questions about HDFC Mutual Funds.")
        print("Type 'quit' or 'exit' to end session.")
        print("Try: 'What is the expense ratio of HDFC ELSS?'")
        print("="*80)
        
        while True:
            try:
                # Get user input
                question = input("\nYour Question: ").strip()
                
                if not question:
                    continue
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\nEnding session. Goodbye!")
                    break
                
                # Get answer with advanced processing
                answer_data = self.answer_question_advanced(question, top_k=5)
                
                # Display answer
                print(f"\n{'='*80}")
                print(f"Answer: {answer_data['answer']}")
                
                if answer_data.get('citation'):
                    print(f"\n📌 Source: {answer_data['citation']}")
                
                # Show metadata
                print(f"\nDetails:")
                print(f"  Confidence: {answer_data['confidence']:.0%}")
                
                if answer_data.get('query_analysis'):
                    analysis = answer_data['query_analysis']
                    if analysis.get('fund_name'):
                        print(f"  Fund: {analysis['fund_name']}")
                    if analysis.get('intent'):
                        print(f"  Intent: {analysis['intent']}")
                
                print(f"{'='*80}")
                
            except KeyboardInterrupt:
                print("\n\nSession interrupted. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error processing question: {str(e)}")
                print(f"\nSorry, I encountered an error. Please try again.")
    
    def close(self):
        """Close pipeline connections"""
        if self.retriever:
            self.retriever.close()
        logger.info("Phase 4 & 5 pipeline closed")


def main():
    """Main entry point for Phase 4 & 5"""
    print("\n" + "="*80)
    print("Phase 4 & 5: RAG Pipeline + Query Processing")
    print("="*80)
    print("\nThis will:")
    print("1. Initialize Query Processor (Phase 5)")
    print("   - Entity extraction")
    print("   - Intent detection")
    print("   - Query enhancement")
    print("2. Initialize RAG Retriever (Phase 4)")
    print("3. Initialize Response Generator (Phase 4)")
    print("4. Test with sample questions")
    print("5. Run interactive Q&A session")
    print("\nPrerequisites:")
    print("- Phase 3 complete (embeddings in database)")
    print("- PostgreSQL running")
    print("="*80)
    
    # Get database connection string
    print("\nEnter PostgreSQL connection string:")
    print("Format: postgresql://user:password@host:port/database")
    
    db_url = input("\nConnection string: ").strip()
    
    if not db_url:
        print("\n❌ No connection string provided")
        return
    
    print("\nUse LLM for response generation? (y/n)")
    print("Note: Requires HUGGINGFACEHUB_API_TOKEN environment variable")
    use_llm = input("Use LLM? (y/n): ").strip().lower() == 'y'
    
    print("\nPress Enter to start Phase 4 & 5 pipeline...")
    input()
    
    try:
        # Initialize pipeline
        pipeline = Phase45Pipeline(db_url)
        pipeline.initialize(use_llm=use_llm)
        
        # Run automated tests
        print("\n" + "="*80)
        print("Running automated pipeline tests...")
        print("="*80)
        pipeline.test_complete_pipeline()
        
        # Run interactive session
        print("\n" + "="*80)
        print("Starting interactive session...")
        print("="*80)
        pipeline.run_interactive_session()
        
        # Cleanup
        pipeline.close()
        
        print("\n✅ Phase 4 & 5 Complete!")
        print("RAG pipeline with advanced query processing is fully functional.")
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure PostgreSQL is running")
        print("2. Verify Phase 3 completed (embeddings in database)")
        print("3. Check connection string credentials")


if __name__ == "__main__":
    main()
