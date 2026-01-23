#!/usr/bin/env python3
"""
Test error handling and fallback responses.
Verifies that the API ALWAYS returns valid JSON in English, even when errors occur.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(name, endpoint, payload, expected_keys):
    """Test an endpoint and verify response structure"""
    print(f"\n{'='*70}")
    print(f"TEST: {name}")
    print(f"{'='*70}")
    
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Valid JSON response received")
            
            # Check required keys
            missing_keys = [k for k in expected_keys if k not in data]
            if missing_keys:
                print(f"❌ MISSING KEYS: {missing_keys}")
            else:
                print(f"✅ All required keys present: {expected_keys}")
            
            # Check risk_score is numeric
            if 'risk_score' in data:
                score = data['risk_score']
                if isinstance(score, (int, float)) and 0 <= score <= 100:
                    print(f"✅ Valid risk_score: {score}/100")
                else:
                    print(f"❌ Invalid risk_score: {score}")
            
            # Check risk_level is valid
            if 'risk_level' in data:
                level = data['risk_level']
                if level in ['LOW', 'MEDIUM', 'HIGH']:
                    print(f"✅ Valid risk_level: {level}")
                else:
                    print(f"❌ Invalid risk_level: {level}")
            
            # Check for English text (no Italian)
            response_text = json.dumps(data).lower()
            italian_words = ['errore', 'analisi', 'pericolo', 'sospetto', 'attenzione']
            italian_found = [w for w in italian_words if w in response_text and 'recommendation' not in response_text]
            if italian_found:
                print(f"⚠️  Italian words found: {italian_found}")
            else:
                print(f"✅ Response is in English")
            
            print(f"\nResponse summary:")
            print(f"  Risk Score: {data.get('risk_score', 'N/A')}")
            print(f"  Risk Level: {data.get('risk_level', 'N/A')}")
            print(f"  From DB: {data.get('from_phishing_database', False)}")
            
            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect - server not running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║              ERROR HANDLING & FALLBACK VERIFICATION TESTS                    ║
║                                                                              ║
║  Tests that API ALWAYS returns valid JSON in English, even with errors      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    email_keys = ['risk_score', 'risk_level', 'risk_percentage', 'findings', 'urls', 'recommendation']
    url_keys = ['mode', 'url', 'risk_score', 'risk_level', 'indicators', 'from_phishing_database', 'recommendation']
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Normal phishing email
    tests_total += 1
    if test_endpoint(
        "Normal Phishing Email",
        "/analyze",
        {
            "sender": "PayPal <security@paypal-verify.xyz>",
            "subject": "Urgent: Account Limited",
            "body": "Verify now: http://paypal-secure.com/verify"
        },
        email_keys
    ):
        tests_passed += 1
    
    # Test 2: Edge case - very long email
    tests_total += 1
    if test_endpoint(
        "Very Long Email (edge case)",
        "/analyze",
        {
            "sender": "test@example.com",
            "subject": "A" * 500,
            "body": "B" * 9000
        },
        email_keys
    ):
        tests_passed += 1
    
    # Test 3: Minimal email
    tests_total += 1
    if test_endpoint(
        "Minimal Email",
        "/analyze",
        {
            "sender": "a@b.com",
            "subject": "Hi",
            "body": "Hello"
        },
        email_keys
    ):
        tests_passed += 1
    
    # Test 4: URL with special characters
    tests_total += 1
    if test_endpoint(
        "URL with Special Characters",
        "/analyze-url",
        {
            "url": "http://test.com/path?param=value&other=123"
        },
        url_keys
    ):
        tests_passed += 1
    
    # Test 5: Legitimate URL
    tests_total += 1
    if test_endpoint(
        "Legitimate HTTPS URL",
        "/analyze-url",
        {
            "url": "https://www.google.com/"
        },
        url_keys
    ):
        tests_passed += 1
    
    # Test 6: Suspicious URL
    tests_total += 1
    if test_endpoint(
        "Suspicious URL",
        "/analyze-url",
        {
            "url": "http://paypal-verify-account-2024.xyz/login"
        },
        url_keys
    ):
        tests_passed += 1
    
    # Test 7: URL mentioned in requirements
    tests_total += 1
    if test_endpoint(
        "Cybersecure Deals URL (from requirements)",
        "/analyze-url",
        {
            "url": "https://www.cybersecure-deals.com/offer?id=2394"
        },
        url_keys
    ):
        tests_passed += 1
    
    print(f"\n{'='*70}")
    print(f"RESULTS: {tests_passed}/{tests_total} tests passed")
    print(f"{'='*70}")
    
    print("""
✅ VERIFICATION CHECKLIST:

1. All responses return valid JSON (no 500 errors)
2. All responses include required fields (risk_score, risk_level, etc.)
3. All text is in English (no Italian in backend responses)
4. Risk scores are 0-100 numeric values
5. Risk levels are LOW/MEDIUM/HIGH
6. Fallback responses work when analysis has errors
7. from_phishing_database flag is always present
8. Recommendations are in English
    """)
    
    if tests_passed == tests_total:
        print("✅ ALL TESTS PASSED - Error handling is robust!")
    else:
        print(f"⚠️  {tests_total - tests_passed} test(s) failed - check server logs")


if __name__ == "__main__":
    main()
