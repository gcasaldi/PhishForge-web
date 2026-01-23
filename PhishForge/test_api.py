"""
Python test client for PhishForge API
API usage examples
"""

import requests
import json

API_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def analyze_email(sender, subject, body):
    """Analyze an email using the API"""
    response = requests.post(
        f"{API_URL}/analyze",
        json={
            "sender": sender,
            "subject": subject,
            "body": body
        }
    )
    return response.json()

def main():
    print_section("PhishForge API - Python Test Client")
    
    # Test 1: Phishing email (high risk)
    print_section("TEST 1: Phishing Email (High Risk)")
    
    result = analyze_email(
        sender="PayPal Security <noreply@paypal-verify.xyz>",
        subject="URGENT: Verify your account now!",
        body="""
        Your PayPal account has been locked due to suspicious activity.
        
        Click here immediately to verify your identity:
        http://bit.ly/paypal-verify-now
        
        WARNING: You have only 24 hours before permanent suspension!
        
        Failure to verify will result in account closure.
        """
    )
    
    print(f"🎯 Risk Level: {result['risk_level'].upper()}")
    print(f"📊 Risk Score: {result['risk_score']}/100 ({result['risk_percentage']}%)")
    print(f"\n💡 Recommendation: {result['recommendation']}")
    
    if result['findings']:
        print(f"\n⚠️  Found {len(result['findings'])} issues:")
        for i, finding in enumerate(result['findings'], 1):
            print(f"\n  {i}. {finding['educational']['title']}")
            print(f"     Risk: +{finding['risk_score']} points")
            print(f"     Detail: {finding['detail']}")
    
    # Test 2: Legitimate email (low risk)
    print_section("TEST 2: Legitimate Email (Low Risk)")
    
    result = analyze_email(
        sender="Company Newsletter <newsletter@company.com>",
        subject="Monthly Newsletter - January 2025",
        body="""
        Hello valued customer,
        
        Here's our monthly newsletter with updates and news.
        
        Visit our website for more information:
        https://www.company.com
        
        Best regards,
        The Team
        """
    )
    
    print(f"🎯 Risk Level: {result['risk_level'].upper()}")
    print(f"📊 Risk Score: {result['risk_score']}/100 ({result['risk_percentage']}%)")
    print(f"\n💡 Recommendation: {result['recommendation']}")
    
    if result['findings']:
        print(f"\n⚠️  Found {len(result['findings'])} issues")
    else:
        print("\n✅ No suspicious signals detected")
    
    # Test 3: Health check
    print_section("TEST 3: API Health Check")
    
    health = requests.get(f"{API_URL}/health").json()
    print(f"Status: {health['status']}")
    print(f"Version: {health['version']}")
    print(f"Detector Loaded: {health['detector_loaded']}")
    
    # Test 4: Get configuration
    print_section("TEST 4: API Configuration")
    
    keywords = requests.get(f"{API_URL}/keywords").json()
    print(f"Suspicious Keywords: {keywords['count']} loaded")
    print(f"Examples: {', '.join(keywords['keywords'][:5])}")
    
    tlds = requests.get(f"{API_URL}/tlds").json()
    print(f"\nSuspicious TLDs: {tlds['count']} loaded")
    print(f"Examples: {', '.join(tlds['tlds'][:5])}")
    
    shorteners = requests.get(f"{API_URL}/url-shorteners").json()
    print(f"\nURL Shorteners: {shorteners['count']} loaded")
    print(f"Examples: {', '.join(shorteners['shorteners'][:5])}")
    
    print_section("All Tests Completed!")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API")
        print("Make sure the API is running on http://localhost:8000")
        print("Start it with: uvicorn api:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")
