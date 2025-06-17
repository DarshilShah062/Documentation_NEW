#!/usr/bin/env python3
"""
CricBattle Document Management System
Main entry point for the application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import streamlit
        import openai
        import pinecone
        import langchain
        import watchdog
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        return False

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✅ Requirements installed successfully")

def create_documentation_folder():
    """Create Documentation folder if it doesn't exist"""
    doc_folder = Path("Documentation")
    if not doc_folder.exists():
        doc_folder.mkdir()
        print("✅ Created Documentation folder")
    
    # Create a sample file if folder is empty
    if not list(doc_folder.glob("*.md")):
        sample_content = """# Welcome to CricBattle Documentation

This is a sample document to get you started.

## Features

- Upload markdown files
- Automatic processing
- Vector embeddings
- Pinecone integration

## Getting Started

1. Add your markdown files to the Documentation folder
2. Use the web interface to manage documents
3. The system will automatically process new files

Happy documenting! 🏏
"""
        with open(doc_folder / "welcome.md", "w") as f:
            f.write(sample_content)
        print("✅ Created sample welcome.md file")

def main():
    """Main application entry point"""
    print("🏏 CricBattle Document Management System")
    print("=" * 50)
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return
    
    # Check and install requirements
    if not check_requirements():
        try:
            install_requirements()
        except Exception as e:
            print(f"❌ Failed to install requirements: {e}")
            return
    
    # Check environment variables
    if not os.path.exists(".env"):
        print("❌ .env file not found. Please create it with your API keys.")
        return
    
    # Create documentation folder
    create_documentation_folder()
    
    # Launch Streamlit app
    print("🚀 Launching Streamlit application...")
    print("📊 Dashboard will open in your browser")
    print("🔗 URL: http://localhost:8501")
    print("\n💡 Tips:")
    print("   - Add .md files to the Documentation folder")
    print("   - Enable auto-watch for automatic processing")
    print("   - Use the web interface to manage documents")
    print("\n🛑 Press Ctrl+C to stop the application")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped")

if __name__ == "__main__":
    main()
