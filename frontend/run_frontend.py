#!/usr/bin/env python3
"""
Frontend runner for Weather Outfit AI
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run the Streamlit frontend."""
    # Get the directory of this script
    frontend_dir = Path(__file__).parent
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Run streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "app.py",
        "--server.address", "0.0.0.0",
        "--server.port", "8501",
        "--browser.gatherUsageStats", "false"
    ]
    
    print("🚀 Starting Weather Outfit AI Frontend...")
    print("📱 Frontend will be available at: http://localhost:8501")
    print("🔧 Make sure the FastAPI backend is running at: http://localhost:8000")
    print("---")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Frontend stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting frontend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
