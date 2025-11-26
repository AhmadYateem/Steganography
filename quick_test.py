import requests
import json

BASE_URL = "http://localhost:5000/api"

print("="*50)
print("Testing Signup")
print("="*50)

try:
    response = requests.post(f"{BASE_URL}/auth/signup", json={
        "username": "testuser3",
        "email": "test3@example.com",
        "password": "TestPass123!"
    }, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.json().get('success'):
        token = response.json().get('access_token')
        print("\n" + "="*50)
        print("Testing History")
        print("="*50)
        
        history_response = requests.get(f"{BASE_URL}/history", 
            headers={"Authorization": f"Bearer {token}"},
            timeout=10)
        print(f"Status: {history_response.status_code}")
        print(f"Response: {json.dumps(history_response.json(), indent=2)}")
        
except Exception as e:
    print(f"Error: {e}")
