"""
ChromaDB Vector Store Implementation
Alternative to pgvector for embedding storage and search
"""
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("ChromaDB not installed. Run: pip install chromadb")

logger = logging.getLogger(__name__)


class ChromaVectorStore:
    """
    Vector store using ChromaDB for similarity search
    """
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "mutual_funds"
    ):
        """
        Initialize ChromaDB vector store
        
        Args:
            persist_directory: Directory to persist database
            collection_name: Name of the collection
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "ChromaDB is required. Install with: pip install chromadb"
            )
        
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize persistent client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Cosine similarity
        )
        
        logger.info(f"ChromaDB initialized at {persist_directory}")
        logger.info(f"Collection: {collection_name}")
    
    def add_embeddings(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: np.ndarray
    ) -> int:
        """
        Add embeddings to ChromaDB
        
        Args:
            chunks: List of chunk dictionaries
            embeddings: Numpy array of embeddings
            
        Returns:
            Number of embeddings added
        """
        if not chunks or len(embeddings) == 0:
            logger.warning("No chunks or embeddings provided")
            return 0
        
        try:
            ids = []
            documents = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = chunk.get('chunk_id', f"chunk_{i}")
                chunk_text = chunk.get('chunk_text', '')
                metadata = {
                    'fund_name': chunk.get('fund_name', 'Unknown'),
                    'chunk_type': chunk.get('chunk_type', 'general'),
                    'source_url': chunk.get('metadata', {}).get('source_url', ''),
                    'scraped_at': chunk.get('metadata', {}).get('scraped_at', '')
                }
                
                ids.append(chunk_id)
                documents.append(chunk_text)
                metadatas.append(metadata)
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings.tolist(),
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(ids)} embeddings to ChromaDB")
            return len(ids)
            
        except Exception as e:
            logger.error(f"Failed to add embeddings: {str(e)}")
            return 0
    
    def similarity_search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        filter_fund_name: Optional[str] = None,
        filter_chunk_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter_fund_name: Optional filter by fund name
            filter_chunk_type: Optional filter by chunk type
            
        Returns:
            List of matching chunks with similarity scores
        """
        try:
            # Build where clause using $and for multiple conditions
            where_filter = None
            
            if filter_fund_name and filter_chunk_type:
                # Multiple conditions require $and operator
                where_filter = {
                    "$and": [
                        {"fund_name": filter_fund_name},
                        {"chunk_type": filter_chunk_type}
                    ]
                }
            elif filter_fund_name:
                where_filter = {"fund_name": filter_fund_name}
            elif filter_chunk_type:
                where_filter = {"chunk_type": filter_chunk_type}
            
            # Query collection
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                where=where_filter,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            
            if results and results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    result = {
                        'chunk_id': results['ids'][0][i],
                        'chunk_text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'similarity_score': 1 - results['distances'][0][i]  # Convert distance to similarity
                    }
                    
                    # Extract fund_name from metadata for compatibility
                    result['fund_name'] = result['metadata'].get('fund_name', 'Unknown')
                    result['chunk_type'] = result['metadata'].get('chunk_type', 'general')
                    
                    formatted_results.append(result)
            
            logger.info(f"Found {len(formatted_results)} similar chunks")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {str(e)}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            count = self.collection.count()
            
            return {
                'collection_name': self.collection_name,
                'total_chunks': count,
                'persist_directory': self.persist_directory
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {str(e)}")
            return {}
    
    def delete_collection(self):
        """Delete the collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
    
    def clear_all(self):
        """Clear all data from collection"""
        try:
            # Delete and recreate
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Cleared all data from collection")
        except Exception as e:
            logger.error(f"Failed to clear collection: {str(e)}")


def main():
    """Test ChromaDB vector store"""
    print("="*80)
    print("Testing ChromaDB Vector Store")
    print("="*80)
    
    if not CHROMADB_AVAILABLE:
        print("\n❌ ChromaDB not installed")
        print("\nInstall with:")
        print("  pip install chromadb")
        return
    
    try:
        # Initialize vector store
        print("\nInitializing ChromaDB...")
        store = ChromaVectorStore(persist_directory="./test_chroma_db")
        
        # Test data
        test_chunks = [
            {
                'chunk_id': 'test_chunk_1',
                'chunk_text': 'HDFC ELSS Fund has expense ratio of 0.68%',
                'fund_name': 'HDFC ELSS Fund',
                'chunk_type': 'investment_details',
                'metadata': {'source_url': 'https://example.com/1'}
            },
            {
                'chunk_id': 'test_chunk_2',
                'chunk_text': 'Minimum SIP is ₹500',
                'fund_name': 'HDFC ELSS Fund',
                'chunk_type': 'investment_details',
                'metadata': {'source_url': 'https://example.com/2'}
            }
        ]
        
        # Mock embeddings (random for testing)
        test_embeddings = np.random.rand(2, 384).astype(np.float32)
        
        # Add embeddings
        print("\nAdding test embeddings...")
        count = store.add_embeddings(test_chunks, test_embeddings)
        print(f"Added {count} embeddings")
        
        # Get stats
        stats = store.get_collection_stats()
        print(f"\nCollection Stats: {stats}")
        
        # Test similarity search
        print("\nTesting similarity search...")
        query_embedding = np.random.rand(384).astype(np.float32)
        
        results = store.similarity_search(
            query_embedding=query_embedding,
            top_k=2
        )
        
        print(f"\nSearch Results: {len(results)} matches")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Score: {result['similarity_score']:.4f}")
            print(f"   Text: {result['chunk_text']}")
            print(f"   Fund: {result['fund_name']}")
        
        # Cleanup
        print("\nCleaning up...")
        store.clear_all()
        
        print("\n✅ ChromaDB Test Complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
