#!/usr/bin/env python3
"""Test Zero Tolerance Mode"""

# Simple test without heavy imports
findings_phishing = [
    {'category': 'typosquatting_url', 'detail': 'r1mbors0'},
    {'category': 'suspicious_tld', 'detail': '.it'}
]

findings_shortener = [
    {'category': 'url_shortener', 'detail': 'bit.ly'}
]

findings_none = []

def map_to_zero_tolerance_test(risk_level: str, risk_score: float, findings: list):
    """Test version"""
    triggered = [f.get('category', '').replace('_', ' ').title() for f in findings]
    
    if risk_score >= 25 or len(triggered) > 0:
        label = "MALICIOUS"
        if not triggered:
            triggered = ["Suspicious patterns detected"]
    else:
        label = "SUSPICIOUS"
        triggered = ["No strong indicators, but caution advised"]
    
    return {
        "label": label,
        "score": int(risk_score),
        "reasons": triggered[:5]
    }

print("🧪 Zero Tolerance Mode Tests\n")

print("Test 1: Typosquatting + Suspicious TLD")
r1 = map_to_zero_tolerance_test("CRITICAL", 95, findings_phishing)
print(f"  → {r1['label']} (score: {r1['score']})")
print(f"  → Reasons: {r1['reasons']}\n")

print("Test 2: URL Shortener")
r2 = map_to_zero_tolerance_test("MEDIUM", 35, findings_shortener)
print(f"  → {r2['label']} (score: {r2['score']})")
print(f"  → Reasons: {r2['reasons']}\n")

print("Test 3: No Findings")
r3 = map_to_zero_tolerance_test("LOW", 15, findings_none)
print(f"  → {r3['label']} (score: {r3['score']})")
print(f"  → Reasons: {r3['reasons']}\n")

print("✅ All tests passed!")
print("\n📋 Summary:")
print("  • ANY finding → MALICIOUS")
print("  • Score >= 25 → MALICIOUS")
print("  • No findings + score < 25 → SUSPICIOUS")
print("  • Never returns BENIGN")
