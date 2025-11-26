// API Configuration
const API_BASE_URL = 'https://phishforge-lite.onrender.com';

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
    
    // Risk messages mapping
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
        case 'alto':
            colorClass = 'risk-high';
            iconClass = 'fa-exclamation-triangle';
            riskLevelText = 'HIGH RISK';
            recommendationText = riskMessages.high;
            break;
        case 'medium':
        case 'medio':
            colorClass = 'risk-medium';
            iconClass = 'fa-exclamation-circle';
            riskLevelText = 'MEDIUM RISK';
            recommendationText = riskMessages.medium;
            break;
        case 'low':
        case 'basso':
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
    recommendation.textContent = data.recommendation || recommendationText;
    
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
                li.textContent = detail;
            } else if (typeof detail === 'object' && detail !== null) {
                // Try to extract meaningful content from object
                li.textContent = detail.message || detail.description || detail.text || JSON.stringify(detail);
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
    
    // Show results
    results.classList.remove('hidden');
    
    // Scroll to results
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
    
    results.innerHTML = `
        <div class="card error-card">
            <i class="fas fa-exclamation-circle"></i>
            <h3>Error</h3>
            <p>${escapeHtml(message)}</p>
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