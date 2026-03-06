"""
Phase 3 Runner - Embeddings & Vector Database Setup
Generates embeddings and stores them in PostgreSQL + pgvector
"""
import json
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from src.config import DATA_PROCESSED_DIR
from src.embeddings.embedding_generator import EmbeddingGenerator
from src.vector_db.schema_manager import VectorDBSchema
from src.vector_db.vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase3Pipeline:
    """
    Phase 3 Pipeline - Embeddings & Vector Database
    """
    
    def __init__(self, db_connection_string: str):
        """
        Initialize Phase 3 pipeline
        
        Args:
            db_connection_string: PostgreSQL connection string
        """
        self.db_connection_string = db_connection_string
        self.embedding_gen = None
        self.vector_store = None
        self.schema_manager = None
    
    def initialize(self, embedding_model: str = "all-mpnet-base-v2"):
        """Initialize components"""
        logger.info("="*80)
        logger.info("Initializing Phase 3 Pipeline")
        logger.info("="*80)
        
        # Initialize embedding generator
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_gen = EmbeddingGenerator(model_name=embedding_model)
        logger.info(f"✓ Model loaded. Dimension: {self.embedding_gen.dimension}")
        
        # Initialize vector store
        logger.info("Connecting to vector database...")
        self.vector_store = VectorStore(self.db_connection_string)
        
        if not self.vector_store.connect():
            raise ConnectionError("Failed to connect to vector database")
        logger.info("✓ Connected to PostgreSQL database")
        
        # Initialize schema manager
        self.schema_manager = VectorDBSchema(self.db_connection_string)
        self.schema_manager.conn = self.vector_store.conn
        self.schema_manager.cursor = self.vector_store.cursor
        
        logger.info("✓ Phase 3 components initialized successfully")
    
    def setup_database(self):
        """Set up database schema"""
        logger.info("\nSetting up database schema...")
        
        if self.schema_manager.create_schema():
            logger.info("✓ Database schema created successfully")
            
            # Create HNSW index for fast search
            if self.embedding_gen.dimension:
                self.schema_manager.create_hnsw_index(self.embedding_gen.dimension)
                logger.info("✓ HNSW index created for fast similarity search")
        else:
            raise RuntimeError("Failed to create database schema")
    
    def process_and_store_embeddings(self) -> Dict:
        """
        Process chunks and generate embeddings
        
        Returns:
            Processing statistics
        """
        logger.info("\n" + "="*80)
        logger.info("Processing Chunks & Generating Embeddings")
        logger.info("="*80)
        
        # Load processed chunks from Phase 2
        processed_dir = Path(DATA_PROCESSED_DIR)
        json_files = list(processed_dir.glob("processed_chunks_*.json"))
        
        if not json_files:
            raise FileNotFoundError(
                "No processed chunks found. Please run Phase 2 first."
            )
        
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        logger.info(f"Loading processed chunks from {latest_file.name}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        chunks = data.get('chunks', [])
        logger.info(f"Found {len(chunks)} chunks to process")
        
        # Extract texts for embedding
        texts = [chunk['chunk_text'] for chunk in chunks]
        
        # Generate embeddings in batches
        logger.info(f"\nGenerating embeddings (batch processing)...")
        embeddings = self.embedding_gen.generate_embeddings(
            texts, 
            batch_size=32,
            show_progress=True
        )
        
        logger.info(f"✓ Generated embeddings shape: {embeddings.shape}")
        
        # Add embeddings to chunks
        chunks_with_embeddings = []
        for i, chunk in enumerate(chunks):
            chunk_copy = chunk.copy()
            chunk_copy['embedding'] = embeddings[i]
            chunks_with_embeddings.append(chunk_copy)
        
        # Store in vector database
        logger.info(f"\nStoring {len(chunks_with_embeddings)} embeddings in database...")
        stored_count = self.vector_store.store_embeddings(
            chunks_with_embeddings,
            embedding_dim=self.embedding_gen.dimension
        )
        
        logger.info(f"✓ Stored {stored_count} embeddings successfully")
        
        # Get statistics
        stats = self.schema_manager.get_table_stats()
        
        return {
            'total_chunks_processed': len(chunks),
            'embeddings_generated': len(embeddings),
            'embeddings_stored': stored_count,
            'embedding_dimension': self.embedding_gen.dimension,
            'database_stats': stats
        }
    
    def test_similarity_search(self, query: str = "What is the expense ratio?"):
        """
        Test similarity search with a sample query
        
        Args:
            query: Sample query text
        """
        logger.info("\n" + "="*80)
        logger.info("Testing Similarity Search")
        logger.info("="*80)
        
        # Generate query embedding
        query_embedding = self.embedding_gen.generate_embedding_single(query)
        
        # Search
        results = self.vector_store.similarity_search(
            query_embedding,
            top_k=5
        )
        
        logger.info(f"\nQuery: '{query}'")
        logger.info(f"Found {len(results)} similar chunks:\n")
        
        for i, result in enumerate(results, 1):
            logger.info(f"{i}. Score: {result['similarity_score']:.4f}")
            logger.info(f"   Fund: {result['fund_name']}")
            logger.info(f"   Type: {result['chunk_type']}")
            logger.info(f"   Text: {result['chunk_text'][:100]}...\n")
    
    def run_pipeline(self, test_query: str = None):
        """
        Run complete Phase 3 pipeline
        
        Args:
            test_query: Optional query to test similarity search
        """
        try:
            # Step 1: Initialize components
            self.initialize()
            
            # Step 2: Setup database
            self.setup_database()
            
            # Step 3: Process and store embeddings
            stats = self.process_and_store_embeddings()
            
            # Step 4: Test similarity search (optional)
            if test_query:
                self.test_similarity_search(test_query)
            
            # Print summary
            self._print_summary(stats)
            
            return stats
            
        except Exception as e:
            logger.error(f"\n❌ Phase 3 failed: {str(e)}")
            raise
        finally:
            # Cleanup
            if self.vector_store:
                self.vector_store.disconnect()
    
    def _print_summary(self, stats: Dict):
        """Print pipeline summary"""
        logger.info("\n" + "="*80)
        logger.info("PHASE 3 COMPLETION SUMMARY")
        logger.info("="*80)
        logger.info(f"Total Chunks Processed: {stats['total_chunks_processed']}")
        logger.info(f"Embeddings Generated: {stats['embeddings_generated']}")
        logger.info(f"Embeddings Stored: {stats['embeddings_stored']}")
        logger.info(f"Embedding Dimension: {stats['embedding_dimension']}")
        logger.info(f"\nDatabase Statistics:")
        logger.info(f"  - Total chunks in DB: {stats['database_stats'].get('total_chunks', 0)}")
        logger.info(f"  - Unique funds: {stats['database_stats'].get('unique_funds', 0)}")
        logger.info(f"  - Chunk types: {stats['database_stats'].get('chunk_types', 0)}")
        logger.info("="*80)


def main():
    """Main entry point for Phase 3"""
    print("\n" + "="*80)
    print("Phase 3: Embeddings & Vector Database Setup")
    print("="*80)
    print("\nThis will:")
    print("1. Load Sentence Transformers model (all-mpnet-base-v2)")
    print("2. Generate embeddings for all processed chunks")
    print("3. Set up PostgreSQL + pgvector database")
    print("4. Store embeddings with HNSW indexing")
    print("5. Test similarity search")
    print("\nPrerequisites:")
    print("- PostgreSQL 13+ with pgvector extension installed")
    print("- Phase 2 complete (processed chunks in data/processed/)")
    print("- Dependencies: pip install sentence-transformers psycopg2-binary")
    print("="*80)
    
    # Get database connection string
    print("\nEnter PostgreSQL connection string:")
    print("Format: postgresql://user:password@host:port/database")
    print("Example: postgresql://postgres:password@localhost:5432/rag_mutual_funds")
    
    db_url = input("\nConnection string: ").strip()
    
    if not db_url:
        print("\n❌ No connection string provided")
        return
    
    print("\nPress Enter to start Phase 3 pipeline...")
    input()
    
    try:
        # Run pipeline
        pipeline = Phase3Pipeline(db_url)
        stats = pipeline.run_pipeline(test_query="What is the expense ratio of HDFC ELSS Fund?")
        
        print(f"\n✅ Phase 3 Complete!")
        print(f"   - Processed {stats['total_chunks_processed']} chunks")
        print(f"   - Generated {stats['embeddings_generated']} embeddings")
        print(f"   - Stored {stats['embeddings_stored']} embeddings in database")
        print(f"   - Embedding dimension: {stats['embedding_dimension']}")
        print("\nNext step: Implement RAG retrieval pipeline (Phase 4)")
        
    except Exception as e:
        print(f"\n❌ Phase 3 failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure PostgreSQL is running")
        print("2. Verify pgvector extension is installed")
        print("3. Check connection string credentials")
        print("4. Confirm Phase 2 output exists in data/processed/")


if __name__ == "__main__":
    main()
