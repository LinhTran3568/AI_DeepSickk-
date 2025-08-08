"""
Test OpenRouter API trực tiếp để debug
"""
import requests
import json

def test_openrouter_api():
    api_key = "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"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/bitcoin-trading-bot",
        "X-Title": "Bitcoin Trading Bot"
    }
    
    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": "Hello, this is a test message."
            }
        ],
        "max_tokens": 100
    }
    
    print("🔍 Testing OpenRouter API...")
    print(f"URL: https://openrouter.ai/api/v1/chat/completions")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ API Test Success!")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"\n❌ API Test Failed!")
            print(f"Error: {response.text}")
            
            # Try to suggest fixes
            if response.status_code == 401:
                print("\n🔧 Possible fixes:")
                print("1. API key expired or invalid")
                print("2. Need to register/verify account on OpenRouter")
                print("3. Insufficient credits")
                print("4. Wrong model name")
        
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_openrouter_api()
