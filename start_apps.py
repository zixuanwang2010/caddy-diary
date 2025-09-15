#!/usr/bin/env python3
"""
Caddy Diary - App Startup Script
This script helps you start both the main diary app and the phone app.
"""

import subprocess
import sys
import time
import threading
import os
import webbrowser
from pathlib import Path

def print_banner():
    """Print a nice banner for the app startup"""
    print("=" * 60)
    print("🎉 Welcome to Caddy Diary! 🎉")
    print("=" * 60)
    print("Starting your AI-powered diary applications...")
    print()

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import whisper
        print("✅ All dependencies are installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def run_app(app_file, port, name):
    """Run a Flask app on the specified port"""
    try:
        print(f"🚀 Starting {name} on port {port}...")
        subprocess.run([sys.executable, app_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {name}: {e}")
    except KeyboardInterrupt:
        print(f"\n🛑 Stopping {name}...")

def open_browser():
    """Open the landing page in the default browser"""
    time.sleep(3)  # Wait for apps to start
    try:
        print("🌐 Opening landing page in your browser...")
        webbrowser.open('http://localhost:5000')
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("Please manually open: http://localhost:5000")

def main():
    """Main function to start both apps"""
    print_banner()
    
    if not check_dependencies():
        return
    
    print("📱 App URLs:")
    print("   • Landing Page: http://localhost:5000")
    print("   • Try It Out:   http://localhost:5001")
    print("   • Manual Entry: http://localhost:5000/diary")
    print()
    print("💡 Tip: Click 'Try It Out' on the landing page to experience both options!")
    print()
    print("Press Ctrl+C to stop both applications")
    print("-" * 60)
    
    # Start both apps in separate threads
    app1_thread = threading.Thread(target=run_app, args=('app.py', 5000, 'Main App'))
    app2_thread = threading.Thread(target=run_app, args=('phone_app.py', 5001, 'Phone App'))
    browser_thread = threading.Thread(target=open_browser)
    
    try:
        app1_thread.start()
        time.sleep(2)  # Give first app time to start
        app2_thread.start()
        browser_thread.start()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down applications...")
        print("Thank you for using Caddy Diary! 👋")
        sys.exit(0)

if __name__ == "__main__":
    main() 