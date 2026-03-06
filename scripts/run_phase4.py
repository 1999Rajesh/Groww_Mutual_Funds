"""
Phase 4 Runner - RAG Pipeline Implementation
Combines retrieval and generation for complete RAG system
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from src.rag.retriever import RAGRetriever
from src.rag.response_generator import ResponseGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase4Pipeline:
    """
    Phase 4 RAG Pipeline - Retrieval Augmented Generation
    """
    
    def __init__(self, db_connection_string: str):
        """
        Initialize Phase 4 pipeline
        
        Args:
            db_connection_string: PostgreSQL connection string
        """
        self.db_connection_string = db_connection_string
        self.retriever = None
        self.generator = None
    
    def initialize(self, use_llm: bool = False):
        """Initialize RAG components"""
        logger.info("="*80)
        logger.info("Initializing Phase 4 RAG Pipeline")
        logger.info("="*80)
        
        # Initialize retriever
        logger.info("Initializing RAG Retriever...")
        self.retriever = RAGRetriever(self.db_connection_string)
        logger.info("✓ RAG Retriever ready")
        
        # Initialize response generator
        logger.info(f"Initializing Response Generator (use_llm={use_llm})...")
        self.generator = ResponseGenerator(use_llm=use_llm)
        logger.info("✓ Response Generator ready")
        
        logger.info("✓ Phase 4 components initialized successfully")
    
    def answer_question(
        self,
        question: str,
        top_k: int = 5,
        use_reranking: bool = True,
        include_citation: bool = True
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG pipeline
        
        Args:
            question: User's question
            top_k: Number of chunks to retrieve
            use_reranking: Apply diversity re-ranking
            include_citation: Include citation in response
            
        Returns:
            Dictionary with answer and metadata
        """
        logger.info(f"\nProcessing question: '{question}'")
        
        # Step 1: Retrieve relevant chunks
        logger.info("Step 1: Retrieving relevant context...")
        retrieved_chunks = self.retriever.retrieve_with_reranking(
            query=question,
            top_k=top_k,
            use_diversity=use_reranking
        )
        
        if not retrieved_chunks:
            logger.warning("No relevant chunks found")
            return {
                'question': question,
                'answer': "I don't have enough information to answer that question from my knowledge base.",
                'confidence': 0.0,
                'citation': None,
                'chunks_retrieved': 0
            }
        
        logger.info(f"Retrieved {len(retrieved_chunks)} relevant chunks")
        
        # Step 2: Format context
        logger.info("Step 2: Formatting context...")
        context = self.retriever.get_context_text(
            retrieved_chunks,
            format_type="structured"
        )
        
        # Step 3: Generate response
        logger.info("Step 3: Generating response...")
        response_data = self.generator.generate_response(
            question=question,
            context=context,
            retrieved_chunks=retrieved_chunks
        )
        
        # Add retrieval metadata
        response_data['chunks_retrieved'] = len(retrieved_chunks)
        response_data['retrieved_chunks'] = [
            {
                'chunk_id': chunk.get('chunk_id'),
                'fund_name': chunk.get('fund_name'),
                'chunk_type': chunk.get('chunk_type'),
                'similarity_score': chunk.get('similarity_score')
            }
            for chunk in retrieved_chunks
        ]
        
        logger.info(f"Response generated (confidence: {response_data['confidence']:.2f})")
        
        return response_data
    
    def test_pipeline(self):
        """Test RAG pipeline with sample questions"""
        logger.info("\n" + "="*80)
        logger.info("Testing RAG Pipeline")
        logger.info("="*80)
        
        # Test questions covering different topics
        test_questions = [
            "What is the expense ratio of HDFC ELSS Tax Saver Fund?",
            "What is the minimum SIP amount for HDFC Large Cap Fund?",
            "What is the lock-in period for ELSS funds?",
            "What is the exit load for HDFC Small Cap Fund?",
            "What is the risk level of HDFC Balanced Advantage Fund?"
        ]
        
        results = []
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{'='*80}")
            print(f"Question {i}/{len(test_questions)}: {question}")
            print(f"{'='*80}")
            
            # Get answer
            answer_data = self.answer_question(question, top_k=3)
            
            print(f"\nAnswer:")
            print(f"{answer_data['answer']}")
            
            if answer_data.get('citation'):
                print(f"\nCitation: {answer_data['citation']}")
            
            print(f"\nMetadata:")
            print(f"  Confidence: {answer_data['confidence']:.2f}")
            print(f"  Chunks Retrieved: {answer_data['chunks_retrieved']}")
            
            if answer_data.get('retrieved_chunks'):
                print(f"  Top Chunk:")
                chunk = answer_data['retrieved_chunks'][0]
                print(f"    Fund: {chunk['fund_name']}")
                print(f"    Type: {chunk['chunk_type']}")
                print(f"    Score: {chunk['similarity_score']:.4f}")
            
            results.append(answer_data)
        
        return results
    
    def run_interactive_session(self):
        """Run interactive Q&A session"""
        print("\n" + "="*80)
        print("RAG Interactive Q&A Session")
        print("="*80)
        print("\nAsk questions about HDFC Mutual Funds.")
        print("Type 'quit' or 'exit' to end session.")
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
                
                # Get answer
                answer_data = self.answer_question(question, top_k=5)
                
                # Display answer
                print(f"\nAnswer: {answer_data['answer']}")
                
                if answer_data.get('citation'):
                    print(f"\n📌 Source: {answer_data['citation']}")
                
                print(f"Confidence: {answer_data['confidence']:.0%}")
                
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
        logger.info("Phase 4 pipeline closed")


def main():
    """Main entry point for Phase 4"""
    print("\n" + "="*80)
    print("Phase 4: RAG Pipeline Implementation")
    print("="*80)
    print("\nThis will:")
    print("1. Initialize RAG Retriever (Phase 3 embeddings)")
    print("2. Initialize Response Generator")
    print("3. Test with sample questions")
    print("4. Run interactive Q&A session")
    print("\nPrerequisites:")
    print("- Phase 3 complete (embeddings in database)")
    print("- PostgreSQL running")
    print("="*80)
    
    # Get database connection string
    print("\nEnter PostgreSQL connection string:")
    print("Format: postgresql://user:password@host:port/database")
    print("Example: postgresql://postgres:password@localhost:5432/rag_mutual_funds")
    
    db_url = input("\nConnection string: ").strip()
    
    if not db_url:
        print("\n❌ No connection string provided")
        return
    
    print("\nUse LLM for response generation? (y/n)")
    print("Note: Requires HUGGINGFACEHUB_API_TOKEN environment variable")
    use_llm = input("Use LLM? (y/n): ").strip().lower() == 'y'
    
    print("\nPress Enter to start Phase 4 pipeline...")
    input()
    
    try:
        # Initialize pipeline
        pipeline = Phase4Pipeline(db_url)
        pipeline.initialize(use_llm=use_llm)
        
        # Run tests
        print("\n" + "="*80)
        print("Running automated tests...")
        print("="*80)
        pipeline.test_pipeline()
        
        # Run interactive session
        print("\n" + "="*80)
        print("Starting interactive session...")
        print("="*80)
        pipeline.run_interactive_session()
        
        # Cleanup
        pipeline.close()
        
        print("\n✅ Phase 4 Complete!")
        print("RAG pipeline is fully functional.")
        
    except Exception as e:
        print(f"\n❌ Phase 4 failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure PostgreSQL is running")
        print("2. Verify Phase 3 completed (embeddings in database)")
        print("3. Check connection string credentials")


if __name__ == "__main__":
    main()
