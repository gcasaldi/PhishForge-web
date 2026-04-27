// API Configuration - Intelligent fallback (Local → Remote)
let API_URL = "http://localhost:8000/analyze/email";
const API_HEALTH_LOCAL = "http://localhost:8000/health";
const API_HEALTH_REMOTE = "https://www.virustotal.com/api/v3";
const API_URL_REMOTE = "https://gcasaldi.github.io/PhishForge-web/PhishForge/phishforge-web/api-handler.php";
const API_TIMEOUT = 30000; // 30 seconds

let isLocalAPIAvailable = false;
let apiSource = "unknown"; // Will be "local" or "remote"

// Check API availability on load
window.addEventListener('load', checkAPIHealth);

async function checkAPIHealth() {
  try {
    // Try local API first (3 second timeout)
    const localResponse = await fetch(API_HEALTH_LOCAL, { 
      signal: AbortSignal.timeout(3000)
    });
    if (localResponse.ok) {
      isLocalAPIAvailable = true;
      apiSource = "local";
      API_URL = "http://localhost:8000/analyze/email";
      console.log("✅ API locale disponibile");
      document.getElementById("api-status").innerHTML = '✅ API Local (Localhost)';
      document.getElementById("api-status").className = 'api-status ready';
      return;
    }
  } catch (err) {
    console.log("ℹ️ API locale non disponibile, uso rilevamento client-side...");
  }

  // Use client-side detection (no remote API needed)
  isLocalAPIAvailable = false;
  apiSource = "client";
  console.log("✅ API client-side disponibile");
  document.getElementById("api-status").innerHTML = '✅ Client-Side Detection';
  document.getElementById("api-status").className = 'api-status ready';
}

document.getElementById("analyze-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const subject = document.getElementById("subject").value || "";
  const sender = document.getElementById("sender").value || "";
  const body = document.getElementById("body").value || "";
  const attachment_filename = document.getElementById("attachment_filename").value || "";

  // Validation
  if (!body.trim() && !subject.trim()) {
    showError("Inserisci almeno il soggetto o il corpo dell'email.");
    return;
  }

  // Show loading state
  const resultContainer = document.getElementById("result-container");
  const resultContent = document.getElementById("result-content");
  resultContainer.classList.add("show");
  resultContent.innerHTML = '<div class="loading">🔍 Analizzando email...</div>';

  try {
    let result;
    
    // Use appropriate API based on availability
    if (apiSource === "local") {
      // Local API
      result = await analyzeWithLocalAPI(subject, sender, body, attachment_filename);
    } else {
      // Client-side detection (works everywhere)
      result = analyzeClientSide(subject, sender, body, attachment_filename);
    }
    
    displayResults(result);

  } catch (err) {
    if (err.name === 'AbortError') {
      showError(`⏱️ Timeout - L'API locale impiega troppo tempo a rispondere. Verifica che sia in esecuzione.`);
    } else {
      showError(`❌ Errore di analisi: ${err.message}`);
    }
  }
});

async function analyzeWithLocalAPI(subject, sender, body, attachment_filename) {
  const payload = {
    subject: subject || "No subject",
    sender: sender || "unknown@example.com",
    body: body || "No body content"
  };
  
  if (attachment_filename.trim()) {
    payload.attachments = [{
      filename: attachment_filename.trim(),
      mime_type: getMimeType(attachment_filename),
      size: 0
    }];
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

  const resp = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal: controller.signal
  });

  clearTimeout(timeoutId);

  if (!resp.ok) {
    const errorText = await resp.text();
    if (resp.status === 503) {
      showError(`⚠️ API locale non disponibile. Assicurati che sia in esecuzione: http://localhost:8000`);
    } else {
      showError(`Errore API (${resp.status}): ${errorText}`);
    }
    throw new Error("API response error");
  }

  return await resp.json();
}

function analyzeClientSide(subject, sender, body, attachment_filename) {
  """
  Rilevamento phishing client-side - Non richiede API esterna
  """
  let riskScore = 0;
  let findings = [];

  // ANALISI MITTENTE
  const senderLower = sender.toLowerCase();
  
  // Check for domains che impersonano
  const fakeDomainsPatterns = [
    /paypal.*verify|verify.*paypal/i,
    /amazon.*security|security.*amazon/i,
    /bank.*urgent|urgent.*bank/i,
    /apple.*account|account.*apple/i,
    /microsoft.*confirm|confirm.*microsoft/i,
    /google.*verify|verify.*google/i,
    /(-|_)(paypal|amazon|apple|bank|security|account)/i,
  ];

  for (let pattern of fakeDomainsPatterns) {
    if (pattern.test(senderLower)) {
      riskScore += 25;
      findings.push({
        risk_score: 25,
        category: "spoofing",
        detail: `⚠️ Indirizzo mittente sospetto: contiene pattern riconoscibile come phishing`
      });
      break;
    }
  }

  // Check for suspicious sender patterns
  if (senderLower.includes("noreply") && senderLower.includes("bit.ly")) {
    riskScore += 15;
    findings.push({
      risk_score: 15,
      category: "sender",
      detail: "📧 Mittente automatico con URL abbreviato"
    });
  }

  // ANALISI SUBJECT
  const subjectLower = subject.toLowerCase();
  const urgentKeywords = ["urgent", "immediate", "verify", "confirm", "action required", "suspended", "locked", "compromised"];
  const urgentScore = urgentKeywords.filter(k => subjectLower.includes(k)).length;
  
  if (urgentScore >= 2) {
    riskScore += 20;
    findings.push({
      risk_score: 20,
      category: "suspicious_keywords",
      detail: `🚩 Linguaggio urgente rilevato (${urgentScore} parole sospette)`
    });
  } else if (urgentScore >= 1) {
    riskScore += 10;
    findings.push({
      risk_score: 10,
      category: "suspicious_keywords",
      detail: "⚠️ Parole urgenti nel subject"
    });
  }

  // ANALISI BODY
  const bodyLower = body.toLowerCase();

  // Extract URLs
  const urlRegex = /(?:https?:\/\/)?(?:www\.)?[^\s]+\.[^\s]+/gi;
  const urls = body.match(urlRegex) || [];
  const uniqueUrls = [...new Set(urls)];

  // Check URLs
  let urlRiskScore = 0;
  const suspiciousUrlPatterns = [
    /bit\.ly|tinyurl|short\.link|goo\.gl/i,  // URL shorteners
    /paypal.*verify|verify.*paypal|paypal[-_]security|secure[-_]paypal/i,
    /amazon[-_](verify|secure|account)|amazon.*login/i,
    /apple[-_](verify|account|security)/i,
    /bank(-verify|[-_]security|[-_]login)/i,
    /dhl[-_]?tracking|fedex[-_]?tracking|ups[-_]?tracking/i,
  ];

  uniqueUrls.forEach(url => {
    let urlScore = 0;
    
    // Check suspicious patterns
    for (let pattern of suspiciousUrlPatterns) {
      if (pattern.test(url)) {
        urlScore += 30;
        break;
      }
    }
    
    // Check for HTTP (not HTTPS)
    if (url.startsWith("http://") && !url.includes("localhost")) {
      urlScore += 15;
    }
    
    // Check for IP instead of domain
    if (/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/.test(url)) {
      urlScore += 25;
    }
    
    urlRiskScore = Math.max(urlRiskScore, urlScore);
  });

  if (urlRiskScore > 0) {
    riskScore += urlRiskScore;
    findings.push({
      risk_score: urlRiskScore,
      category: "phishing_urls",
      detail: `🔗 URL sospetto rilevato (score: ${urlRiskScore})`
    });
  }

  // Check phishing keywords in body
  const phishingKeywords = [
    "click here", "verify account", "confirm identity", "update payment",
    "urgent action", "account compromised", "suspicious activity",
    "click immediately", "verify now", "confirm password", "update your account",
    "claim reward", "collect prize"
  ];

  const keywordCount = phishingKeywords.filter(k => bodyLower.includes(k)).length;
  if (keywordCount > 0) {
    const keywordScore = Math.min(20, keywordCount * 5);
    riskScore += keywordScore;
    findings.push({
      risk_score: keywordScore,
      category: "suspicious_keywords",
      detail: `🚩 ${keywordCount} parole phishing rilevate nel corpo`
    });
  }

  // ANALISI ALLEGATI
  if (attachment_filename.trim()) {
    const attachmentLower = attachment_filename.toLowerCase();
    const dangerousExtensions = [".exe", ".scr", ".dll", ".vbs", ".bat", ".cmd", ".msi"];
    
    // Check for dangerous extensions
    for (let ext of dangerousExtensions) {
      if (attachmentLower.endsWith(ext)) {
        riskScore += 35;
        findings.push({
          risk_score: 35,
          category: "attachment",
          detail: `⚠️ ATTENZIONE! Allegato eseguibile pericoloso (${ext})`
        });
        break;
      }
    }
    
    // Check for compound extensions (e.g., .pdf.exe)
    if (/\.\w+\.\w+$/.test(attachment_filename)) {
      riskScore += 25;
      findings.push({
        risk_score: 25,
        category: "attachment",
        detail: "📎 Allegato con estensione compound (molto sospetto)"
      });
    }
  }

  // Clamp risk score to 100
  riskScore = Math.min(100, riskScore);

  // Determine risk level
  let riskLevel = "SAFE";
  if (riskScore >= 70) riskLevel = "CRITICAL";
  else if (riskScore >= 50) riskLevel = "HIGH";
  else if (riskScore >= 30) riskLevel = "MEDIUM";
  else if (riskScore >= 15) riskLevel = "LOW";

  // Generate recommendation
  let recommendation = "";
  if (riskLevel === "CRITICAL") {
    recommendation = "🚨 PHISHING CONFERMATO - Elimina immediatamente questa email e NON cliccare su nessun link!";
  } else if (riskLevel === "HIGH") {
    recommendation = "⚠️ ALTA PROBABILITÀ DI PHISHING - Verifica attentamente il mittente e NON fornire dati personali!";
  } else if (riskLevel === "MEDIUM") {
    recommendation = "⚡ SOSPETTO - Procedi con cautela e verifica l'autenticità attraverso canali ufficiali.";
  } else if (riskLevel === "LOW") {
    recommendation = "ℹ️ Alcuni elementi richiedono attenzione - Verifica sempre i link prima di cliccare.";
  } else {
    recommendation = "✅ Email probabilmente sicura, ma mantieni sempre la vigilanza.";
  }

  return {
    risk_score: riskScore,
    risk_level: riskLevel,
    risk_percentage: riskScore,
    findings: findings,
    urls: uniqueUrls.map(url => ({ url, risk_score: urlRiskScore })),
    recommendation: recommendation,
    ml_score: null,
    attachment_score: null
  };
}

function getMimeType(filename) {
  const ext = filename.split('.').pop().toLowerCase();
  const types = {
    'exe': 'application/x-msdownload',
    'dll': 'application/x-msdownload',
    'zip': 'application/zip',
    'pdf': 'application/pdf',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  };
  return types[ext] || 'application/octet-stream';
}

function showError(message) {
  const resultContainer = document.getElementById("result-container");
  const resultContent = document.getElementById("result-content");
  resultContainer.classList.add("show");
  resultContent.innerHTML = `<div class="error-message">❌ ${escapeHtml(message)}</div>`;
}

function displayResults(data) {
  const resultContent = document.getElementById("result-content");
  
  // Safely extract data with defaults
  const riskScore = data.risk_score || 0;
  const riskLevel = data.risk_level || "LOW";
  const riskPercentage = data.risk_percentage || 0;
  const findings = Array.isArray(data.findings) ? data.findings : [];
  const urls = Array.isArray(data.urls) ? data.urls : [];
  const recommendation = data.recommendation || "Analisi completata";
  const mlScore = data.ml_score || null;
  
  // Optional fields (safely check)
  const attachmentScore = data.attachment_score || null;
  
  // Normalize risk level
  const normalizedLevel = riskLevel.toUpperCase();
  
  // Build HTML output
  let html = `
    <div style="text-align: center; margin-bottom: 30px;">
      <div class="score-display" style="color: ${getScoreColor(riskScore)}">
        ${riskScore}<span style="font-size: 0.6em; font-weight: normal;">/100</span>
      </div>
      <div class="risk-badge risk-${normalizedLevel}">
        ${getRiskIcon(normalizedLevel)} ${normalizedLevel} RISK
      </div>
    </div>
    
    <div style="margin-top: 20px; padding: 20px; background: #f0f4ff; border-left: 5px solid #667eea; border-radius: 8px;">
      <strong style="font-size: 1.1em;">💡 Raccomandazione:</strong>
      <p style="margin-top: 10px; line-height: 1.6;">${escapeHtml(recommendation)}</p>
    </div>
  `;
  
  // Component scores (if available)
  if (attachmentScore !== null || mlScore !== null) {
    html += '<div style="margin-top: 20px; padding: 15px; background: white; border-radius: 8px; border: 1px solid #e2e8f0;">';
    html += '<strong>🔍 Analisi Dettagliata:</strong>';
    html += '<ul style="margin-top: 15px; list-style: none; padding: 0;">';
    
    if (attachmentScore !== null) {
      html += `<li style="padding: 8px 0; border-bottom: 1px solid #e2e8f0;">📎 <strong>Rischio Allegati:</strong> ${attachmentScore}/100</li>`;
    }
    if (mlScore !== null) {
      html += `<li style="padding: 8px 0;">🤖 <strong>ML Detection:</strong> ${Math.round(mlScore)}/100</li>`;
    }
    
    html += '</ul></div>';
  }
  
  // Detailed Findings
  if (findings.length > 0) {
    html += '<div class="findings-list">';
    html += '<h3 style="margin-bottom: 15px; color: #2d3748; margin-top: 30px;">📊 Fattori di Rischio Rilevati</h3>';
    
    findings.slice(0, 8).forEach((finding, idx) => {
      const category = finding.category || "sconosciuto";
      const detail = finding.detail || "Nessun dettaglio";
      const score = finding.risk_score || 0;
      
      const categoryLabels = {
        'suspicious_keywords': '🚩 Parole Sospette',
        'phishing_urls': '🔗 URL Phishing',
        'spoofing': '🎭 Spoofing',
        'ml_detection': '🤖 ML Detection',
        'attachment': '📎 Allegati',
        'sender': '📧 Mittente',
        'encoding': '🔒 Encoding Strano'
      };
      
      const displayCategory = categoryLabels[category] || `📌 ${category}`;
      
      html += `
        <div class="finding-item" style="border-left: 4px solid ${getScoreColor(score)};">
          <div class="finding-category">${displayCategory}</div>
          <div style="margin-top: 8px; color: #4a5568;">${escapeHtml(detail)}</div>
          <div style="margin-top: 8px; font-size: 0.9rem; color: #718096;">
            Contributo al rischio: <strong style="color: ${getScoreColor(score)};">+${score}</strong>
          </div>
        </div>
      `;
    });
    
    if (findings.length > 8) {
      html += `<p style="text-align: center; color: #718096; margin-top: 15px; font-style: italic;">
        ... e ${findings.length - 8} altri fattori di rischio
      </p>`;
    }
    
    html += '</div>';
  } else {
    html += '<div style="margin-top: 20px; padding: 15px; background: #c6f6d5; border-radius: 8px; text-align: center; color: #22543d;">';
    html += '<strong>✅ Nessun fattore di rischio rilevato</strong>';
    html += '</div>';
  }
  
  // URLs found
  if (urls && urls.length > 0) {
    html += '<div style="margin-top: 30px; padding: 15px; background: white; border-radius: 8px; border: 1px solid #e2e8f0;">';
    html += `<strong>🔗 URL Trovati (${urls.length}):</strong>`;
    html += '<ul style="margin-top: 10px; word-break: break-all; list-style: none; padding: 0;">';
    urls.slice(0, 5).forEach(urlObj => {
      const urlStr = typeof urlObj === 'string' ? urlObj : (urlObj.url || '');
      const urlScore = urlObj.risk_score ? `(rischio: ${urlObj.risk_score}/100)` : '';
      html += `<li style="margin: 8px 0; padding: 8px; background: #f7fafc; border-radius: 4px; font-family: monospace; font-size: 0.9em;">${escapeHtml(urlStr)} <span style="color: #718096;">${urlScore}</span></li>`;
    });
    if (urls.length > 5) {
      html += `<li style="color: #718096; margin-top: 8px;">... e altri ${urls.length - 5} URL</li>`;
    }
    html += '</ul></div>';
  }
  
  resultContent.innerHTML = html;
}

function getScoreColor(score) {
  if (score >= 70) return "#e53e3e";
  if (score >= 50) return "#dd6b20";
  if (score >= 30) return "#f59e0b";
  return "#10b981";
}

function getRiskIcon(level) {
  const levelUpper = (level || '').toUpperCase();
  switch(levelUpper) {
    case "CRITICAL": return "🚨";
    case "HIGH": return "🚨";
    case "MEDIUM": return "⚠️";
    case "LOW": return "ℹ️";
    case "SAFE": return "✅";
    default: return "ℹ️";
  }
}

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

