# Quick Start Guide - RAG Mutual Funds Application

## ✅ Application Status
Both Backend and Frontend servers are now running successfully!

## 🌐 Access URLs
- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🚀 Starting the Application

### Option 1: Start All Services (Recommended)
```bash
python start_all.py
```

This script will:
1. Check prerequisites (Python, Node.js, npm)
2. Install dependencies
3. Start backend server (port 8000)
4. Start frontend server (port 3000)
5. Wait for services to be ready

### Option 2: Start Services Separately

#### Backend Server
```bash
# Activate virtual environment first
.venv\Scripts\Activate.ps1  # Windows PowerShell
# or
.venv\Scripts\activate.bat  # Windows CMD

# Start FastAPI server
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Server
```bash
cd frontend
npm run dev
```

## 🔧 Troubleshooting

### Frontend Issues

**Problem**: `localhost:3000` shows "Connection Refused"
**Solution**: 
- Make sure the frontend server is running: `cd frontend && npm run dev`
- Check if port 3000 is already in use
- Verify `.env.local` file exists in the frontend directory

**Problem**: Import errors in Next.js
**Solution**: 
- Ensure all imports use correct relative paths
- The `page.tsx` should import from `../lib/store` and `../components/ChatInterface`

### Backend Issues

**Problem**: Backend shows "degraded" status
**Solution**: 
- This is normal if PostgreSQL is not configured
- The app uses ChromaDB by default which should work
- Check that vector store components are initialized

**Problem**: Dependency installation fails
**Solution**: 
```bash
# Reinstall Python dependencies
pip install -r src/requirements.txt --force-reinstall

# For psycopg2 issues, you can skip it if using ChromaDB
pip install fastapi uvicorn python-jose[cryptography] passlib
```

### Port Already in Use

If ports 3000 or 8000 are already in use:

**Windows:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000
# Kill the process (replace PID with actual number)
taskkill /F /PID <PID>
```

## 📝 Environment Configuration

### Backend (.env file)
```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/rag_mutual_funds

# Embedding Configuration
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2

# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=your-api-key-here
```

### Frontend (frontend/.env.local)
```env
# Backend API Configuration
API_BASE_URL=http://localhost:8000
WS_BASE_URL=ws://localhost:8000

# Next.js Configuration
NEXT_PUBLIC_APP_NAME="RAG Mutual Funds"
```

## ✨ Features

### Frontend
- Modern React/Next.js interface
- Real-time chat with mutual funds bot
- Example queries for quick testing
- Responsive design with Tailwind CSS
- Clear conversation functionality

### Backend
- RESTful API with FastAPI
- WebSocket support for real-time communication
- JWT authentication
- Rate limiting
- RAG pipeline for query processing
- Interactive API docs at `/docs`

## 🎯 Testing the Application

1. Open http://localhost:3000 in your browser
2. Try one of the example queries:
   - "What is the expense ratio of HDFC ELSS Fund?"
   - "Minimum SIP for large cap funds?"
   - "Lock-in period for tax saver funds?"
3. Check the API documentation at http://localhost:8000/docs

## 🛑 Stopping the Application

**If started with start_all.py:**
- Close the terminal windows running the servers
- Or press Ctrl+C in each terminal

**Manual stop:**
```powershell
# Stop Node.js processes
taskkill /F /IM node.exe

# Stop Python processes (be careful with this command)
taskkill /F /IM python.exe
```

## 📊 Current Status

✅ Backend Server: Running on port 8000
✅ Frontend Server: Running on port 3000
✅ .env.local created with correct configuration
✅ Import paths fixed in page.tsx
✅ Application accessible at http://localhost:3000

## 💡 Tips

- Both servers run in development mode with hot reload
- Changes to frontend code automatically refresh
- Check terminal outputs for any errors
- The backend may show "degraded" status if PostgreSQL is not configured - this is normal for ChromaDB setup
