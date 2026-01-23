#!/bin/bash

# Script per testare l'API PhishForge

echo "======================================"
echo "  PhishForge API Test Suite"
echo "======================================"
echo ""

API_URL="http://localhost:8000"

# Colori per output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funzione per testare un endpoint
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    
    echo -e "${YELLOW}Testing: $name${NC}"
    echo "Endpoint: $method $endpoint"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ Success (HTTP $http_code)${NC}"
        echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    else
        echo -e "${RED}✗ Failed (HTTP $http_code)${NC}"
        echo "$body"
    fi
    
    echo ""
    echo "--------------------------------------"
    echo ""
}

# Test 1: Health Check
test_endpoint "Health Check" "GET" "/health"

# Test 2: Root endpoint
test_endpoint "Root Info" "GET" "/"

# Test 3: Phishing email (high risk)
test_endpoint "Phishing Email Analysis" "POST" "/analyze" '{
  "sender": "PayPal Security <noreply@paypal-verify.xyz>",
  "subject": "Urgent! Your account will be suspended!",
  "body": "Your PayPal account has been locked due to suspicious activity. Click here immediately to verify your identity: http://bit.ly/paypal-verify-now. You have 24 hours before permanent suspension!"
}'

# Test 4: Legitimate email (low risk)
test_endpoint "Legitimate Email Analysis" "POST" "/analyze" '{
  "sender": "Newsletter <info@company.com>",
  "subject": "Monthly update",
  "body": "Hello, here is our monthly newsletter with updates about our services. Visit our website at https://www.company.com for more information."
}'

# Test 5: Medium risk email
test_endpoint "Medium Risk Email Analysis" "POST" "/analyze" '{
  "sender": "Support Team <support@service-help.com>",
  "subject": "Password reset requested",
  "body": "We received a request to reset your password. If this was you, please click the link below. The link will expire in 1 hour."
}'

# Test 6: Get suspicious keywords
test_endpoint "Get Suspicious Keywords" "GET" "/keywords"

# Test 7: Get suspicious TLDs
test_endpoint "Get Suspicious TLDs" "GET" "/tlds"

# Test 8: Get URL shorteners
test_endpoint "Get URL Shorteners" "GET" "/url-shorteners"

echo "======================================"
echo "  Test Suite Completed"
echo "======================================"
