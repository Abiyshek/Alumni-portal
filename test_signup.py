#!/usr/bin/env python
"""Test signup endpoint"""

import requests
import json

BASE_URL = 'http://localhost:5000'

print("Testing Signup Endpoint\n" + "="*50)

signup_data = {
    'email': 'newuser@example.com',
    'password': 'password123',
    'name': 'New User'
}

try:
    print(f"\nPOST {BASE_URL}/api/auth/signup")
    print(f"Body: {json.dumps(signup_data, indent=2)}")
    
    response = requests.post(
        f'{BASE_URL}/api/auth/signup', 
        json=signup_data,
        headers={'Content-Type': 'application/json'},
        timeout=5
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.ok:
        data = response.json()
        print(f"\n✓ Signup successful!")
        print(f"  User: {data['user']['name']}")
        print(f"  Email: {data['user']['email']}")
        print(f"  Role: {data['user']['role']}")
    else:
        print(f"\n✗ Signup failed with status {response.status_code}")
        
except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n" + "="*50)
