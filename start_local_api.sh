#!/bin/bash

# Script per avviare l'API locale PhishForge
# SOLO per uso locale - non esposta pubblicamente

echo "🚀 Avvio PhishForge Local API..."
echo "================================"
echo ""

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 non trovato. Installare Python 3.8+"
    exit 1
fi

echo "✓ Python trovato: $(python3 --version)"

# Verifica dipendenze
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 Installazione dipendenze..."
    pip install -r requirements.txt
fi

echo "✓ Dipendenze installate"
echo ""

# Avvia l'API
echo "🔧 Avvio server su http://127.0.0.1:8000"
echo "📚 Documentazione API: http://127.0.0.1:8000/docs"
echo ""
echo "⚠️  IMPORTANTE: L'API è accessibile SOLO da localhost per sicurezza"
echo ""
echo "Premi Ctrl+C per fermare il server"
echo ""

python3 local_api.py
