import os
import requests
import json

# Get the API key from environment
api_key = os.environ.get("ANTHROPIC_API_KEY_MAUDE", "")

print(f"API key found: {bool(api_key)}")

# Make a simple direct request to the API
headers = {
    "x-api-key": api_key,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

data = {
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 100,
    "messages": [
        {"role": "user", "content": "Say hello"}
    ]
}

try:
    print("Making test API request...")
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=data,
        timeout=30.0
    )
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print("API key works! Response:")
        result = response.json()
        print(result["content"][0]["text"])
    else:
        print(f"API error: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")