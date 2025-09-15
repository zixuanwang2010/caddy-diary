#!/usr/bin/env python3
"""
Startup script for the Flask Diary Application
"""

import os
import sys
from app import app

def main():
    """Start the Flask application"""
    print("Starting Flask Diary Application...")
    print("=" * 40)
    
    # Set environment variables if not already set
    if not os.getenv('SECRET_KEY'):
        os.environ['SECRET_KEY'] = 'your-secret-key-here'
        print("✓ Set default secret key")
    
    # Check if required directories exist
    static_dir = os.path.join(app.root_path, 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        print("✓ Created static directory")
    
    # Print configuration info
    print(f"✓ Flask app configured")
    print(f"✓ Debug mode: {app.config['DEBUG']}")
    print(f"✓ Secret key: {'Set' if app.secret_key else 'Not set'}")
    
    # Start the application
    print("\nStarting server...")
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 40)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 