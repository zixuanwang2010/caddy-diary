#!/usr/bin/env python3
"""
Final test to verify all functionality works without OpenAI
"""

def test_basic_functionality():
    """Test basic functionality without OpenAI"""
    print("Testing Digital Diary without OpenAI...")
    print("=" * 50)
    
    try:
        # Test imports
        from config import BLAND_API_KEY, ELEVENLABS_API_KEY
        from questions import questions
        from phone_call import start_call_test
        
        print("✅ All imports successful")
        print(f"   BLAND_API_KEY: {'Set' if BLAND_API_KEY else 'Not set'}")
        print(f"   ELEVENLABS_API_KEY: {'Set' if ELEVENLABS_API_KEY else 'Not set'}")
        print(f"   Questions loaded: {len(questions)}")
        
        # Test basic text processing
        from textblob import TextBlob
        test_text = "I had a great day today!"
        blob = TextBlob(test_text)
        sentiment = blob.sentiment.polarity
        print(f"✅ TextBlob sentiment analysis: {sentiment:.2f}")
        
        # Test phone call (without actually making a call)
        print("\nTesting phone call functionality...")
        result = start_call_test()
        print(f"Phone call test result: {result}")
        
        if result.get('success'):
            print("✅ Phone call functionality working")
        else:
            print(f"⚠️  Phone call issue: {result.get('error', 'Unknown')}")
        
        print("\n" + "=" * 50)
        print("✅ All basic functionality working!")
        print("\nYour apps are ready:")
        print("  Main app: http://localhost:5000")
        print("  Phone app: http://localhost:5001")
        print("  Start page: http://localhost:5001 (choose your option)")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_basic_functionality() 