"""
Phase 9 Frontend Setup and Runner Script
Initialize and run the Next.js frontend application
"""
import sys
import os
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_node_installation():
    """Check if Node.js and npm are installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        logger.info(f"Node.js version: {result.stdout.strip()}")
        
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        logger.info(f"npm version: {result.stdout.strip()}")
        
        return True
    except FileNotFoundError:
        logger.error("Node.js or npm not found")
        return False


def install_dependencies(frontend_dir: Path):
    """Install npm dependencies"""
    print("\n" + "="*80)
    print("Installing Frontend Dependencies")
    print("="*80)
    
    try:
        logger.info("Running npm install...")
        result = subprocess.run(
            ['npm', 'install'],
            cwd=frontend_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ Dependencies installed successfully")
            return True
        else:
            logger.error(f"npm install failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to install dependencies: {str(e)}")
        return False


def setup_environment():
    """Setup environment variables"""
    print("\n" + "="*80)
    print("Phase 9: Frontend Configuration")
    print("="*80)
    
    print("\nFrontend Configuration:")
    api_url = input("\nBackend API URL [http://localhost:8000]: ").strip() or "http://localhost:8000"
    ws_url = input("WebSocket URL [ws://localhost:8000]: ").strip() or "ws://localhost:8000"
    
    # Create .env.local file
    env_content = f"""# Backend API Configuration
API_BASE_URL={api_url}
WS_BASE_URL={ws_url}

# Next.js Configuration
NEXT_PUBLIC_APP_NAME="RAG Mutual Funds"
"""
    
    env_path = Path("frontend/.env.local")
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    logger.info(f"✅ Environment file created at: {env_path}")
    
    return api_url, ws_url


def run_development_server(frontend_dir: Path):
    """Start Next.js development server"""
    print("\n" + "="*80)
    print("Starting Next.js Development Server")
    print("="*80)
    
    try:
        logger.info("Running npm run dev...")
        
        # Run in background on Windows
        if sys.platform == 'win32':
            subprocess.Popen(
                ['npm', 'run', 'dev'],
                cwd=frontend_dir,
                shell=True
            )
        else:
            subprocess.run(
                ['npm', 'run', 'dev'],
                cwd=frontend_dir
            )
        
        print("\n✅ Frontend server started!")
        print("\nAccess the application at:")
        print("  http://localhost:3000")
        print("\nPress Ctrl+C to stop the server")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠ Server stopped by user")
        return True
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        return False


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("Phase 9: Frontend Web Application - RAG Mutual Funds")
    print("="*80)
    print("\nThis will:")
    print("1. Check Node.js installation")
    print("2. Install frontend dependencies (React, Next.js, Redux)")
    print("3. Configure backend API connection")
    print("4. Start development server")
    print("\nFeatures:")
    print("  • Modern React/Next.js application")
    print("  • Real-time chat interface")
    print("  • Redux state management")
    print("  • WebSocket support")
    print("  • Responsive design with Tailwind CSS")
    print("="*80)
    
    # Get project paths
    project_root = Path(__file__).parent.parent
    frontend_dir = project_root / "frontend"
    
    if not frontend_dir.exists():
        logger.error("Frontend directory not found")
        return 1
    
    # Check Node.js
    print("\nChecking Node.js installation...")
    if not check_node_installation():
        print("\n❌ Please install Node.js (v18+) and npm first")
        print("Download from: https://nodejs.org/")
        return 1
    
    print("✅ Node.js and npm available")
    
    # Setup environment
    api_url, ws_url = setup_environment()
    
    # Install dependencies
    print("\nInstalling frontend dependencies...")
    if not install_dependencies(frontend_dir):
        print("\n❌ Failed to install dependencies")
        print("Try running: cd frontend && npm install")
        return 1
    
    # Run development server
    if not run_development_server(frontend_dir):
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
