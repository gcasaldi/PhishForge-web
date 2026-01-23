import sys
sys.path.insert(0, 'PhishForge')
from phishforge_detector import analyze_email_content

# Test email legittima
result = analyze_email_content(
    subject="Monthly Newsletter - January 2026",
    body="Hello,\n\nHere is our monthly newsletter with updates.\n\nVisit our website: https://www.company.com\n\nBest regards,\nThe Team",
    sender="newsletter@company.com"
)

print(f"Risk Score: {result['risk_score']}")
print(f"Findings: {len(result.get('findings', []))}")
for finding in result.get('findings', [])[:5]:
    print(f"  - {finding.get('category')}: {finding.get('detail')}")
