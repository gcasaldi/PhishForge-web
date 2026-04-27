#!/bin/bash

###############################################################################
# PhishForge Local API Launcher
# 
# Avvia l'API locale FastAPI per il rilevamento phishing
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}PhishForge Local API Launcher${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 non trovato. Installa Python 3.8+${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python trovato: $(python3 --version)${NC}"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 non trovato${NC}"
    exit 1
fi

echo -e "${GREEN}✓ pip3 trovato${NC}"

# Check if local_api.py exists
if [ ! -f "local_api.py" ]; then
    echo -e "${RED}❌ local_api.py non trovato nella directory corrente${NC}"
    echo -e "${YELLOW}   Assicurati di eseguire questo script dalla root del progetto${NC}"
    exit 1
fi

echo -e "${GREEN}✓ local_api.py trovato${NC}"
echo ""

# Check dependencies
echo -e "${BLUE}Verificando dipendenze...${NC}"

required_packages=("fastapi" "uvicorn" "pydantic")
missing_packages=()

for package in "${required_packages[@]}"; do
    if ! python3 -c "import ${package}" 2>/dev/null; then
        missing_packages+=("$package")
    fi
done

if [ ${#missing_packages[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠ Pacchetti mancanti: ${missing_packages[*]}${NC}"
    echo -e "${YELLOW}   Installazione in corso...${NC}"
    pip3 install fastapi uvicorn scikit-learn pandas requests beautifulsoup4
    echo -e "${GREEN}✓ Dipendenze installate${NC}"
else
    echo -e "${GREEN}✓ Tutte le dipendenze trovate${NC}"
fi

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}✓ Avvio API locale su http://localhost:8000${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "${YELLOW}💡 Suggerimenti:${NC}"
echo -e "   • Accedi alla web app: http://localhost:8000/docs (Swagger UI)"
echo -e "   • Accedi alla app web: apri PhishForge/phishforge-web/index.html in un browser"
echo -e "   • Per terminare: Premi Ctrl+C"
echo ""

# Start the API
python3 -m uvicorn local_api:app --host 0.0.0.0 --port 8000 --reload

