import requests
import json

API_URL = "http://localhost:8080"

def test_health():
    response = requests.get(f"{API_URL}/health")
    print("Health check:", response.json())

def test_chat(message):
    data = {
        "message": message,
        "model": "gemini-2.5-flash"
    }
    response = requests.post(f"{API_URL}/chat", json=data)
    if response.status_code == 200:
        result = response.json()
        print(f"\nQ: {message}")
        print(f"A: {result['text']}")
        if result.get('images'):
            print(f"Images: {len(result['images'])} found")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_health()
    test_chat("What is the capital of France?")
    test_chat("Generate a picture of a cute cat")