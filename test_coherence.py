#!/usr/bin/env python3
"""
Test script to verify all configurations are coherent
"""

def test_config_imports():
    """Test that all config imports work correctly"""
    print("Testing configuration imports...")
    print("=" * 50)
    
    try:
        # Test config.py imports
        from config import BLAND_API_KEY, ELEVENLABS_API_KEY
        print("✅ config.py imports successful")
        print(f"   BLAND_API_KEY: {'Set' if BLAND_API_KEY else 'Not set'}")
        print(f"   ELEVENLABS_API_KEY: {'Set' if ELEVENLABS_API_KEY else 'Not set'}")
    except ImportError as e:
        print(f"❌ config.py import failed: {e}")
        return False
    
    try:
        # Test questions.py imports
        from questions import questions, QUESTIONS
        print("✅ questions.py imports successful")
        print(f"   Daily questions count: {len(questions)}")
        print(f"   Conversational questions count: {len(QUESTIONS)}")
    except ImportError as e:
        print(f"❌ questions.py import failed: {e}")
        return False
    
    try:
        # Test phone_call.py imports
        from phone_call import start_call_test
        print("✅ phone_call.py imports successful")
    except ImportError as e:
        print(f"❌ phone_call.py import failed: {e}")
        return False
    
    try:
        # Test app.py imports (basic ones)
        from app import app
        print("✅ app.py imports successful")
    except ImportError as e:
        print(f"❌ app.py import failed: {e}")
        return False
    
    return True

def test_phone_call_functionality():
    """Test phone call functionality"""
    print("\nTesting phone call functionality...")
    print("=" * 50)
    
    try:
        from phone_call import start_call_test
        result = start_call_test()
        print(f"Phone call test result: {result}")
        
        if result.get('success'):
            print("✅ Phone call test successful")
        else:
            print(f"⚠️  Phone call test failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Phone call test exception: {e}")

def main():
    print("Digital Diary Configuration Coherence Test")
    print("=" * 60)
    
    # Test imports
    if test_config_imports():
        print("\n✅ All imports successful!")
    else:
        print("\n❌ Some imports failed!")
        return
    
    # Test phone call
    test_phone_call_functionality()
    
    print("\n" + "=" * 60)
    print("Configuration coherence test completed!")
    print("\nTo run your applications:")
    print("  Main app: python app.py")
    print("  Phone app: python phone_app.py")
    print("  Both apps: python run_apps.py")

if __name__ == "__main__":
    main() 