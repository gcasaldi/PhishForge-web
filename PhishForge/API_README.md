# PhishForge API

API REST per il rilevamento di email phishing basata su FastAPI.

## 🚀 Installazione

```bash
# Installa le dipendenze
pip install -r requirements.txt
```

## 📦 Avvio dell'API

### Metodo 1: Usando uvicorn direttamente
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Metodo 2: Eseguendo il file Python
```bash
python api.py
```

L'API sarà disponibile su `http://localhost:8000`

## 📚 Documentazione

Una volta avviata l'API, puoi accedere a:

- **Swagger UI (interattiva)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 Endpoints

### `GET /`
Informazioni base sull'API

### `GET /health`
Health check per verificare lo stato dell'API

**Risposta:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "detector_loaded": true
}
```

### `POST /analyze`
Analizza un'email per rilevare segnali di phishing

**Request Body:**
```json
{
  "sender": "PayPal Security <noreply@paypal-secure.xyz>",
  "subject": "Urgent: Verify your account immediately!",
  "body": "Your PayPal account has been locked. Click here to verify: http://bit.ly/verify123"
}
```

**Risposta:**
```json
{
  "risk_score": 45,
  "risk_level": "high",
  "risk_percentage": 45.0,
  "findings": [
    {
      "risk_score": 15,
      "category": "sender_mismatch",
      "detail": "Display name mentions 'paypal' but email domain doesn't match",
      "educational": {
        "title": "📧 Suspicious Sender",
        "explanation": "...",
        "tips": [...]
      }
    }
  ],
  "urls": ["http://bit.ly/verify123"],
  "recommendation": "🚨 HIGH RISK: Do not click any links or provide personal information. Delete this email immediately."
}
```

### `GET /keywords`
Lista delle parole chiave sospette utilizzate nell'analisi

### `GET /tlds`
Lista dei domini di primo livello (TLD) considerati sospetti

### `GET /url-shorteners`
Lista degli URL shortener rilevati

## 💻 Esempi di Utilizzo

### cURL
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "PayPal <fake@paypal-verify.xyz>",
    "subject": "Account suspended!",
    "body": "Click here immediately: http://bit.ly/paypal123"
  }'
```

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "sender": "PayPal <fake@paypal-verify.xyz>",
        "subject": "Account suspended!",
        "body": "Click here immediately: http://bit.ly/paypal123"
    }
)

result = response.json()
print(f"Risk Level: {result['risk_level']}")
print(f"Risk Score: {result['risk_score']}")
```

### JavaScript (fetch)
```javascript
fetch('http://localhost:8000/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    sender: 'PayPal <fake@paypal-verify.xyz>',
    subject: 'Account suspended!',
    body: 'Click here immediately: http://bit.ly/paypal123'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 🔒 CORS

L'API è configurata per accettare richieste da qualsiasi origine (`allow_origins=["*"]`). 

**In produzione**, modifica il file `api.py` per specificare solo i domini autorizzati:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tua-app.com"],  # Domini specifici
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🚀 Deploy

### Render.com
1. Crea un nuovo Web Service
2. Collega il repository GitHub
3. Imposta:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api:app --host 0.0.0.0 --port $PORT`

### Railway.app
1. Crea un nuovo progetto da GitHub
2. Railway rileverà automaticamente Python
3. Aggiungi variabile d'ambiente se necessario

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build e run:
```bash
docker build -t phishforge-api .
docker run -p 8000:8000 phishforge-api
```

## 📱 Integrazione con App Mobile

L'API può essere facilmente integrata con:
- **Flutter/Dart**: package `http` o `dio`
- **React Native**: `fetch` o `axios`
- **Swift (iOS)**: `URLSession`
- **Kotlin (Android)**: `Retrofit` o `OkHttp`

## 🔧 Sviluppo

Per modificare il comportamento del detector, modifica il file `PhishForge Detector.py`.

L'API caricherà automaticamente le modifiche in modalità reload:
```bash
uvicorn api:app --reload
```

## 📝 Licenza

MIT License - vedi file LICENSE
