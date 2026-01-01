#!/usr/bin/env python3
"""
Quick test script to verify Azure OpenAI connection
"""
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

def test_azure_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    endpoint = os.getenv("OPENAI_API_BASE")
    api_version = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")
    deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")

    print(f"API Key: {api_key[:10]}..." if api_key else "API Key: None")
    print(f"Endpoint: {endpoint}")
    print(f"API Version: {api_version}")
    print(f"Deployment: {deployment_name}")
    
    if not all([api_key, endpoint, deployment_name]):
        print("❌ Missing required environment variables")
        return False

    try:
        # Ensure endpoint includes protocol
        if endpoint and not endpoint.startswith(("http://", "https://")):
            endpoint = "https://" + endpoint

        client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version,
        )
        
        print("✅ Client initialized successfully")
        
        # Test a simple completion
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "user", "content": "Say 'Hello, Azure OpenAI is working!'"}
            ],
            max_tokens=50
        )
        
        if response.choices and response.choices[0].message:
            print(f"✅ API Response: {response.choices[0].message.content}")
            return True
        else:
            print("❌ No response from API")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_azure_openai()