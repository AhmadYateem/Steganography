#!/usr/bin/env python3
"""Test authentication endpoints"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_signup():
    """Test signup endpoint"""
    print("\n" + "="*50)
    print("Testing SIGNUP")
    print("="*50)
    
    response = requests.post(f"{BASE_URL}/auth/signup", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return data

def test_login(username="testuser", password="TestPass123!"):
    """Test login endpoint"""
    print("\n" + "="*50)
    print("Testing LOGIN")
    print("="*50)
    
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username_or_email": username,
        "password": password
    })
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return data

def test_me(access_token):
    """Test /me endpoint"""
    print("\n" + "="*50)
    print("Testing GET /me")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/auth/me", headers={
        "Authorization": f"Bearer {access_token}"
    })
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return data

def test_history(access_token):
    """Test history endpoint"""
    print("\n" + "="*50)
    print("Testing GET /history")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/history", headers={
        "Authorization": f"Bearer {access_token}"
    })
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return data

def test_encode_with_auth(access_token):
    """Test encode with authentication (should save to history)"""
    print("\n" + "="*50)
    print("Testing ENCODE with auth (should save history)")
    print("="*50)
    
    response = requests.post(f"{BASE_URL}/encode", 
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json={
            "algorithm": "zwc",
            "cover_text": "Hello, this is a normal message.",
            "secret_message": "Secret!",
            "password": "test123"
        }
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return data

def test_limits():
    """Test limits endpoint"""
    print("\n" + "="*50)
    print("Testing GET /limits")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/limits")
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return data

def main():
    print("\n" + "="*60)
    print("   STEGANOGRAPHY AUTH SYSTEM TEST")
    print("="*60)
    
    # Test limits (public)
    test_limits()
    
    # Test signup
    signup_result = test_signup()
    
    if signup_result.get('success'):
        access_token = signup_result.get('access_token')
        
        # Test /me
        test_me(access_token)
        
        # Test encode with auth
        test_encode_with_auth(access_token)
        
        # Test history
        test_history(access_token)
    else:
        # If signup fails (user exists), try login
        print("\nSignup failed, trying login...")
        login_result = test_login()
        
        if login_result.get('success'):
            access_token = login_result.get('access_token')
            
            # Test /me
            test_me(access_token)
            
            # Test encode with auth
            test_encode_with_auth(access_token)
            
            # Test history
            test_history(access_token)
        else:
            print("\nBoth signup and login failed!")
    
    print("\n" + "="*60)
    print("   TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
