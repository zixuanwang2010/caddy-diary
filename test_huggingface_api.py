#!/usr/bin/env python3
"""
Test script to verify HuggingFace API key and BART-CNN model are working.
Run this to check if your API key is valid and the model can generate summaries.
"""

import requests
import json

# Import your config
from config import HUGGINGFACE_API_KEY

def test_huggingface_api():
    """Test the HuggingFace API with multiple models"""
    
    if not HUGGINGFACE_API_KEY:
        print("❌ No HuggingFace API key found in config.py")
        return False
    
    print(f"🔑 Testing API key: {HUGGINGFACE_API_KEY[:10]}...")
    
    # Test with multiple models
    models_to_test = [
        "facebook/bart-large-cnn",
        "sshleifer/distilbart-cnn-12-6",  # Alternative summarization model
        "gpt2"  # Simple text generation model
    ]
    
    test_text = "Today I am feeling great. The highlight of my day was doing Clip and Climb with my friends."
    
    for model_name in models_to_test:
        print(f"\n🧪 Testing model: {model_name}")
        print("=" * 50)
        
        API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        
        try:
            if "bart" in model_name.lower() or "distilbart" in model_name.lower():
                # Summarization models
                payload = {"inputs": test_text, "max_length": 100, "do_sample": True, "temperature": 0.7}
            else:
                # Text generation models
                payload = {"inputs": test_text, "max_length": 100, "temperature": 0.7}
            
            print(f"📝 Test text: {test_text}")
            print("🔄 Sending request to HuggingFace API...")
            
            response = requests.post(API_URL, headers=headers, json=payload)
            
            print(f"📊 Response status: {response.status_code}")
            print(f"📄 Response text: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    if 'summary_text' in result[0]:
                        summary = result[0]['summary_text']
                        print(f"✅ SUCCESS! Generated summary: {summary}")
                        return True
                    elif 'generated_text' in result[0]:
                        generated = result[0]['generated_text']
                        print(f"✅ SUCCESS! Generated text: {generated}")
                        return True
                    else:
                        print(f"✅ SUCCESS! Response: {result[0]}")
                        return True
                else:
                    print("❌ Unexpected response format")
                    print(f"Response JSON: {json.dumps(result, indent=2)}")
            elif response.status_code == 401:
                print("❌ 401 Unauthorized - Invalid API key")
                print("This means your API key is not working with ANY model")
                return False
            elif response.status_code == 503:
                print("⚠️ 503 Service Unavailable - Model is loading")
                print("This is normal for the first request. Try again in a few seconds.")
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error making request: {str(e)}")
    
    return False

def test_account_status():
    """Test if the account itself is working"""
    print("\n🔍 Testing account status...")
    
    if not HUGGINGFACE_API_KEY:
        return False
    
    # Test with a simple model info request
    API_URL = "https://huggingface.co/api/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    
    try:
        response = requests.get(API_URL, headers=headers)
        print(f"Account test status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Account access is working")
            return True
        else:
            print(f"❌ Account test failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Account test error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing HuggingFace API with multiple models...")
    print("=" * 60)
    
    # First test account status
    account_ok = test_account_status()
    
    # Then test models
    success = test_huggingface_api()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 API test successful! Your setup should work with the diary app.")
    else:
        print("💥 API test failed. Here are possible issues:")
        print("1. Your API key is invalid or expired")
        print("2. Your HuggingFace account has restrictions")
        print("3. You need to verify your email address")
        print("4. Your account needs billing information")
        print("\nTry creating a new token or check your account status.") 