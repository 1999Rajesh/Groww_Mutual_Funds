"""
Complete Application Startup Script
Starts both Backend (FastAPI) and Frontend (Next.js)
"""
import sys
import os
import subprocess
import logging
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def check_prerequisites():
    """Check if all required tools are installed"""
    print("\n" + "="*80)
    print("Checking Prerequisites")
    print("="*80)
    
    # Check Python
    try:
        result = subprocess.run(['python', '--version'], capture_output=True, text=True, shell=True)
        logger.info(f"✓ Python: {result.stdout.strip()}")
    except FileNotFoundError:
        logger.error("❌ Python not found. Please install Python 3.8+")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, shell=True)
        logger.info(f"✓ Node.js: {result.stdout.strip()}")
    except FileNotFoundError:
        logger.error("❌ Node.js not found. Please install Node.js 18+")
        return False
    
    # Check npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True, shell=True)
        logger.info(f"✓ npm: {result.stdout.strip()}")
    except FileNotFoundError:
        logger.error("❌ npm not found. Please install Node.js")
        return False
    
    return True


def setup_backend():
    """Setup and start backend server"""
    print("\n" + "="*80)
    print("Setting Up Backend Server")
    print("="*80)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        logger.info("Creating .env file from .env.example...")
        if Path(".env.example").exists():
            subprocess.run(['copy', '.env.example', '.env'], shell=True)
            logger.info("✓ .env file created")
        else:
            logger.warning("⚠ .env.example not found")
    
    # Install backend dependencies
    logger.info("Installing backend dependencies...")
    try:
        result = subprocess.run(
            'pip install -r src/requirements.txt',
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0:
            logger.info("✓ Backend dependencies installed")
        else:
            logger.warning(f"⚠ Some dependencies may have issues: {result.stderr}")
    except Exception as e:
        logger.error(f"❌ Failed to install backend dependencies: {str(e)}")
        return False
    
    return True


def setup_frontend():
    """Setup and start frontend server"""
    print("\n" + "="*80)
    print("Setting Up Frontend Server")
    print("="*80)
    
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        logger.error("❌ Frontend directory not found")
        return False
    
    # Create .env.local if it doesn't exist
    env_local = frontend_dir / ".env.local"
    if not env_local.exists():
        logger.info("Creating frontend .env.local file...")
        env_content = """# Backend API Configuration
API_BASE_URL=http://localhost:8000
WS_BASE_URL=ws://localhost:8000

# Next.js Configuration
NEXT_PUBLIC_APP_NAME="RAG Mutual Funds"
"""
        with open(env_local, 'w') as f:
            f.write(env_content)
        logger.info("✓ .env.local created")
    
    # Install frontend dependencies
    logger.info("Installing frontend dependencies...")
    try:
        result = subprocess.run(
            'npm install',
            cwd=frontend_dir,
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0:
            logger.info("✓ Frontend dependencies installed")
        else:
            logger.warning(f"⚠ Some dependencies may have issues: {result.stderr}")
    except Exception as e:
        logger.error(f"❌ Failed to install frontend dependencies: {str(e)}")
        return False
    
    return True


def start_backend():
    """Start backend server in background"""
    print("\n" + "="*80)
    print("Starting Backend Server (Port 8000)")
    print("="*80)
    
    try:
        # Start backend in background
        if sys.platform == 'win32':
            # Windows: Use START command
            subprocess.Popen(
                'start "Backend Server" python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload',
                shell=True
            )
        else:
            # Unix-like systems
            subprocess.Popen(
                ['python', '-m', 'uvicorn', 'src.api.main:app', '--host', '0.0.0.0', '--port', '8000', '--reload'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        logger.info("✓ Backend server starting...")
        logger.info("  Backend URL: http://localhost:8000")
        logger.info("  API Docs: http://localhost:8000/docs")
        
        # Wait for backend to start
        logger.info("\nWaiting for backend to be ready...")
        time.sleep(5)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to start backend: {str(e)}")
        return False


def start_frontend():
    """Start frontend server in background"""
    print("\n" + "="*80)
    print("Starting Frontend Server (Port 3000)")
    print("="*80)
    
    frontend_dir = Path("frontend")
    
    try:
        # Start frontend in background
        if sys.platform == 'win32':
            # Windows: Use START command
            subprocess.Popen(
                'start "Frontend Server" npm run dev',
                cwd=frontend_dir,
                shell=True
            )
        else:
            # Unix-like systems
            subprocess.Popen(
                ['npm', 'run', 'dev'],
                cwd=frontend_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        logger.info("✓ Frontend server starting...")
        logger.info("  Frontend URL: http://localhost:3000")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to start frontend: {str(e)}")
        return False


def wait_for_services():
    """Wait for services to be ready"""
    print("\n" + "="*80)
    print("Waiting for Services to Start")
    print("="*80)
    
    import requests
    
    max_attempts = 30
    delay = 2
    
    # Wait for backend
    logger.info("Checking backend health...")
    for i in range(max_attempts):
        try:
            response = requests.get('http://localhost:8000/health', timeout=2)
            if response.status_code == 200:
                logger.info("✓ Backend is ready!")
                break
        except:
            pass
        
        if i < max_attempts - 1:
            logger.info(f"  Attempt {i+1}/{max_attempts}... waiting {delay}s")
            time.sleep(delay)
    else:
        logger.warning("⚠ Backend may not be fully ready yet")
    
    # Wait for frontend
    logger.info("\nChecking frontend availability...")
    for i in range(max_attempts):
        try:
            response = requests.get('http://localhost:3000', timeout=2)
            if response.status_code == 200:
                logger.info("✓ Frontend is ready!")
                break
        except:
            pass
        
        if i < max_attempts - 1:
            logger.info(f"  Attempt {i+1}/{max_attempts}... waiting {delay}s")
            time.sleep(delay)
    else:
        logger.warning("⚠ Frontend may not be fully ready yet")
    
    return True


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("🚀 Starting RAG Mutual Funds Application")
    print("="*80)
    print("\nThis will start:")
    print("  1. Backend Server (FastAPI) on port 8000")
    print("  2. Frontend Server (Next.js) on port 3000")
    print("\nAccess the application at:")
    print("  http://localhost:3000")
    print("\nAPI Documentation at:")
    print("  http://localhost:8000/docs")
    print("="*80)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please install required software.")
        return 1
    
    # Setup backend
    if not setup_backend():
        print("\n❌ Backend setup failed")
        return 1
    
    # Setup frontend
    if not setup_frontend():
        print("\n❌ Frontend setup failed")
        return 1
    
    # Start backend
    if not start_backend():
        print("\n❌ Failed to start backend")
        return 1
    
    # Start frontend
    if not start_frontend():
        print("\n❌ Failed to start frontend")
        return 1
    
    # Wait for services
    wait_for_services()
    
    print("\n" + "="*80)
    print("✅ Application Started Successfully!")
    print("="*80)
    print("\n📊 Application URLs:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print("\n💡 Tips:")
    print("   - Both servers are running in separate windows")
    print("   - Close the terminal windows to stop the servers")
    print("   - Check the terminal outputs for any errors")
    print("="*80)
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠ Application stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
