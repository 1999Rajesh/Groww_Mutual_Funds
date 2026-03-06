"""
RAG Retriever Module
Retrieves relevant chunks from vector database for RAG pipeline
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime

from src.embeddings.embedding_generator import EmbeddingGenerator
from src.vector_db.vector_store import VectorStore

logger = logging.getLogger(__name__)


class RAGRetriever:
    """
    Retrieves relevant context for RAG-based question answering
    """
    
    def __init__(self, db_connection_string: str, embedding_model: str = "all-mpnet-base-v2"):
        """
        Initialize RAG retriever
        
        Args:
            db_connection_string: PostgreSQL connection string
            embedding_model: Sentence transformer model name
        """
        self.db_connection_string = db_connection_string
        
        # Initialize embedding generator
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_generator = EmbeddingGenerator(model_name=embedding_model)
        
        # Initialize vector store
        logger.info("Connecting to vector database...")
        self.vector_store = VectorStore(db_connection_string)
        
        if not self.vector_store.connect():
            raise ConnectionError("Failed to connect to vector database")
        
        logger.info("✓ RAG Retriever initialized successfully")
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_fund_name: Optional[str] = None,
        filter_chunk_type: Optional[str] = None,
        min_similarity_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query
        
        Args:
            query: User query text
            top_k: Number of chunks to retrieve
            filter_fund_name: Optional filter by fund name
            filter_chunk_type: Optional filter by chunk type
            min_similarity_threshold: Minimum similarity score to include
            
        Returns:
            List of relevant chunks with metadata
        """
        logger.info(f"Retrieving chunks for query: '{query}'")
        
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embedding_single(query)
        
        # Search in vector database
        results = self.vector_store.similarity_search(
            query_embedding,
            top_k=top_k * 2,  # Get more initially to filter by threshold
            filter_fund_name=filter_fund_name,
            filter_chunk_type=filter_chunk_type
        )
        
        # Filter by similarity threshold
        filtered_results = [
            result for result in results
            if result.get('similarity_score', 0) >= min_similarity_threshold
        ]
        
        # Return top_k results
        final_results = filtered_results[:top_k]
        
        logger.info(f"Retrieved {len(final_results)} relevant chunks (from {len(results)} initial results)")
        
        return final_results
    
    def retrieve_with_reranking(
        self,
        query: str,
        top_k: int = 5,
        use_diversity: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve and re-rank chunks for better coverage
        
        Args:
            query: User query text
            top_k: Number of chunks to return
            use_diversity: Apply diversity re-ranking
            
        Returns:
            List of re-ranked chunks
        """
        # Initial retrieval
        results = self.retrieve(query, top_k=top_k * 2)
        
        if not results:
            return []
        
        if use_diversity:
            # Apply diversity re-ranking (MMR-like approach)
            reranked = self._maximal_margin_relevance(query, results, top_k)
        else:
            # Just return top_k by similarity
            reranked = sorted(results, key=lambda x: x['similarity_score'], reverse=True)[:top_k]
        
        logger.info(f"Re-ranked chunks using {'diversity' if use_diversity else 'similarity'} strategy")
        
        return reranked
    
    def _maximal_margin_relevance(
        self,
        query: str,
        candidates: List[Dict],
        k: int,
        lambda_param: float = 0.7
    ) -> List[Dict]:
        """
        Maximal Marginal Relevance (MMR) for diverse retrieval
        
        Args:
            query: Query text
            candidates: Candidate chunks
            k: Number to select
            lambda_param: Balance between relevance and diversity (0-1)
            
        Returns:
            Selected diverse chunks
        """
        if len(candidates) <= k:
            return candidates
        
        selected = []
        remaining = candidates.copy()
        
        # Select first item (highest similarity)
        remaining.sort(key=lambda x: x['similarity_score'], reverse=True)
        selected.append(remaining.pop(0))
        
        while len(selected) < k and remaining:
            best_score = -float('inf')
            best_idx = 0
            
            for i, candidate in enumerate(remaining):
                # Relevance to query
                relevance = candidate['similarity_score']
                
                # Diversity (dissimilarity to already selected)
                max_sim_to_selected = max([
                    self._cosine_similarity_chunks(selected_item, candidate)
                    for selected_item in selected
                ])
                
                # MMR score
                mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim_to_selected
                
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = i
            
            selected.append(remaining.pop(best_idx))
        
        return selected
    
    def _cosine_similarity_chunks(self, chunk1: Dict, chunk2: Dict) -> float:
        """Estimate similarity between two chunks based on text overlap"""
        # Simplified: Use existing similarity scores as proxy
        # In production, would compute actual cosine similarity
        return 0.5  # Placeholder
    
    def get_context_text(
        self,
        retrieved_chunks: List[Dict[str, Any]],
        format_type: str = "concatenated"
    ) -> str:
        """
        Format retrieved chunks into context text
        
        Args:
            retrieved_chunks: List of retrieved chunks
            format_type: Formatting style ('concatenated', 'numbered', 'structured')
            
        Returns:
            Formatted context text
        """
        if not retrieved_chunks:
            return "No relevant information found."
        
        if format_type == "concatenated":
            # Simple concatenation
            context = "\n\n".join([
                chunk['chunk_text']
                for chunk in retrieved_chunks
            ])
        
        elif format_type == "numbered":
            # Numbered list
            context = "\n".join([
                f"{i+1}. {chunk['chunk_text']}"
                for i, chunk in enumerate(retrieved_chunks)
            ])
        
        elif format_type == "structured":
            # Structured with metadata
            parts = []
            for i, chunk in enumerate(retrieved_chunks, 1):
                part = f"[Source {i}]\n"
                part += f"Fund: {chunk.get('fund_name', 'Unknown')}\n"
                part += f"Type: {chunk.get('chunk_type', 'general')}\n"
                part += f"Content: {chunk['chunk_text']}\n"
                if chunk.get('metadata', {}).get('source_url'):
                    part += f"Source URL: {chunk['metadata']['source_url']}\n"
                parts.append(part)
            context = "\n\n".join(parts)
        
        else:
            context = self.get_context_text(retrieved_chunks, format_type="concatenated")
        
        logger.info(f"Formatted context: {len(context)} characters ({len(retrieved_chunks)} chunks)")
        
        return context
    
    def close(self):
        """Close database connections"""
        if self.vector_store:
            self.vector_store.disconnect()
        logger.info("RAG Retriever connections closed")


def main():
    """Test RAG retriever"""
    print("="*80)
    print("Testing RAG Retriever")
    print("="*80)
    
    # Example connection string
    connection_string = "postgresql://postgres:password@localhost:5432/rag_mutual_funds"
    
    try:
        # Initialize retriever
        retriever = RAGRetriever(connection_string)
        
        # Test queries
        test_queries = [
            "What is the expense ratio of HDFC ELSS Fund?",
            "Minimum SIP amount for large cap fund?",
            "ELSS lock-in period?",
            "Exit load for small cap fund?"
        ]
        
        for query in test_queries:
            print(f"\n{'='*80}")
            print(f"Query: {query}")
            print(f"{'='*80}")
            
            # Retrieve chunks
            results = retriever.retrieve(query, top_k=3)
            
            print(f"\nRetrieved {len(results)} chunks:\n")
            
            for i, result in enumerate(results, 1):
                print(f"{i}. Score: {result['similarity_score']:.4f}")
                print(f"   Fund: {result['fund_name']}")
                print(f"   Type: {result['chunk_type']}")
                print(f"   Text: {result['chunk_text'][:150]}...\n")
            
            # Get formatted context
            context = retriever.get_context_text(results, format_type="structured")
            print(f"\nFormatted Context:\n{context[:500]}...\n")
        
        # Close connections
        retriever.close()
        
        print("\n✅ RAG Retriever Test Complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure PostgreSQL is running")
        print("2. Verify Phase 3 completed (embeddings in database)")
        print("3. Check connection string credentials")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
