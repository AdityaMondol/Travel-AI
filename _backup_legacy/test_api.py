#!/usr/bin/env python
"""Quick API test script"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✓ Status: {response.status_code}")
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_llm():
    """Test LLM connectivity"""
    print("\nTesting LLM connectivity...")
    try:
        response = requests.post(f"{BASE_URL}/test", timeout=30)
        print(f"✓ Status: {response.status_code}")
        data = response.json()
        print(f"  Response: {data.get('response', 'No response')[:100]}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_chat():
    """Test chat endpoint"""
    print("\nTesting chat endpoint...")
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "session_id": "test_session",
                "message": "Hello, what is 2+2?"
            },
            timeout=30,
            stream=True
        )
        print(f"✓ Status: {response.status_code}")
        
        # Read streaming response
        print("  Streaming response:")
        for line in response.iter_lines():
            if line:
                print(f"    {line.decode()[:80]}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("=== Leonore AI API Test ===\n")
    
    health_ok = test_health()
    llm_ok = test_llm()
    chat_ok = test_chat()
    
    print("\n=== Summary ===")
    print(f"Health: {'✓' if health_ok else '✗'}")
    print(f"LLM: {'✓' if llm_ok else '✗'}")
    print(f"Chat: {'✓' if chat_ok else '✗'}")
