#!/usr/bin/env python3
"""
Verification script to test all fixes and AWS connectivity
Run this after backend is started: python verify_fixes.py
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = 'http://localhost:5000'
AUTH_TOKEN = None

# Test credentials
TEST_EMAIL = 'admin@alumni.edu'
TEST_PASSWORD = 'admin123'

def print_header(title):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def log_result(test_name, passed, details=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {test_name}")
    if details:
        print(f"       {details}")

def test_health_endpoint():
    """Test /api/health endpoint"""
    print_header("1. HEALTH CHECK ENDPOINT")
    try:
        response = requests.get(f'{BASE_URL}/api/health', timeout=5)
        passed = response.status_code == 200
        log_result("Health endpoint accessible", passed, f"Status: {response.status_code}")
        
        if passed:
            data = response.json()
            print(f"       Database: {data.get('database')}")
            print(f"       AWS Status: {data.get('aws')}")
            print(f"       Version: {data.get('version')}")
        return passed
    except Exception as e:
        log_result("Health endpoint accessible", False, f"Error: {str(e)}")
        return False

def test_authentication():
    """Test login and get auth token"""
    print_header("2. AUTHENTICATION")
    global AUTH_TOKEN
    try:
        response = requests.post(
            f'{BASE_URL}/api/login',
            json={'email': TEST_EMAIL, 'password': TEST_PASSWORD},
            timeout=5
        )
        passed = response.status_code == 200
        log_result("Login successful", passed, f"Status: {response.status_code}")
        
        if passed:
            data = response.json()
            AUTH_TOKEN = data.get('token')
            print(f"       Token acquired (first 20 chars): {AUTH_TOKEN[:20]}...")
        return passed
    except Exception as e:
        log_result("Login successful", False, f"Error: {str(e)}")
        return False

def test_campaigns_endpoint():
    """Test /api/campaigns endpoint with real data"""
    print_header("3. CAMPAIGNS ENDPOINT (Real Data)")
    try:
        headers = {'Authorization': f'Bearer {AUTH_TOKEN}'}
        response = requests.get(f'{BASE_URL}/api/campaigns', headers=headers, timeout=5)
        passed = response.status_code == 200
        log_result("Campaigns endpoint accessible", passed, f"Status: {response.status_code}")
        
        if passed:
            campaigns = response.json()
            print(f"       Total campaigns returned: {len(campaigns)}")
            for camp in campaigns:
                print(f"       • {camp.get('name')} - Goal: ${camp.get('goal'):,}, Raised: ${camp.get('raised'):,}")
        return passed
    except Exception as e:
        log_result("Campaigns endpoint accessible", False, f"Error: {str(e)}")
        return False

def test_alumni_endpoint():
    """Test /api/alumni endpoint"""
    print_header("4. ALUMNI LIST ENDPOINT")
    try:
        headers = {'Authorization': f'Bearer {AUTH_TOKEN}'}
        response = requests.get(f'{BASE_URL}/api/alumni', headers=headers, timeout=5)
        passed = response.status_code == 200
        log_result("Alumni list accessible", passed, f"Status: {response.status_code}")
        
        if passed:
            alumni = response.json()
            print(f"       Total alumni in database: {len(alumni)}")
            if alumni:
                first_alum = alumni[0]
                print(f"       Sample: {first_alum.get('name')} - {first_alum.get('department')}")
        return passed
    except Exception as e:
        log_result("Alumni list accessible", False, f"Error: {str(e)}")
        return False

def test_record_engagement():
    """Test record engagement endpoint"""
    print_header("5. RECORD ENGAGEMENT ENDPOINT")
    
    if not AUTH_TOKEN:
        log_result("Record engagement payload", False, "No auth token")
        return False
    
    try:
        headers = {'Authorization': f'Bearer {AUTH_TOKEN}'}
        payload = {
            'alumni_id': 1,
            'event_type': 'attendance',
            'description': 'Test engagement',
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        response = requests.post(
            f'{BASE_URL}/api/alumni/engagement',
            headers=headers,
            json=payload,
            timeout=5
        )
        passed = response.status_code in [200, 201]
        log_result("Record engagement works", passed, f"Status: {response.status_code}")
        
        if not passed:
            print(f"       Response: {response.text}")
        return passed
    except Exception as e:
        log_result("Record engagement works", False, f"Error: {str(e)}")
        return False

def test_record_donation():
    """Test record donation endpoint"""
    print_header("6. RECORD DONATION ENDPOINT")
    
    if not AUTH_TOKEN:
        log_result("Record donation payload", False, "No auth token")
        return False
    
    try:
        headers = {'Authorization': f'Bearer {AUTH_TOKEN}'}
        payload = {
            'alumni_id': 1,
            'amount': 500.00,
            'fund_type': 'general',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'payment_method': 'card'
        }
        response = requests.post(
            f'{BASE_URL}/api/alumni/donation',
            headers=headers,
            json=payload,
            timeout=5
        )
        passed = response.status_code in [200, 201]
        log_result("Record donation works", passed, f"Status: {response.status_code}")
        
        if not passed:
            print(f"       Response: {response.text}")
        return passed
    except Exception as e:
        log_result("Record donation works", False, f"Error: {str(e)}")
        return False

def test_aws_status():
    """Test AWS status endpoint"""
    print_header("7. AWS CONNECTIVITY CHECK")
    
    if not AUTH_TOKEN:
        log_result("AWS status check", False, "No auth token")
        return False
    
    try:
        headers = {'Authorization': f'Bearer {AUTH_TOKEN}'}
        response = requests.get(f'{BASE_URL}/api/aws-status', headers=headers, timeout=5)
        passed = response.status_code in [200, 206]
        
        data = response.json()
        aws_configured = data.get('aws_configured', False)
        boto3_available = data.get('boto3_available', False)
        
        log_result("AWS status endpoint", passed, f"Status: {response.status_code}")
        print(f"       boto3 available: {boto3_available}")
        print(f"       AWS configured: {aws_configured}")
        
        if aws_configured:
            buckets = data.get('s3_buckets', [])
            print(f"       Found S3 buckets: {len(buckets)}")
            for bucket in buckets:
                print(f"         • {bucket}")
        else:
            errors = data.get('errors', [])
            if errors:
                print(f"       Errors:")
                for error in errors:
                    print(f"         • {error}")
        
        return True
    except Exception as e:
        log_result("AWS status endpoint", False, f"Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "🔍 MINI PROJECT ALUMNI ML PLATFORM - VERIFICATION SUITE ".center(70, "="))
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {
        'Health Check': test_health_endpoint(),
        'Authentication': test_authentication(),
        'Campaigns (Real Data)': test_campaigns_endpoint(),
        'Alumni List': test_alumni_endpoint(),
        'Record Engagement': test_record_engagement(),
        'Record Donation': test_record_donation(),
        'AWS Status': test_aws_status(),
    }
    
    # Summary
    print_header("SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}\n")
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n{'='*70}")
    if passed == total:
        print("✅ All tests passed! Application is ready for use.".center(70))
    else:
        print(f"⚠️  {total - passed} test(s) failed. Check backend logs.".center(70))
    print(f"{'='*70}\n")
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
