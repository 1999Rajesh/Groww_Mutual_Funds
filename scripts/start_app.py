"""
Quick Start Script - Runs both Backend and Frontend
"""
import sys
import os
import subprocess
import time
from pathlib import Path

print("\n" + "="*80)
print("RAG Mutual Funds - Quick Start")
print("="*80)
print("\nStarting Backend API (Phase 8) and Frontend (Phase 9)...")
print("="*80)

# Check if GOOGLE_API_KEY is set
if not os.getenv("GOOGLE_API_KEY"):
    print("\n⚠️  WARNING: GOOGLE_API_KEY not set!")
    print("Please set the environment variable:")
    print('  export GOOGLE_API_KEY="your-api-key-here"')
    print("\nOr create a .env file with:")
    print('  GOOGLE_API_KEY=your-api-key-here')
    print("\nContinuing anyway (will use fallback responses)...\n")

# Start Backend (Phase 8)
print("\n[1/2] Starting Backend API on http://localhost:8000...")
print("      Swagger UI: http://localhost:8000/docs")

backend_cmd = [
    sys.executable, "-m", "uvicorn", 
    "src.api.main:app",
    "--host", "0.0.0.0",
    "--port", "8000",
    "--reload"
]

backend_process = subprocess.Popen(backend_cmd, cwd=str(Path(__file__).parent))

# Wait for backend to start
print("      Waiting for backend to initialize...")
time.sleep(5)

# Start Frontend (Phase 9)
print("\n[2/2] Starting Frontend Web App on http://localhost:3000...")

frontend_dir = Path(__file__).parent / "frontend"

if not frontend_dir.exists():
    print("❌ Frontend directory not found!")
    backend_process.terminate()
    sys.exit(1)

# Check if node_modules exists
node_modules = frontend_dir / "node_modules"
if not node_modules.exists():
    print("      Installing dependencies (first time only)...")
    subprocess.run(["npm", "install"], cwd=str(frontend_dir))

frontend_cmd = ["npm", "run", "dev"]
frontend_process = subprocess.Popen(frontend_cmd, cwd=str(frontend_dir))

print("\n" + "="*80)
print("✅ Application Started Successfully!")
print("="*80)
print("\n📍 Access Points:")
print("   Frontend Web App: http://localhost:3000")
print("   Backend API:      http://localhost:8000")
print("   API Documentation: http://localhost:8000/docs")
print("\n🎯 What to do next:")
print("   1. Open your browser and go to: http://localhost:3000")
print("   2. Try example queries or ask your own questions")
print("   3. Explore the chat interface features")
print("\n⚠️  To stop the application, press Ctrl+C in this terminal")
print("="*80)

try:
    # Wait for processes
    backend_process.wait()
    frontend_process.wait()
except KeyboardInterrupt:
    print("\n\n⚠️  Shutting down...")
    backend_process.terminate()
    frontend_process.terminate()
    print("✅ Application stopped")
