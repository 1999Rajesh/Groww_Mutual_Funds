"""
Embedding Generator Module
Generates embeddings using Sentence Transformers
"""
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("sentence-transformers not installed. Run: pip install sentence-transformers")

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Generates embeddings for text chunks using Sentence Transformers
    """
    
    def __init__(self, model_name: str = "all-mpnet-base-v2"):
        """
        Initialize embedding generator
        
        Args:
            model_name: Name of the sentence transformer model
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers library is required. "
                "Install with: pip install sentence-transformers"
            )
        
        self.model_name = model_name
        self.model = None
        self.dimension = None
        
        logger.info(f"Initializing embedding generator with model: {model_name}")
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model"""
        try:
            self.model = SentenceTransformer(self.model_name)
            
            # Get embedding dimension
            test_embedding = self.model.encode(["test"])
            self.dimension = len(test_embedding[0])
            
            logger.info(f"Model loaded successfully. Dimension: {self.dimension}")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    def generate_embeddings(self, texts: List[str], batch_size: int = 32, 
                           show_progress: bool = True) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            batch_size: Batch size for encoding
            show_progress: Show progress bar
            
        Returns:
            Numpy array of embeddings (n_texts x dimension)
        """
        if not texts:
            logger.warning("No texts provided for embedding generation")
            return np.array([])
        
        logger.info(f"Generating embeddings for {len(texts)} texts...")
        
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
                normalize_embeddings=True  # L2 normalization for cosine similarity
            )
            
            logger.info(f"Generated embeddings shape: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def generate_embedding_single(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Text string to embed
            
        Returns:
            Numpy array of embedding (dimension,)
        """
        if not text:
            raise ValueError("Text cannot be empty")
        
        embeddings = self.generate_embeddings([text], show_progress=False)
        return embeddings[0]
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information
        
        Returns:
            Dictionary with model details
        """
        return {
            'model_name': self.model_name,
            'dimension': self.dimension,
            'device': str(self.model.device) if self.model else 'Not loaded',
            'normalized': True
        }


def main():
    """Test embedding generator"""
    print("="*80)
    print("Testing Embedding Generator")
    print("="*80)
    
    # Sample texts
    sample_texts = [
        "HDFC ELSS Tax Saver Fund has an expense ratio of 0.68%",
        "Minimum SIP amount for HDFC Large Cap Fund is ₹500",
        "ELSS funds have a lock-in period of 3 years",
        "HDFC Small Cap Fund carries Very High risk level"
    ]
    
    try:
        # Initialize generator
        generator = EmbeddingGenerator(model_name="all-mpnet-base-v2")
        
        print(f"\nModel Info: {generator.get_model_info()}")
        
        # Generate embeddings
        embeddings = generator.generate_embeddings(sample_texts)
        
        print(f"\nGenerated embeddings:")
        print(f"Shape: {embeddings.shape}")
        print(f"First embedding (first 10 values): {embeddings[0][:10]}")
        
        # Test single embedding
        single_embedding = generator.generate_embedding_single(sample_texts[0])
        print(f"\nSingle embedding shape: {single_embedding.shape}")
        
        # Test similarity (cosine similarity already baked in due to normalization)
        similarity = np.dot(embeddings[0], embeddings[1])
        print(f"\nSimilarity between text 1 and 2: {similarity:.4f}")
        
        print("\n✅ Embedding Generator Test Successful!")
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("\nTo use this module, install:")
        print("  pip install sentence-transformers")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
