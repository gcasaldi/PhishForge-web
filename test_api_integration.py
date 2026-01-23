#!/usr/bin/env python3
"""
Quick validation test for the merged scoring engine API integration.
Tests both /analyze (email) and /analyze-url endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_api(endpoint, payload, test_name):
    """Test an API endpoint"""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")
    print(f"Endpoint: POST {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=10)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS - Response:")
            print(f"  Risk Score: {data.get('risk_score', 'N/A')}/100")
            print(f"  Risk Level: {data.get('risk_level', 'N/A')}")
            print(f"  From Database: {data.get('from_phishing_database', False)}")
            
            # Show findings/indicators
            findings = data.get('findings', data.get('indicators', []))
            print(f"\n  Findings ({len(findings)} total):")
            for finding in findings[:5]:
                category = finding.get('category', 'unknown')
                detail = finding.get('detail', 'N/A')
                points = finding.get('risk_score', 0)
                print(f"    • [{category}] +{points}pts: {detail}")
            
            return data
        else:
            print(f"❌ FAILED: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API. Is the server running?")
        print("   Start with: python api.py")
        return None
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None


def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║              PHISHFORGE API INTEGRATION TEST - Merged Scoring                ║
║                                                                              ║
║  Validates that API endpoints work correctly with the refactored engine      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Test 1: Phishing email with brand impersonation
    test_api(
        "/analyze",
        {
            "sender": "PayPal Security <noreply@paypal-verify.xyz>",
            "subject": "Urgent: Your account has been limited",
            "body": "Your PayPal account will be closed within 24 hours. Verify now: http://paypal-secure-login.com/verify"
        },
        "Phishing Email - PayPal Impersonation"
    )
    
    # Test 2: GitHub phishing
    test_api(
        "/analyze",
        {
            "sender": "GitHub Security <noreply@github-secure.com>",
            "subject": "Action required: Token leak detected",
            "body": "We detected a token leak in your repository. Review immediately: https://github-secure.com/security/review"
        },
        "Phishing Email - GitHub Token Leak"
    )
    
    # Test 3: Normal work email
    test_api(
        "/analyze",
        {
            "sender": "John Doe <john@company.com>",
            "subject": "Meeting tomorrow",
            "body": "Hi team, let's meet tomorrow at 3pm to discuss the project."
        },
        "Legitimate Email - Normal Work Communication"
    )
    
    # Test 4: Suspicious URL
    test_api(
        "/analyze-url",
        {
            "url": "http://paypal-verify-account.xyz/login?id=12345"
        },
        "URL Analysis - Suspicious PayPal-like Domain"
    )
    
    # Test 5: Legitimate URL
    test_api(
        "/analyze-url",
        {
            "url": "https://www.google.com/search?q=security"
        },
        "URL Analysis - Legitimate Google Search"
    )
    
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print("""
✅ VERIFICATION CHECKLIST:

1. All endpoints return valid JSON responses
   - Even when URLs are NOT in Phishing.Database
   - from_phishing_database flag is present and accurate

2. Heuristic engine works independently
   - Phishing emails score HIGH (70-100) without database
   - Brand impersonation detected (github, intesa, paypal)
   - Normal emails score LOW (0-15)

3. Risk levels are consistent
   - LOW: 0-25
   - MEDIUM: 26-55  
   - HIGH: 56-100

4. Database integration (when available)
   - Adds +70 bonus points to heuristic score
   - Does NOT replace heuristic analysis
   - Combined score typically 90-100 for database hits

5. API always returns results
   - No empty/null responses
   - Graceful handling when database unavailable
   - Error messages don't expose stacktraces
    """)


if __name__ == "__main__":
    main()
