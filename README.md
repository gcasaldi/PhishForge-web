# PhishForge Frontend - Web App Pubblica

Interfaccia web per l'analizzatore di email phishing PhishForge.

## 🌐 Demo Live

Questa web app sarà pubblicata su GitHub Pages e comunica con l'API backend privata su Render.

## 📁 Struttura

```
frontend/
├── index.html    # Interfaccia principale
├── script.js     # Logica JavaScript
└── style.css     # Stili CSS
```

## 🚀 Come Usare

### 1. Configurazione API

In `script.js`, aggiorna l'URL dell'API dopo il deploy su Render:

```javascript
const API_BASE
```

### 2. Test Locale

Apri semplicemente `index.html` in un browser.

### 3. Deploy su GitHub Pages

#### Metodo 1: Interfaccia GitHub
1. Vai su **Settings** del repository
2. Sezione **Pages**
3. Source: **Deploy from a branch**
4. Branch: **main** → cartella: **/frontend**
5. Salva

#### Metodo 2: GitHub Actions
GitHub rileverà automaticamente i file HTML e li pubblicherà.

## ✨ Funzionalità

- ✅ Interfaccia moderna e responsive
- ✅ Analisi in tempo reale delle email
- ✅ Visualizzazione dettagliata dei rischi
- ✅ Spiegazioni educative per ogni problema
- ✅ Esempi predefiniti da testare
- ✅ Design mobile-friendly

## 🎨 Design

- Gradiente moderno viola/blu
- Card con shadow ed effetti
- Icone Font Awesome
- Animazioni fluide
- Completamente responsive

## 🔒 Sicurezza

- Il codice Python rimane privato nel repository backend
- Solo l'interfaccia HTML/CSS/JS è pubblica
- Comunicazione sicura con l'API via HTTPS (dopo deploy)

## 📱 Compatibilità

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## 🛠️ Personalizzazione

### Colori
Modifica le variabili CSS in `style.css`:

```css
:root {
    --primary-color: #2563eb;
    --danger-color: #dc2626;
    --warning-color: #f59e0b;
    --success-color: #10b981;
}
```

### Testi
Modifica i contenuti in `index.html`.

### Logica
Modifica le funzioni in `script.js`.

## 📄 Licenza

MIT License