#!/usr/bin/env python3
"""
Test script per URL di phishing ad alto rischio
"""

import sys
sys.path.insert(0, '/workspaces/PhishForge-Lite/PhishForge')

from phishforge_detector import score_url

# URL ad alto rischio segnalati dall'utente
high_risk_urls = [
    "http://185.203.119.47/login",
    "https://micros0ft-support.com/login",
    "https://paypal.secure-login.verify-user.com",
    "https://secure-amazon-account.info/verify",
    "https://office365-login-security.net/reset",
    "https://login-update-secure-service.com/auth/verify",
    "https://аррӏеid.com",  # IDN homograph attack
    "http://bit.ly/2Fh7XxP",
    "https://accounts-google.verify-session.com",
    "https://icloud-security-alert.info/signin"
]

print("=" * 80)
print("TEST URL DI PHISHING AD ALTO RISCHIO")
print("=" * 80)

for url in high_risk_urls:
    print(f"\n{'=' * 80}")
    print(f"URL: {url}")
    print('=' * 80)
    
    result = score_url(url)
    
    print(f"Risk Score: {result['risk_score']}/100")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Da Database: {result.get('from_phishing_database', False)}")
    
    print("\nIndicatori:")
    for indicator in result['indicators']:
        print(f"  - [{indicator['risk_score']}] {indicator['category']}: {indicator['detail']}")
    
    # Verifica se è classificato correttamente
    if result['risk_level'] != 'HIGH':
        print(f"\n⚠️  PROBLEMA: Questo URL dovrebbe essere HIGH, ma è {result['risk_level']}!")

print("\n" + "=" * 80)
print("TEST COMPLETATO")
print("=" * 80)
