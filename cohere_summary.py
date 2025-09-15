#!/usr/bin/env python3
"""
Cohere API integration for text summarization and advice generation
"""

import requests
import json

# Use the working API key directly
COHERE_API_KEY = "Rh7i8fxeE7zWaHxnpjQgvNZZBdtKegafsFM2wQgH"

def expand_text_for_cohere(text):
    """
    Expand short text to meet Cohere's minimum character requirement (250+ chars)
    """
    if len(text) >= 250:
        return text
    
    # If text is too short, expand it by adding context
    expanded_text = f"""
    Here is a diary entry with multiple answers to daily reflection questions:
    
    {text}
    
    This represents a person's daily reflection covering their mood, highlights, challenges, future plans, and personal goals. Please provide a natural, warm summary of their day.
    """
    
    return expanded_text.strip()

def generate_summary_with_cohere(text):
    """
    Generate a summary using Cohere's API
    """
    if not text or text.strip() == "":
        return "You reflected on your day."
    
    if not COHERE_API_KEY:
        print("[DEBUG] No Cohere API key found, using fallback")
        return None
    
    try:
        # Expand text if it's too short for Cohere
        expanded_text = expand_text_for_cohere(text)
        print(f"[DEBUG] Original text length: {len(text)} chars")
        print(f"[DEBUG] Expanded text length: {len(expanded_text)} chars")
        
        # Cohere API endpoint for summarization
        url = "https://api.cohere.ai/v1/summarize"
        
        headers = {
            "Authorization": f"Bearer {COHERE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Prepare the request data
        data = {
            "text": expanded_text,
            "length": "medium",  # Options: short, medium, long
            "format": "paragraph",
            "model": "summarize-xlarge",
            "additional_command": "Write this as a natural, diary-style summary that addresses the person in second person (you). Make it warm and reflective."
        }
        
        print(f"[DEBUG] Sending request to Cohere API...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            summary = result.get('summary', '')
            print(f"[DEBUG] Cohere API response: {summary}")
            return summary
        else:
            print(f"[DEBUG] Cohere API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"[DEBUG] Error with Cohere API: {str(e)}")
        return None

def generate_advice_with_cohere(summary, sentiment):
    """
    Generate personalized advice using Cohere's API based on the summary and sentiment
    """
    if not summary or not COHERE_API_KEY:
        print("[DEBUG] No summary or Cohere API key available for advice generation")
        return None
    
    try:
        # Create a prompt for advice generation
        sentiment_mood = "positive" if "positive" in sentiment.lower() else "negative" if "negative" in sentiment.lower() else "neutral"
        
        advice_prompt = f"""
        Based on this diary summary: "{summary}"
        
        And the person's mood being {sentiment_mood}, provide specific, actionable advice in 1-2 sentences that directly addresses what they shared. 
        
        Make the advice:
        - Personal and encouraging
        - Specific to their situation
        - Actionable and practical
        - Warm and supportive in tone
        - Focused on growth and improvement
        
        Keep it concise but meaningful.
        """
        
        # Use Cohere's generate endpoint for advice
        url = "https://api.cohere.ai/v1/generate"
        
        headers = {
            "Authorization": f"Bearer {COHERE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "command",
            "prompt": advice_prompt,
            "max_tokens": 100,
            "temperature": 0.7,
            "k": 0,
            "stop_sequences": ["\n\n", "###"],
            "return_likelihoods": "NONE"
        }
        
        print(f"[DEBUG] Sending advice request to Cohere API...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'generations' in result and len(result['generations']) > 0:
                advice = result['generations'][0]['text'].strip()
                print(f"[DEBUG] Cohere advice response: {advice}")
                return advice
        else:
            print(f"[DEBUG] Cohere API error for advice: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"[DEBUG] Error with Cohere advice generation: {str(e)}")
        return None

def test_cohere_summary():
    """Test the Cohere summary generator"""
    print("🧪 Testing Cohere Summary Generator...")
    
    # Test with short text (like your actual diary entry)
    test_text = "Answer 1: Today I'm feeling pretty good.. Answer 2: opening my new hockey shoes. Answer 3: Making a joke about my dad and he go angry at me. Answer 4: I'm not really looking forward to anything.. Answer 5: I would like to improve my math skills.."
    
    result = generate_summary_with_cohere(test_text)
    
    if result:
        print(f"✅ Cohere summary: {result}")
    else:
        print("❌ Cohere API not available or failed")
    
    return result

def test_cohere_advice():
    """Test the Cohere advice generator"""
    print("🧪 Testing Cohere Advice Generator...")
    
    # Test with a sample summary and sentiment
    test_summary = "You had a mixed day today. You were feeling good and excited about your new hockey shoes, but there was some tension with your dad over a joke. You're also thinking about improving your math skills."
    test_sentiment = "Overall mood: Neutral (sentiment score: 0.1)"
    
    result = generate_advice_with_cohere(test_summary, test_sentiment)
    
    if result:
        print(f"✅ Cohere advice: {result}")
    else:
        print("❌ Cohere advice generation failed")
    
    return result

if __name__ == "__main__":
    test_cohere_summary()
    print("\n" + "="*50 + "\n")
    test_cohere_advice() 