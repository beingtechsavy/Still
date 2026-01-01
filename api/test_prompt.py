import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv("OPENAI_API_BASE")
model_name = os.getenv("OPENAI_DEPLOYMENT_NAME")
deployment = os.getenv("OPENAI_DEPLOYMENT_NAME")

subscription_key = os.getenv("OPENAI_API_KEY")
api_version = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": "I am going to Paris, what should I see?",
        }
    ],
    max_completion_tokens=40000,
    model=deployment
)

print(response.choices[0].message.content)