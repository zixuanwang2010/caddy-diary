#!/usr/bin/env python3
"""
Test script for phone call functionality
"""

import os
from phone_call import start_call_test

def test_phone_call():
    print("Testing phone call functionality...")
    print("=" * 50)
    
    # Check environment variables
    bland_api_key = os.getenv('BLAND_API_KEY')
    print(f"BLAND_API_KEY set: {'Yes' if bland_api_key else 'No'}")
    
    if bland_api_key:
        print(f"API Key (first 10 chars): {bland_api_key[:10]}...")
    else:
        print("⚠️  BLAND_API_KEY not found in environment variables")
        print("   Please set it using: export BLAND_API_KEY='your_api_key'")
        print("   Or add it to your .env file")
    
    print("\n" + "=" * 50)
    print("Testing phone call...")
    
    # Test the phone call
    result = start_call_test()
    
    print(f"\nResult: {result}")
    
    if result.get('success'):
        print("✅ Phone call test successful!")
        if result.get('call_id'):
            print(f"Call ID: {result['call_id']}")
        else:
            print("⚠️  No call ID returned")
    else:
        print("❌ Phone call test failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_phone_call() 