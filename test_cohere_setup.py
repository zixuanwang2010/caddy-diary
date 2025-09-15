#!/usr/bin/env python3
"""
Test script to help set up Cohere API
"""

def get_cohere_api_key():
    """Instructions for getting Cohere API key"""
    print("🔑 How to get your Cohere API key:")
    print("1. Go to https://cohere.ai/")
    print("2. Sign up for a free account")
    print("3. Go to your dashboard")
    print("4. Copy your API key")
    print("5. Add it to config.py: COHERE_API_KEY = 'your-key-here'")
    print("\n📝 Free tier includes:")
    print("- 5 requests per minute")
    print("- Good quality summaries")
    print("- No credit card required")
    
    return input("\nEnter your Cohere API key (or press Enter to skip): ").strip()

def test_cohere_connection():
    """Test if Cohere API is working"""
    try:
        from cohere_summary import generate_summary_with_cohere
        
        test_text = "Answer 1: Today im feeling fine. Answer 2: The highlight was getting my new hockey shoes. Answer 3: The challenges I faced were when my dad crashed out on me. Answer 4: Im looking forward to nothing tommorow. Answer 5: I would like to improve my muscle mass."
        
        print("🧪 Testing Cohere connection...")
        result = generate_summary_with_cohere(test_text)
        
        if result:
            print("✅ Cohere API is working!")
            print(f"Summary: {result}")
            return True
        else:
            print("❌ Cohere API failed or no API key")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Cohere: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Cohere API Setup")
    print("=" * 30)
    
    # Check if API key exists
    try:
        from config import COHERE_API_KEY
        if COHERE_API_KEY:
            print(f"✅ API key found: {COHERE_API_KEY[:10]}...")
            test_cohere_connection()
        else:
            print("❌ No API key found in config.py")
            new_key = get_cohere_api_key()
            if new_key:
                print("📝 Add this to your config.py:")
                print(f"COHERE_API_KEY = '{new_key}'")
    except ImportError:
        print("❌ Could not import config.py")
        get_cohere_api_key() 