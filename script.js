// API Configuration
const API_BASE_URL = 'https://phishforge-lite.onrender.com';

// Stats update interval (10 seconds)
const STATS_UPDATE_INTERVAL = 10000;
let statsInterval = null;

// Predefined examples
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
    },
    phishingUrl: 'http://paypal-verify.xyz/account/login',
    legitimateUrl: 'https://www.paypal.com'
};

// DOM Elements
const form = document.getElementById('emailForm');
const urlForm = document.getElementById('urlForm');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const analyzeBtn = document.getElementById('analyzeBtn');
const analyzeUrlBtn = document.getElementById('analyzeUrlBtn');

// Current mode
let currentMode = 'email';

// Event Listeners
form.addEventListener('submit', handleSubmit);
urlForm.addEventListener('submit', handleUrlSubmit);

// Initialize stats on page load
document.addEventListener('DOMContentLoaded', () => {
    fetchStats(); // Fetch immediately
    statsInterval = setInterval(fetchStats, STATS_UPDATE_INTERVAL); // Then every 10 seconds
});

// Fetch real-time statistics
async function fetchStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        if (!response.ok) {
            throw new Error('Failed to fetch statistics');
        }
        
        const data = await response.json();
        updateStatsDisplay(data);
    } catch (error) {
        console.error('Error fetching stats:', error);
        // Show placeholder values if API fails
        updateStatsDisplay({
            total_analyzed: '-',
            high_risk: '-',
            critical_risk: '-'
        });
    }
}

// Update statistics display
function updateStatsDisplay(stats) {
    const totalAnalyzed = document.getElementById('totalAnalyzed');
    const highRisk = document.getElementById('highRisk');
    const criticalRisk = document.getElementById('criticalRisk');
    
    if (totalAnalyzed) {
        animateNumber(totalAnalyzed, stats.total_analyzed);
    }
    if (highRisk) {
        animateNumber(highRisk, stats.high_risk);
    }
    if (criticalRisk) {
        animateNumber(criticalRisk, stats.critical_risk);
    }
}

// Animate number changes
function animateNumber(element, newValue) {
    const currentValue = parseInt(element.textContent) || 0;
    const targetValue = parseInt(newValue) || 0;
    
    if (currentValue === targetValue || element.textContent === '-') {
        element.textContent = formatNumber(targetValue);
        return;
    }
    
    const duration = 500; // milliseconds
    const steps = 20;
    const stepValue = (targetValue - currentValue) / steps;
    const stepDuration = duration / steps;
    
    let currentStep = 0;
    const timer = setInterval(() => {
        currentStep++;
        const value = Math.round(currentValue + (stepValue * currentStep));
        element.textContent = formatNumber(value);
        
        if (currentStep >= steps) {
            clearInterval(timer);
            element.textContent = formatNumber(targetValue);
        }
    }, stepDuration);
}

// Format number with thousands separator
function formatNumber(num) {
    if (isNaN(num)) return '-';
    return num.toLocaleString('en-US');
}

// Event Listeners
form.addEventListener('submit', handleSubmit);
urlForm.addEventListener('submit', handleUrlSubmit);

// Switch mode function
function switchMode(mode) {
    currentMode = mode;
    
    // Update tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        if (btn.dataset.mode === mode) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Update forms
    document.querySelectorAll('.analysis-mode').forEach(modeDiv => {
        if (modeDiv.id === mode + 'Mode') {
            modeDiv.classList.add('active');
        } else {
            modeDiv.classList.remove('active');
        }
    });
    
    // Hide results when switching modes
    results.classList.add('hidden');
}

// Form submit handler
async function handleSubmit(e) {
    e.preventDefault();
    
    const sender = document.getElementById('sender').value;
    const subject = document.getElementById('subject').value;
    const body = document.getElementById('body').value;
    
    // Show loading
    showLoading();
    
    try {
        const result = await analyzeEmail(sender, subject, body);
        displayResults(result, 'email');
    } catch (error) {
        showError(error.message);
    }
}

// URL form submit handler
async function handleUrlSubmit(e) {
    e.preventDefault();
    
    const url = document.getElementById('url').value;
    
    // Show loading
    showLoading();
    
    try {
        const result = await analyzeUrl(url);
        displayResults(result, 'url');
    } catch (error) {
        showError(error.message);
    }
}

// API call
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
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || 'Analysis error. Please try again later.');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        // Network error handling
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('Connection error. Check your internet connection and try again.');
        }
        throw error;
    }
}

// URL analysis API call
async function analyzeUrl(url) {
    try {
        const response = await fetch(`${API_BASE_URL}/analyze-url`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || 'Analysis error. Please try again later.');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        // Network error handling
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('Connection error. Check your internet connection and try again.');
        }
        throw error;
    }
}

// Show loading
function showLoading() {
    results.classList.add('hidden');
    loading.classList.remove('hidden');
    analyzeBtn.disabled = true;
    analyzeUrlBtn.disabled = true;
}

// Hide loading
function hideLoading() {
    loading.classList.add('hidden');
    analyzeBtn.disabled = false;
    analyzeUrlBtn.disabled = false;
}

// Global translation map for Italian to English
const italianToEnglishMap = {
    "🚨 PERICOLO ELEVATO: Non cliccare sui link, non fornire informazioni personali. Elimina questa email.": 
        "🚨 DANGER: This email is high risk. Do NOT click any links or share personal information. Delete this message.",
    "✅ Rischio basso, ma verifica sempre il dominio e usa HTTPS quando possibile.": 
        "✅ Low risk, but always double-check the sender and the domain before trusting any links.",
    "✅ Rischio basso, ma rimani vigile. Verifica sempre l'identità del mittente per richieste inusuali.":
        "✅ Low risk, but stay vigilant. Always verify the sender's identity for unusual requests.",
    "🚨 PERICOLO: Questo URL è ad alto rischio. NON visitarlo. Potrebbe rubare dati o installare malware.":
        "🚨 DANGER: This URL is high risk. Do NOT visit it. It may steal data, impersonate trusted services, or install malware.",
    "⚠️ ATTENZIONE: Questa email presenta caratteristiche tipiche di phishing. Non cliccare sui link e non fornire informazioni personali.":
        "⚠️ WARNING: This email shows typical phishing characteristics. Do not click links or provide personal information.",
    "⚡ CAUTELA: Questa email presenta alcuni segnali sospetti. Verifica attentamente prima di intraprendere azioni.":
        "⚡ CAUTION: This email has some suspicious signs. Verify carefully before taking action.",
    "✅ Questa email sembra legittima, ma mantieni sempre un atteggiamento prudente.":
        "✅ This email appears legitimate, but always maintain a cautious attitude.",
    // Additional Italian phrases
    "Mittente sospetto": "Suspicious sender",
    "URL sospetto": "Suspicious URL",
    "Dominio non sicuro": "Unsafe domain",
    "Linguaggio urgente": "Urgent language",
    "Richiesta di informazioni personali": "Request for personal information",
    "Link mascherato": "Masked link",
    "Errori grammaticali": "Grammar errors",
    "Allegato sospetto": "Suspicious attachment",
    "Phishing": "Phishing",
    "Legittimo": "Legitimate",
    "Sospetto": "Suspicious",
    "Alto rischio": "High risk",
    "Medio rischio": "Medium risk",
    "Basso rischio": "Low risk",
    "Errore": "Error",
    "Analisi fallita": "Analysis failed",
    "Connessione fallita": "Connection failed"
};

// Global function to translate Italian text to English
function translateToEnglish(text) {
    if (!text || typeof text !== 'string') return text;
    
    // Try exact match first
    if (italianToEnglishMap[text]) {
        return italianToEnglishMap[text];
    }
    
    // Try partial matches
    for (const [italian, english] of Object.entries(italianToEnglishMap)) {
        if (text.includes(italian)) {
            text = text.replace(italian, english);
        }
    }
    
    return text;
}

// Display results
function displayResults(data, mode = 'email') {
    hideLoading();
    
    // Show mode badge
    const modeBadge = document.getElementById('modeBadge');
    if (mode === 'url') {
        modeBadge.textContent = 'Mode: URL only';
        modeBadge.style.display = 'inline-block';
    } else {
        modeBadge.style.display = 'none';
    }
    
    // Risk Card
    const riskCard = document.getElementById('riskCard');
    const riskIcon = document.getElementById('riskIcon');
    const riskLevel = document.getElementById('riskLevel');
    const riskScore = document.getElementById('riskScore');
    const riskBarFill = document.getElementById('riskBarFill');
    const recommendation = document.getElementById('recommendation').querySelector('p');
    
    // Map risk levels (handles various formats)
    const riskLevelNormalized = data.risk_level ? data.risk_level.toLowerCase() : 'low';
    
    // Risk messages mapping - English only
    const riskMessages = {
        low: "Low risk. No clear phishing indicators were detected, but stay cautious and verify the sender if something feels unusual.",
        medium: "Medium risk. Some suspicious patterns were found. Double-check the sender and links before clicking or sharing any information.",
        high: "High risk. This message matches common phishing patterns. Do not click any links or share credentials. Treat it as a likely phishing attempt."
    };
    
    // Configure colors and icons based on risk level
    let colorClass = '';
    let iconClass = '';
    let riskLevelText = '';
    let recommendationText = '';
    
    switch(riskLevelNormalized) {
        case 'high':
            colorClass = 'risk-high';
            iconClass = 'fa-exclamation-triangle';
            riskLevelText = 'HIGH RISK';
            recommendationText = riskMessages.high;
            break;
        case 'medium':
            colorClass = 'risk-medium';
            iconClass = 'fa-exclamation-circle';
            riskLevelText = 'MEDIUM RISK';
            recommendationText = riskMessages.medium;
            break;
        case 'low':
            colorClass = 'risk-low';
            iconClass = 'fa-check-circle';
            riskLevelText = 'LOW RISK';
            recommendationText = riskMessages.low;
            break;
        default:
            colorClass = 'risk-low';
            iconClass = 'fa-shield-alt';
            riskLevelText = 'ANALYSIS COMPLETE';
            recommendationText = 'Analysis complete. Check the details below.';
    }
    
    // Apply styles
    riskCard.className = `card risk-card ${colorClass}`;
    riskIcon.className = `fas ${iconClass}`;
    riskLevel.textContent = riskLevelText;
    riskScore.textContent = `${data.risk_score}/100`;
    riskBarFill.style.width = `${data.risk_score}%`;
    riskBarFill.className = `risk-bar-fill ${colorClass}`;
    
    // Use backend recommendation or fallback to English default, translate if Italian
    const backendRecommendation = data.recommendation || recommendationText;
    recommendation.textContent = translateToEnglish(backendRecommendation);
    
    // AI Explainability Section
    displayExplainability(data);
    
    // Details/Findings - display as bulleted list
    const findingsContainer = document.getElementById('findingsContainer');
    findingsContainer.innerHTML = '';
    
    // Handles 'details', 'analysisDetails', 'indicators' (can be strings or objects), and 'findings'
    const detailsList = data.analysisDetails || data.details || data.indicators || [];
    const findingsList = data.findings || [];
    
    if (detailsList.length > 0) {
        const detailsCard = document.createElement('div');
        detailsCard.className = 'card';
        
        const header = document.createElement('h3');
        header.innerHTML = `<i class="fas fa-list"></i> Analysis Details`;
        detailsCard.appendChild(header);
        
        const ul = document.createElement('ul');
        ul.className = 'details-list';
        
        detailsList.forEach((detail, idx) => {
            const li = document.createElement('li');
            
            // Handle both string and object formats
            if (typeof detail === 'string') {
                li.textContent = translateToEnglish(detail);
            } else if (typeof detail === 'object' && detail !== null) {
                // Try to extract meaningful content from object
                const content = detail.message || detail.description || detail.text || JSON.stringify(detail);
                li.textContent = translateToEnglish(content);
            } else {
                li.textContent = String(detail);
            }
            
            ul.appendChild(li);
        });
        
        detailsCard.appendChild(ul);
        findingsContainer.appendChild(detailsCard);
    }
    
    if (findingsList.length > 0) {
        const findingsCard = document.createElement('div');
        findingsCard.className = 'card';
        
        const header = document.createElement('h3');
        header.innerHTML = `<i class="fas fa-exclamation-triangle"></i> Issues Detected (${findingsList.length})`;
        findingsCard.appendChild(header);
        
        findingsList.forEach((finding, index) => {
            const findingElement = createFindingElement(finding, index);
            findingsCard.appendChild(findingElement);
        });
        
        findingsContainer.appendChild(findingsCard);
    }
    
    // AI Explainability Section
    displayExplainability(data);
    
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
    
    // Attachment Analysis
    const attachmentContainer = document.getElementById('attachmentContainer');
    const attachmentContent = document.getElementById('attachmentContent');
    
    // Debug logging
    console.log('Full API response:', data);
    console.log('Attachment score:', data.attachment_score);
    console.log('Attachment details:', data.attachment_details);
    
    const attachmentScore = data.attachment_score;
    const attachmentDetails = data.attachment_details;
    
    // Show attachment analysis when attachment_score is not null
    if (attachmentScore !== null && attachmentScore !== undefined) {
        console.log('Rendering attachment analysis section - Score:', attachmentScore);
        
        attachmentContainer.classList.remove('hidden');
        attachmentContainer.style.display = 'block';
        attachmentContent.innerHTML = '';
        
        const score = attachmentScore;
        const details = attachmentDetails || {};
        
        // Display attachments found (if any)
        if (details.attachments && details.attachments.length > 0) {
            const attachmentsListDiv = document.createElement('div');
            attachmentsListDiv.className = 'attachments-list';
            attachmentsListDiv.innerHTML = '<h4><i class="fas fa-paperclip"></i> Attachments Found:</h4>';
            
            const listContainer = document.createElement('div');
            listContainer.className = 'attachment-files-container';
            
            details.attachments.forEach(attachment => {
                const fileDiv = document.createElement('div');
                fileDiv.className = 'attachment-file-item';
                
                const fileName = attachment.filename || attachment.name || 'Unknown file';
                const fileExtension = fileName.includes('.') ? fileName.split('.').pop().toLowerCase() : '';
                const fileSize = attachment.size ? `(${attachment.size})` : '';
                
                fileDiv.innerHTML = `
                    <div class="attachment-file-info">
                        <i class="fas fa-file"></i>
                        <span class="attachment-filename">${escapeHtml(fileName)}</span>
                        ${fileSize ? `<span class="attachment-filesize">${fileSize}</span>` : ''}
                    </div>
                    ${fileExtension ? `<span class="attachment-extension">.${fileExtension}</span>` : ''}
                `;
                
                listContainer.appendChild(fileDiv);
            });
            
            attachmentsListDiv.appendChild(listContainer);
            attachmentContent.appendChild(attachmentsListDiv);
        }
        
        // Score display
        const scoreDiv = document.createElement('div');
        scoreDiv.className = `attachment-score ${score > 0 ? 'high-risk' : ''}`;
        scoreDiv.innerHTML = `
            <span class="attachment-score-label">Risk Score:</span>
            <span class="attachment-score-value ${score === 0 ? 'safe' : ''}">${score}</span>
        `;
        attachmentContent.appendChild(scoreDiv);
        
        // Warning banner for high-risk attachments
        if (score > 0) {
            const warningDiv = document.createElement('div');
            warningDiv.className = 'attachment-warning';
            warningDiv.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                <span>High-risk attachment format detected. Do NOT open this file.</span>
            `;
            attachmentContent.appendChild(warningDiv);
        }
        
        // Detection flags
        const detailsDiv = document.createElement('div');
        detailsDiv.className = 'attachment-details';
        
        const flags = [
            { key: 'double_extension', label: 'Double Extension', icon: 'fa-file-alt' },
            { key: 'html_disguised', label: 'HTML Disguised', icon: 'fa-mask' },
            { key: 'mime_mismatch', label: 'MIME Mismatch', icon: 'fa-exclamation-circle' },
            { key: 'high_risk_type', label: 'High-Risk Type', icon: 'fa-skull-crossbones' }
        ];
        
        flags.forEach(flag => {
            const detailItem = document.createElement('div');
            detailItem.className = 'attachment-detail-item';
            
            const isDetected = details[flag.key] === true;
            const statusIcon = isDetected ? 'fa-times-circle' : 'fa-check-circle';
            const statusClass = isDetected ? 'detected' : 'safe';
            const statusText = isDetected ? 'Detected' : 'Safe';
            
            detailItem.innerHTML = `
                <div class="attachment-detail-label">
                    <i class="fas ${flag.icon}"></i>
                    <span>${flag.label}</span>
                </div>
                <div class="attachment-detail-value ${statusClass}">
                    <span>${statusText}</span>
                    <i class="fas ${statusIcon}"></i>
                </div>
            `;
            
            detailsDiv.appendChild(detailItem);
        });
        
        attachmentContent.appendChild(detailsDiv);
        console.log('Attachment analysis section rendered successfully');
    } else {
        console.log('No attachment data found, hiding section');
        attachmentContainer.classList.add('hidden');
        attachmentContainer.style.display = 'none';
    }
    
    // Show results
    results.classList.remove('hidden');
    
    // Scroll to results
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Display AI Explainability
function displayExplainability(data) {
    const explainabilityContainer = document.getElementById('explainabilityContainer');
    const threatLabel = document.getElementById('threatLabel');
    const confidenceScore = document.getElementById('confidenceScore');
    const riskFactorsList = document.getElementById('riskFactorsList');
    
    // Safety checks - return if elements don't exist
    if (!explainabilityContainer || !threatLabel || !confidenceScore || !riskFactorsList) {
        console.warn('Explainability elements not found in DOM');
        return;
    }
    
    // Show explainability section
    explainabilityContainer.style.display = 'block';
    
    // Threat classification label (legit, suspicious, phishing)
    const label = data.label || data.classification || data.risk_level || 'Unknown';
    threatLabel.textContent = label.toUpperCase();
    threatLabel.className = 'classification-value';
    
    // Add color coding
    const labelLower = label.toLowerCase();
    if (labelLower.includes('phishing') || labelLower === 'high') {
        threatLabel.classList.add('threat-high');
    } else if (labelLower.includes('suspicious') || labelLower === 'medium') {
        threatLabel.classList.add('threat-medium');
    } else {
        threatLabel.classList.add('threat-low');
    }
    
    // Confidence score
    const confidence = data.confidence_score || data.risk_score || 0;
    confidenceScore.textContent = `${confidence}%`;
    confidenceScore.className = 'classification-value';
    
    // Risk factors - why is this risky?
    riskFactorsList.innerHTML = '';
    
    const riskFactors = data.risk_factors || data.factors || [];
    
    if (riskFactors.length > 0) {
        const ul = document.createElement('ul');
        ul.className = 'risk-factors-ul';
        
        riskFactors.forEach(factor => {
            const li = document.createElement('li');
            li.className = 'risk-factor-item';
            
            const factorText = typeof factor === 'string' ? factor : 
                             (factor.description || factor.message || factor.reason || JSON.stringify(factor));
            
            li.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                <span>${escapeHtml(translateToEnglish(factorText))}</span>
            `;
            ul.appendChild(li);
        });
        
        riskFactorsList.appendChild(ul);
    } else {
        // Fallback message if no risk factors provided
        const fallbackDiv = document.createElement('div');
        fallbackDiv.className = 'risk-factors-fallback';
        
        const riskLevel = (data.risk_level || '').toLowerCase();
        
        if (riskLevel === 'low') {
            fallbackDiv.innerHTML = `
                <i class="fas fa-check-circle"></i>
                <p>No significant risk factors detected. This message appears legitimate based on our analysis.</p>
            `;
        } else if (riskLevel === 'medium') {
            fallbackDiv.innerHTML = `
                <i class="fas fa-exclamation-circle"></i>
                <p>Some suspicious patterns detected. Review the analysis details carefully before taking action.</p>
            `;
        } else {
            fallbackDiv.innerHTML = `
                <i class="fas fa-shield-alt"></i>
                <p>Multiple phishing indicators identified. See analysis details below for specific concerns.</p>
            `;
        }
        
        riskFactorsList.appendChild(fallbackDiv);
    }
}

// Create element for a finding
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
            <strong>📚 Tips:</strong>
            <ul>
                ${finding.educational.tips.map(tip => `<li>${escapeHtml(tip)}</li>`).join('')}
            </ul>
        </div>
    `;
    
    findingDiv.appendChild(header);
    findingDiv.appendChild(content);
    
    return findingDiv;
}

// Toggle finding expansion
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

// Show error
function showError(message) {
    hideLoading();
    
    // Translate error message if it's in Italian
    const translatedMessage = translateToEnglish(message) || message;
    
    results.innerHTML = `
        <div class="card error-card">
            <i class="fas fa-exclamation-circle"></i>
            <h3>Error</h3>
            <p>${escapeHtml(translatedMessage)}</p>
            <button class="btn btn-secondary" onclick="resetForm()">
                <i class="fas fa-redo"></i> Try Again
            </button>
        </div>
    `;
    
    results.classList.remove('hidden');
}

// Load example
function loadExample(type) {
    if (type === 'phishing' || type === 'legitimate') {
        // Email example
        switchMode('email');
        const example = examples[type];
        document.getElementById('sender').value = example.sender;
        document.getElementById('subject').value = example.subject;
        document.getElementById('body').value = example.body;
        form.scrollIntoView({ behavior: 'smooth' });
    }
}

// Reset form
function resetForm() {
    form.reset();
    urlForm.reset();
    results.classList.add('hidden');
    
    // Scroll to appropriate form based on current mode
    if (currentMode === 'url') {
        urlForm.scrollIntoView({ behavior: 'smooth' });
    } else {
        form.scrollIntoView({ behavior: 'smooth' });
    }
}

// Escape HTML for security
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

// Check API health on load (optional)
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

// Execute health check
checkApiHealth();