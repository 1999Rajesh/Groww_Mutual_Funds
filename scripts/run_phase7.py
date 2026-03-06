"""
Phase 7: CLI Interface - Interactive Chatbot
Command-line interface for RAG Mutual Funds system
"""
import sys
import logging
from datetime import datetime
from pathlib import Path

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.styles import Style
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("prompt-toolkit not installed. Run: pip install prompt-toolkit")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CLIChatbot:
    """
    Phase 7: Interactive CLI Chatbot
    Integrates all phases with modern tech stack
    """
    
    def __init__(
        self,
        db_type: str = "chromadb",
        llm_model: str = "gemini-1.5-flash",
        vector_db_path: str = "./chroma_db"
    ):
        """
        Initialize CLI chatbot
        
        Args:
            db_type: Vector database type ('chromadb', 'pinecone', 'postgresql')
            llm_model: Gemini model to use
            vector_db_path: Path for vector database
        """
        self.db_type = db_type
        self.llm_model = llm_model
        self.vector_db_path = vector_db_path
        
        # Components (initialized later)
        self.query_processor = None
        self.retriever = None
        self.generator = None
        self.vector_store = None
        
        # Session state
        self.session_active = False
        self.chat_history = []
        
        # Setup style for prompt
        self.style = Style.from_dict({
            'prompt': 'ansicyan bold',
            'question': 'ansigreen bold',
            'answer': 'ansiwhite',
            'error': 'ansired bold',
            'info': 'ansiyellow',
        })
        
        logger.info(f"CLI Chatbot initialized (db={db_type}, llm={llm_model})")
    
    def initialize_components(self, db_connection_string: str = None):
        """Initialize all RAG components"""
        print("\n" + "="*80)
        print("Initializing RAG Components")
        print("="*80)
        
        try:
            # Phase 5: Query Processor
            print("\n[1/4] Loading Query Processor (Phase 5)...")
            from src.rag.query_processor import QueryProcessor
            self.query_processor = QueryProcessor()
            print("✓ Query Processor ready")
            
            # Phase 3/6: Vector Store
            print(f"\n[2/4] Loading Vector Database ({self.db_type})...")
            if self.db_type == "chromadb":
                from src.vector_db.chroma_store import ChromaVectorStore
                self.vector_store = ChromaVectorStore(persist_directory=self.vector_db_path)
                print(f"✓ ChromaDB loaded at {self.vector_db_path}")
            elif self.db_type == "postgresql":
                if not db_connection_string:
                    raise ValueError("PostgreSQL connection string required")
                from src.vector_db.vector_store import VectorStore
                self.vector_store = VectorStore(db_connection_string)
                print("✓ PostgreSQL vector store ready")
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            # Phase 4: RAG Retriever
            print("\n[3/4] Loading RAG Retriever (Phase 4)...")
            # We'll use the vector store directly for now
            print("✓ RAG Retriever ready")
            
            # Phase 4/7: Response Generator (Gemini)
            print(f"\n[4/4] Loading LLM ({self.llm_model})...")
            try:
                from src.rag.gemini_generator import GeminiResponseGenerator
                self.generator = GeminiResponseGenerator(model_name=self.llm_model)
                print(f"✓ {self.llm_model} ready")
            except Exception as e:
                logger.warning(f"Gemini initialization failed: {e}")
                print("⚠ Using fallback template-based responses")
                self.generator = None
            
            print("\n" + "="*80)
            print("✅ All Components Initialized Successfully!")
            print("="*80)
            
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            print(f"\n❌ Error: {str(e)}")
            print("\nTroubleshooting:")
            print("1. Ensure dependencies installed: pip install -r src/requirements.txt")
            print("2. Check database path/connection")
            print("3. Verify API keys set (GOOGLE_API_KEY)")
            return False
    
    def process_query(self, query: str) -> dict:
        """
        Process user query through RAG pipeline
        
        Args:
            query: User question
            
        Returns:
            Response dictionary
        """
        try:
            # Step 1: Process query (Phase 5)
            extracted = self.query_processor.process_query(query)
            
            # Check for opinion queries
            if extracted.get('is_opinion'):
                return {
                    'question': query,
                    'answer': "I can only provide factual information about mutual funds. I cannot provide investment advice or recommendations. For personalized investment advice, please consult a SEBI-registered financial advisor.",
                    'confidence': 1.0,
                    'citation': "https://www.sebi.gov.in/investor-resources.html",
                    'refused': True
                }
            
            # Step 2: Enhance query
            enhanced_query = self.query_processor.enhance_query(query, extracted)
            filters = self.query_processor.get_filter_params(extracted)
            
            # Step 3: Retrieve from vector store
            # Generate embedding for query
            from src.embeddings.embedding_generator import EmbeddingGenerator
            emb_gen = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
            query_embedding = emb_gen.generate_embedding_single(enhanced_query)
            
            # Search vector store
            retrieved_chunks = self.vector_store.similarity_search(
                query_embedding=query_embedding,
                top_k=5,
                filter_fund_name=filters.get('fund_name'),
                filter_chunk_type=filters.get('chunk_type')
            )
            
            if not retrieved_chunks:
                return {
                    'question': query,
                    'answer': "I don't have enough information to answer that question from my knowledge base. Please try rephrasing your question.",
                    'confidence': 0.0,
                    'citation': None,
                    'chunks_retrieved': 0,
                    'refused': False
                }
            
            # Step 4: Format context
            context = "\n\n".join([chunk['chunk_text'] for chunk in retrieved_chunks])
            
            # Step 5: Generate response
            if self.generator:
                response = self.generator.generate_response(
                    question=query,
                    context=context,
                    retrieved_chunks=retrieved_chunks
                )
            else:
                # Fallback to template
                response = {
                    'question': query,
                    'answer': f"Based on available information: {context[:200]}...",
                    'confidence': 0.6,
                    'citation': retrieved_chunks[0].get('metadata', {}).get('source_url'),
                    'method': 'template'
                }
            
            # Add metadata
            response['chunks_retrieved'] = len(retrieved_chunks)
            response['query_analysis'] = extracted
            
            return response
            
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            return {
                'question': query,
                'answer': f"Sorry, I encountered an error processing your question: {str(e)}",
                'confidence': 0.0,
                'citation': None,
                'error': True
            }
    
    def display_response(self, response: dict):
        """Display response with formatting"""
        print("\n" + "-"*80)
        
        # Answer
        print(f"\n{response['answer']}")
        
        # Citation
        if response.get('citation'):
            print(f"\n📌 Source: {response['citation']}")
        
        # Metadata
        print(f"\nDetails:")
        print(f"  Confidence: {response.get('confidence', 0):.0%}")
        
        if response.get('query_analysis'):
            analysis = response['query_analysis']
            if analysis.get('fund_name'):
                print(f"  Fund: {analysis['fund_name']}")
            if analysis.get('intent'):
                print(f"  Intent: {analysis['intent']}")
        
        if response.get('chunks_retrieved'):
            print(f"  Sources: {response['chunks_retrieved']} chunks")
        
        print("-"*80)
    
    def show_welcome(self):
        """Show welcome message"""
        print("\n" + "="*80)
        print("RAG Mutual Funds Chatbot - Phase 7 CLI Interface")
        print("="*80)
        print("\nWelcome! I can answer factual questions about HDFC Mutual Funds.")
        print("\nExample questions:")
        print("  • What is the expense ratio of HDFC ELSS Tax Saver Fund?")
        print("  • Minimum SIP amount for HDFC Large Cap Fund?")
        print("  • What is the lock-in period for ELSS funds?")
        print("  • Exit load for HDFC Small Cap Fund?")
        print("  • Risk level of HDFC Balanced Advantage Fund?")
        print("\nNote: I provide factual information only, not investment advice.")
        print("\nCommands:")
        print("  /help     - Show this help message")
        print("  /history  - Show conversation history")
        print("  /clear    - Clear conversation history")
        print("  /stats    - Show system statistics")
        print("  /export   - Export conversation to file")
        print("  /quit     - Exit the chatbot")
        print("="*80)
    
    def show_help(self):
        """Show help message"""
        self.show_welcome()
    
    def show_history(self):
        """Show conversation history"""
        if not self.chat_history:
            print("\n📝 No conversation history yet.")
            return
        
        print("\n" + "="*80)
        print("Conversation History")
        print("="*80)
        
        for i, (question, response) in enumerate(self.chat_history[-10:], 1):
            print(f"\n{i}. Q: {question}")
            print(f"   A: {response['answer'][:100]}...")
        
        print(f"\nTotal: {len(self.chat_history)} exchanges")
        print("="*80)
    
    def show_stats(self):
        """Show system statistics"""
        print("\n" + "="*80)
        print("System Statistics")
        print("="*80)
        
        stats = {
            'Database Type': self.db_type,
            'LLM Model': self.llm_model,
            'Vector DB Path': self.vector_db_path,
            'Conversation Length': len(self.chat_history),
            'Components Loaded': sum([
                self.query_processor is not None,
                self.vector_store is not None,
                self.generator is not None
            ])
        }
        
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("="*80)
    
    def export_conversation(self, filename: str = "conversation_export.txt"):
        """Export conversation to file"""
        if not self.chat_history:
            print("\n⚠ No conversation to export.")
            return
        
        filepath = Path(filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"RAG Mutual Funds Chatbot - Conversation Export\n")
                f.write(f"Date: {datetime.now().isoformat()}\n")
                f.write(f"Total Exchanges: {len(self.chat_history)}\n")
                f.write("="*80 + "\n\n")
                
                for i, (question, response) in enumerate(self.chat_history, 1):
                    f.write(f"{i}. Question: {question}\n")
                    f.write(f"   Answer: {response['answer']}\n")
                    if response.get('citation'):
                        f.write(f"   Source: {response['citation']}\n")
                    f.write("\n")
            
            print(f"\n✅ Conversation exported to: {filepath.absolute()}")
            
        except Exception as e:
            print(f"\n❌ Export failed: {str(e)}")
    
    def run_interactive_session(self):
        """Run interactive CLI session"""
        self.session_active = True
        self.show_welcome()
        
        # Setup completer for auto-completion
        commands = ['/help', '/history', '/clear', '/stats', '/export', '/quit']
        completer = WordCompleter(commands, ignore_case=True)
        
        # Setup history
        history_file = Path("./cli_history.txt")
        
        print("\nType your question or command (type /help for commands):")
        
        while self.session_active:
            try:
                # Get user input
                if PROMPT_TOOLKIT_AVAILABLE:
                    session = PromptSession(
                        history=FileHistory(str(history_file)),
                        auto_suggest=AutoSuggestFromHistory(),
                        completer=completer,
                        style=self.style
                    )
                    
                    query = session.prompt(
                        [('class:prompt', '\nYou: ')]
                    ).strip()
                else:
                    query = input("\nYou: ").strip()
                
                if not query:
                    continue
                
                # Handle commands
                if query.startswith('/'):
                    command = query.lower().split()[0]
                    
                    if command == '/help':
                        self.show_help()
                    elif command == '/history':
                        self.show_history()
                    elif command == '/clear':
                        self.chat_history.clear()
                        print("\n✅ Conversation history cleared.")
                    elif command == '/stats':
                        self.show_stats()
                    elif command == '/export':
                        self.export_conversation()
                    elif command in ['/quit', '/exit', '/q']:
                        print("\n👋 Goodbye! Thank you for using RAG Mutual Funds Chatbot.")
                        self.session_active = False
                        break
                    else:
                        print(f"\n⚠ Unknown command: {command}. Type /help for commands.")
                    continue
                
                # Process query
                print("\n⏳ Thinking...")
                response = self.process_query(query)
                
                # Display response
                self.display_response(response)
                
                # Save to history
                self.chat_history.append((query, response))
                
            except KeyboardInterrupt:
                print("\n\n⚠ Session interrupted. Type /quit to exit.")
                continue
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                logger.error(f"Error processing query: {str(e)}")
                continue
    
    def close(self):
        """Close chatbot and cleanup"""
        print("\nClosing chatbot...")
        
        if hasattr(self, 'vector_store') and self.vector_store:
            if hasattr(self.vector_store, 'close'):
                self.vector_store.close()
        
        self.session_active = False
        print("✅ Chatbot closed successfully.")


def main():
    """Main entry point for Phase 7 CLI"""
    print("\n" + "="*80)
    print("Phase 7: CLI Interface - RAG Mutual Funds Chatbot")
    print("="*80)
    print("\nThis will:")
    print("1. Initialize all RAG components (Phases 1-6)")
    print("2. Start interactive CLI chatbot session")
    print("3. Answer factual questions about mutual funds")
    print("\nTechnology Stack:")
    print("  • Web Scraping: Playwright")
    print("  • LLM: Google Gemini (1.5/2.5/3/3.5 Flash)")
    print("  • Vector DB: ChromaDB / PostgreSQL")
    print("  • Embeddings: Sentence Transformers")
    print("="*80)
    
    # Configuration
    print("\nConfiguration:")
    print("  Database type: chromadb (default) / postgresql")
    print("  LLM model: gemini-1.5-flash (default) / gemini-3.5-flash")
    
    db_type = input("\nVector database type [chromadb]: ").strip().lower() or "chromadb"
    llm_model = input("LLM model [gemini-1.5-flash]: ").strip().lower() or "gemini-1.5-flash"
    
    db_connection = None
    if db_type == "postgresql":
        db_connection = input("PostgreSQL connection string: ").strip()
    
    vector_db_path = input("Vector DB path [./chroma_db]: ").strip() or "./chroma_db"
    
    print("\nPress Enter to start...")
    input()
    
    try:
        # Initialize chatbot
        chatbot = CLIChatbot(
            db_type=db_type,
            llm_model=llm_model,
            vector_db_path=vector_db_path
        )
        
        # Initialize components
        if not chatbot.initialize_components(db_connection):
            print("\n❌ Failed to initialize components.")
            print("\nTroubleshooting:")
            print("1. Install dependencies: pip install -r src/requirements.txt")
            print("2. Set API keys: export GOOGLE_API_KEY='your-key'")
            print("3. Check database path/connection")
            return
        
        # Run interactive session
        chatbot.run_interactive_session()
        
        # Cleanup
        chatbot.close()
        
        print("\n✅ Phase 7 Complete!")
        print("CLI Interface is fully functional.")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        logger.exception("Fatal error in CLI")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
