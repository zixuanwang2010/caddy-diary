#!/usr/bin/env python3
"""
Alternative summary generator using Google Gemini API
This is free and doesn't require complex setup like HuggingFace
"""

import requests
import json

def generate_summary_with_gemini(text, api_key):
    """
    Generate a diary summary using Google Gemini API
    """
    if not api_key or not text:
        return "You reflected on your day."
    
    try:
        # Google Gemini API endpoint
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        
        # Create the prompt for diary summary
        prompt = f"""
        You are a diary assistant. Write a single, natural, flowing diary summary in second person, as if you are reflecting on your own day. 
        Make it conversational, humanistic, and not robotic. Do NOT list or repeat the answers, but synthesize them into a real diary entry.
        
        Here are the diary answers: {text}
        
        Write a natural diary summary in 2-3 sentences maximum.
        """
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 150
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Make the request
        response = requests.post(
            f"{url}?key={api_key}",
            headers=headers,
            json=payload
        )
        
        print(f"[DEBUG] Gemini API response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract the generated text
            if 'candidates' in result and len(result['candidates']) > 0:
                content = result['candidates'][0]['content']
                if 'parts' in content and len(content['parts']) > 0:
                    summary = content['parts'][0]['text'].strip()
                    if len(summary) > 20:
                        print(f"[DEBUG] Gemini summary: {summary}")
                        return summary
        
        print(f"[DEBUG] Gemini API failed: {response.text}")
        return None
        
    except Exception as e:
        print(f"[DEBUG] Gemini API error: {str(e)}")
        return None

def test_gemini_api():
    """
    Test the Gemini API with a sample request
    """
    print("🧪 Testing Google Gemini API...")
    
    # You'll need to get a free API key from: https://makersuite.google.com/app/apikey
    api_key = input("Enter your Gemini API key (or press Enter to skip): ").strip()
    
    if not api_key:
        print("No API key provided. Skipping test.")
        return False
    
    test_text = "Today I am feeling great. The highlight of my day was doing Clip and Climb with my friends. The challenges I faced today was climbing the Beanstalk wall in Clip and Climb. I am looking forward to work experience. I would like to improve my strength and fitness."
    
    print("Testing with sample text...")
    result = generate_summary_with_gemini(test_text, api_key)
    
    if result:
        print(f"✅ SUCCESS! Generated summary: {result}")
        return True
    else:
        print("❌ Failed to generate summary")
        return False

if __name__ == "__main__":
    test_gemini_api() 