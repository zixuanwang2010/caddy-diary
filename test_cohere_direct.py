#!/usr/bin/env python3
"""
Direct test of Cohere API
"""

import requests
import json

# Your API key
COHERE_API_KEY = "Rh7i8fxeE7zWaHxnpjQgvNZZBdtKegafsFM2wQgH"

def test_cohere_direct():
    """Test Cohere API directly"""
    print("🧪 Testing Cohere API directly...")
    
    test_text = "Answer 1: Today im feeling fine. Answer 2: The highlight was getting my new hockey shoes. Answer 3: The challenges I faced were when my dad crashed out on me. Answer 4: Im looking forward to nothing tommorow. Answer 5: I would like to improve my muscle mass."
    
    try:
        # Cohere API endpoint for summarization
        url = "https://api.cohere.ai/v1/summarize"
        
        headers = {
            "Authorization": f"Bearer {COHERE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Prepare the request data
        data = {
            "text": test_text,
            "length": "medium",
            "format": "paragraph",
            "model": "summarize-xlarge",
            "additional_command": "Write this as a natural, diary-style summary that addresses the person in second person (you). Make it warm and reflective."
        }
        
        print(f"[DEBUG] Sending request to Cohere API...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"[DEBUG] Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            summary = result.get('summary', '')
            print(f"✅ Cohere API working!")
            print(f"Summary: {summary}")
            return True
        else:
            print(f"❌ Cohere API error: {response.status_code}")
            print(f"Error details: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error with Cohere API: {str(e)}")
        return False

if __name__ == "__main__":
    test_cohere_direct() 