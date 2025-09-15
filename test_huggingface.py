#!/usr/bin/env python3
"""
Test script for Hugging Face API integration
"""

def test_huggingface_api():
    """Test Hugging Face API functionality"""
    print("Testing Hugging Face API Integration...")
    print("=" * 50)
    
    try:
        from config import HUGGINGFACE_API_KEY
        import requests
        
        if not HUGGINGFACE_API_KEY:
            print("⚠️  HUGGINGFACE_API_KEY not set")
            print("   Please set it using: $env:HUGGINGFACE_API_KEY='your_api_key'")
            return False
        
        print(f"✅ HUGGINGFACE_API_KEY found: {HUGGINGFACE_API_KEY[:10]}...")
        
        # Test sentiment analysis
        print("\nTesting sentiment analysis...")
        test_text = "I had a wonderful day today!"
        API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        
        response = requests.post(API_URL, headers=headers, json={"inputs": test_text})
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sentiment analysis working: {result}")
        else:
            print(f"❌ Sentiment analysis failed: {response.status_code} - {response.text}")
        
        # Test summarization
        print("\nTesting summarization...")
        test_text = "Today I went to the park and had a picnic with my friends. The weather was beautiful and we played games. It was a really fun day."
        API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        
        response = requests.post(API_URL, headers=headers, json={"inputs": test_text})
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Summarization working: {result}")
        else:
            print(f"❌ Summarization failed: {response.status_code} - {response.text}")
        
        print("\n" + "=" * 50)
        print("✅ Hugging Face API integration test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_huggingface_api() 