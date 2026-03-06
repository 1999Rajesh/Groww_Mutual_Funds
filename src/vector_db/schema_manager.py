"""
Vector Database Schema Manager
Creates and manages PostgreSQL + pgvector tables
"""
import logging
from typing import Optional, List, Dict
from datetime import datetime

try:
    import psycopg2
    from psycopg2.extras import execute_values
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("psycopg2 not installed. Run: pip install psycopg2-binary")

logger = logging.getLogger(__name__)


class VectorDBSchema:
    """
    Manages PostgreSQL + pgvector database schema
    """
    
    def __init__(self, connection_string: str):
        """
        Initialize database connection
        
        Args:
            connection_string: PostgreSQL connection string
                Format: "postgresql://user:password@host:port/database"
        """
        if not PSYCOPG2_AVAILABLE:
            raise ImportError(
                "psycopg2 library is required. "
                "Install with: pip install psycopg2-binary"
            )
        
        self.connection_string = connection_string
        self.conn = None
        self.cursor = None
        
        logger.info("Initializing Vector Database Schema Manager")
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            self.cursor = self.conn.cursor()
            logger.info("Connected to PostgreSQL database successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Database connection closed")
    
    def enable_pgvector(self):
        """Enable pgvector extension in PostgreSQL"""
        try:
            self.cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            self.conn.commit()
            logger.info("pgvector extension enabled successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to enable pgvector extension: {str(e)}")
            self.conn.rollback()
            return False
    
    def create_schema(self):
        """Create database schema for RAG chatbot"""
        try:
            # Enable pgvector first
            if not self.enable_pgvector():
                return False
            
            # Create chunks table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS fund_chunks (
                id SERIAL PRIMARY KEY,
                chunk_id VARCHAR(100) UNIQUE NOT NULL,
                fund_name VARCHAR(500) NOT NULL,
                chunk_type VARCHAR(50) NOT NULL,
                chunk_text TEXT NOT NULL,
                embedding vector(768),  -- Dimension will be updated dynamically
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Create index on chunk_id for fast lookups
            CREATE INDEX IF NOT EXISTS idx_chunk_id ON fund_chunks(chunk_id);
            
            -- Create index on fund_name for filtering
            CREATE INDEX IF NOT EXISTS idx_fund_name ON fund_chunks(fund_name);
            
            -- Create index on chunk_type for filtering
            CREATE INDEX IF NOT EXISTS idx_chunk_type ON fund_chunks(chunk_type);
            
            -- Create GIN index on metadata JSONB
            CREATE INDEX IF NOT EXISTS idx_metadata ON fund_chunks USING GIN(metadata);
            
            -- Create HNSW index for approximate nearest neighbor search (will be added after embeddings)
            -- Note: HNSW index creation requires data to be loaded first
            """
            
            self.cursor.execute(create_table_query)
            self.conn.commit()
            
            logger.info("Database schema created successfully")
            logger.info("Tables created: fund_chunks")
            logger.info("Indexes created: idx_chunk_id, idx_fund_name, idx_chunk_type, idx_metadata")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create schema: {str(e)}")
            self.conn.rollback()
            return False
    
    def create_hnsw_index(self, embedding_dimension: int = 768):
        """
        Create HNSW index for fast approximate nearest neighbor search
        
        Args:
            embedding_dimension: Dimension of embeddings
        """
        try:
            # First, update the vector dimension if needed
            alter_query = f"""
            ALTER TABLE fund_chunks 
            ALTER COLUMN embedding TYPE vector({embedding_dimension})
            USING embedding::vector({embedding_dimension});
            """
            self.cursor.execute(alter_query)
            self.conn.commit()
            
            # Create HNSW index
            hnsw_query = f"""
            CREATE INDEX IF NOT EXISTS idx_embedding_hnsw 
            ON fund_chunks 
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
            """
            
            self.cursor.execute(hnsw_query)
            self.conn.commit()
            
            logger.info(f"HNSW index created successfully for dimension {embedding_dimension}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create HNSW index: {str(e)}")
            self.conn.rollback()
            return False
    
    def get_table_stats(self) -> Dict:
        """
        Get table statistics
        
        Returns:
            Dictionary with table stats
        """
        try:
            stats_query = """
            SELECT 
                COUNT(*) as total_chunks,
                COUNT(DISTINCT fund_name) as unique_funds,
                COUNT(DISTINCT chunk_type) as chunk_types
            FROM fund_chunks;
            """
            
            self.cursor.execute(stats_query)
            result = self.cursor.fetchone()
            
            return {
                'total_chunks': result[0],
                'unique_funds': result[1],
                'chunk_types': result[2]
            }
            
        except Exception as e:
            logger.error(f"Failed to get table stats: {str(e)}")
            return {}
    
    def drop_schema(self):
        """Drop all tables (for testing/reset)"""
        try:
            self.cursor.execute("DROP TABLE IF EXISTS fund_chunks CASCADE")
            self.conn.commit()
            logger.info("Schema dropped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to drop schema: {str(e)}")
            self.conn.rollback()
            return False
    
    def check_connection(self) -> bool:
        """Check if database connection is active"""
        try:
            self.cursor.execute("SELECT 1")
            return True
        except:
            return False


def main():
    """Test vector database schema"""
    print("="*80)
    print("Testing Vector Database Schema Manager")
    print("="*80)
    
    # Example connection string (replace with your actual credentials)
    # For local PostgreSQL: postgresql://postgres:password@localhost:5432/rag_mutual_funds
    connection_string = "postgresql://postgres:password@localhost:5432/rag_mutual_funds"
    
    try:
        # Initialize schema manager
        db_schema = VectorDBSchema(connection_string)
        
        # Connect
        if not db_schema.connect():
            print("\n❌ Failed to connect to database")
            print("\nMake sure:")
            print("1. PostgreSQL is running")
            print("2. Database 'rag_mutual_funds' exists")
            print("3. Connection string is correct")
            return
        
        # Create schema
        if db_schema.create_schema():
            print("\n✅ Database schema created successfully!")
            
            # Get stats
            stats = db_schema.get_table_stats()
            print(f"\nTable Statistics:")
            print(f"  Total chunks: {stats.get('total_chunks', 0)}")
            print(f"  Unique funds: {stats.get('unique_funds', 0)}")
            print(f"  Chunk types: {stats.get('chunk_types', 0)}")
        else:
            print("\n❌ Failed to create schema")
        
        # Disconnect
        db_schema.disconnect()
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("\nTo use this module, install:")
        print("  pip install psycopg2-binary")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
