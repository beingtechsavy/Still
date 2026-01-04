#!/usr/bin/env python3
"""
Debug Azure OpenAI connection with detailed error reporting
"""
import os
import requests
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

def test_azure_openai_detailed():
    # Get environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    endpoint = os.getenv("OPENAI_API_BASE")
    api_version = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")
    deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")
    
    print("=== ENVIRONMENT VARIABLES ===")
    print(f"API Key present: {bool(api_key)}")
    print(f"API Key (first 10 chars): {api_key[:10] if api_key else 'None'}")
    print(f"Endpoint: {endpoint}")
    print(f"API Version: {api_version}")
    print(f"Deployment Name: {deployment_name}")
    print()
    
    if not all([api_key, endpoint, deployment_name]):
        print("❌ Missing required environment variables")
        return False
    
    # Ensure endpoint format
    if endpoint and not endpoint.startswith(("http://", "https://")):
        endpoint = "https://" + endpoint
    
    print("=== TESTING WITH REQUESTS (Raw HTTP) ===")
    # Test with raw requests first
    url = f"{endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"
    print(f"URL: {url}")
    
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in one sentence."}
        ],
        "max_tokens": 50
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Raw HTTP request successful!")
        else:
            print(f"❌ Raw HTTP request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Raw HTTP request failed: {e}")
        return False
    
    print("\n=== TESTING WITH AZURE OPENAI SDK ===")
    try:
        client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version,
        )
        
        print("✅ Client initialized")
        
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in one sentence."}
            ],
            max_tokens=50
        )
        
        print(f"✅ SDK Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ SDK request failed: {e}")
        print(f"Exception type: {type(e)}")
        return False

if __name__ == "__main__":
    test_azure_openai_detailed()