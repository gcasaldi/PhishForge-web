"""
Configurazione API per PhishForge
"""

# API Locale (più veloce, solo localhost)
LOCAL_API = {
    "url": "http://127.0.0.1:8000",
    "host": "127.0.0.1",
    "port": 8000,
    "description": "API locale - Solo per sviluppo e uso personale"
}

# API Render (cloud, pubblica) - DISABILITATA per sicurezza
RENDER_API = {
    "url": "https://phishforge-lite.onrender.com",
    "description": "API cloud Render - DEPRECATA, usa API locale"
}

# Configurazione attiva
ACTIVE_API = LOCAL_API

# Configurazione ML
ML_CONFIG = {
    "url_model_enabled": True,
    "email_model_enabled": False,  # Richiede dataset Kaggle
    "database_enabled": True,  # Database phishing 533k+ domini
    "heuristics_enabled": True
}

# Configurazione sicurezza
SECURITY_CONFIG = {
    "cors_origins": [
        "http://localhost",
        "http://localhost:*",
        "http://127.0.0.1",
        "http://127.0.0.1:*"
    ],
    "rate_limit_requests": 100,
    "rate_limit_window": 60  # secondi
}
