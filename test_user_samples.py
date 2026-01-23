#!/usr/bin/env python3
"""Test delle URL e email fornite dall'utente per verificare il rilevamento"""

import sys
import os
import importlib.util
from pathlib import Path

# Load the detector module
detector_path = Path(__file__).parent / "PhishForge" / "phishforge_detector.py"
spec = importlib.util.spec_from_file_location("detector", detector_path)
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load module from {detector_path}")
detector = importlib.util.module_from_spec(spec)
sys.modules["detector"] = detector
spec.loader.exec_module(detector)

# URL di test
URL_LIST = [
    "http://login-paypa1.com/account/security-update",
    "https://secure-deloitte-login0.com/auth",
    "http://microsoftsupport-reset-passw0rd.com",
    "https://amazon-updating-order.live",
    "https://google-auth-reset-verify.com",
    "https://icloud-verify-id.apple.support-center.io",
    "https://chasebank.us-refund.xyz",
    "http://ups-package-support.xyz",
    "http://secure-bank-verification.net",
    "https://posteverify-it-security.com",
    "http://inps-secure-online.net",
    "https://support0-microsoft.com",
    "https://apps-goog1e-security.net",
    "https://office365-login-authentication.support",
    "https://facebook-secure-helpdesk.com",
    "http://paypa1-securitycenter.com",
    "http://amazon-secure-verification.live",
    "http://secure-bank-verify.net",
]

# Email di test
EMAIL_LIST = [
    {
        "from": "PaypaI Support <support@paypa1-security.com>",
        "subject": "Important! Your account has been limited",
        "body": "Please confirm your identity: http://paypa1-securitycenter.com"
    },
    {
        "from": "Victor Weber <viwebe@DEL0ITTE.com>",
        "subject": "Strategy presentation for review",
        "body": "InterviewSchedule.pdf.html"
    },
    {
        "from": "Microsoft Helpdesk <security@microsoft-reset.com>",
        "subject": "Password expired",
        "body": "reset_pass.doc.pdf"
    },
    {
        "from": "Amazon Support <orders@amazon-update-orders.com>",
        "subject": "Order failed",
        "body": "http://amazon-secure-verification.live"
    },
    {
        "from": "Google Careers <careers@google-recruitment-careers.com>",
        "subject": "Pre-selected for Google interview",
        "body": ""
    },
    {
        "from": "Apple ID <verify@apple.support-center.io>",
        "subject": "Verify your Apple ID",
        "body": ""
    },
    {
        "from": "Bank Security <refund@secure-bank-verify.net>",
        "subject": "Refund waiting",
        "body": "http://secure-bank-verification.net"
    },
    {
        "from": "Accounting <invoice@company-finance.net>",
        "subject": "Invoice #004829 attached",
        "body": "invoice_004829.xlxs.exe"
    },
    {
        "from": "UPS Delivery <tracking@ups-delivery-status.com>",
        "subject": "Package undelivered",
        "body": "http://ups-package-support.xyz"
    },
    {
        "from": "Poste Italiane <support@post-everify.it>",
        "subject": "Il tuo pacco è in attesa",
        "body": "https://posteverify-it-security.com"
    },
    {
        "from": "INPS Online <notifiche@inps-online-support.it>",
        "subject": "Nuova comunicazione urgente",
        "body": "http://inps-secure-online.net"
    },
    {
        "from": "Security Alert <alert@account-securityverify.com>",
        "subject": "Suspicious login detected",
        "body": ""
    },
    {
        "from": "HR <hr@companycareer.net>",
        "subject": "New policy 2025",
        "body": "policy_update.htm"
    },
    {
        "from": "Office Admin <admin@office-secure.net>",
        "subject": "Document for signature",
        "body": "signature_request.pdf.html"
    },
    {
        "from": "IT Support <helpdesk@company-itserver.net>",
        "subject": "Critical update required",
        "body": "update_security.zip"
    }
]

def test_urls():
    print("\n" + "="*80)
    print("TEST URL PHISHING")
    print("="*80)
    
    failures = []
    
    for url in URL_LIST:
        result = detector.score_url(url)
        risk_level = result.get('risk_level', 'UNKNOWN')
        score = result.get('risk_score', 0)
        
        # Dovrebbero essere tutti HIGH
        status = "✓" if risk_level == "HIGH" else "✗"
        print(f"\n{status} URL: {url}")
        print(f"  Risk: {risk_level} (Score: {score})")
        
        if risk_level != "HIGH":
            failures.append({
                'url': url,
                'expected': 'HIGH',
                'got': risk_level,
                'score': score,
                'indicators': [f['detail'] for f in result.get('findings', [])]
            })
    
    return failures

def test_emails():
    print("\n" + "="*80)
    print("TEST EMAIL PHISHING")
    print("="*80)
    
    failures = []
    
    for i, email in enumerate(EMAIL_LIST, 1):
        email_text = f"From: {email['from']}\nSubject: {email['subject']}\n\n{email['body']}"
        result = detector.score_email(email['from'], email['subject'], email['body'])
        risk_level = result.get('risk_level', 'UNKNOWN')
        score = result.get('score', 0)  # Changed from 'risk_score' to 'score'
        
        # Dovrebbero essere tutti HIGH
        status = "✓" if risk_level == "HIGH" else "✗"
        print(f"\n{status} Email #{i}: {email['subject'][:50]}")
        print(f"  From: {email['from']}")
        print(f"  Risk: {risk_level} (Score: {score})")
        
        if risk_level != "HIGH":
            failures.append({
                'email': f"#{i}: {email['subject']}",
                'from': email['from'],
                'expected': 'HIGH',
                'got': risk_level,
                'score': score,
                'indicators': [f['detail'] for f in result.get('findings', [])]
            })
    
    return failures

def main():
    print("\n" + "="*80)
    print("VERIFICA SISTEMA DI RILEVAMENTO PHISHING")
    print("="*80)
    
    url_failures = test_urls()
    email_failures = test_emails()
    
    print("\n" + "="*80)
    print("RIEPILOGO RISULTATI")
    print("="*80)
    
    print(f"\nURL testati: {len(URL_LIST)}")
    print(f"URL non rilevati come HIGH: {len(url_failures)}")
    
    print(f"\nEmail testate: {len(EMAIL_LIST)}")
    print(f"Email non rilevate come HIGH: {len(email_failures)}")
    
    if url_failures:
        print("\n--- URL NON RILEVATI CORRETTAMENTE ---")
        for failure in url_failures:
            print(f"\nURL: {failure['url']}")
            print(f"Previsto: {failure['expected']}, Ottenuto: {failure['got']} (Score: {failure['score']})")
            print(f"Indicatori: {', '.join(failure['indicators'][:5])}")
    
    if email_failures:
        print("\n--- EMAIL NON RILEVATE CORRETTAMENTE ---")
        for failure in email_failures:
            print(f"\nEmail: {failure['email']}")
            print(f"From: {failure['from']}")
            print(f"Previsto: {failure['expected']}, Ottenuto: {failure['got']} (Score: {failure['score']})")
            print(f"Indicatori: {', '.join(failure['indicators'][:5])}")
    
    total_failures = len(url_failures) + len(email_failures)
    total_tests = len(URL_LIST) + len(EMAIL_LIST)
    
    print(f"\n{'='*80}")
    print(f"TOTALE: {total_tests - total_failures}/{total_tests} test passati")
    print(f"{'='*80}\n")
    
    return total_failures == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
