"""
Vector Store Manager
Handles storing embeddings and similarity search
"""
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime

try:
    import psycopg2
    from psycopg2.extras import execute_values
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Manages vector storage and similarity search in PostgreSQL + pgvector
    """
    
    def __init__(self, connection_string: str):
        """
        Initialize vector store
        
        Args:
            connection_string: PostgreSQL connection string
        """
        if not PSYCOPG2_AVAILABLE:
            raise ImportError("psycopg2 is required. Install with: pip install psycopg2-binary")
        
        self.connection_string = connection_string
        self.conn = None
        self.cursor = None
        
        logger.info("Initializing Vector Store")
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            self.cursor = self.conn.cursor()
            logger.info("Connected to vector store successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to vector store: {str(e)}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Vector store connection closed")
    
    def store_embeddings(self, chunks: List[Dict[str, Any]], embedding_dim: int = 768):
        """
        Store chunks with embeddings in database
        
        Args:
            chunks: List of chunk dictionaries with embeddings
                Format: {
                    'chunk_id': str,
                    'fund_name': str,
                    'chunk_type': str,
                    'chunk_text': str,
                    'embedding': np.ndarray,
                    'metadata': dict
                }
            embedding_dim: Dimension of embeddings
        """
        if not chunks:
            logger.warning("No chunks provided for storage")
            return 0
        
        try:
            # Prepare data for bulk insert
            values = []
            for chunk in chunks:
                embedding_bytes = chunk['embedding'].tobytes() if isinstance(chunk['embedding'], np.ndarray) else None
                
                values.append((
                    chunk['chunk_id'],
                    chunk['fund_name'],
                    chunk['chunk_type'],
                    chunk['chunk_text'],
                    embedding_bytes,
                    json.dumps(chunk.get('metadata', {}))
                ))
            
            # Bulk insert query
            insert_query = """
            INSERT INTO fund_chunks (chunk_id, fund_name, chunk_type, chunk_text, embedding, metadata)
            VALUES %s
            ON CONFLICT (chunk_id) DO UPDATE SET
                fund_name = EXCLUDED.fund_name,
                chunk_type = EXCLUDED.chunk_type,
                chunk_text = EXCLUDED.chunk_text,
                embedding = EXCLUDED.embedding,
                metadata = EXCLUDED.metadata,
                updated_at = CURRENT_TIMESTAMP;
            """
            
            execute_values(self.cursor, insert_query, values)
            self.conn.commit()
            
            logger.info(f"Stored {len(chunks)} embeddings successfully")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Failed to store embeddings: {str(e)}")
            self.conn.rollback()
            return 0
    
    def similarity_search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        filter_fund_name: Optional[str] = None,
        filter_chunk_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using cosine similarity
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter_fund_name: Optional filter by fund name
            filter_chunk_type: Optional filter by chunk type
            
        Returns:
            List of matching chunks with similarity scores
        """
        try:
            # Convert numpy array to bytes
            embedding_bytes = query_embedding.tobytes()
            
            # Build query
            where_clauses = []
            params = [embedding_bytes]
            
            if filter_fund_name:
                where_clauses.append("fund_name ILIKE %s")
                params.append(f"%{filter_fund_name}%")
            
            if filter_chunk_type:
                where_clauses.append("chunk_type = %s")
                params.append(filter_chunk_type)
            
            where_clause = " AND ".join(where_clauses)
            if where_clause:
                where_clause = "WHERE " + where_clause
            
            query = f"""
            SELECT 
                chunk_id,
                fund_name,
                chunk_type,
                chunk_text,
                metadata,
                1 - (embedding <=> %s::vector) AS similarity_score
            FROM fund_chunks
            {where_clause}
            ORDER BY similarity_score DESC
            LIMIT %s;
            """
            
            params.append(top_k)
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            
            # Format results
            formatted_results = []
            for row in results:
                formatted_results.append({
                    'chunk_id': row[0],
                    'fund_name': row[1],
                    'chunk_type': row[2],
                    'chunk_text': row[3],
                    'metadata': row[4],
                    'similarity_score': float(row[5])
                })
            
            logger.info(f"Found {len(formatted_results)} similar chunks")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {str(e)}")
            return []
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific chunk by ID
        
        Args:
            chunk_id: Chunk identifier
            
        Returns:
            Chunk dictionary or None
        """
        try:
            query = """
            SELECT chunk_id, fund_name, chunk_type, chunk_text, metadata
            FROM fund_chunks
            WHERE chunk_id = %s;
            """
            
            self.cursor.execute(query, (chunk_id,))
            result = self.cursor.fetchone()
            
            if result:
                return {
                    'chunk_id': result[0],
                    'fund_name': result[1],
                    'chunk_type': result[2],
                    'chunk_text': result[3],
                    'metadata': result[4]
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve chunk: {str(e)}")
            return None
    
    def get_all_funds(self) -> List[str]:
        """
        Get list of all unique fund names
        
        Returns:
            List of fund names
        """
        try:
            query = "SELECT DISTINCT fund_name FROM fund_chunks ORDER BY fund_name;"
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            return [row[0] for row in results]
        except Exception as e:
            logger.error(f"Failed to get funds: {str(e)}")
            return []
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """
        Delete a chunk by ID
        
        Args:
            chunk_id: Chunk identifier
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            query = "DELETE FROM fund_chunks WHERE chunk_id = %s;"
            self.cursor.execute(query, (chunk_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to delete chunk: {str(e)}")
            self.conn.rollback()
            return False
    
    def clear_all(self):
        """Clear all chunks from database"""
        try:
            self.cursor.execute("TRUNCATE TABLE fund_chunks;")
            self.conn.commit()
            logger.info("All chunks cleared from database")
        except Exception as e:
            logger.error(f"Failed to clear chunks: {str(e)}")
            self.conn.rollback()


def main():
    """Test vector store"""
    print("="*80)
    print("Testing Vector Store Manager")
    print("="*80)
    
    # Example connection string
    connection_string = "postgresql://postgres:password@localhost:5432/rag_mutual_funds"
    
    try:
        # Initialize vector store
        store = VectorStore(connection_string)
        
        # Connect
        if not store.connect():
            print("\n❌ Failed to connect to database")
            return
        
        print("\n✅ Connected to vector store successfully!")
        
        # Test getting all funds
        funds = store.get_all_funds()
        print(f"\nFunds in database: {len(funds)}")
        for fund in funds[:5]:  # Show first 5
            print(f"  - {fund}")
        
        # Disconnect
        store.disconnect()
        print("\n✅ Vector Store Test Complete!")
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("\nTo use this module, install:")
        print("  pip install psycopg2-binary")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
