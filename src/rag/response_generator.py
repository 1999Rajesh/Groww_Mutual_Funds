"""
Response Generator Module
Generates responses using retrieved context and LLM
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    from langchain.llms import HuggingFaceHub
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("LangChain not installed. Run: pip install langchain langchain-community")

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """
    Generates responses using retrieved context and language models
    """
    
    def __init__(self, use_llm: bool = True, llm_type: str = "huggingface"):
        """
        Initialize response generator
        
        Args:
            use_llm: Whether to use LLM for generation
            llm_type: Type of LLM to use ('huggingface', 'openai', etc.)
        """
        self.use_llm = use_llm
        self.llm_type = llm_type
        self.llm_chain = None
        
        if self.use_llm:
            self._initialize_llm(llm_type)
        
        # Define prompt template for factual Q&A
        self.prompt_template = """You are a helpful assistant for mutual fund information. 
Answer the user's question using ONLY the provided context. 
If the answer cannot be found in the context, say "I don't have that information in my knowledge base."
Always provide factual information only. Do not give investment advice.

Context:
{context}

Question: {question}

Answer (factual, with citation if available):"""
        
        if LANGCHAIN_AVAILABLE:
            self.prompt = PromptTemplate(
                template=self.prompt_template,
                input_variables=["context", "question"]
            )
    
    def _initialize_llm(self, llm_type: str):
        """Initialize the language model"""
        try:
            if llm_type == "huggingface":
                # Use Hugging Face Hub (free tier)
                import os
                from langchain_huggingface import HuggingFaceEndpoint
                
                # Get API key from environment or use default
                hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
                
                if not hf_token:
                    logger.warning("HUGGINGFACEHUB_API_TOKEN not set. Using mock mode.")
                    self.use_llm = False
                    return
                
                self.llm = HuggingFaceEndpoint(
                    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
                    huggingfacehub_api_token=hf_token,
                    temperature=0.1,  # Low temperature for factual responses
                    max_new_tokens=512,
                    top_p=0.95
                )
                
                self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt)
                logger.info("✓ Hugging Face LLM initialized")
            
            elif llm_type == "mock":
                # Mock LLM for testing without API
                self.use_llm = False
                logger.info("Using mock LLM (template-based responses)")
            
            else:
                logger.warning(f"Unknown LLM type: {llm_type}. Using mock mode.")
                self.use_llm = False
        
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            self.use_llm = False
    
    def generate_response(
        self,
        question: str,
        context: str,
        retrieved_chunks: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate response to a question
        
        Args:
            question: User's question
            context: Retrieved context text
            retrieved_chunks: Optional list of retrieved chunks for citations
            
        Returns:
            Dictionary with response and metadata
        """
        logger.info(f"Generating response for question: '{question}'")
        
        if self.use_llm and self.llm_chain:
            # Use LLM for generation
            try:
                response = self.llm_chain.run(question=question, context=context)
                confidence = 0.85  # High confidence when using LLM
            except Exception as e:
                logger.error(f"LLM generation failed: {str(e)}")
                response = self._generate_template_response(question, context)
                confidence = 0.65
        else:
            # Use template-based generation
            response = self._generate_template_response(question, context)
            confidence = 0.70
        
        # Extract citation from retrieved chunks
        citation = self._extract_citation(retrieved_chunks) if retrieved_chunks else None
        
        # Build response metadata
        response_data = {
            'question': question,
            'answer': response.strip(),
            'confidence': confidence,
            'citation': citation,
            'context_used': context[:500],  # Store first 500 chars for debugging
            'generated_at': datetime.now().isoformat(),
            'method': 'llm' if self.use_llm else 'template'
        }
        
        logger.info(f"Generated response (confidence: {confidence:.2f}, method: {response_data['method']})")
        
        return response_data
    
    def _generate_template_response(self, question: str, context: str) -> str:
        """
        Generate response using templates (fallback when LLM unavailable)
        
        Args:
            question: User's question
            context: Retrieved context
            
        Returns:
            Generated response
        """
        # Simple template-based response
        if not context or context.strip() == "":
            return "I don't have enough information to answer that question from my knowledge base."
        
        # Extract key information from context
        lines = context.split('\n')
        relevant_lines = [line.strip() for line in lines if line.strip()]
        
        if len(relevant_lines) > 3:
            # Summarize if too long
            summary = relevant_lines[0] + ". " + relevant_lines[1] + ". " + relevant_lines[2] + "..."
        else:
            summary = ". ".join(relevant_lines)
        
        response = f"Based on the available information: {summary}"
        
        return response
    
    def _extract_citation(self, retrieved_chunks: List[Dict[str, Any]]) -> Optional[str]:
        """
        Extract citation from retrieved chunks
        
        Args:
            retrieved_chunks: List of retrieved chunks
            
        Returns:
            Citation URL or None
        """
        if not retrieved_chunks:
            return None
        
        # Try to get source URL from first chunk's metadata
        first_chunk = retrieved_chunks[0]
        metadata = first_chunk.get('metadata', {})
        
        if isinstance(metadata, dict):
            return metadata.get('source_url')
        
        return None
    
    def generate_answer_with_citation(
        self,
        question: str,
        context: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> str:
        """
        Generate answer with citation link
        
        Args:
            question: User's question
            context: Retrieved context
            retrieved_chunks: Retrieved chunks for citation
            
        Returns:
            Formatted answer with citation
        """
        response_data = self.generate_response(question, context, retrieved_chunks)
        
        answer = response_data['answer']
        citation = response_data.get('citation')
        
        if citation:
            formatted_answer = f"{answer}\n\nSource: {citation}"
        else:
            formatted_answer = answer
        
        return formatted_answer


def main():
    """Test response generator"""
    print("="*80)
    print("Testing Response Generator")
    print("="*80)
    
    try:
        # Initialize generator
        generator = ResponseGenerator(use_llm=False)  # Use template mode for testing
        
        # Test cases
        test_cases = [
            {
                'question': "What is the expense ratio of HDFC ELSS Fund?",
                'context': "HDFC ELSS Tax Saver Fund has an expense ratio of 0.68%. This is a direct plan growth option.",
                'retrieved_chunks': [
                    {
                        'chunk_text': "Expense Ratio: 0.68%",
                        'metadata': {'source_url': 'https://www.indmoney.com/mutual-funds/hdfc-elss'}
                    }
                ]
            },
            {
                'question': "What is the minimum SIP?",
                'context': "The minimum SIP amount for HDFC Large Cap Fund is ₹500. Minimum lumpsum is ₹5000.",
                'retrieved_chunks': [
                    {
                        'chunk_text': "Minimum SIP: ₹500",
                        'metadata': {'source_url': 'https://www.indmoney.com/mutual-funds/hdfc-large-cap'}
                    }
                ]
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*80}")
            print(f"Test Case {i}:")
            print(f"Question: {test_case['question']}")
            print(f"Context: {test_case['context']}")
            print(f"{'='*80}")
            
            # Generate response
            response_data = generator.generate_response(
                question=test_case['question'],
                context=test_case['context'],
                retrieved_chunks=test_case['retrieved_chunks']
            )
            
            print(f"\nGenerated Answer:")
            print(f"{response_data['answer']}")
            
            print(f"\nMetadata:")
            print(f"  Confidence: {response_data['confidence']:.2f}")
            print(f"  Citation: {response_data.get('citation', 'N/A')}")
            print(f"  Method: {response_data['method']}")
        
        print("\n✅ Response Generator Test Complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
