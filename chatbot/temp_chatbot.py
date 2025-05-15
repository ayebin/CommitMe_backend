import requests
import os
from dotenv import load_dotenv

HF_TOKEN = ""

API_URL = "https://api-inference.huggingface.co/models/gpt2"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

data = {
    "inputs": "The capital of South Korea is",
    "parameters": {
        "max_new_tokens": 20
    }
}

response = requests.post(API_URL, headers=headers, json=data)

print("Status Code:", response.status_code)
print("Raw Response:", response.text)
