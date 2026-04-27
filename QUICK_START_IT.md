# 🚀 Quick Start - PhishForge API Locale

## Avvia in 3 Comandi

```bash
# 1. Vai nella cartella del progetto
cd /workspaces/PhishForge-web

# 2. Avvia l'API locale
./run_local_api.sh

# 3. Apri il browser (in un'altra finestra terminal)
# Linux/Mac:
open PhishForge/phishforge-web/index.html

# Windows: scrivere il path completo nel browser
# es: C:\Users\tuonome\PhishForge-web\PhishForge\phishforge-web\index.html
```

---

## Cosa Vedrai

✅ **Pagina web con 2 tab:**
- **🔍 Analizzatore**: Incolla email e ricevi analisi phishing
- **❓ Come Funziona**: Guida completa + FAQ

✅ **Status dell'API**: Verde = pronto, Rosso = avvia con run_local_api.sh

---

## Test Rapido

### Copia una di queste email nel form per testare:

**PHISHING (score alto):**
```
Mittente: security@paypal-verify.xyz
Oggetto: ⚠️ URGENT: Verify Your Account Now!!!
Body: Your account has been suspended due to suspicious activity.
Click here IMMEDIATELY to verify: http://bit.ly/paypal-verify-now
Do NOT ignore this message!
```

**LEGITTIMA (score basso):**
```
Mittente: support@amazon.com
Oggetto: Your Order #12345 Has Shipped
Body: Hi,
Your order has been shipped! Track your package here:
https://amazon.com/orders/12345
Thank you for shopping with us.
```

---

## 📊 Capire i Risultati

**Score 0-100:**
- 0-15 ✅ SAFE = Email sicura
- 15-30 ℹ️ LOW = Verifica
- 30-50 ⚡ MEDIUM = Sospetta
- 50-70 🚨 HIGH = Probabile phishing
- 70+ 🚨 CRITICAL = Phishing confermato

**Per ogni email ricevi:**
1. Score totale
2. Livello rischio con icona
3. Raccomandazione immediata
4. Dettagli dei fattori rilevati
5. Lista URL trovati con loro rischio

---

## 🐛 Se Non Funziona

### Errore: "API Local Not Running"
```bash
# Termina processo sulla porta 8000
lsof -i :8000     # Vedi il processo
kill -9 <PID>     # Termina

# Riavvia
./run_local_api.sh
```

### Errore: "Detector not available"
```bash
# Installa dipendenze
pip3 install -r requirements.txt

# Riavvia
./run_local_api.sh
```

### Errore: "Permission denied" 
```bash
# Rendi eseguibile
chmod +x run_local_api.sh
chmod +x test_local_setup.sh

./run_local_api.sh
```

---

## 📚 Ulteriori Informazioni

- **Guida completa**: Leggi `GUIDA_API_LOCALE.md`
- **API Documentation**: http://localhost:8000/docs (quando API è in esecuzione)
- **Swagger UI**: Prova endpoint direttamente dal browser
- **Troubleshooting**: `test_local_setup.sh` per diagnostica

---

## ⚠️ Importante

**PhishForge è uno STRUMENTO DI SUPPORTO:**
- ✅ Usa come primo filtro
- ✅ Non clicare link sospetti
- ✅ Verifica mittente da canali UFFICIALI
- ✅ Contatta IT in caso di dubbio

**NON fare affidamento al 100% da PhishForge!**

---

**Fatto! Hai il tuo rilevatore phishing offline e privato.**

Domande? Consulta la guida completa o i log dell'API.

Buona analisi! 🛡️
