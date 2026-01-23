#!/usr/bin/env python3
"""
Test ML Integration in PhishForge API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("="*60)
print("Testing ML Integration in PhishForge API")
print("="*60)
print("\nStarting API server...")

# Start the API server in background
import subprocess
import time
import sys

server_process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "api:app", "--host", "127.0.0.1", "--port", "8000"],
    cwd="/workspaces/PhishForge-Lite",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for server to start
time.sleep(3)

try:

try:
    # Test 1: Analyze URL endpoint with phishing URL
    print("\n1. Testing /analyze-url with phishing URL")
    print("-" * 60)
    response = requests.post(
        f"{BASE_URL}/analyze-url",
        json={"url": "http://paypal-verify.com/login"}
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Risk Score: {result['risk_score']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"From Database: {result['from_phishing_database']}")
    print(f"Indicators: {len(result['indicators'])} found")
    for indicator in result['indicators'][:3]:
        print(f"  - {indicator['category']}: {indicator['detail'][:80]}")

    # Test 2: Analyze URL endpoint with legitimate URL
    print("\n2. Testing /analyze-url with legitimate URL")
    print("-" * 60)
    response = requests.post(
        f"{BASE_URL}/analyze-url",
        json={"url": "https://www.google.com/search"}
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Risk Score: {result['risk_score']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Indicators: {len(result['indicators'])} found")

    # Test 3: Analyze email endpoint
    print("\n3. Testing /analyze with phishing email")
    print("-" * 60)
    response = requests.post(
        f"{BASE_URL}/analyze",
        json={
            "sender": "security@paypal-verify.com",
            "subject": "Urgent: Verify your account immediately!",
            "body": "Your PayPal account has been suspended. Click here to verify: http://paypal-verify.com/login"
        }
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Risk Score: {result['risk_score']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"URLs found: {result['urls']}")
    print(f"Findings: {len(result['findings'])} detected")
    for finding in result['findings'][:3]:
        print(f"  - {finding['category']}: {finding['detail'][:80]}")

    print("\n" + "="*60)
    print("✅ All tests completed successfully!")
    print("="*60)

finally:
    # Stop the server
    server_process.terminate()
    server_process.wait()

