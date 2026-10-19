
import os
import requests

# Read the API key securely from the environment
api_key = os.getenv("AWS_BEARER_TOKEN_BEDROCK")

if not api_key:
    raise RuntimeError(
        "API key not found. Set AWS_BEARER_TOKEN_BEDROCK first."
    )

# AWS Region shown in your screenshot: Mumbai
region = "ap-south-1"

# First model to test: Amazon Nova Lite
model_id = "apac.amazon.nova-lite-v1:0"

url = (
    f"https://bedrock-runtime.{region}.amazonaws.com"
    f"/model/{model_id}/converse"
)

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

payload = {
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "text": (
                        "Reply with: "
                        "Hello! AWS Bedrock is connected to Python."
                    )
                }
            ],
        }
    ],
    "inferenceConfig": {
        "maxTokens": 100,
        "temperature": 0.2,
    },
}

try:
    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=60,
    )

    if not response.ok:
        print("Request failed:", response.status_code)
        print(response.text)
        response.raise_for_status()

    result = response.json()
    answer = result["output"]["message"]["content"][0]["text"]

    print("\nBedrock connection successful!")
    print("AI response:", answer)

except requests.RequestException as exc:
    print("Request error:", exc)

except (KeyError, IndexError, ValueError) as exc:
    print("Could not read the response:", exc)
