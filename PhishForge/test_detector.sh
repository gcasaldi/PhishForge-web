#!/bin/bash

echo "🧪 Test 1: Phishing email (high risk)"
echo "=========================================="
python "PhishForge Detector.py" \
  --subject "URGENT: Verify Your Account Now!" \
  --sender "PayPal Security <hacker@paypal-verify.xyz>" \
  --body-file esempio_phishing.txt

echo ""
echo ""
echo "🧪 Test 2: Legitimate email (low risk)"
echo "=========================================="
python "PhishForge Detector.py" \
  --subject "Monthly summary" \
  --sender "Customer Service <noreply@yourbank.com>" \
  --body-file esempio_legittimo.txt
