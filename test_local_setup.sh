#!/bin/bash

###############################################################################
# PhishForge API Local Test Suite
# Test completo dell'API locale e della webapp
###############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}PhishForge Local API Test${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Test 1: Verifica Python
echo -e "${BLUE}[TEST 1] Verifica Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 non trovato${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $(python3 --version | cut -d' ' -f2) trovato${NC}"
echo ""

# Test 2: Verifica dipendenze
echo -e "${BLUE}[TEST 2] Verifica dipendenze Python...${NC}"
required_packages=("fastapi" "uvicorn" "pydantic" "sklearn")
for package in "${required_packages[@]}"; do
    if python3 -c "import ${package}" 2>/dev/null; then
        echo -e "${GREEN}  ✓ $package${NC}"
    else
        echo -e "${RED}  ✗ $package (mancante)${NC}"
    fi
done
echo ""

# Test 3: Verifica file principali
echo -e "${BLUE}[TEST 3] Verifica file principali...${NC}"
files=("local_api.py" "PhishForge/phishforge-web/index.html" "PhishForge/phishforge-web/script.js")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}  ✓ $file${NC}"
    else
        echo -e "${RED}  ✗ $file (NON TROVATO)${NC}"
    fi
done
echo ""

# Test 4: Verifica importabilità detector
echo -e "${BLUE}[TEST 4] Verifica PhishForge detector...${NC}"
if python3 -c "import sys; sys.path.insert(0, 'PhishForge'); from phishforge_detector import analyze_email_content" 2>/dev/null; then
    echo -e "${GREEN}✓ PhishForge detector importabile${NC}"
else
    echo -e "${YELLOW}⚠ PhishForge detector non completo - necessiterà modelli ML${NC}"
fi
echo ""

# Test 5: Test API con curl (se il server è già in esecuzione)
echo -e "${BLUE}[TEST 5] Test API endpoint /health...${NC}"
if command -v curl &> /dev/null; then
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        response=$(curl -s http://localhost:8000/health)
        echo -e "${GREEN}✓ API raggiungibile${NC}"
        echo "  Risposta: $response"
    else
        echo -e "${YELLOW}⚠ API non disponibile (avvia con: ./run_local_api.sh)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ curl non disponibile - skip test API${NC}"
fi
echo ""

# Test 6: Verifica script.js contiene API locale
echo -e "${BLUE}[TEST 6] Verifica script.js usa API locale...${NC}"
if grep -q "localhost:8000" PhishForge/phishforge-web/script.js; then
    echo -e "${GREEN}✓ script.js configurato per API locale${NC}"
else
    echo -e "${RED}✗ script.js NON usa API locale!${NC}"
fi
echo ""

# Test 7: Verifica HTML contiene tab di aiuto
echo -e "${BLUE}[TEST 7] Verifica HTML ha tab 'Come Funziona'...${NC}"
if grep -q "switchTab('help')" PhishForge/phishforge-web/index.html; then
    echo -e "${GREEN}✓ HTML ha sezione aiuto interattiva${NC}"
else
    echo -e "${YELLOW}⚠ Sezione aiuto non trovata${NC}"
fi
echo ""

# Riepilogo
echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}✓ Verifica preliminare completata!${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "${YELLOW}Prossimi passi:${NC}"
echo "1. Avvia l'API: ${BLUE}./run_local_api.sh${NC}"
echo "2. Apri browser: ${BLUE}PhishForge/phishforge-web/index.html${NC}"
echo "3. Prova un'analisi con l'email di test"
echo ""
echo -e "${BLUE}================================${NC}"
echo "Email di test disponibili:"
echo "- phishing: test_phishing_email.py"
echo "- legittima: test_legit_email.py"
echo "================================${NC}"
