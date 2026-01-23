#!/usr/bin/env python3
"""
Test per verificare che gli URL legittimi non siano classificati come HIGH
"""

import sys
sys.path.insert(0, '/workspaces/PhishForge-Lite/PhishForge')

from phishforge_detector import score_url

# URL legittimi che NON devono essere classificati come HIGH
legit_urls = [
    "https://www.paypal.com/signin",
    "https://www.amazon.com/ap/signin",
    "https://login.microsoftonline.com",
    "https://accounts.google.com/signin",
    "https://appleid.apple.com",
    "https://www.icloud.com",
    "https://outlook.office.com/login",
    "https://github.com/login",
    "https://www.facebook.com/login"
]

print("=" * 80)
print("TEST URL LEGITTIMI (NON devono essere HIGH)")
print("=" * 80)

problemi = 0

for url in legit_urls:
    result = score_url(url)
    
    status_icon = "✅" if result['risk_level'] != 'HIGH' else "❌"
    print(f"\n{status_icon} {url}")
    print(f"   Score: {result['risk_score']}/100 | Level: {result['risk_level']}")
    
    if result['risk_level'] == 'HIGH':
        problemi += 1
        print(f"   ⚠️ FALSO POSITIVO! Indicatori:")
        for ind in result['indicators']:
            print(f"      - [{ind['risk_score']}] {ind['category']}")

print("\n" + "=" * 80)
if problemi == 0:
    print("✅ SUCCESSO: Nessun falso positivo!")
else:
    print(f"❌ ATTENZIONE: {problemi} falsi positivi rilevati")
print("=" * 80)
