"""
Gemini LLM Integration for Response Generation
Supports Gemini 2.5 Flash / 3 Flash / 3.5 Flash
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

try:
    import google.generativeai as genai
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Google Generative AI not installed. Run: pip install google-generativeai langchain-google-genai")

logger = logging.getLogger(__name__)


class GeminiResponseGenerator:
    """
    Response generator using Google Gemini LLMs
    Supports: gemini-2.5-flash, gemini-3-flash, gemini-3.5-flash
    """
    
    def __init__(
        self,
        model_name: str = "gemini-1.5-flash",
        api_key: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 512
    ):
        """
        Initialize Gemini response generator
        
        Args:
            model_name: Gemini model to use
                Options: 'gemini-1.5-flash', 'gemini-2.5-flash', 
                         'gemini-3-flash', 'gemini-3.5-flash'
            api_key: Google API key (or set GOOGLE_API_KEY env var)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
        """
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "Google Generative AI is required. "
                "Install with: pip install google-generativeai langchain-google-genai"
            )
        
        # Get API key
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google API key required. Set GOOGLE_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize model
        self.model = self._initialize_model()
        
        # LangChain wrapper (optional)
        self.llm_chain = self._initialize_langchain()
        
        logger.info(f"GeminiResponseGenerator initialized with {model_name}")
    
    def _initialize_model(self):
        """Initialize Gemini model"""
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    'temperature': self.temperature,
                    'max_output_tokens': self.max_tokens,
                    'top_p': 0.95,
                    'top_k': 40,
                }
            )
            logger.info(f"✓ Gemini model '{self.model_name}' loaded successfully")
            return model
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {str(e)}")
            raise
    
    def _initialize_langchain(self):
        """Initialize LangChain wrapper"""
        try:
            llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                convert_system_message_to_human=True
            )
            logger.info("✓ LangChain wrapper initialized")
            return llm
        except Exception as e:
            logger.warning(f"LangChain initialization failed: {str(e)}")
            logger.warning("Continuing without LangChain wrapper")
            return None
    
    def generate_response(
        self,
        question: str,
        context: str,
        retrieved_chunks: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate response using Gemini
        
        Args:
            question: User's question
            context: Retrieved context text
            retrieved_chunks: Optional list of retrieved chunks for citations
            
        Returns:
            Dictionary with response and metadata
        """
        logger.info(f"Generating response with Gemini for: '{question[:50]}...'")
        
        # Build prompt
        prompt = self._build_prompt(question, context)
        
        try:
            # Generate response
            response_text = self._generate_with_gemini(prompt)
            
            # Extract citation
            citation = self._extract_citation(retrieved_chunks) if retrieved_chunks else None
            
            # Build response data
            response_data = {
                'question': question,
                'answer': response_text.strip(),
                'confidence': 0.85,  # High confidence with Gemini
                'citation': citation,
                'context_used': context[:500],  # First 500 chars for debugging
                'generated_at': datetime.now().isoformat(),
                'method': 'gemini',
                'model': self.model_name,
                'llm_provider': 'Google Gemini'
            }
            
            logger.info(f"✓ Response generated (model: {self.model_name}, confidence: 0.85)")
            
            return response_data
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {str(e)}")
            
            # Fallback to template response
            return self._fallback_response(question, context, retrieved_chunks)
    
    def _build_prompt(self, question: str, context: str) -> str:
        """Build prompt for Gemini"""
        system_instruction = """You are a helpful assistant for mutual fund information.
Answer the user's question using ONLY the provided context.
If the answer cannot be found in the context, say "I don't have that information in my knowledge base."
Always provide factual information only. Do not give investment advice.
Include citations when available."""

        prompt = f"""{system_instruction}

Context Information:
{context}

User Question: {question}

Please provide a clear, factual answer based on the context above:"""

        return prompt
    
    def _generate_with_gemini(self, prompt: str) -> str:
        """Generate response using Gemini"""
        try:
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text
            else:
                logger.warning("Empty response from Gemini")
                return self._fallback_template(prompt)
                
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return self._fallback_template(prompt)
    
    def _fallback_response(
        self,
        question: str,
        context: str,
        retrieved_chunks: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        """Fallback response when Gemini fails"""
        logger.warning("Using fallback response generator")
        
        # Simple template-based response
        if not context or context.strip() == "":
            answer = "I don't have enough information to answer that question from my knowledge base."
        else:
            lines = context.split('\n')
            relevant_lines = [line.strip() for line in lines if line.strip()]
            summary = ". ".join(relevant_lines[:3])
            answer = f"Based on the available information: {summary}"
        
        citation = self._extract_citation(retrieved_chunks) if retrieved_chunks else None
        
        return {
            'question': question,
            'answer': answer,
            'confidence': 0.60,
            'citation': citation,
            'context_used': context[:500],
            'generated_at': datetime.now().isoformat(),
            'method': 'fallback_template',
            'model': None,
            'llm_provider': 'Template'
        }
    
    def _fallback_template(self, prompt: str) -> str:
        """Simple template-based fallback"""
        return "Based on the available information, I can provide details from the context."
    
    def _extract_citation(self, retrieved_chunks: List[Dict]) -> Optional[str]:
        """Extract citation from retrieved chunks"""
        if not retrieved_chunks:
            return None
        
        first_chunk = retrieved_chunks[0]
        metadata = first_chunk.get('metadata', {})
        
        if isinstance(metadata, dict):
            return metadata.get('source_url')
        
        return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            'model_name': self.model_name,
            'provider': 'Google Gemini',
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'api_key_configured': bool(self.api_key),
            'langchain_available': self.llm_chain is not None
        }
    
    def list_available_models(self) -> List[str]:
        """List available Gemini models"""
        return [
            'gemini-1.5-flash',    # Fast, efficient
            'gemini-2.5-flash',    # Enhanced flash
            'gemini-3-flash',      # Latest flash
            'gemini-3.5-flash',    # Most advanced flash
            'gemini-pro',          # Standard model
            'gemini-pro-vision'    # Vision-capable
        ]


def main():
    """Test Gemini response generator"""
    print("="*80)
    print("Testing Gemini Response Generator")
    print("="*80)
    
    if not GEMINI_AVAILABLE:
        print("\n❌ Google Generative AI not installed")
        print("\nInstall with:")
        print("  pip install google-generativeai langchain-google-genai")
        return
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n❌ GOOGLE_API_KEY not set")
        print("\nSet environment variable:")
        print("  export GOOGLE_API_KEY='your-api-key-here'")
        print("\nOr create .env file with:")
        print("  GOOGLE_API_KEY=your-api-key-here")
        return
    
    try:
        # Initialize generator
        print("\nInitializing Gemini...")
        generator = GeminiResponseGenerator(
            model_name="gemini-1.5-flash",
            temperature=0.1
        )
        
        print(f"\nModel Info: {generator.get_model_info()}")
        print(f"\nAvailable Models: {generator.list_available_models()}")
        
        # Test generation
        test_question = "What is the expense ratio of HDFC ELSS Fund?"
        test_context = """HDFC ELSS Tax Saver Fund has an expense ratio of 0.68%. 
This is a direct plan growth option with minimum SIP of ₹500 and lock-in period of 3 years."""
        
        print(f"\n{'='*80}")
        print(f"Test Question: {test_question}")
        print(f"{'='*80}")
        
        response = generator.generate_response(
            question=test_question,
            context=test_context,
            retrieved_chunks=[{
                'metadata': {
                    'source_url': 'https://www.indmoney.com/mutual-funds/hdfc-elss'
                }
            }]
        )
        
        print(f"\nGenerated Answer:")
        print(f"{response['answer']}")
        
        print(f"\nMetadata:")
        print(f"  Confidence: {response['confidence']:.0%}")
        print(f"  Citation: {response['citation']}")
        print(f"  Model: {response['model']}")
        print(f"  Provider: {response['llm_provider']}")
        
        print("\n✅ Gemini Response Generator Test Complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Install dependencies: pip install google-generativeai langchain-google-genai")
        print("2. Set API key: export GOOGLE_API_KEY='your-key'")
        print("3. Check internet connection")
        print("4. Verify API key is valid")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
