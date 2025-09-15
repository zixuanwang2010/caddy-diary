import os
import requests
from dotenv import load_dotenv
from config import BLAND_API_KEY

# Load environment variables
load_dotenv()

# Voice settings for phone call
VOICE_ID = "clara"  # Clear, professional voice

BLAND_API_URL = "https://api.bland.ai/v1/calls"

def make_phone_call(phone_number, diary_content):
    """Make a phone call using Bland AI with actual diary content"""
    try:
        if not BLAND_API_KEY:
            return {'error': 'BLAND_API_KEY not found. Please set your Bland AI API key in environment variables.'}
        
        # Create a personalized message based on the diary content
        if diary_content and diary_content.strip():
            message = f"Here's your daily diary summary: {diary_content}"
        else:
            message = "You haven't completed your diary entry yet. Please go back and answer the questions to get your personalized summary."
        
        headers = {
            "Authorization": f"Bearer {BLAND_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "phone_number": phone_number,
            "task": message,
            "voice_id": VOICE_ID
        }
        print(f"Making API call to Bland AI with phone number: {phone_number}")
        print(f"Message content: {message[:100]}...")  # Log first 100 chars
        response = requests.post(BLAND_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"API call successful: {result}")
            return result
        else:
            print(f"API call failed with status {response.status_code}: {response.text}")
            return {'error': f'API call failed: {response.status_code} - {response.text}'}
    except Exception as e:
        print(f"Error making phone call: {str(e)}")
        return {'error': f'Exception occurred: {str(e)}'}

def start_call_test(phone_number=None, diary_content=None):
    try:
        if not phone_number:
            phone_number = '0000000000'
        
        print(f"Starting call with phone number: {phone_number}")
        print(f"Diary content provided: {diary_content[:100] if diary_content else 'None'}...")
        
        result = make_phone_call(phone_number, diary_content)
        if result and 'error' not in result:
            return {'success': True, 'call_id': result.get('call_id'), 'message': 'Call initiated successfully'}
        else:
            error_msg = result.get('error', 'Unknown error occurred') if result else 'No response from API'
            return {'success': False, 'error': error_msg}
    except Exception as e:
        print(f"Exception in start_call_test: {str(e)}")
        return {'success': False, 'error': str(e)} 