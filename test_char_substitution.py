#!/usr/bin/env python3
"""
Test completo per il rilevamento di sostituzioni di caratteri (typosquatting)
"""

import sys
sys.path.insert(0, '/workspaces/PhishForge-Lite/PhishForge')

from phishforge_detector import has_char_substitution, score_url

print("=" * 80)
print("TEST RILEVAMENTO SOSTITUZIONI DI CARATTERI (TYPOSQUATTING)")
print("=" * 80)

# Domini con sostituzioni che DEVONO essere rilevati
phishing_domains = [
    # Sostituzioni 0→o
    "micr0soft-support.com",
    "micros0ft.com",
    "g00gle.com",
    "amaz0n.com",
    "fac3b00k.com",
    
    # Sostituzioni 1→l/i
    "paypa1.com",
    "app1e.com",
    "1nstagram.com",
    
    # Sostituzioni 3→e
    "netf1ix.com",
    "g00g1e.com",
    
    # Sostituzioni 5→s
    "micro5oft.com",
    
    # Combinazioni multiple
    "supp0rt-l0gin.com",
    "secur3-updat3.com",
    "ver1fy-acc0unt.com",
    
    # Generici sospetti
    "login-s3cure.com",
    "bank-supp0rt.com",
    "auth3nticate.com",
]

# Domini legittimi che NON devono essere segnalati
legit_domains = [
    "microsoft.com",
    "google.com",
    "amazon.com",
    "paypal.com",
    "apple.com",
    "company2023.com",  # Anno
    "server123.com",    # Numeri alla fine
    "office365.com",    # 365 è legittimo
]

print("\n🔍 TEST DOMINI PHISHING (devono essere rilevati):")
print("-" * 80)
failed_detections = 0
for domain in phishing_domains:
    detected = has_char_substitution(domain)
    icon = "✅" if detected else "❌"
    print(f"{icon} {domain:40s} - Rilevato: {detected}")
    if not detected:
        failed_detections += 1

print("\n✅ TEST DOMINI LEGITTIMI (NON devono essere rilevati):")
print("-" * 80)
false_positives = 0
for domain in legit_domains:
    detected = has_char_substitution(domain)
    icon = "✅" if not detected else "❌"
    print(f"{icon} {domain:40s} - Rilevato: {detected}")
    if detected:
        false_positives += 1

print("\n" + "=" * 80)
print("TEST URL COMPLETI CON SCORING")
print("=" * 80)

test_urls = [
    "https://micros0ft-support.com/login",
    "https://paypa1-secure.com/verify",
    "https://g00gle-accounts.com/signin",
    "https://amaz0n-security.info/update",
    "https://supp0rt-app1e.com/auth"
]

for url in test_urls:
    result = score_url(url)
    risk_icon = "🚨" if result['risk_level'] == 'HIGH' else "⚠️" if result['risk_level'] == 'MEDIUM' else "✅"
    print(f"\n{risk_icon} {url}")
    print(f"   Score: {result['risk_score']}/100 | Level: {result['risk_level']}")
    
    # Cerca l'indicatore typosquatting
    typosquatting = [i for i in result['indicators'] if 'typosquatting' in i['category']]
    if typosquatting:
        print(f"   ✅ Typosquatting rilevato: {typosquatting[0]['detail']}")
    else:
        print(f"   ❌ Typosquatting NON rilevato!")

print("\n" + "=" * 80)
print("RISULTATI FINALI")
print("=" * 80)
print(f"Mancati rilevamenti (phishing): {failed_detections}/{len(phishing_domains)}")
print(f"Falsi positivi (legittimi): {false_positives}/{len(legit_domains)}")

if failed_detections == 0 and false_positives == 0:
    print("\n🎉 PERFETTO! Tutti i test superati!")
elif failed_detections == 0:
    print(f"\n⚠️  Buono, ma {false_positives} falsi positivi")
else:
    print(f"\n❌ Attenzione: {failed_detections} phishing non rilevati!")

print("=" * 80)
