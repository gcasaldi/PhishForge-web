"""
Quick test per verificare che l'API funzioni
"""
import requests
import json
import sys

def test_api():
    base_url = "http://localhost:8000"
    
    # Test 1: Health check
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Analyze phishing email
    print("\n🔍 Testing analyze endpoint with phishing email...")
    try:
        data = {
            "sender": "PayPal Security <fake@paypal-verify.xyz>",
            "subject": "URGENT: Account suspended!",
            "body": "Your account has been locked. Click here: http://bit.ly/verify123"
        }
        response = requests.post(f"{base_url}/analyze", json=data, timeout=5)
        result = response.json()
        
        print(f"✅ Analysis completed:")
        print(f"   Risk Level: {result['risk_level']}")
        print(f"   Risk Score: {result['risk_score']}/100")
        print(f"   Findings: {len(result['findings'])} issues detected")
        
        return True
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("  PhishForge API - Quick Test")
    print("="*60 + "\n")
    
    success = test_api()
    
    print("\n" + "="*60)
    if success:
        print("✅ API is working correctly!")
    else:
        print("❌ API test failed")
        print("Make sure the API is running: uvicorn api:app --reload")
    print("="*60)
    
    sys.exit(0 if success else 1)
