#!/bin/bash

# PhishForge Detector - Test Suite
# Runs tests on example emails to verify the detector works correctly

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║         🛡️  PHISHFORGE DETECTOR - TEST SUITE                      ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Running automated tests on example emails..."
echo ""

# Test counter
TESTS_RUN=0
TESTS_PASSED=0

# Test 1: High risk phishing email
echo "═══════════════════════════════════════════════════════════════════════"
echo "🧪 Test 1: High-risk phishing email"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

OUTPUT=$(python "PhishForge Detector.py" \
  --subject "URGENT: Verify Your Account Now!" \
  --sender "PayPal Security <hacker@paypal-verify.xyz>" \
  --body-file esempio_phishing.txt)

echo "$OUTPUT"
echo ""

# Check if high risk was detected
if echo "$OUTPUT" | grep -q "HIGH RISK"; then
    echo "✅ PASSED: Correctly identified as HIGH RISK"
    ((TESTS_PASSED++))
else
    echo "❌ FAILED: Should be HIGH RISK"
fi
((TESTS_RUN++))

echo ""
echo ""

# Test 2: Low risk legitimate email
echo "═══════════════════════════════════════════════════════════════════════"
echo "🧪 Test 2: Low-risk legitimate email"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

OUTPUT=$(python "PhishForge Detector.py" \
  --subject "Monthly summary" \
  --sender "Customer Service <noreply@yourbank.com>" \
  --body-file esempio_legittimo.txt)

echo "$OUTPUT"
echo ""

# Check if low risk was detected
if echo "$OUTPUT" | grep -q "LOW RISK"; then
    echo "✅ PASSED: Correctly identified as LOW RISK"
    ((TESTS_PASSED++))
else
    echo "❌ FAILED: Should be LOW RISK"
fi
((TESTS_RUN++))

echo ""
echo ""

# Summary
echo "═══════════════════════════════════════════════════════════════════════"
echo "📊 TEST SUMMARY"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "Tests run:    $TESTS_RUN"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $((TESTS_RUN - TESTS_PASSED))"
echo ""

if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
    echo "✅ All tests passed! PhishForge is working correctly."
    exit 0
else
    echo "⚠️  Some tests failed. Please check the output above."
    exit 1
fi
