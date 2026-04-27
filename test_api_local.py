#!/usr/bin/env python3
'''
PhishForge Local API Integration Test
Verifica che l'API locale funzioni correttamente
'''

import sys
import time
import subprocess
import requests
import json
from pathlib import Path

def print_status(status, msg):
    colors = {
        'ok': '\033[92m',      # Green
        'err': '\033[91m',     # Red
        'warn': '\033[93m',    # Yellow
        'info': '\033[94m',    # Blue
        'end': '\033[0m'       # End
    }
    icon = {'ok': '✓', 'err': '✗', 'warn': '⚠', 'info': 'ℹ'}[status]
    print(f"{colors[status]}{icon} {msg}{colors['end']}")

def check_api_running():
    """Verifica se l'API è in esecuzione"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def test_email_analysis():
    """Test analisi email"""
    print_status('info', 'Test analisi email phishing...')
    
    phishing_email = {
        "subject": "🚨 URGENT: Verify Your Account Immediately!",
        "sender": "security@paypal-verify.xyz",
        "body": """
Dear Valued Customer,

Your PayPal account has been LIMITED due to unusual activity. 
You must verify your identity IMMEDIATELY to restore full access.

Click here to verify: http://bit.ly/paypalverify123

Do NOT ignore this message or your account will be permanently closed!

Regards,
PayPal Security Team
        """,
        "attachments": []
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/analyze/email",
            json=phishing_email,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print_status('ok', f"Email phishing: Score {result['risk_score']}/100 ({result['risk_level']})")
            
            # Verifica che sia effettivamente rilevato come phishing
            if result['risk_score'] >= 50:
                print_status('ok', f"Rilevamento corretto! (score >= 50)")
            else:
                print_status('warn', f"Score basso - verificare detector ({result['risk_score']})")
            
            print(f"  Raccomandazione: {result['recommendation'][:60]}...")
            return True
        else:
            print_status('err', f"Errore API: {response.status_code}")
            print(f"  {response.text[:100]}")
            return False
            
    except requests.exceptions.Timeout:
        print_status('err', "Timeout - API troppo lenta")
        return False
    except Exception as e:
        print_status('err', f"Errore: {str(e)}")
        return False

def test_legit_email():
    """Test email legittima"""
    print_status('info', 'Test analisi email legittima...')
    
    legit_email = {
        "subject": "Your Order #12345 Has Shipped",
        "sender": "orders@amazon.com",
        "body": """
Hi Customer,

Great news! Your order has been shipped.

Order: #12345
Tracking: https://amazon.com/track/abc123

Thank you for shopping with us!

Best regards,
Amazon Customer Service
        """,
        "attachments": []
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/analyze/email",
            json=legit_email,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print_status('ok', f"Email legittima: Score {result['risk_score']}/100 ({result['risk_level']})")
            
            # Verifica che sia rilevato come sicuro/basso rischio
            if result['risk_score'] <= 30:
                print_status('ok', f"Rilevamento corretto! (score <= 30)")
            else:
                print_status('warn', f"Score alto - email legittima potrebbe avere falsi positivi ({result['risk_score']})")
            
            return True
        else:
            print_status('err', f"Errore API: {response.status_code}")
            return False
            
    except Exception as e:
        print_status('err', f"Errore: {str(e)}")
        return False

def test_url_analysis():
    """Test analisi URL"""
    print_status('info', 'Test analisi URL sospetto...')
    
    url_request = {
        "url": "http://paypal-verify-account-security.xyz/login"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/analyze/url",
            json=url_request,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print_status('ok', f"URL sospetto: Score {result['risk_score']}/100 ({result['risk_level']})")
            return True
        else:
            print_status('err', f"Errore API: {response.status_code}")
            return False
            
    except Exception as e:
        print_status('err', f"Errore: {str(e)}")
        return False

def main():
    print("\n" + "="*50)
    print("PhishForge Local API Test Suite")
    print("="*50 + "\n")
    
    # Check API
    print_status('info', 'Verificando API su http://localhost:8000...')
    
    if not check_api_running():
        print_status('err', 'API non raggiungibile!')
        print_status('warn', 'Avvia l\'API con: ./run_local_api.sh')
        sys.exit(1)
    
    print_status('ok', 'API disponibile!')
    
    # Run tests
    results = []
    print("\n--- TEST EMAIL PHISHING ---")
    results.append(("Email Phishing", test_email_analysis()))
    
    print("\n--- TEST EMAIL LEGITTIMA ---")
    results.append(("Email Legittima", test_legit_email()))
    
    print("\n--- TEST URL ---")
    results.append(("Analisi URL", test_url_analysis()))
    
    # Summary
    print("\n" + "="*50)
    print("RISULTATI TEST")
    print("="*50)
    
    for name, passed in results:
        status = 'ok' if passed else 'err'
        print_status(status, f"{name}: {'PASS' if passed else 'FAIL'}")
    
    passed_count = sum(1 for _, p in results if p)
    print(f"\n{passed_count}/{len(results)} test passati")
    
    if passed_count == len(results):
        print_status('ok', 'Tutti i test passati! ✓')
        print("\nL'API locale funziona correttamente.")
        print("Puoi iniziare a usare PhishForge!")
    else:
        print_status('warn', 'Alcuni test falliti - controlla la configurazione')
        sys.exit(1)

if __name__ == "__main__":
    main()
