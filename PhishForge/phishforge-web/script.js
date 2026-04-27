// API Local URL - Change to remote if needed
const API_URL = "http://localhost:8000/analyze/email";
const API_TIMEOUT = 30000; // 30 seconds

// Check API availability on load
window.addEventListener('load', checkAPIHealth);

async function checkAPIHealth() {
  try {
    const response = await fetch("http://localhost:8000/health", { 
      signal: AbortSignal.timeout(5000)
    });
    if (response.ok) {
      console.log("✅ API local disponibile");
      document.getElementById("api-status").innerHTML = '✅ API Local Ready';
      document.getElementById("api-status").className = 'api-status ready';
    }
  } catch {
    console.warn("⚠️ API local non disponibile - verificare che sia in esecuzione");
    document.getElementById("api-status").innerHTML = '⚠️ API Local Not Running';
    document.getElementById("api-status").className = 'api-status offline';
  }
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
    // Build request payload for local API
    const payload = {
      subject: subject || "No subject",
      sender: sender || "unknown@example.com",
      body: body || "No body content"
    };
    
    // Add attachment if provided
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
        showError(`⚠️ Detector non disponibile. Assicurati che l'API locale sia in esecuzione: http://localhost:8000`);
      } else {
        showError(`Errore API (${resp.status}): ${errorText}`);
      }
      return;
    }

    const data = await resp.json();
    displayResults(data);

  } catch (err) {
    if (err.name === 'AbortError') {
      showError(`⏱️ Timeout - L'API locale impiega troppo tempo a rispondere. Verifica che sia in esecuzione.`);
    } else {
      showError(`❌ Errore di rete: ${err.message}. Assicurati che l'API locale sia in esecuzione su http://localhost:8000`);
    }
  }
});

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

