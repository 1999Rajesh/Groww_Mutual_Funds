# Phase 8 Backend API - Quick Start Guide

## 🚀 Running the Backend API

### Prerequisites Check

```bash
# 1. Install Phase 8 dependencies
pip install fastapi uvicorn pyjwt passlib python-jose[cryptography] python-multipart

# Or install all dependencies
pip install -r src/requirements.txt

# 2. Verify installation
pip show fastapi uvicorn pyjwt
```

### Quick Start (3 Steps)

```bash
# Step 1: Navigate to project
cd c:\Users\Rajesh\Documents\RAG_Mutual_Funds

# Step 2: Run Phase 8
python run_phase8.py

# Step 3: Access API documentation
Open browser: http://localhost:8000/docs
```

---

## 📡 API Testing Examples

### 1. Register a User

**Using cURL**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"testuser\",\"password\":\"password123\"}"
```

**Using Python**:
```python
import requests

response = requests.post("http://localhost:8000/api/v1/auth/register", 
                        json={"username": "testuser", "password": "password123"})
print(response.json())
# Output: {"message": "User registered successfully", "username": "testuser"}
```

---

### 2. Login and Get Token

**Using cURL**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"testuser\",\"password\":\"password123\"}"
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Using Python**:
```python
response = requests.post("http://localhost:8000/api/v1/auth/login", 
                        json={"username": "testuser", "password": "password123"})
token = response.json()["access_token"]
```

---

### 3. Submit Query

**Using cURL**:
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"question\":\"What is the expense ratio of HDFC ELSS Fund?\"}"
```

**Response**:
```json
{
  "question": "What is the expense ratio of HDFC ELSS Fund?",
  "answer": "HDFC ELSS Tax Saver Fund has an expense ratio of 0.68%...",
  "confidence": 0.85,
  "citation": "https://www.indmoney.com/mutual-funds/hdfc-elss-taxsaver-direct-plan-growth-option-2685",
  "chunks_retrieved": 3,
  "processing_time_ms": 2345.67
}
```

**Using Python**:
```python
headers = {"Authorization": f"Bearer {token}"}
response = requests.post("http://localhost:8000/api/v1/query", 
                        headers=headers, 
                        json={"question": "What is the expense ratio of HDFC ELSS Fund?"})
print(response.json())
```

---

### 4. Health Check

**Using cURL**:
```bash
curl "http://localhost:8000/health"
```

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-03-05T11:30:00",
  "components": {
    "api": true,
    "rag_pipeline": true,
    "vector_store": true,
    "llm": true
  }
}
```

---

## 🌐 WebSocket Example

### JavaScript Client

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/chat');

ws.onopen = () => {
  console.log('Connected to chat');
  
  // Send message
  ws.send(JSON.stringify({
    message: "What is the minimum SIP for large cap funds?",
    session_id: "session_123"
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'typing') {
    console.log('Typing:', data.message);
  } else if (data.type === 'response') {
    console.log('Answer:', data.data.answer);
    console.log('Confidence:', data.data.confidence);
    console.log('Source:', data.data.citation);
  }
};

ws.onerror = (error) => {
  console.error('WebSocket Error:', error);
};
```

### Python Client

```python
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    print(f"Received: {data}")

def on_open(ws):
    print("Connected")
    
    # Send query
    ws.send(json.dumps({
        "message": "What is the expense ratio of large cap funds?",
        "session_id": "session_123"
    }))

def on_close(ws, close_status_code, close_msg):
    print("Disconnected")

# Connect
ws = websocket.WebSocketApp(
    "ws://localhost:8000/ws/chat",
    on_open=on_open,
    on_message=on_message,
    on_close=on_close
)

ws.run_forever()
```

---

## 🔧 Configuration Options

### Environment Variables (.env)

```bash
# Security
SECRET_KEY=your-super-secret-key-change-this-in-production

# Database
DB_TYPE=chromadb

# LLM
LLM_MODEL=gemini-1.5-flash
GOOGLE_API_KEY=your-gemini-api-key-here

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Server
HOST=0.0.0.0
PORT=8000
```

### Production Settings

Update `src/api/main.py`:

```python
# Line 17-18: Stronger secret key
SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(32).hex())

# Line 20: Longer token expiration
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour

# Line 297: Restrict CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domain
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## 📊 Endpoint Reference

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/v1/auth/register` | No | Register new user |
| POST | `/api/v1/auth/login` | No | Login and get token |
| POST | `/api/v1/auth/logout` | Yes | Logout current user |
| POST | `/api/v1/query` | Yes | Submit query |
| GET | `/api/v1/query/history` | Yes | Get query history |
| WS | `/ws/chat` | No | WebSocket chat |
| GET | `/health` | No | Health check |
| GET | `/api/v1/stats` | Yes | System statistics |

---

## 🎯 Common Use Cases

### Example 1: Simple Q&A Flow

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Register
requests.post(f"{BASE_URL}/api/v1/auth/register", 
             json={"username": "user1", "password": "pass123"})

# 2. Login
resp = requests.post(f"{BASE_URL}/api/v1/auth/login", 
                    json={"username": "user1", "password": "pass123"})
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 3. Ask question
resp = requests.post(f"{BASE_URL}/api/v1/query", 
                    headers=headers, 
                    json={"question": "Expense ratio of HDFC ELSS?"})

result = resp.json()
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']:.0%}")
print(f"Source: {result['citation']}")
```

### Example 2: Batch Queries

```python
questions = [
    "What is the expense ratio of HDFC Large Cap Fund?",
    "Minimum SIP for HDFC Small Cap Fund?",
    "Lock-in period for HDFC ELSS Fund?"
]

results = []
for q in questions:
    resp = requests.post(f"{BASE_URL}/api/v1/query", 
                        headers=headers, 
                        json={"question": q})
    results.append(resp.json())

for i, result in enumerate(results, 1):
    print(f"\n{i}. {result['question']}")
    print(f"   {result['answer']}")
```

### Example 3: Real-time Chat

```javascript
class RAGChatBot {
  constructor() {
    this.ws = null;
    this.connect();
  }

  connect() {
    this.ws = new WebSocket('ws://localhost:8000/ws/chat');
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'response') {
        this.displayAnswer(data.data);
      }
    };
  }

  ask(question) {
    this.ws.send(JSON.stringify({ message: question }));
  }

  displayAnswer(data) {
    console.log(`Q: ${data.question}`);
    console.log(`A: ${data.answer}`);
    console.log(`Confidence: ${(data.confidence * 100).toFixed(0)}%`);
    if (data.citation) {
      console.log(`Source: ${data.citation}`);
    }
  }
}

// Usage
const bot = new RAGChatBot();
bot.ask("What is the NAV of HDFC Balanced Advantage Fund?");
```

---

## 🐛 Troubleshooting

### Issue: Can't start server - "Address already in use"

**Solution**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>

# Or use different port
python run_phase8.py
# Enter port: 8001
```

### Issue: "GOOGLE_API_KEY not set"

**Solution**:
```bash
# Windows PowerShell
$env:GOOGLE_API_KEY="your-api-key-here"

# Linux/Mac
export GOOGLE_API_KEY='your-api-key-here'

# Or add to .env file
echo "GOOGLE_API_KEY=your-key" >> .env
```

### Issue: "RAG pipeline not initialized"

**Solution**:
```bash
# Ensure previous phases completed
python run_phase1.py  # Scrape data
python run_phase2.py  # Process data
python run_phase3.py  # Generate embeddings

# Then restart API
python run_phase8.py
```

### Issue: 401 Unauthorized

**Solution**:
- Check token is valid JWT
- Ensure token not expired (default 30 min)
- Include "Bearer " prefix in Authorization header
- Token format: `Authorization: Bearer eyJhbG...`

---

## 📈 Performance Tips

### 1. Enable Response Caching

```python
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

@app.get("/api/v1/query/{question}")
@cache(expire=600)  # Cache for 10 minutes
async def cached_query(question: str):
    ...
```

### 2. Optimize Database Queries

```python
# Use connection pooling
# Implement query caching
# Index frequently accessed fields
```

### 3. Adjust Rate Limits

```python
# For high-traffic scenarios
RATE_LIMIT_REQUESTS = 200  # Increase from 100
RATE_LIMIT_WINDOW = 60
```

---

## ✅ Success Indicators

You'll know it's working when you see:

```
INFO:     Starting up RAG Mutual Funds API...
✓ Query Processor loaded
✓ ChromaDB loaded
✓ Embedding Generator loaded
✓ gemini-1.5-flash loaded
✅ RAG Pipeline initialized successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

And can successfully:
- ✅ Access Swagger UI at `/docs`
- ✅ Register a user
- ✅ Login and receive token
- ✅ Submit authenticated queries
- ✅ Receive responses with citations
- ✅ Connect via WebSocket

---

## 🆘 Getting Help

1. Check Swagger UI: `http://localhost:8000/docs`
2. Review logs in terminal output
3. Verify all prerequisites installed
4. Ensure API keys configured correctly
5. Test endpoints individually

---

**Quick Test**: If you can register, login, and get an answer to "Expense ratio of HDFC ELSS?", Phase 8 is working! ✅
