"""
Phase 8 Backend API Runner Script
Start the FastAPI server with proper configuration
"""
import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []
    
    try:
        import fastapi
    except ImportError:
        missing.append("fastapi")
    
    try:
        import uvicorn
    except ImportError:
        missing.append("uvicorn")
    
    try:
        from passlib.context import CryptContext
    except ImportError:
        missing.append("passlib")
    
    try:
        import jwt
    except ImportError:
        missing.append("pyjwt")
    
    if missing:
        print("\n❌ Missing dependencies:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\nInstall with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True


def setup_environment():
    """Setup environment variables"""
    print("\n" + "="*80)
    print("Phase 8: Backend API Setup")
    print("="*80)
    
    # Get configuration from user
    print("\nConfiguration:")
    
    host = input("\nServer host [0.0.0.0]: ").strip() or "0.0.0.0"
    port = input("Server port [8000]: ").strip() or "8000"
    reload = input("Enable auto-reload for development? [y/N]: ").strip().lower() == 'y'
    
    # Set environment variables
    os.environ["HOST"] = host
    os.environ["PORT"] = port
    
    print(f"\nServer Configuration:")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Auto-reload: {'Yes' if reload else 'No'}")
    
    return host, port, reload


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("Phase 8: Backend API - RAG Mutual Funds")
    print("="*80)
    print("\nThis will start the FastAPI backend server with:")
    print("  • REST API endpoints for queries")
    print("  • JWT authentication")
    print("  • Rate limiting")
    print("  • WebSocket streaming")
    print("  • Automatic API documentation (Swagger UI)")
    print("="*80)
    
    # Check dependencies
    print("\nChecking dependencies...")
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first.")
        return 1
    
    print("✅ All dependencies available")
    
    # Setup environment
    host, port, reload = setup_environment()
    
    print("\nPress Enter to start the server...")
    input()
    
    try:
        import uvicorn
        
        print("\n" + "="*80)
        print("Starting FastAPI Server...")
        print("="*80)
        
        # Run server
        uvicorn.run(
            "src.api.main:app",
            host=host,
            port=int(port),
            reload=reload,
            log_level="info"
        )
        
        print("\n✅ Server stopped gracefully")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠ Server interrupted by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error starting server: {str(e)}")
        logger.exception("Server error")
        return 1


if __name__ == "__main__":
    sys.exit(main())
