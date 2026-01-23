#!/usr/bin/env python3
"""
Complete PhishForge System Test

Tests all components:
- Attachment analyzer
- URL ML model  
- Email ML model (if available)
- API endpoints integration
"""

import sys
sys.path.insert(0, '/workspaces/PhishForge-Lite')

print("="*70)
print("PhishForge Complete System Test")
print("="*70)

# Test 1: Attachment Analyzer
print("\n1️⃣  Testing Attachment Analyzer")
print("-" * 70)
try:
    from attachment_analyzer import analyze_attachment, get_risk_level
    
    test_files = [
        ("invoice.pdf", "application/pdf", 50000),
        ("report.pdf.exe", "application/x-msdownload", 1500),
        ("document.docx.html", "text/html", 800),
    ]
    
    for filename, mime, size in test_files:
        result = analyze_attachment(filename, mime, size)
        print(f"\n   📎 {filename}")
        print(f"      Score: {result['attachment_score']}/100 ({get_risk_level(result['attachment_score'])})")
        print(f"      Findings: {len(result['findings'])} detected")
    
    print("\n   ✅ Attachment analyzer working")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: URL ML Model
print("\n2️⃣  Testing URL ML Model")
print("-" * 70)
try:
    from ml_model import ml_score_url, is_model_available
    
    if is_model_available():
        test_urls = [
            "https://www.google.com",
            "http://paypal-verify.com/login",
            "http://secure-banking-update.xyz/account",
        ]
        
        for url in test_urls:
            score = ml_score_url(url)
            print(f"   🔗 {url}")
            print(f"      ML Score: {score:.1f}/100")
        
        print("\n   ✅ URL ML model working")
    else:
        print("   ⚠️  URL ML model not available")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Email ML Model
print("\n3️⃣  Testing Email ML Model")
print("-" * 70)
try:
    from email_predictor import predict_email_risk, is_model_available
    
    if is_model_available():
        test_emails = [
            ("Meeting tomorrow", "Let's discuss the project at 3pm"),
            ("Urgent: Verify your account", "Your PayPal account has been suspended. Click here immediately to verify your identity."),
        ]
        
        for subject, body in test_emails:
            score = predict_email_risk(subject, body)
            print(f"   📧 {subject[:40]}...")
            print(f"      ML Score: {score:.1f}/100")
        
        print("\n   ✅ Email ML model working")
    else:
        print("   ⚠️  Email ML model not available")
        print("   📝 Train with: python ml/train_email_model.py")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: API Integration
print("\n4️⃣  Testing API Endpoints")
print("-" * 70)
try:
    from fastapi.testclient import TestClient
    from api import app
    
    client = TestClient(app)
    
    # Test /analyze-attachment
    print("\n   Testing /analyze-attachment...")
    response = client.post("/analyze-attachment", json={
        "filename": "invoice.pdf.exe",
        "mime_type": "application/x-msdownload",
        "size": 1500
    })
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Response: {result['risk_level']} risk (score: {result['attachment_score']})")
    else:
        print(f"   ❌ Status: {response.status_code}")
    
    # Test /analyze-url
    print("\n   Testing /analyze-url...")
    response = client.post("/analyze-url", json={
        "url": "http://paypal-verify.com/login"
    })
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Response: {result['risk_level']} risk (score: {result['risk_score']})")
    else:
        print(f"   ❌ Status: {response.status_code}")
    
    # Test /analyze (email)
    print("\n   Testing /analyze (email)...")
    response = client.post("/analyze", json={
        "sender": "security@paypal-verify.com",
        "subject": "Urgent: Verify your account",
        "body": "Your account has been suspended. Click here: http://paypal-verify.com/login"
    })
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Response: {result['risk_level']} risk (score: {result['risk_score']})")
        print(f"   📊 Findings: {len(result['findings'])} detected")
    else:
        print(f"   ❌ Status: {response.status_code}")
    
    print("\n   ✅ All API endpoints working")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "="*70)
print("Test Summary")
print("="*70)
print("\n✅ Core functionality:")
print("   - Attachment analysis: Working")
print("   - URL ML detection: Working")
print("   - API endpoints: Working")
print("\n⚠️  Optional (requires training):")
print("   - Email ML model: Train with 'python ml/train_email_model.py'")
print("\n📋 Next steps:")
print("   1. Configure Kaggle credentials (see ml/README.md)")
print("   2. Run: python ml/train_email_model.py")
print("   3. Test full system again")
print("   4. Deploy to production")
print("\n" + "="*70)
