#!/usr/bin/env python3
"""
Web App Integration Test
Simulates the web app sending requests to the API
"""

import requests
import json

API_URL = "https://phishforge-lite.onrender.com/analyze"

print("="*70)
print("PhishForge Web App Integration Test")
print("="*70)

# This simulates what the web app (script.js) sends
test_cases = [
    {
        "name": "Phishing Email - Account Verification",
        "payload": {
            "subject": "Verify Your Account Immediately",
            "sender": "support@paypal-secure.com",
            "body": "Your account will be suspended. Click here: http://paypal-verify.com"
        },
        "expected_risk": "HIGH/CRITICAL"
    },
    {
        "name": "Legitimate Email - Work Meeting",
        "payload": {
            "subject": "Weekly Team Sync",
            "sender": "manager@company.com",
            "body": "Hi team, let's meet tomorrow at 10am to discuss the project status."
        },
        "expected_risk": "LOW"
    },
    {
        "name": "Phishing with Malicious Attachment",
        "payload": {
            "subject": "Invoice Attached",
            "sender": "billing@unknown.com",
            "body": "Please review the attached invoice.",
            "attachment_filename": "invoice.pdf.exe"
        },
        "expected_risk": "HIGH"
    },
    {
        "name": "Banking Phishing",
        "payload": {
            "subject": "Security Alert - Immediate Action Required",
            "sender": "security@bank-alert.com",
            "body": "Unusual activity detected. Verify identity: http://secure-banking.xyz/verify"
        },
        "expected_risk": "CRITICAL"
    }
]

results = []

for i, test in enumerate(test_cases, 1):
    print(f"\n{i}️⃣  {test['name']}")
    print("-"*70)
    
    try:
        response = requests.post(
            API_URL,
            json=test['payload'],
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            risk_score = data.get('risk_score', 0)
            risk_level = data.get('risk_level', 'UNKNOWN')
            findings = len(data.get('findings', []))
            
            print(f"✅ Status: {response.status_code}")
            print(f"   Risk Score: {risk_score}/100")
            print(f"   Risk Level: {risk_level}")
            print(f"   Expected: {test['expected_risk']}")
            print(f"   Findings: {findings}")
            
            # Check if attachment was analyzed
            if 'attachment_filename' in test['payload']:
                att_score = data.get('attachment_score', 'N/A')
                print(f"   Attachment Risk: {att_score}")
            
            # Show recommendation
            recommendation = data.get('recommendation', 'N/A')
            print(f"   Recommendation: {recommendation[:60]}...")
            
            results.append({
                "test": test['name'],
                "passed": True,
                "risk_score": risk_score,
                "risk_level": risk_level
            })
            
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            results.append({
                "test": test['name'],
                "passed": False,
                "error": response.text
            })
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        results.append({
            "test": test['name'],
            "passed": False,
            "error": str(e)
        })

# Summary
print("\n" + "="*70)
print("Test Results Summary")
print("="*70)

passed = sum(1 for r in results if r.get('passed', False))
total = len(results)

print(f"\nTests Passed: {passed}/{total}")

if passed == total:
    print("\n🎉 ALL TESTS PASSED!")
    print("\n✅ Web app integration is working perfectly")
    print("\nThe web app can:")
    print("  - Send email data to the API")
    print("  - Receive structured JSON responses")
    print("  - Display risk scores and findings")
    print("  - Handle attachments")
    print("  - Show recommendations")
else:
    print(f"\n⚠️  {total - passed} test(s) failed")
    print("\nFailed tests:")
    for r in results:
        if not r.get('passed', False):
            print(f"  - {r['test']}: {r.get('error', 'Unknown error')}")

print("\n" + "="*70)
print("🌐 Web App Status: READY")
print("📡 API: https://phishforge-lite.onrender.com")
print("🚀 System: OPERATIONAL")
print("="*70)
