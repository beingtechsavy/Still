import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv(override=True)

# Debugging environment variables
print("Debugging Environment Variables:")
print("API Key:", os.getenv("OPENAI_API_KEY"))
print("API Base:", os.getenv("OPENAI_API_BASE"))
print("API Version:", os.getenv("OPENAI_API_VERSION"))
print("Deployment Name:", os.getenv("OPENAI_DEPLOYMENT_NAME"))

api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")
api_version = os.getenv("OPENAI_API_VERSION")
deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")

print(f"Testing Azure OpenAI Connection:")
print(f"Base: {api_base}")
print(f"Version: {api_version}")
print(f"Deployment: {deployment_name}")

client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=api_base
)

try:
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "user", "content": "Test."}
        ],
        max_completion_tokens=10
    )
    print("Success!")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")
