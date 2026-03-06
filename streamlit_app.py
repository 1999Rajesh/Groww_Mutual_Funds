"""
Streamlit Chatbot for Mutual Funds RAG System
Deploy with: streamlit run streamlit_app.py
"""
import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Import RAG components
from src.rag.query_processor import QueryProcessor
from src.vector_db.chroma_store import ChromaVectorStore
from src.embeddings.embedding_generator import EmbeddingGenerator

# Page config
st.set_page_config(
    page_title="Mutual Funds FAQ Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #1f77b4;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .citation-box {
        background-color: #fff3e0;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        border-left: 3px solid #ff9800;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }
    .metadata-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def init_rag_pipeline():
    """Initialize RAG pipeline components (cached)"""
    try:
        query_processor = QueryProcessor()
        vector_store = ChromaVectorStore()
        embedding_gen = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
        return {
            "query_processor": query_processor,
            "vector_store": vector_store,
            "embedding_gen": embedding_gen,
            "initialized": True
        }
    except Exception as e:
        st.error(f"Failed to initialize RAG pipeline: {e}")
        return {"initialized": False, "error": str(e)}


def load_metadata():
    """Load metadata from file"""
    metadata_path = Path("./data/metadata.json")
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "last_updated": None,
        "total_funds": 0,
        "data_sources": ["HDFC AMC", "Groww"]
    }


def is_opinionated_question(question: str) -> bool:
    """Check if question is asking for advice/opinion (not factual)"""
    opinion_keywords = [
        'should i', 'should we', 'shall i', 'recommend', 'suggest', 
        'advice', 'buy', 'sell', 'invest in', 'good fund', 'best fund',
        'which fund', 'where to invest', 'portfolio', 'hold', 'exit'
    ]
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in opinion_keywords)


def get_educational_link(question: str) -> str:
    """Return relevant educational link based on question topic"""
    question_lower = question.lower()
    
    if 'expense' in question_lower or 'ratio' in question_lower:
        return 'https://www.amfiindia.com/mutual-funds/what-is-mutual-fund/understanding-mutual-funds'
    elif 'elss' in question_lower or 'tax' in question_lower or 'lock-in' in question_lower:
        return 'https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognised=yes&sid=1&ssid=13&smid=0'
    elif 'sip' in question_lower or 'invest' in question_lower:
        return 'https://www.amfiindia.com/mutual-funds/what-is-mutual-fund/understanding-mutual-funds'
    elif 'exit load' in question_lower or 'charges' in question_lower:
        return 'https://www.camsonline.com/Investors/Customer-service-briefs/Mutual-Fund-Glossary'
    elif 'risk' in question_lower or 'riskometer' in question_lower:
        return 'https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognised=yes&sid=1&ssid=13&smid=0'
    elif 'capital gains' in question_lower or 'statement' in question_lower or 'tax' in question_lower:
        return 'https://www.camsonline.com/Investors/Statements/Consolidated-Account-Statement'
    else:
        return 'https://www.amfiindia.com/mutual-funds/what-is-mutual-fund/understanding-mutual-funds'


def process_query(question: str, pipeline: dict) -> dict:
    """Process a query through the RAG pipeline"""
    try:
        start_time = datetime.now()
        
        # Check for opinion/advice questions first
        if is_opinionated_question(question):
            educational_link = get_educational_link(question)
            return {
                "answer": "I can only provide factual information from official sources. For personalized investment advice, please consult a SEBI-registered investment advisor.\n\n📚 **Educational Resource:** Learn more about mutual funds basics.",
                "citation": educational_link,
                "confidence": 1.0,
                "is_opinion_refusal": True
            }
        
        # Extract query info
        query_processor = pipeline["query_processor"]
        vector_store = pipeline["vector_store"]
        embedding_gen = pipeline["embedding_gen"]
        
        extracted = query_processor.process_query(question)
        enhanced_query = extracted.get('enhanced_query', question)
        
        # Generate embedding and search
        query_embedding = embedding_gen.generate_embeddings([enhanced_query])[0]
        results = vector_store.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=5,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Process results
        chunks = []
        if results and results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                distance = results['distances'][0][i] if results['distances'] else 0
                chunks.append({
                    'text': doc,
                    'metadata': metadata,
                    'similarity': 1 - distance  # Convert distance to similarity
                })
        
        # Generate answer
        if chunks:
            # Use only top 2 chunks for concise answer
            context_texts = [c['text'] for c in chunks[:2]]
            answer = "Based on available information:\n\n"
            for text in context_texts:
                answer += f"• {text}\n\n"
            
            # Get SINGLE citation from best matching chunk
            citation = chunks[0]['metadata'].get('source_url', '')
            confidence = min(0.9, max(0.4, chunks[0]['similarity']))
        else:
            answer = "I couldn't find specific information about that. Please try rephrasing your question or ask about HDFC mutual funds."
            citation = ""
            confidence = 0.3
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            "answer": answer,
            "citation": citation,
            "confidence": confidence,
            "chunks_retrieved": len(chunks),
            "processing_time_ms": round(processing_time, 2),
            "query_analysis": extracted,
            "is_opinion_refusal": False
        }
        
    except Exception as e:
        return {
            "answer": f"Sorry, an error occurred: {str(e)}",
            "citation": "",
            "confidence": 0,
            "error": str(e),
            "is_opinion_refusal": False
        }


def main():
    # Header
    st.markdown('<h1 class="main-header">💰 Mutual Funds FAQ Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Ask questions about HDFC Mutual Fund schemes</p>', unsafe_allow_html=True)
    
    # Initialize pipeline
    pipeline = init_rag_pipeline()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 System Status")
        
        # Load metadata
        metadata = load_metadata()
        
        # Status indicators
        if pipeline.get("initialized"):
            st.success("✅ RAG Pipeline Ready")
            
            # Vector DB count
            try:
                db_count = pipeline["vector_store"].collection.count()
                st.metric("Documents Indexed", db_count)
            except:
                st.metric("Documents Indexed", "N/A")
        else:
            st.error("❌ Pipeline Not Initialized")
            st.write(pipeline.get("error", "Unknown error"))
        
        st.divider()
        
        # Metadata
        st.markdown("### 📋 Data Information")
        
        # Data sources
        data_sources = metadata.get('data_sources', ['HDFC AMC', 'Groww'])
        if isinstance(data_sources, list):
            st.markdown("**Data Sources:**")
            for source in data_sources[:3]:
                st.markdown(f"• {source}")
        
        # Last updated
        last_updated = metadata.get('last_updated')
        if last_updated:
            try:
                dt = datetime.fromisoformat(last_updated)
                st.markdown(f"**Last Updated:** {dt.strftime('%b %d, %Y')}")
            except:
                st.markdown(f"**Last Updated:** {last_updated[:10]}")
        
        # Total funds
        total_funds = metadata.get('total_funds', 0)
        st.metric("Total Funds", total_funds)
        
        st.divider()
        
        # Sample questions
        st.markdown("### 💡 Try These Questions")
        sample_questions = [
            "What is the expense ratio of HDFC ELSS?",
            "What is the lock-in period for ELSS funds?",
            "Tell me about HDFC Top 100 Fund",
            "What is the minimum SIP amount?",
        ]
        for q in sample_questions:
            if st.button(q, key=f"sample_{q[:20]}"):
                st.session_state.sample_question = q
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Check for sample question click
    if "sample_question" in st.session_state:
        question = st.session_state.sample_question
        del st.session_state.sample_question
        
        # Add to messages and process
        st.session_state.messages.append({"role": "user", "content": question})
        
        if pipeline.get("initialized"):
            with st.spinner("Thinking..."):
                response = process_query(question, pipeline)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["answer"],
                "citation": response.get("citation", ""),
                "confidence": response.get("confidence", 0),
                "is_opinion_refusal": response.get("is_opinion_refusal", False)
            })
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show citation for assistant messages
            if message["role"] == "assistant" and message.get("citation"):
                citation = message["citation"]
                confidence = message.get("confidence", 0)
                is_opinion_refusal = message.get("is_opinion_refusal", False)
                
                st.markdown(f"""
                <div class="citation-box">
                    📚 <strong>Source:</strong> <a href="{citation}" target="_blank">{citation[:70]}...</a><br>
                    📊 <strong>Confidence:</strong> {confidence:.0%}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Ask about mutual funds..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process and display response
        with st.chat_message("assistant"):
            if pipeline.get("initialized"):
                with st.spinner("Searching knowledge base..."):
                    response = process_query(prompt, pipeline)
                
                st.markdown(response["answer"])
                
                # Show citation
                if response.get("citation"):
                    citation = response["citation"]
                    confidence = response.get("confidence", 0)
                    
                    st.markdown(f"""
                    <div class="citation-box">
                        📚 <strong>Source:</strong> <a href="{citation}" target="_blank">{citation[:70]}...</a><br>
                        📊 <strong>Confidence:</strong> {confidence:.0%}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["answer"],
                    "citation": response.get("citation", ""),
                    "confidence": response.get("confidence", 0),
                    "is_opinion_refusal": response.get("is_opinion_refusal", False)
                })
            else:
                st.error("RAG pipeline not initialized. Please check the system status.")
    
    # Footer
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col2:
        st.markdown(
            "<p style='text-align: center; color: #888; font-size: 0.8rem;'>"
            "Powered by RAG | Data from HDFC AMC & Groww"
            "</p>",
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()
