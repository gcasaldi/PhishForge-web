const API_URL = "https://phishforge-lite.onrender.com/analyze";

document.getElementById("analyze-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const subject = document.getElementById("subject").value || "";
  const sender = document.getElementById("sender").value || "";
  const body = document.getElementById("body").value || "";
  const attachment_filename = document.getElementById("attachment_filename").value || "";

  // Validation
  if (!body.trim() && !subject.trim()) {
    showError("Please enter at least the email subject or body.");
    return;
  }

  // Show loading state
  const resultContainer = document.getElementById("result-container");
  const resultContent = document.getElementById("result-content");
  resultContainer.classList.add("show");
  resultContent.innerHTML = '<div class="loading">🔍 Analyzing email...</div>';

  try {
    // Build request payload
    const payload = {
      subject: subject || "No subject",
      sender: sender || "unknown@example.com",
      body: body || "No body content"
    };
    
    // Add attachment if provided
    if (attachment_filename.trim()) {
      payload.attachment_filename = attachment_filename.trim();
    }

    const resp = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!resp.ok) {
      const errorText = await resp.text();
      showError(`API Error (${resp.status}): ${errorText}`);
      return;
    }

    const data = await resp.json();
    displayResults(data);

  } catch (err) {
    showError(`Network error: ${err.message || err}`);
  }
});

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
  const recommendation = data.recommendation || "No recommendation available";
  const riskFactors = Array.isArray(data.risk_factors) ? data.risk_factors : [];
  
  // Optional fields (safely check)
  const attachmentScore = data.attachment_score || null;
  const senderRisk = data.sender_risk || null;
  
  // Build HTML output
  let html = `
    <div style="text-align: center;">
      <div class="score-display" style="color: ${getScoreColor(riskScore)}">
        ${riskScore}/100
      </div>
      <div class="risk-badge risk-${riskLevel}">
        ${getRiskIcon(riskLevel)} ${riskLevel} RISK
      </div>
    </div>
    
    <div style="margin-top: 20px; padding: 15px; background: white; border-radius: 8px;">
      <strong>📋 Recommendation:</strong>
      <p style="margin-top: 10px;">${escapeHtml(recommendation)}</p>
    </div>
  `;
  
  // Component scores (if available)
  if (senderRisk !== null || attachmentScore !== null) {
    html += '<div style="margin-top: 20px; padding: 15px; background: white; border-radius: 8px;">';
    html += '<strong>🔍 Component Scores:</strong>';
    html += '<ul style="margin-top: 10px; list-style: none; padding: 0;">';
    
    if (senderRisk !== null) {
      html += `<li>🎭 Sender Risk: <strong>${senderRisk}</strong></li>`;
    }
    if (attachmentScore !== null) {
      html += `<li>📎 Attachment Risk: <strong>${attachmentScore}</strong></li>`;
    }
    
    html += '</ul></div>';
  }
  
  // Risk Factors (Enterprise Explainability)
  if (riskFactors.length > 0) {
    html += '<div class="risk-factors">';
    html += '<h3>🧠 Risk Analysis (Enterprise Explainability)</h3>';
    html += '<ul>';
    riskFactors.slice(0, 10).forEach(factor => {
      html += `<li>• ${escapeHtml(factor)}</li>`;
    });
    html += '</ul></div>';
  }
  
  // Detailed Findings
  if (findings.length > 0) {
    html += '<div class="findings-list">';
    html += '<h3 style="margin-bottom: 15px; color: #2d3748;">📊 Detailed Findings</h3>';
    
    findings.slice(0, 5).forEach(finding => {
      const category = finding.category || "unknown";
      const detail = finding.detail || "No details";
      const score = finding.risk_score || 0;
      
      html += `
        <div class="finding-item">
          <div class="finding-category">${escapeHtml(category)}</div>
          <div style="margin-top: 5px; color: #4a5568;">${escapeHtml(detail)}</div>
          <div style="margin-top: 5px; font-size: 0.9rem; color: #718096;">
            Risk contribution: <strong>+${score}</strong>
          </div>
        </div>
      `;
    });
    
    if (findings.length > 5) {
      html += `<p style="text-align: center; color: #718096; margin-top: 10px;">
        ... and ${findings.length - 5} more findings
      </p>`;
    }
    
    html += '</div>';
  }
  
  // URLs found
  if (urls.length > 0) {
    html += '<div style="margin-top: 20px; padding: 15px; background: white; border-radius: 8px;">';
    html += `<strong>🔗 URLs Found (${urls.length}):</strong>`;
    html += '<ul style="margin-top: 10px; word-break: break-all;">';
    urls.slice(0, 5).forEach(url => {
      html += `<li style="margin: 5px 0;"><code>${escapeHtml(url)}</code></li>`;
    });
    if (urls.length > 5) {
      html += `<li style="color: #718096;">... and ${urls.length - 5} more</li>`;
    }
    html += '</ul></div>';
  }
  
  resultContent.innerHTML = html;
}

function getScoreColor(score) {
  if (score >= 70) return "#e53e3e";
  if (score >= 40) return "#dd6b20";
  return "#38a169";
}

function getRiskIcon(level) {
  switch(level) {
    case "HIGH": return "🚨";
    case "MEDIUM": return "⚠️";
    case "LOW": return "✅";
    default: return "ℹ️";
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

