#!/usr/bin/env python3
"""
Setup and run script for Caddy Diary with user authentication
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required Python packages"""
    print("Installing required dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    return True

def create_database():
    """Create the database and tables"""
    print("Setting up database...")
    try:
        from app import app, db
        with app.app_context():
            db.create_all()
            print("✅ Database created successfully!")
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False
    return True

def main():
    print("🚀 Setting up Caddy Diary with User Authentication")
    print("=" * 50)
    
    # Install dependencies
    if not install_dependencies():
        print("Failed to install dependencies. Exiting.")
        return
    
    # Create database
    if not create_database():
        print("Failed to create database. Exiting.")
        return
    
    print("\n🎉 Setup complete! Starting the application...")
    print("=" * 50)
    print("📱 The app will be available at: http://localhost:5000")
    print("🔐 Sign up at: http://localhost:5000/signup")
    print("📝 Start writing at: http://localhost:5000/diary")
    print("=" * 50)
    
    # Run the app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"❌ Error running app: {e}")

if __name__ == "__main__":
    main()
