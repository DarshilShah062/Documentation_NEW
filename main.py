#!/usr/bin/env python3
"""
CricBattle Document Management System
Main entry point for deployment
"""

import os
import sys
import subprocess
from pathlib import Path
import streamlit as st

def check_deployment_environment():
    """Check if running in deployment environment"""
    return (
        os.getenv('STREAMLIT_SHARING_MODE') or 
        'streamlit.io' in os.getenv('HOSTNAME', '') or
        hasattr(st, 'secrets') or
        'STREAMLIT_CLOUD' in os.environ
    )

def main():
    """Main application entry point"""
    if check_deployment_environment():
        # Running in cloud - import streamlit app modules
        print("🚀 Running in Streamlit Cloud environment")
        # The streamlit_app.py will be executed directly by Streamlit Cloud
        pass
    else:
        # Running locally - show startup information and launch app
        print("🏏 CricBattle Document Management System")
        print("=" * 50)
        
        # Check if requirements.txt exists
        if not os.path.exists("requirements.txt"):
            print("❌ requirements.txt not found")
            return
        
        # Check environment variables
        if not os.path.exists(".env") and not hasattr(st, 'secrets'):
            print("❌ .env file not found. Please create it with your API keys.")
            return
        
        print("🚀 Launching Streamlit application...")
        print("📊 Dashboard will open in your browser")
        print("🔗 URL: http://localhost:8501")
        print("\n💡 Tips:")
        print("   - Your documents are stored in Google Drive")
        print("   - Use the web interface to manage documents")
        print("   - All processing is cloud-based")
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
