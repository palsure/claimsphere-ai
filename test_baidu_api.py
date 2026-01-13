#!/usr/bin/env python3
"""
Test script to verify Baidu API credentials
"""
import os
import sys
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.ernie_service import ErnieService


def test_baidu_api():
    """Test Baidu API credentials"""
    print("=" * 60)
    print("Testing Baidu API Credentials")
    print("=" * 60)
    
    # Get credentials from environment
    api_key = os.getenv('BAIDU_API_KEY', '')
    secret_key = os.getenv('BAIDU_SECRET_KEY', '')
    
    if not api_key or not secret_key:
        print("❌ ERROR: BAIDU_API_KEY or BAIDU_SECRET_KEY not found in environment")
        print("\nPlease set these in your .env file:")
        print("  BAIDU_API_KEY=your-api-key")
        print("  BAIDU_SECRET_KEY=your-secret-key")
        return False
    
    print(f"✓ API Key found: {api_key[:8]}...{api_key[-4:]}")
    print(f"✓ Secret Key found: {secret_key[:4]}...{secret_key[-4:]}")
    print()
    
    # Initialize service
    print("Initializing ERNIE Service...")
    try:
        ernie_service = ErnieService(api_key=api_key, secret_key=secret_key)
        print("✓ ERNIE Service initialized")
    except Exception as e:
        print(f"❌ Failed to initialize ERNIE Service: {e}")
        return False
    
    # Test 1: Get access token
    print("\n" + "-" * 60)
    print("Test 1: Getting Access Token")
    print("-" * 60)
    try:
        # Directly test the token endpoint to get detailed error
        import requests
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": api_key,
            "client_secret": secret_key
        }
        
        print(f"  Testing token endpoint...")
        response = requests.post(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                print(f"✓ Access token obtained successfully")
                print(f"  Token (first 20 chars): {token[:20]}...")
                print(f"  Expires in: {data.get('expires_in', 'N/A')} seconds")
            else:
                print("❌ No access token in response")
                print(f"  Response: {data}")
                return False
        elif response.status_code == 401:
            print("❌ 401 Unauthorized - Invalid API credentials")
            print(f"  Response: {response.text[:200]}")
            print("\n  Possible causes:")
            print("    - API key or secret key is incorrect")
            print("    - API key has been revoked or expired")
            print("    - Wrong API key type (need Baidu AI Studio, not Qianfan)")
            print("\n  How to fix:")
            print("    1. Visit: https://console.bce.baidu.com/ai/#/ai/overview/index")
            print("    2. Create a new API key in Baidu AI Studio")
            print("    3. Update BAIDU_API_KEY and BAIDU_SECRET_KEY in .env")
            return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
        
        # Set the token in the service for next test
        ernie_service.access_token = token
        ernie_service.token_expires_at = int(time.time()) + data.get("expires_in", 2592000)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        error_str = str(e)
        if "401" in error_str or "Unauthorized" in error_str:
            print("❌ 401 Unauthorized - Invalid API credentials")
            print("  Please check your BAIDU_API_KEY and BAIDU_SECRET_KEY")
        else:
            print(f"❌ Error getting access token: {e}")
        return False
    
    # Test 2: Call ERNIE API
    print("\n" + "-" * 60)
    print("Test 2: Calling ERNIE API")
    print("-" * 60)
    try:
        messages = [
            {"role": "user", "content": "Say 'Hello, Baidu API is working!' in one sentence."}
        ]
        response = ernie_service.call_ernie_api(messages, model="ernie-4.0-8k")
        
        if response and "result" in response:
            result = response.get("result", "")
            print(f"✓ API call successful!")
            print(f"  Response: {result}")
            
            # Check usage
            if "usage" in response:
                usage = response["usage"]
                print(f"  Tokens used: {usage.get('total_tokens', 'N/A')}")
            
            return True
        else:
            print("❌ API call returned unexpected response")
            print(f"  Response: {response}")
            return False
            
    except Exception as e:
        error_str = str(e)
        if "401" in error_str or "Unauthorized" in error_str:
            print("❌ 401 Unauthorized - Invalid API credentials")
            print("  Please check your BAIDU_API_KEY and BAIDU_SECRET_KEY")
        elif "access token" in error_str.lower():
            print("❌ Access token issue - credentials may be invalid")
        else:
            print(f"❌ Error calling ERNIE API: {e}")
        return False


if __name__ == "__main__":
    print()
    success = test_baidu_api()
    print("\n" + "=" * 60)
    if success:
        print("✅ Baidu API credentials are VALID and working!")
        print("=" * 60)
        print("\nYou can use ERNIE as a fallback for AI processing.")
        sys.exit(0)
    else:
        print("❌ Baidu API credentials are INVALID or not working")
        print("=" * 60)
        print("\n📋 Summary:")
        print("  - The API key is not recognized by Baidu AI Studio")
        print("  - Error: 'unknown client id' / 'invalid_client'")
        print("\n💡 This is OK if you're using OLLAMA as primary AI.")
        print("  The system will automatically fallback to regex extraction.")
        print("\n🔧 To fix (optional):")
        print("  1. Make sure you're using Baidu AI Studio keys (not Qianfan)")
        print("  2. Visit: https://console.bce.baidu.com/ai/#/ai/overview/index")
        print("  3. Create new API credentials in Baidu AI Studio")
        print("  4. Update .env with the new keys")
        sys.exit(1)
