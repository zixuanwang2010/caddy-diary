import subprocess
import sys
import time
import threading
import os

def run_app(app_file, port):
    """Run a Flask app on the specified port"""
    try:
        subprocess.run([sys.executable, app_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {app_file}: {e}")
    except KeyboardInterrupt:
        print(f"\nStopping {app_file}...")

def main():
    print("Starting Digital Diary Applications...")
    print("=" * 50)
    print("Main App (Manual Entry): http://localhost:5000")
    print("Phone App (Voice Recording): http://localhost:5001")
    print("=" * 50)
    print("Press Ctrl+C to stop both applications")
    print()
    
    # Start both apps in separate threads
    app1_thread = threading.Thread(target=run_app, args=('app.py', 5000))
    app2_thread = threading.Thread(target=run_app, args=('phone_app.py', 5001))
    
    try:
        app1_thread.start()
        time.sleep(2)  # Give first app time to start
        app2_thread.start()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down applications...")
        sys.exit(0)

if __name__ == "__main__":
    main() 