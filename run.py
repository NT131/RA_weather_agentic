#!/usr/bin/env python3
"""
Main runner script for Weather Outfit AI.
Provides easy access to both CLI and web interfaces.
"""
import argparse
import asyncio
import sys

def main():
    parser = argparse.ArgumentParser(description="Weather Outfit AI")
    parser.add_argument(
        "mode",
        choices=["cli", "web", "frontend", "chat", "recommend"],
        help="Mode to run: 'cli' for interactive CLI, 'web' for FastAPI server, 'frontend' for Streamlit UI, 'chat' for CLI chat, 'recommend' for single recommendation"
    )
    parser.add_argument("--message", "-m", help="Message for single recommendation mode")
    parser.add_argument("--location", "-l", help="Location for weather data")
    parser.add_argument("--context", "-c", help="Additional context")
    parser.add_argument("--port", "-p", type=int, default=8000, help="Port for web server (default: 8000)")
    parser.add_argument("--host", default="0.0.0.0", help="Host for web server (default: 0.0.0.0)")
    parser.add_argument("--frontend-port", type=int, default=8501, help="Port for frontend server (default: 8501)")

    args = parser.parse_args()

    if args.mode == "web":
        # Run FastAPI server
        import uvicorn
        from weather_outfit_ai.config import config
        
        config.validate()
        print("🌤️ Starting Weather Outfit AI web server...")
        print(f"Server will be available at: http://{args.host}:{args.port}")
        print(f"API documentation: http://{args.host}:{args.port}/docs")
        
        uvicorn.run(
            "weather_outfit_ai.app:app",
            host=args.host,
            port=args.port,
            reload=False,
            log_level="info"
        )
    
    elif args.mode == "frontend":
        # Run Streamlit frontend
        import subprocess
        import os
        from pathlib import Path
        
        frontend_dir = Path(__file__).parent / "frontend"
        if not frontend_dir.exists():
            print("❌ Frontend directory not found")
            sys.exit(1)
        
        print("🚀 Starting Weather Outfit AI Frontend...")
        print(f"📱 Frontend will be available at: http://{args.host}:{args.frontend_port}")
        print("🔧 Make sure the FastAPI backend is running at: http://localhost:8000")
        print("---")
        
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(frontend_dir / "app.py"),
            "--server.address", args.host,
            "--server.port", str(args.frontend_port),
            "--browser.gatherUsageStats", "false"
        ]
        
        try:
            subprocess.run(cmd, check=True)
        except KeyboardInterrupt:
            print("\n👋 Frontend stopped")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error starting frontend: {e}")
            print("💡 Make sure Streamlit is installed: pip install streamlit")
            sys.exit(1)
    
    elif args.mode == "cli" or args.mode == "chat":
        # Run CLI interface
        from weather_outfit_ai.cli import app as cli_app
        
        if args.mode == "chat":
            # Direct to chat command
            cli_app(["chat"])
        else:
            cli_app()
    
    elif args.mode == "recommend":
        # Single recommendation
        if not args.message:
            print("Error: --message (-m) is required for recommend mode")
            sys.exit(1)
        
        from weather_outfit_ai.cli import app as cli_app
        
        cmd_args = ["recommend", args.message]
        if args.location:
            cmd_args.extend(["--location", args.location])
        if args.context:
            cmd_args.extend(["--context", args.context])
        
        cli_app(cmd_args)

if __name__ == "__main__":
    main()
