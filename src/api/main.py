"""
Phase 8: Backend API - FastAPI Application
RESTful API with authentication, rate limiting, and WebSocket support
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import jwt
from passlib.context import CryptContext
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
RATE_LIMIT_REQUESTS = 100  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

# ============================================================================
# Pydantic Models
# ============================================================================

class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    question: str = Field(..., min_length=1, max_length=1000, description="User's question")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve")
    use_llm: bool = Field(default=True, description="Use LLM for response generation")


class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    question: str
    answer: str
    confidence: float
    citation: Optional[str] = None
    chunks_retrieved: int
    processing_time_ms: float
    model: Optional[str] = None


class ChatMessage(BaseModel):
    """Chat message model"""
    message: str
    session_id: Optional[str] = None


class Token(BaseModel):
    """Authentication token model"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload model"""
    username: Optional[str] = None


class UserCreate(BaseModel):
    """User registration model"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    email: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str
    components: Dict[str, bool]


class MetadataResponse(BaseModel):
    """Metadata response including last updated date"""
    last_updated: Optional[str] = None
    data_source: Optional[str] = None
    total_funds: Optional[int] = None
    vector_db_count: Optional[int] = None


# ============================================================================
# Security Components
# ============================================================================

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user store (replace with database in production)
users_db = {}
blocked_tokens = set()

# Rate limiting storage
rate_limit_store: Dict[str, List[float]] = {}


# ============================================================================
# Helper Functions
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # Check if token is blocked
        if token in blocked_tokens:
            raise credentials_exception
            
    except jwt.PyJWTError:
        raise credentials_exception
    
    return username


def check_rate_limit(client_ip: str) -> bool:
    """Check if client has exceeded rate limit"""
    now = datetime.now().timestamp()
    window_start = now - RATE_LIMIT_WINDOW
    
    # Clean old entries
    if client_ip in rate_limit_store:
        rate_limit_store[client_ip] = [
            ts for ts in rate_limit_store[client_ip] 
            if ts > window_start
        ]
    else:
        rate_limit_store[client_ip] = []
    
    # Check limit
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Add current request
    rate_limit_store[client_ip].append(now)
    return True


# ============================================================================
# RAG Components Integration
# ============================================================================

class RAGPipeline:
    """RAG Pipeline for processing queries"""
    
    def __init__(self):
        self.query_processor = None
        self.embedding_generator = None
        self.vector_store = None
        self.response_generator = None
        self.initialized = False
    
    def initialize(self, db_type: str = "chromadb", llm_model: str = "gemini-1.5-flash"):
        """Initialize RAG components"""
        try:
            logger.info("Initializing RAG pipeline...")
            
            # Phase 5: Query Processor
            from src.rag.query_processor import QueryProcessor
            self.query_processor = QueryProcessor()
            logger.info("✓ Query Processor loaded")
            
            # Phase 3/6: Vector Store
            if db_type == "chromadb":
                from src.vector_db.chroma_store import ChromaVectorStore
                self.vector_store = ChromaVectorStore(persist_directory="./chroma_db")
                logger.info("✓ ChromaDB loaded")
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            # Phase 3: Embedding Generator
            from src.embeddings.embedding_generator import EmbeddingGenerator
            self.embedding_generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
            logger.info("✓ Embedding Generator loaded")
            
            # Phase 4/7: Response Generator (Gemini)
            try:
                from src.rag.gemini_generator import GeminiResponseGenerator
                self.response_generator = GeminiResponseGenerator(model_name=llm_model)
                logger.info(f"✓ {llm_model} loaded")
            except Exception as e:
                logger.warning(f"Gemini initialization failed: {e}")
                self.response_generator = None
            
            self.initialized = True
            logger.info("✅ RAG Pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {str(e)}")
            self.initialized = False
    
    async def process_query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """Process query through RAG pipeline"""
        start_time = datetime.now()
        
        try:
            # Step 1: Process query (Phase 5)
            extracted = self.query_processor.process_query(question)
            
            # Check for opinion queries
            if extracted.get('is_opinion'):
                return {
                    'question': question,
                    'answer': "I can only provide factual information about mutual funds. I cannot provide investment advice or recommendations.",
                    'confidence': 1.0,
                    'citation': "https://www.sebi.gov.in/investor-resources.html",
                    'refused': True,
                    'chunks_retrieved': 0,
                    'processing_time_ms': (datetime.now() - start_time).total_seconds() * 1000
                }
            
            # Step 2: Enhance query
            enhanced_query = self.query_processor.enhance_query(question, extracted)
            
            # Step 3: Generate embedding
            query_embedding = self.embedding_generator.generate_embedding_single(enhanced_query)
            
            # Step 4: Retrieve from vector store
            filters = self.query_processor.get_filter_params(extracted)
            retrieved_chunks = self.vector_store.similarity_search(
                query_embedding=query_embedding,
                top_k=top_k,
                filter_fund_name=filters.get('fund_name'),
                filter_chunk_type=filters.get('chunk_type')
            )
            
            if not retrieved_chunks:
                return {
                    'question': question,
                    'answer': "I don't have enough information to answer that question from my knowledge base.",
                    'confidence': 0.0,
                    'citation': None,
                    'chunks_retrieved': 0,
                    'processing_time_ms': (datetime.now() - start_time).total_seconds() * 1000
                }
            
            # Step 5: Format context
            context = "\n\n".join([chunk['chunk_text'] for chunk in retrieved_chunks])
            
            # Step 6: Generate response
            if self.response_generator:
                response_data = self.response_generator.generate_response(
                    question=question,
                    context=context,
                    retrieved_chunks=retrieved_chunks
                )
            else:
                response_data = {
                    'question': question,
                    'answer': f"Based on available information: {context[:200]}...",
                    'confidence': 0.6,
                    'citation': retrieved_chunks[0].get('metadata', {}).get('source_url')
                }
            
            # Add metadata
            response_data['chunks_retrieved'] = len(retrieved_chunks)
            response_data['processing_time_ms'] = (datetime.now() - start_time).total_seconds() * 1000
            response_data['query_analysis'] = extracted
            
            return response_data
            
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            return {
                'question': question,
                'answer': f"Sorry, I encountered an error processing your question: {str(e)}",
                'confidence': 0.0,
                'citation': None,
                'error': True,
                'chunks_retrieved': 0,
                'processing_time_ms': (datetime.now() - start_time).total_seconds() * 1000
            }


# Global RAG pipeline instance
rag_pipeline = RAGPipeline()


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="RAG Mutual Funds API",
    description="Backend API for RAG-based Mutual Funds Chatbot",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate Limiting Middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to all requests"""
    client_ip = request.client.host
    
    if not check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Too many requests. Please try again later.",
                "retry_after": RATE_LIMIT_WINDOW
            }
        )
    
    response = await call_next(request)
    return response


# Startup Event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting up RAG Mutual Funds API...")
    
    # Initialize RAG pipeline
    db_type = os.getenv("DB_TYPE", "chromadb")
    llm_model = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    rag_pipeline.initialize(db_type=db_type, llm_model=llm_model)
    
    logger.info("✅ Application startup complete")


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.post("/api/v1/auth/register", response_model=Dict[str, str], tags=["Authentication"])
async def register(user: UserCreate):
    """Register a new user"""
    if user.username in users_db:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    users_db[user.username] = {
        "username": user.username,
        "password": get_password_hash(user.password),
        "email": user.email,
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "message": "User registered successfully",
        "username": user.username
    }


@app.post("/api/v1/auth/login", response_model=Token, tags=["Authentication"])
async def login(user: UserCreate):
    """Login and get access token"""
    if user.username not in users_db:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    db_user = users_db[user.username]
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/v1/auth/logout", tags=["Authentication"])
async def logout(current_user: str = Depends(get_current_user)):
    """Logout current user"""
    # In production, implement proper token blacklisting
    logger.info(f"User {current_user} logged out")
    return {"message": "Logged out successfully"}


# ============================================================================
# Query Endpoints
# ============================================================================

@app.post("/api/v1/query", response_model=QueryResponse, tags=["Queries"])
async def post_query(
    request: QueryRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Submit a query and get AI-powered response
    
    Requires authentication. Returns answer with citations.
    """
    if not rag_pipeline.initialized:
        raise HTTPException(
            status_code=503,
            detail="RAG pipeline not initialized"
        )
    
    # Process query
    result = await rag_pipeline.process_query(
        question=request.question,
        top_k=request.top_k
    )
    
    if result.get('error'):
        raise HTTPException(
            status_code=500,
            detail=result['answer']
        )
    
    return QueryResponse(
        question=result['question'],
        answer=result['answer'],
        confidence=result['confidence'],
        citation=result.get('citation'),
        chunks_retrieved=result['chunks_retrieved'],
        processing_time_ms=result['processing_time_ms'],
        model=result.get('model')
    )


@app.post("/api/v1/public/query", response_model=QueryResponse, tags=["Queries"])
async def post_public_query(request: QueryRequest):
    """
    Submit a query and get AI-powered response (Public endpoint, no auth required)
    
    No authentication required. Returns answer with citations.
    """
    if not rag_pipeline.initialized:
        raise HTTPException(
            status_code=503,
            detail="RAG pipeline not initialized"
        )
    
    # Process query
    result = await rag_pipeline.process_query(
        question=request.question,
        top_k=request.top_k
    )
    
    if result.get('error'):
        raise HTTPException(
            status_code=500,
            detail=result['answer']
        )
    
    return QueryResponse(
        question=result['question'],
        answer=result['answer'],
        confidence=result['confidence'],
        citation=result.get('citation'),
        chunks_retrieved=result['chunks_retrieved'],
        processing_time_ms=result['processing_time_ms'],
        model=result.get('model')
    )


@app.get("/api/v1/query/history", tags=["Queries"])
async def get_query_history(
    limit: int = 20,
    current_user: str = Depends(get_current_user)
):
    """Get user's query history"""
    # TODO: Implement persistent storage for query history
    return {
        "queries": [],
        "total": 0,
        "limit": limit
    }


# ============================================================================
# WebSocket Endpoint
# ============================================================================

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            message = data.get("message", "")
            session_id = data.get("session_id")
            
            if not message:
                continue
            
            # Send typing indicator
            await websocket.send_json({
                "type": "typing",
                "message": "Processing..."
            })
            
            # Process query
            result = await rag_pipeline.process_query(message)
            
            # Stream response back
            await websocket.send_json({
                "type": "response",
                "data": {
                    "question": result['question'],
                    "answer": result['answer'],
                    "confidence": result['confidence'],
                    "citation": result.get('citation'),
                    "chunks_retrieved": result['chunks_retrieved'],
                    "processing_time_ms": result['processing_time_ms']
                }
            })
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    components = {
        "api": True,
        "rag_pipeline": rag_pipeline.initialized,
        "vector_store": rag_pipeline.vector_store is not None if rag_pipeline.initialized else False,
        "llm": rag_pipeline.response_generator is not None if rag_pipeline.initialized else False
    }
    
    overall_status = "healthy" if all(components.values()) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
        components=components
    )


@app.get("/api/v1/stats", tags=["Statistics"])
async def get_statistics(current_user: str = Depends(get_current_user)):
    """Get system statistics"""
    stats = {
        "rag_pipeline": {
            "initialized": rag_pipeline.initialized,
            "db_type": "chromadb",
            "llm_model": "gemini-1.5-flash"
        },
        "rate_limiting": {
            "requests_per_minute": RATE_LIMIT_REQUESTS,
            "window_seconds": RATE_LIMIT_WINDOW
        },
        "users": {
            "total": len(users_db)
        }
    }
    
    return stats


@app.get("/api/v1/metadata", response_model=MetadataResponse, tags=["Metadata"])
async def get_metadata():
    """Get metadata including last updated date from data files"""
    try:
        # Try to read last_updated from metadata file first
        last_updated = None
        total_funds = 0
        data_source = "HDFC AMC & Groww"
        
        # Check for metadata.json (created by scheduler)
        metadata_path = Path("./data/metadata.json")
        if metadata_path.exists():
            import json
            with open(metadata_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
                last_updated = meta.get('last_updated')
                total_funds = meta.get('total_funds', 0)
                # Read data_sources array and join for display
                data_sources = meta.get('data_sources', [])
                if data_sources:
                    data_source = ", ".join(data_sources[:2])  # Show first 2 sources
        else:
            # Fallback to checking processed data files
            data_paths = [
                Path("./data/processed/funds.json"),
                Path("./data/raw/funds.json")
            ]
            
            for data_path in data_paths:
                if data_path.exists():
                    import json
                    with open(data_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Check if data has last_updated field
                        if isinstance(data, dict) and 'last_updated' in data:
                            last_updated = data['last_updated']
                            total_funds = data.get('count', 0)
                        elif isinstance(data, list) and len(data) > 0:
                            # Check first item for last_updated
                            if isinstance(data[0], dict) and 'last_updated' in data[0]:
                                last_updated = data[0]['last_updated']
                            total_funds = len(data)
                        break
        
        # Get vector DB count
        vector_db_count = 0
        if rag_pipeline.initialized and rag_pipeline.vector_store:
            try:
                vector_db_count = rag_pipeline.vector_store.collection.count()
            except:
                pass
        
        return MetadataResponse(
            last_updated=last_updated,
            data_source=data_source,
            total_funds=total_funds,
            vector_db_count=vector_db_count
        )
        
    except Exception as e:
        logger.error(f"Metadata retrieval failed: {str(e)}")
        # Return partial data even on error
        return MetadataResponse(
            last_updated=None,
            data_source="HDFC AMC & Groww",
            total_funds=0,
            vector_db_count=0
        )


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Run the FastAPI application"""
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
