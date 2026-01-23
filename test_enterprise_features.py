#!/usr/bin/env python3
"""
PhishForge Enterprise Features Test Suite

Tests all SOC-grade enhancements:
- Typosquatting detection
- Double extension detection
- Risk factors explainability
- Real-time stats tracking
"""

import requests
import json
from datetime import datetime

# API endpoint
BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_typosquatting():
    """Test digit substitution detection"""
    print_section("TEST 1: Typosquatting Detection")
    
    payload = {
        "sender": "PayPal Security <noreply@paypa1.com>",
        "subject": "Account Verification Required",
        "body": "Please verify your account at http://paypa1-secure.com/verify"
    }
    
    print(f"\n📧 Test Email:")
    print(f"   Sender: {payload['sender']}")
    print(f"   Domain: paypa1.com (1 instead of l)")
    
    response = requests.post(f"{BASE_URL}/analyze", json=payload)
    data = response.json()
    
    print(f"\n📊 Results:")
    print(f"   Risk Score: {data['risk_score']}/100")
    print(f"   Risk Level: {data['risk_level']}")
    print(f"   Sender Risk: {data.get('sender_risk', 'N/A')}")
    
    # Check if typosquatting was detected
    typosquatting_detected = any(
        'typosquatting' in f.lower() or 'substitution' in f.lower() 
        for f in data.get('risk_factors', [])
    )
    
    print(f"\n✅ Typosquatting Detection: {'PASSED' if typosquatting_detected else 'FAILED'}")
    
    return data['risk_score'] >= 70 and typosquatting_detected


def test_double_extension():
    """Test double extension detection"""
    print_section("TEST 2: Double Extension Detection")
    
    payload = {
        "sender": "support@company.com",
        "subject": "Invoice Attached",
        "body": "Please review the attached invoice.",
        "attachment_filename": "invoice.pdf.exe",
        "attachment_size": 50000
    }
    
    print(f"\n📎 Test Attachment:")
    print(f"   Filename: {payload['attachment_filename']}")
    print(f"   Pattern: .pdf.exe (CRITICAL)")
    
    response = requests.post(f"{BASE_URL}/analyze", json=payload)
    data = response.json()
    
    print(f"\n📊 Results:")
    print(f"   Risk Score: {data['risk_score']}/100")
    print(f"   Risk Level: {data['risk_level']}")
    print(f"   Attachment Score: {data.get('attachment_score', 'N/A')}")
    
    # Check if double extension was detected
    double_ext_detected = any(
        'double extension' in f.lower() or 'pdf.exe' in f.lower()
        for f in data.get('risk_factors', [])
    )
    
    print(f"\n✅ Double Extension Detection: {'PASSED' if double_ext_detected else 'FAILED'}")
    
    return data['risk_score'] >= 80 and double_ext_detected


def test_risk_factors_explainability():
    """Test risk factors output"""
    print_section("TEST 3: Explainability (risk_factors)")
    
    payload = {
        "sender": "Admin Support <admin@micr0soft-support.xyz>",
        "subject": "URGENT: Account suspended - verify now!",
        "body": "Click here to restore: http://bit.ly/restore123",
        "attachment_filename": "form.docx.html"
    }
    
    print(f"\n📧 Complex Phishing Email:")
    print(f"   - Digit substitution: micr0soft")
    print(f"   - Suspicious TLD: .xyz")
    print(f"   - URL shortener: bit.ly")
    print(f"   - Double extension: .docx.html")
    print(f"   - Urgency keywords: URGENT, suspended")
    
    response = requests.post(f"{BASE_URL}/analyze", json=payload)
    data = response.json()
    
    print(f"\n📊 Results:")
    print(f"   Risk Score: {data['risk_score']}/100")
    print(f"   Risk Level: {data['risk_level']}")
    
    risk_factors = data.get('risk_factors', [])
    print(f"\n🔍 Risk Factors ({len(risk_factors)} detected):")
    for i, factor in enumerate(risk_factors[:10], 1):
        print(f"   {i}. {factor}")
    
    has_risk_factors = len(risk_factors) > 0
    print(f"\n✅ Explainability: {'PASSED' if has_risk_factors else 'FAILED'}")
    
    return data['risk_score'] >= 80 and has_risk_factors


def test_stats_tracking():
    """Test real-time stats endpoint"""
    print_section("TEST 4: Real-Time Stats Tracking")
    
    print("\n📈 Sending test emails to generate stats...")
    
    # Send multiple test requests
    test_cases = [
        {"score_expected": "HIGH", "sender": "phishing@evil.xyz", "body": "Click here urgently!"},
        {"score_expected": "MEDIUM", "sender": "marketing@company.com", "body": "Special offer today"},
        {"score_expected": "LOW", "sender": "john@company.com", "body": "Meeting at 3pm"},
    ]
    
    for i, case in enumerate(test_cases, 1):
        payload = {
            "sender": case["sender"],
            "subject": "Test " + str(i),
            "body": case["body"]
        }
        requests.post(f"{BASE_URL}/analyze", json=payload)
        print(f"   Sent test {i}/3...")
    
    # Get stats
    print("\n📊 Fetching stats...")
    response = requests.get(f"{BASE_URL}/stats")
    stats = response.json()
    
    print(f"\n📈 Statistics (since {stats.get('since', 'N/A')}):")
    print(f"   Total Analyzed: {stats.get('total_analyzed', 0):,}")
    print(f"   High Risk (70+): {stats.get('high_risk', 0)} ({stats.get('high_risk_percentage', 0):.1f}%)")
    print(f"   Critical (90+): {stats.get('critical_risk', 0)} ({stats.get('critical_risk_percentage', 0):.1f}%)")
    print(f"   Status: {stats.get('status', 'unknown')}")
    print(f"   Metrics Type: {stats.get('metrics_type', 'unknown')}")
    
    has_stats = stats.get('total_analyzed', 0) > 0
    print(f"\n✅ Stats Tracking: {'PASSED' if has_stats else 'FAILED'}")
    
    return has_stats


def run_all_tests():
    """Run complete enterprise test suite"""
    print("\n" + "🚀"*35)
    print("  PhishForge Enterprise Features - Test Suite")
    print("  SOC/SIEM-Grade Validation")
    print("🚀"*35)
    
    print(f"\n⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "Typosquatting Detection": test_typosquatting(),
        "Double Extension Detection": test_double_extension(),
        "Risk Factors Explainability": test_risk_factors_explainability(),
        "Stats Tracking": test_stats_tracking()
    }
    
    print_section("TEST SUMMARY")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status} - {test_name}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Enterprise features operational!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - review required")
    
    print(f"\n⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite error: {e}")
        exit(1)
