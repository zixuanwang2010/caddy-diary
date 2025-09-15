#!/usr/bin/env python3
"""
Simple test script to verify the Flask application works correctly.
"""

import sys
import os
import requests
import time

def test_app_startup():
    """Test that the app can be imported and basic functionality works"""
    try:
        # Import the app
        from app import app
        
        print("✓ App imported successfully")
        
        # Test basic configuration
        assert app.secret_key is not None, "Secret key should be set"
        print("✓ Secret key configured")
        
        # Test that questions are loaded
        from questions import questions
        assert len(questions) > 0, "Questions should be loaded"
        print(f"✓ {len(questions)} questions loaded")
        
        # Test API keys are loaded
        from config import ELEVENLABS_API_KEY, HUGGINGFACE_API_KEY
        assert ELEVENLABS_API_KEY is not None, "ElevenLabs API key should be loaded"
        assert HUGGINGFACE_API_KEY is not None, "HuggingFace API key should be loaded"
        print("✓ API keys loaded")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during startup test: {e}")
        return False

def test_basic_routes():
    """Test basic route functionality"""
    try:
        from app import app
        
        with app.test_client() as client:
            # Test home route
            response = client.get('/')
            assert response.status_code == 200, "Home route should return 200"
            print("✓ Home route works")
            
            # Test questions route
            response = client.get('/index?question_id=0')
            assert response.status_code == 200, "Questions route should return 200"
            print("✓ Questions route works")
            
            # Test debug session route
            response = client.get('/debug_session')
            assert response.status_code == 200, "Debug session route should return 200"
            print("✓ Debug session route works")
            
        return True
        
    except Exception as e:
        print(f"✗ Error during route test: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available"""
    try:
        import flask
        import whisper
        import requests
        import soundfile
        import torch
        import textblob
        import nltk
        import whisper
        from dotenv import load_dotenv
        
        print("✓ All required dependencies are available")
        return True
        
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Flask Diary Application...")
    print("=" * 40)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("App Startup", test_app_startup),
        ("Basic Routes", test_basic_routes),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        if test_func():
            passed += 1
            print(f"✓ {test_name} test passed")
        else:
            print(f"✗ {test_name} test failed")
    
    print("\n" + "=" * 40)
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! The application should work correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 