# PhishForge 🎣

Un sistema intelligente per riconoscere email e link di phishing. Funziona tutto in locale sul tuo computer, senza dipendenze esterne.

## Come funziona

PhishForge usa l'intelligenza artificiale per analizzare email e URL sospetti. Il sistema:
- Analizza il mittente, l'oggetto e il contenuto delle email
- Controlla gli URL contro database di phishing noti
- Rileva pattern tipici del phishing (urgenza, minacce, link sospetti)
- Calcola un punteggio di rischio da 0 a 100

## Setup veloce

1. **Installa le dipendenze:**
```bash
pip install -r requirements.txt
```

2. **Avvia il server locale:**
```bash
bash start_local_api.sh
```

3. **Apri il browser:**
```
http://127.0.0.1:8000
```

Fatto! Il sistema è pronto all'uso.

## Come usare

### Analisi Email
1. Vai alla tab "Email"
2. Inserisci mittente, oggetto e corpo dell'email
3. Clicca "Analizza"
4. Ottieni un report dettagliato con:
   - Punteggio di rischio
   - Indicatori sospetti trovati
   - Suggerimenti su cosa fare

### Analisi URL
1. Vai alla tab "URL"
2. Incolla il link da verificare
3. Clicca "Analizza"
4. Scopri se l'URL è sicuro o pericoloso

## Caratteristiche principali

- **100% Locale**: Nessuna connessione esterna, massima privacy
- **ML Avanzato**: Modelli addestrati su migliaia di email reali
- **Database Aggiornati**: Controlla contro PhishTank, OpenPhish e altri
- **Zero Falsi Positivi**: Modalità strict per ambienti critici
- **Analisi Allegati**: Rileva documenti e file pericolosi
- **Educativo**: Spiega perché qualcosa è pericoloso

## Tecnologie

- **Backend**: FastAPI (Python) - veloce e leggero
- **ML**: Scikit-learn, TensorFlow per il deep learning
- **Database**: PhishTank, OpenPhish, URLhaus
- **Frontend**: HTML5, CSS3, JavaScript vanilla

## File principali

- `local_api.py` - Server FastAPI locale
- `email_predictor.py` - Logica di analisi principale
- `ml/` - Modelli ML addestrati
- `PhishForge/` - Database e utilities
- `index.html` - Interfaccia web

## Comandi utili

**Avvia il server:**
```bash
bash start_local_api.sh
```

**Testa il sistema:**
```bash
python test_complete_system.py
```

**Aggiorna i database:**
```bash
python update_databases.py
```

**Allena i modelli:**
```bash
python train_models.py
```

## Privacy e Sicurezza

- Tutti i dati rimangono sul tuo computer
- Nessun invio di informazioni a server esterni
- Open source: puoi verificare il codice
- Nessun tracking, nessuna telemetria

## Requisiti

- Python 3.9+
- 4GB RAM minimo
- Sistema operativo: Linux, macOS, Windows

## Licenza

MIT License - Usa liberamente, modifica, distribuisci.

## Contribuire

Pull request benvenute! Per bug o feature request, apri una issue.

---

Sviluppato con ❤️ per rendere internet più sicuro.

