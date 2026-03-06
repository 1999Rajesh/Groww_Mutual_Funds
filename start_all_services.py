"""
Start All Services - Quick Start Script
Starts both Backend (FastAPI) and Frontend (Next.js)
"""
import subprocess
import time
import webbrowser
from pathlib import Path

print("="*80)
print("🚀 Starting RAG Mutual Funds Application")
print("="*80)

# Get the project root directory
ROOT_DIR = Path(__file__).parent

print("\n📍 Project Root:", ROOT_DIR)

# Step 1: Start Backend Server
print("\n" + "="*80)
print("🔧 Starting Backend Server (FastAPI)...")
print("="*80)

backend_process = subprocess.Popen(
    [".venv\\Scripts\\python.exe", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd=str(ROOT_DIR),
    shell=True
)

print("⏳ Waiting for backend to start...")
time.sleep(5)

# Check if backend is running
try:
    import requests
    response = requests.get("http://localhost:8000/api/v1/health", timeout=3)
    if response.status_code == 200:
        print("✅ Backend started successfully!")
        print("   URL: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
    else:
        print("⚠️  Backend may have issues, but continuing...")
except Exception as e:
    print(f"⚠️  Backend check failed: {e}")

# Step 2: Start Frontend Server
print("\n" + "="*80)
print("🎨 Starting Frontend Server (Next.js)...")
print("="*80)

frontend_process = subprocess.Popen(
    ["npm", "run", "dev"],
    cwd=str(ROOT_DIR / "frontend"),
    shell=True
)

print("⏳ Waiting for frontend to start...")
time.sleep(8)

# Check if frontend is running
try:
    response = requests.get("http://localhost:3000", timeout=3)
    if response.status_code == 200:
        print("✅ Frontend started successfully!")
        print("   URL: http://localhost:3000")
        
        # Open browser automatically
        print("\n🌐 Opening application in browser...")
        webbrowser.open("http://localhost:3000")
    else:
        print("⚠️  Frontend may have issues")
except Exception as e:
    print(f"⚠️  Frontend check failed: {e}")

# Final status
print("\n" + "="*80)
print("✅ APPLICATION STARTED SUCCESSFULLY!")
print("="*80)
print("\n📋 Access URLs:")
print("   • Frontend: http://localhost:3000")
print("   • Backend API: http://localhost:8000")
print("   • API Documentation: http://localhost:8000/docs")
print("\n💡 Press Ctrl+C in both terminal windows to stop the servers")
print("="*80)

# Keep the script running
try:
    backend_process.wait()
except KeyboardInterrupt:
    print("\n\n🛑 Stopping all services...")
    backend_process.terminate()
    frontend_process.terminate()
    print("✅ All services stopped")
