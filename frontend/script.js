// Configurazione API
const API_BASE_URL = 'https://phishforge-api.onrender.com'; // Cambia dopo il deploy su Render

// Esempi predefiniti
const examples = {
    phishing: {
        sender: 'PayPal Security <noreply@paypal-verify.xyz>',
        subject: 'URGENT: Your account will be suspended!',
        body: 'Your PayPal account has been locked due to suspicious activity.\n\nClick here immediately to verify your identity: http://bit.ly/paypal-verify-now\n\nWARNING: You have only 24 hours before permanent suspension!\n\nFailure to verify will result in account closure.'
    },
    legitimate: {
        sender: 'Company Newsletter <newsletter@company.com>',
        subject: 'Monthly Newsletter - November 2025',
        body: 'Hello valued customer,\n\nHere is our monthly newsletter with updates and news about our services.\n\nVisit our website for more information: https://www.company.com\n\nBest regards,\nThe Team'
    }
};

// Elementi DOM
const form = document.getElementById('emailForm');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const analyzeBtn = document.getElementById('analyzeBtn');

// Event Listeners
form.addEventListener('submit', handleSubmit);

// Gestione submit del form
async function handleSubmit(e) {
    e.preventDefault();
    
    const sender = document.getElementById('sender').value;
    const subject = document.getElementById('subject').value;
    const body = document.getElementById('body').value;
    
    // Mostra loading
    showLoading();
    
    try {
        const result = await analyzeEmail(sender, subject, body);
        displayResults(result);
    } catch (error) {
        showError(error.message);
    }
}

// Chiamata API
async function analyzeEmail(sender, subject, body) {
    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                sender: sender,
                subject: subject,
                body: body
            })
        });
        
        if (!response.ok) {
            throw new Error('Errore durante l\'analisi. Riprova più tardi.');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// Mostra loading
function showLoading() {
    results.classList.add('hidden');
    loading.classList.remove('hidden');
    analyzeBtn.disabled = true;
}

// Nascondi loading
function hideLoading() {
    loading.classList.add('hidden');
    analyzeBtn.disabled = false;
}

// Mostra risultati
function displayResults(data) {
    hideLoading();
    
    // Risk Card
    const riskCard = document.getElementById('riskCard');
    const riskIcon = document.getElementById('riskIcon');
    const riskLevel = document.getElementById('riskLevel');
    const riskScore = document.getElementById('riskScore');
    const riskBarFill = document.getElementById('riskBarFill');
    const recommendation = document.getElementById('recommendation').querySelector('p');
    
    // Configura colori e icone in base al livello di rischio
    let colorClass = '';
    let iconClass = '';
    
    switch(data.risk_level) {
        case 'high':
            colorClass = 'risk-high';
            iconClass = 'fa-exclamation-triangle';
            break;
        case 'medium':
            colorClass = 'risk-medium';
            iconClass = 'fa-exclamation-circle';
            break;
        case 'low':
            colorClass = 'risk-low';
            iconClass = 'fa-check-circle';
            break;
    }
    
    // Applica stili
    riskCard.className = `card risk-card ${colorClass}`;
    riskIcon.className = `fas ${iconClass}`;
    riskLevel.textContent = data.risk_level.toUpperCase();
    riskScore.textContent = `${data.risk_score}/100`;
    riskBarFill.style.width = `${data.risk_percentage}%`;
    riskBarFill.className = `risk-bar-fill ${colorClass}`;
    recommendation.textContent = data.recommendation;
    
    // Findings
    const findingsContainer = document.getElementById('findingsContainer');
    findingsContainer.innerHTML = '';
    
    if (data.findings && data.findings.length > 0) {
        const findingsCard = document.createElement('div');
        findingsCard.className = 'card';
        
        const header = document.createElement('h3');
        header.innerHTML = `<i class="fas fa-exclamation-triangle"></i> Problemi Rilevati (${data.findings.length})`;
        findingsCard.appendChild(header);
        
        data.findings.forEach((finding, index) => {
            const findingElement = createFindingElement(finding, index);
            findingsCard.appendChild(findingElement);
        });
        
        findingsContainer.appendChild(findingsCard);
    }
    
    // URLs
    const urlsContainer = document.getElementById('urlsContainer');
    const urlsList = document.getElementById('urlsList');
    
    if (data.urls && data.urls.length > 0) {
        urlsContainer.classList.remove('hidden');
        urlsList.innerHTML = '';
        
        data.urls.forEach(url => {
            const urlItem = document.createElement('div');
            urlItem.className = 'url-item';
            urlItem.innerHTML = `
                <i class="fas fa-link"></i>
                <span>${escapeHtml(url)}</span>
            `;
            urlsList.appendChild(urlItem);
        });
    } else {
        urlsContainer.classList.add('hidden');
    }
    
    // Mostra risultati
    results.classList.remove('hidden');
    
    // Scroll ai risultati
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Crea elemento per un finding
function createFindingElement(finding, index) {
    const findingDiv = document.createElement('div');
    findingDiv.className = 'finding-item';
    
    const header = document.createElement('div');
    header.className = 'finding-header';
    header.onclick = () => toggleFinding(index);
    
    header.innerHTML = `
        <div class="finding-title">
            <span>${finding.educational.title}</span>
            <span class="risk-badge">+${finding.risk_score}</span>
        </div>
        <div class="finding-detail">${escapeHtml(finding.detail)}</div>
        <i class="fas fa-chevron-down finding-toggle" id="toggle-${index}"></i>
    `;
    
    const content = document.createElement('div');
    content.className = 'finding-content';
    content.id = `content-${index}`;
    content.style.display = 'none';
    
    content.innerHTML = `
        <div class="finding-explanation">
            <strong>💡 ${escapeHtml(finding.educational.explanation)}</strong>
        </div>
        <div class="finding-tips">
            <strong>📚 Consigli:</strong>
            <ul>
                ${finding.educational.tips.map(tip => `<li>${escapeHtml(tip)}</li>`).join('')}
            </ul>
        </div>
    `;
    
    findingDiv.appendChild(header);
    findingDiv.appendChild(content);
    
    return findingDiv;
}

// Toggle finding espansione
function toggleFinding(index) {
    const content = document.getElementById(`content-${index}`);
    const toggle = document.getElementById(`toggle-${index}`);
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        toggle.classList.add('rotated');
    } else {
        content.style.display = 'none';
        toggle.classList.remove('rotated');
    }
}

// Mostra errore
function showError(message) {
    hideLoading();
    
    results.innerHTML = `
        <div class="card error-card">
            <i class="fas fa-exclamation-circle"></i>
            <h3>Errore</h3>
            <p>${escapeHtml(message)}</p>
            <button class="btn btn-secondary" onclick="resetForm()">
                <i class="fas fa-redo"></i> Riprova
            </button>
        </div>
    `;
    
    results.classList.remove('hidden');
}

// Carica esempio
function loadExample(type) {
    const example = examples[type];
    
    document.getElementById('sender').value = example.sender;
    document.getElementById('subject').value = example.subject;
    document.getElementById('body').value = example.body;
    
    // Scroll al form
    form.scrollIntoView({ behavior: 'smooth' });
}

// Reset form
function resetForm() {
    form.reset();
    results.classList.add('hidden');
    form.scrollIntoView({ behavior: 'smooth' });
}

// Escape HTML per sicurezza
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Check API health al caricamento (opzionale)
async function checkApiHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('API is healthy');
        }
    } catch (error) {
        console.warn('API health check failed:', error);
    }
}

// Esegui health check
checkApiHealth();
const API_BASE_URL = "http://localhost:8000";  // backend locale

async function analyzeEmail() {
  const subject = document.getElementById("subject").value;
  const sender = document.getElementById("sender").value;
  const body = document.getElementById("body").value;

  const resultDiv = document.getElementById("result");
  const detailsList = document.getElementById("details");

  resultDiv.textContent = "Analisi in corso...";
  detailsList.innerHTML = "";

  const resp = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ subject, sender, body })
  });

  const data = await resp.json();

  resultDiv.textContent = `Risk score: ${data.risk_score} (${data.risk_level})`;
  data.details.forEach(d => {
    const li = document.createElement("li");
    li.textContent = d;
    detailsList.appendChild(li);
  });
}
