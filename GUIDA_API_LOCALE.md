# 🛡️ PhishForge - Guida Completa API Locale

## Avvio Rapido

### 1. Avvia l'API Locale

**Opzione A: Script automatico (consigliato)**
```bash
./run_local_api.sh
```

**Opzione B: Manuale con Python**
```bash
pip3 install -r requirements.txt
python3 -m uvicorn local_api:app --host 0.0.0.0 --port 8000 --reload
```

**Opzione C: Con Docker**
```bash
docker build -t phishforge-api .
docker run -p 8000:8000 phishforge-api
```

### 2. Apri la Web App

Una volta che l'API è avviata, apri il browser e vai a:
```
PhishForge/phishforge-web/index.html
```

O in locale:
```
http://localhost:8000/docs   # Swagger UI per testare l'API
```

---

## 🎯 Caratteristiche Principali

### Analisi Multi-Livello

La tua email viene analizzata attraverso **4 sistemi di rilevamento**:

1. **Detector Euristico Avanzato** (533k+ domini phishing noti)
   - Analizza mittente, URL, parole sospette
   - Rileva spoofing e encoding strano
   
2. **Machine Learning per Email**
   - Modello addestrato su milioni di email
   - Rileva pattern di phishing sofisticati
   
3. **Machine Learning per URL**
   - Valuta ogni URL trovato nell'email
   - Score dettagliato per link sospetti
   
4. **Analizzatore Allegati**
   - Identifica estensioni pericolose (.exe, .scr, etc.)
   - Avverte su file compound (.pdf.exe)

### Risultati

Per ogni email ricevi:
- **Score da 0-100** (quanto è sospetta)
- **Livello di Rischio** (SAFE, LOW, MEDIUM, HIGH, CRITICAL)
- **Fattori di Rischio Dettagliati** (cosa ha innescato i rilevamenti)
- **URL Trovati** (con score di rischio individuale)
- **Raccomandazioni** (cosa fare)

---

## 📊 Livelli di Rischio Spiegati

| Score | Livello | Icona | Azione |
|-------|---------|-------|--------|
| 0-15 | SAFE | ✅ | Leggi normalmente |
| 15-30 | LOW | ℹ️ | Verifica mittente |
| 30-50 | MEDIUM | ⚡ | Sospetta - non cliccare |
| 50-70 | HIGH | 🚨 | Molto probabile phishing |
| 70+ | CRITICAL | 🚨 | Phishing confermato |

---

## 🔍 Cosa Analizza in Dettaglio

### Mittente
- ✓ Indirizzo email completo
- ✓ Display name (es: "PayPal <attacker@fake.com>")
- ✓ Rileva quando mittente ufficiale è contraffatto
- ✓ Verifica contro whitelist noti

### Body dell'Email
- ✓ Ricerca parole tipiche di phishing
  - "verify account", "confirm identity", "update payment"
  - "urgente", "azione immediata", "conto bloccato"
- ✓ Analizza tone and urgency linguistica
- ✓ Encoding e Unicode tricks

### Allegati
- ✓ Nomi file sospetti (.exe, .scr, .vbs, .msi)
- ✓ File compound (.pdf.exe) - MOLTO pericoloso
- ✓ Archive con contenuti eseguibili
- ✓ Mimetype mismatch (fake extension)

### URL e Link
- ✓ Estrae tutti i link dall'email
- ✓ Controlla contro database phishing
- ✓ Analizza struttura URL (subdomain squatting)
- ✓ Short URL expansion (bit.ly, tinyurl, etc.)
- ✓ ML classification del rischio

---

## 🔐 Privacy e Sicurezza

✅ **Completamente Offline**
- L'API gira sul tuo computer locale
- Nessun dato inviato a server remoti
- Perfetto per informazioni sensibili

✅ **Nessun Log Persistente** (di default)
- Analisi effimere
- Nessun salvataggio email

✅ **Database Privato**
- Il database phishing (533k domini) è scaricato una sola volta
- Aggiornabile on-demand
- Rimane locale

---

## 🚀 Endpoint API Disponibili

L'API locale espone i seguenti endpoint:

### Health Check
```
GET /health
```
Risposta: Stato dell'API e moduli disponibili

### Analizza Email
```
POST /analyze/email
Content-Type: application/json

{
  "subject": "Verify Your Account",
  "sender": "support@paypal-verify.xyz",
  "body": "Click here to verify: ...",
  "attachments": [
    {
      "filename": "invoice.pdf.exe",
      "mime_type": "application/x-msdownload",
      "size": 1024000
    }
  ]
}
```

### Analizza URL
```
POST /analyze/url
Content-Type: application/json

{
  "url": "http://paypal-verify.xyz/account"
}
```

---

## 📝 Esempi di Test

### Email Phishing Ovvia
```
Subject: URGENT - Account Suspended!!!
Sender: security@paypal-fake.com
Body: Your account has been compromised. 
      CLICK HERE IMMEDIATELY: http://bit.ly/verify123
```
**Expected Score**: 85-95 (CRITICAL)

### Email Legittima
```
Subject: Invoice #12345
Sender: invoice@company.com
Body: Please find your invoice attached. 
      For questions, contact support@company.com
```
**Expected Score**: 5-15 (SAFE)

### Email Sofisticata (Spear-Phishing)
```
Subject: Re: Budget Review - Action needed
Sender: manager@company.com
Body: Hi, I need your help with an urgent payment.
      Please approve this transfer: [link]
      Best, Mike
```
**Expected Score**: 35-55 (depends on URL)

---

## ⚙️ Configurazione Avanzata

### Cambia Porta
```bash
python3 -m uvicorn local_api:app --port 9000
# Poi in script.js: const API_URL = "http://localhost:9000/analyze/email"
```

### Disabilita Reload
```bash
python3 -m uvicorn local_api:app --no-reload
```

### Aumenta Worker
```bash
python3 -m uvicorn local_api:app --workers 4
```

### Aggiorna Database Phishing
```bash
python3 update_databases.py
```

---

## 🐛 Troubleshooting

### "API Local Not Running"
**Soluzione:**
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>

# Restart API
./run_local_api.sh
```

### "Detector not available"
**Soluzione:**
```bash
# Install dependencies
pip3 install -r requirements.txt

# Check if PhishForge detector can be imported
python3 -c "from PhishForge.phishforge_detector import analyze_email_content; print('✓ OK')"
```

### Timeout durante analisi
**Soluzione:**
- Email molto lunga? Considera se è necessaria
- Aumenta il timeout in script.js
- Controlla le risorse del computer

---

## 💾 Note Importanti

⚠️ **PhishForge è uno STRUMENTO DI SUPPORTO, non la soluzione finale**
- Usa come primo filtro di sicurezza
- In caso di dubbi, contatta sempre il tuo IT
- Mantieni la vigilanza - non fare affidamento al 100%

✅ **Migliori Pratiche:**
- Non cliccare link in email sospette
- Contatta mittenti attraverso canali VERIFICATI
- Usa un password manager per non digitare password ogni volta
- Attiva 2FA su account importanti

---

## 📚 Ulteriori Risorse

- [README Principale](../PhishForge/README.md)
- [API Swagger UI](http://localhost:8000/docs) - Quando API è in esecuzione
- [Database Phishing Aggiornati](https://github.com/gcasaldi/PhishForge)

---

**PhishForge v2.0.0 - Local API Edition**
*Rilevamento phishing offline, veloce e privato*
