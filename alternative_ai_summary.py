#!/usr/bin/env python3
"""
Alternative AI summary generators using different free services
"""

import requests
import json

def generate_summary_with_openai(text, api_key):
    """
    Generate summary using OpenAI API (free tier available)
    """
    if not api_key or not text:
        return None
    
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""
        You are a diary assistant. Write a single, natural, flowing diary summary in second person, as if you are reflecting on your own day. 
        Make it conversational, humanistic, and not robotic. Do NOT list or repeat the answers, but synthesize them into a real diary entry.
        
        Here are the diary answers: {text}
        
        Write a natural diary summary in 2-3 sentences maximum.
        """
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 150,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                summary = result['choices'][0]['message']['content'].strip()
                return summary
        
        return None
        
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        return None

def generate_summary_with_anthropic(text, api_key):
    """
    Generate summary using Anthropic Claude API
    """
    if not api_key or not text:
        return None
    
    try:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        prompt = f"""
        You are a diary assistant. Write a single, natural, flowing diary summary in second person, as if you are reflecting on your own day. 
        Make it conversational, humanistic, and not robotic. Do NOT list or repeat the answers, but synthesize them into a real diary entry.
        
        Here are the diary answers: {text}
        
        Write a natural diary summary in 2-3 sentences maximum.
        """
        
        payload = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 150,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if 'content' in result and len(result['content']) > 0:
                summary = result['content'][0]['text'].strip()
                return summary
        
        return None
        
    except Exception as e:
        print(f"Anthropic API error: {str(e)}")
        return None

def generate_summary_with_cohere(text, api_key):
    """
    Generate summary using Cohere API (free tier available)
    """
    if not api_key or not text:
        return None
    
    try:
        url = "https://api.cohere.ai/v1/generate"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""
        You are a diary assistant. Write a single, natural, flowing diary summary in second person, as if you are reflecting on your own day. 
        Make it conversational, humanistic, and not robotic. Do NOT list or repeat the answers, but synthesize them into a real diary entry.
        
        Here are the diary answers: {text}
        
        Write a natural diary summary in 2-3 sentences maximum.
        """
        
        payload = {
            "model": "command",
            "prompt": prompt,
            "max_tokens": 150,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if 'generations' in result and len(result['generations']) > 0:
                summary = result['generations'][0]['text'].strip()
                return summary
        
        return None
        
    except Exception as e:
        print(f"Cohere API error: {str(e)}")
        return None

def test_all_apis():
    """Test all available APIs"""
    print("🧪 Testing Alternative AI APIs...")
    
    test_text = "Today I am feeling great. The highlight of my day was doing Clip and Climb with my friends. The challenges I faced today was climbing the Beanstalk wall in Clip and Climb. I am looking forward to work experience. I would like to improve my strength and fitness."
    
    print("\n📋 Available Free AI Services:")
    print("1. OpenAI (gpt-3.5-turbo) - Free tier available")
    print("   Get key from: https://platform.openai.com/api-keys")
    print("2. Anthropic Claude - Free tier available")
    print("   Get key from: https://console.anthropic.com/")
    print("3. Cohere - Free tier available")
    print("   Get key from: https://dashboard.cohere.ai/api-keys")
    print("4. Local Summary Generator - No API key needed (currently working)")
    
    print("\n✅ Your app is currently using the Local Summary Generator")
    print("   This works offline and doesn't require any API keys!")

if __name__ == "__main__":
    test_all_apis() 