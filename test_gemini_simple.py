#!/usr/bin/env python3
"""
Simple test script for Gemini API
"""

from gemini_summary import generate_summary_with_gemini

def test_gemini():
    """Test Gemini API with a sample request"""
    print("🧪 Testing Google Gemini API...")
    
    # Test with empty API key first
    test_text = "Today I am feeling great. The highlight of my day was doing Clip and Climb with my friends. The challenges I faced today was climbing the Beanstalk wall in Clip and Climb. I am looking forward to work experience. I would like to improve my strength and fitness."
    
    print("Testing with empty API key (should fail gracefully)...")
    result = generate_summary_with_gemini(test_text, "")
    
    if result is None:
        print("✅ Correctly handled empty API key")
    else:
        print(f"❌ Unexpected result with empty key: {result}")
    
    print("\nTo test with a real API key:")
    print("1. Get a free API key from: https://makersuite.google.com/app/apikey")
    print("2. Add it to config.py as GEMINI_API_KEY")
    print("3. Run your diary app - it will automatically use Gemini!")

if __name__ == "__main__":
    test_gemini() 