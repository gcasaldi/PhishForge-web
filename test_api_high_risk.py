#!/usr/bin/env python3
"""
Test dell'API con gli URL di phishing ad alto rischio
"""
import requests
import json

# URL base dell'API (locale)
API_URL = "http://localhost:8000"

# Test URL di phishing ad alto rischio
test_cases = [
    {
        "name": "IP + login path",
        "sender": "Security Alert <alert@security.com>",
        "subject": "Action Required",
        "body": "Please login at http://185.203.119.47/login to verify your account."
    },
    {
        "name": "Typosquatting - micros0ft",
        "sender": "Microsoft Support <support@micros0ft-support.com>",
        "subject": "Security Alert",
        "body": "Your account needs verification. Visit https://micros0ft-support.com/login"
    },
    {
        "name": "Unicode homograph - аррӏеid",
        "sender": "Apple Support <noreply@аррӏеid.com>",
        "subject": "Account Security",
        "body": "Verify your Apple ID at https://аррӏеid.com"
    },
    {
        "name": "Excessive keywords",
        "sender": "Security <noreply@login-update-secure-service.com>",
        "subject": "Update Required",
        "body": "Visit https://login-update-secure-service.com/auth/verify to update your account."
    }
]

print("=" * 80)
print("TEST API - URL DI PHISHING AD ALTO RISCHIO")
print("=" * 80)

try:
    # Test health check
    response = requests.get(f"{API_URL}/health")
    if response.status_code == 200:
        print("\n✅ API is running")
    else:
        print("\n❌ API health check failed")
        exit(1)
except Exception as e:
    print(f"\n❌ Cannot connect to API: {e}")
    print("Assicurati che l'API sia in esecuzione: cd PhishForge && uvicorn api:app --reload")
    exit(1)

print("\n" + "=" * 80)
print("ANALISI EMAIL CON URL AD ALTO RISCHIO")
print("=" * 80)

all_high = True

for test in test_cases:
    print(f"\n📧 Test: {test['name']}")
    print(f"   Sender: {test['sender']}")
    print(f"   Body: {test['body'][:80]}...")
    
    response = requests.post(
        f"{API_URL}/analyze",
        json=test
    )
    
    if response.status_code == 200:
        result = response.json()
        risk_level = result['risk_level']
        risk_score = result['risk_score']
        
        icon = "✅" if risk_level == "HIGH" else "⚠️" if risk_level == "MEDIUM" else "❌"
        print(f"   {icon} Risk Level: {risk_level} ({risk_score}/100)")
        
        if risk_level != "HIGH":
            all_high = False
            print(f"   ⚠️  ATTENZIONE: Dovrebbe essere HIGH!")
            
        # Mostra indicatori URL
        url_indicators = [ind for ind in result.get('indicators', []) 
                         if 'url' in ind.get('category', '').lower() or 
                         'typosquatting' in ind.get('category', '').lower() or
                         'unicode' in ind.get('category', '').lower() or
                         'ip' in ind.get('category', '').lower() or
                         'keyword' in ind.get('category', '').lower()]
        
        if url_indicators:
            print(f"   Indicatori URL rilevati:")
            for ind in url_indicators[:3]:
                print(f"      • [{ind.get('risk_score', 0)}] {ind.get('category', 'N/A')}")
    else:
        print(f"   ❌ Error: {response.status_code}")
        all_high = False

print("\n" + "=" * 80)
if all_high:
    print("🎉 SUCCESSO! Tutti gli URL ad alto rischio sono classificati come HIGH")
else:
    print("⚠️  Alcuni URL non sono classificati correttamente")
print("=" * 80)
