import sys
sys.path.insert(0, 'PhishForge')
from phishforge_detector import analyze_email_content

# Test email di phishing
result = analyze_email_content(
    subject="URGENT: Your PayPal account will be suspended!",
    body="Your PayPal account has been locked due to suspicious activity.\n\nClick here immediately to verify your identity: http://bit.ly/paypal-verify-now\n\nWARNING: You have only 24 hours before permanent suspension!",
    sender="PayPal Security <noreply@paypal-verify.xyz>"
)

print(f"Risk Score: {result['risk_score']}")
print(f"Risk Level: {result['risk_level']}")
print(f"Findings: {len(result.get('findings', []))}")
for finding in result.get('findings', [])[:5]:
    print(f"  - {finding.get('category')}: {finding.get('detail')}")
