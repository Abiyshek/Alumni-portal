#!/usr/bin/env python
"""Test API endpoints"""

import requests
import json

BASE_URL = 'http://localhost:5000'

print("Testing Alumni ML Backend API\n" + "="*50)

# Test 1: Login
print("\n[1] Testing LOGIN endpoint...")
login_data = {
    'email': 'admin@alumni.edu',
    'password': 'admin123'
}

try:
    response = requests.post(f'{BASE_URL}/api/auth/login', json=login_data, timeout=5)
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        token = data.get('token')
        print(f"✓ Login successful!")
        print(f"  Token: {token[:20]}...")
        print(f"  User: {data['user']['name']} ({data['user']['role']})")
        
        # Test 2: Get Alumni with token
        print("\n[2] Testing GET /api/alumni endpoint...")
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{BASE_URL}/api/alumni', headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        if response.ok:
            alumni = response.json()
            print(f"✓ Got {len(alumni)} alumni")
            if alumni:
                first = alumni[0]
                print(f"  First alumni: {first['name']} ({first['company']})")
        else:
            print(f"✗ Error: {response.text}")
    else:
        print(f"✗ Login failed: {response.text}")
except Exception as e:
    print(f"✗ Connection error: {e}")
    print("\n⚠️  Backend might not be running!")
    print("Start it with: cd g:\\MINI_PROJECT\\backend && python app.py")

print("\n" + "="*50)
