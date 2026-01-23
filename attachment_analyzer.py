"""
Attachment Analysis Module for PhishForge

This module analyzes attachment metadata (filename, MIME type, size) 
to detect potential phishing attempts through file manipulation techniques.

SECURITY: This module NEVER reads or stores file content - only metadata analysis.
"""

import re
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# High-risk file extensions that are commonly used in phishing attacks
HIGH_RISK_EXTENSIONS = {
    '.exe', '.bat', '.cmd', '.com', '.pif', '.scr',  # Executables
    '.js', '.jse', '.vbs', '.vbe', '.wsf', '.wsh',   # Scripts
    '.jar', '.app', '.deb', '.rpm',                   # Installers
    '.html', '.htm', '.svg',                          # Web files (can execute JS)
    '.hta',                                           # HTML Applications
    '.msi', '.msp',                                   # Windows Installers
    '.reg',                                           # Registry files
    '.lnk', '.url'                                    # Shortcuts
}

# Safe extensions commonly used in legitimate business documents
SAFE_EXTENSIONS = {
    '.pdf', '.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt',
    '.txt', '.rtf', '.odt', '.ods', '.odp',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
    '.zip', '.rar', '.7z', '.tar', '.gz'
}

# Common MIME types mapping
MIME_TYPE_MAP = {
    # Documents
    '.pdf': 'application/pdf',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.doc': 'application/msword',
    '.xls': 'application/vnd.ms-excel',
    '.ppt': 'application/vnd.ms-powerpoint',
    
    # Images
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    
    # Archives
    '.zip': 'application/zip',
    '.rar': 'application/x-rar-compressed',
    '.7z': 'application/x-7z-compressed',
    
    # Web
    '.html': 'text/html',
    '.htm': 'text/html',
    
    # Executables
    '.exe': 'application/x-msdownload',
    '.js': 'application/javascript',
}


def analyze_attachment(
    filename: str,
    mime_type: Optional[str] = None,
    size: Optional[int] = None
) -> Dict:
    """
    Analyze attachment metadata for phishing indicators.
    
    This function performs string-based pattern analysis on attachment metadata
    without ever reading or storing file content.
    
    Args:
        filename: Name of the attachment file
        mime_type: Declared MIME type (optional)
        size: File size in bytes (optional)
        
    Returns:
        Dict containing:
        - attachment_score: Risk score (0-100)
        - attachment_details: Detailed analysis results
        - findings: List of detected issues
        
    Security:
        This function NEVER accesses file content, only analyzes metadata strings.
    """
    score = 0
    findings = []
    details = {
        "double_extension": False,
        "html_disguised": False,
        "mime_mismatch": False,
        "high_risk_type": False,
        "executable_masquerading": False,
        "suspicious_patterns": []
    }
    
    if not filename or not isinstance(filename, str):
        return {
            "attachment_score": 0,
            "attachment_details": details,
            "findings": []
        }
    
    filename_lower = filename.lower().strip()
    
    # 1. DOUBLE EXTENSION DETECTION
    # Pattern: safe_ext.dangerous_ext (e.g., invoice.pdf.exe, report.docx.html)
    double_ext_pattern = r'.+\.(pdf|docx|xlsx|pptx|doc|xls|ppt|txt)\.(html|htm|exe|js|vbs|bat|cmd)$'
    if re.search(double_ext_pattern, filename_lower, re.IGNORECASE):
        details["double_extension"] = True
        score += 40
        findings.append({
            "risk_score": 40,
            "category": "double_extension",
            "detail": f"Double extension detected in filename: {filename}",
            "educational": {
                "title": "🎭 Double Extension Attack",
                "explanation": "Attackers use double extensions to hide malicious files. 'invoice.pdf.exe' appears as 'invoice.pdf' in some email clients, but it's actually an executable.",
                "tips": [
                    "Always check the full filename including all extensions",
                    "Be extremely cautious of files with multiple dots",
                    "Legitimate documents don't have .exe, .html, or .js after .pdf/.docx"
                ]
            }
        })
        logger.warning(f"Double extension detected: {filename}")
    
    # 2. HTML-DISGUISED DOCUMENTS
    # High-risk patterns: document.pptx.html, report.pdf.html
    html_disguise_pattern = r'.+\.(pdf|docx|xlsx|pptx|doc|xls|ppt)\.(html|htm)$'
    if re.search(html_disguise_pattern, filename_lower, re.IGNORECASE):
        details["html_disguised"] = True
        score += 35
        findings.append({
            "risk_score": 35,
            "category": "html_disguised",
            "detail": f"Document disguised as HTML: {filename}",
            "educational": {
                "title": "📄 HTML-Disguised Document",
                "explanation": "This file pretends to be a document but is actually an HTML file that can execute JavaScript and steal credentials.",
                "tips": [
                    "Legitimate Office documents don't have .html extension",
                    "HTML files can redirect to phishing sites automatically",
                    "Never open files with both document and HTML extensions"
                ]
            }
        })
        logger.warning(f"HTML-disguised document: {filename}")
    
    # 3. EXECUTABLE MASQUERADING
    # Detect executables hidden with multiple extensions
    executable_pattern = r'.+\..+\.(exe|bat|cmd|js|jar|vbs|wsf|scr|com|pif)$'
    if re.search(executable_pattern, filename_lower, re.IGNORECASE):
        if not details["double_extension"]:  # Don't double-count
            details["executable_masquerading"] = True
            score += 45
            findings.append({
                "risk_score": 45,
                "category": "executable_masquerading",
                "detail": f"Executable file with suspicious naming: {filename}",
                "educational": {
                    "title": "⚠️ Hidden Executable",
                    "explanation": "This file is an executable program disguised with multiple extensions to appear safe.",
                    "tips": [
                        "Never run .exe, .bat, .js files from emails",
                        "Legitimate companies send documents, not executables",
                        "Executables can install malware or steal data"
                    ]
                }
            })
            logger.warning(f"Executable masquerading detected: {filename}")
    
    # 4. HIGH-RISK FILE TYPE CHECK
    # Check if the final extension is inherently dangerous
    file_ext = None
    if '.' in filename_lower:
        file_ext = '.' + filename_lower.split('.')[-1]
    
    if file_ext in HIGH_RISK_EXTENSIONS:
        if not (details["double_extension"] or details["executable_masquerading"]):
            details["high_risk_type"] = True
            score += 30
            findings.append({
                "risk_score": 30,
                "category": "high_risk_type",
                "detail": f"High-risk file type: {file_ext}",
                "educational": {
                    "title": "🔴 Dangerous File Type",
                    "explanation": f"Files with {file_ext} extension can execute code on your system and are commonly used in phishing attacks.",
                    "tips": [
                        "Be extremely cautious with executable files from emails",
                        "Verify sender identity before opening such files",
                        "Use antivirus software to scan suspicious files",
                        "When in doubt, contact IT security team"
                    ]
                }
            })
            logger.warning(f"High-risk file type: {filename}")
    
    # 5. MIME TYPE MISMATCH (if MIME type provided)
    if mime_type and file_ext:
        expected_mime = MIME_TYPE_MAP.get(file_ext)
        mime_lower = mime_type.lower().strip()
        
        if expected_mime and expected_mime.lower() != mime_lower:
            # Allow some common variations
            allowed_variations = {
                'application/octet-stream',  # Generic binary
                'application/download',       # Generic download
            }
            
            if mime_lower not in allowed_variations:
                details["mime_mismatch"] = True
                score += 20
                findings.append({
                    "risk_score": 20,
                    "category": "mime_mismatch",
                    "detail": f"MIME type mismatch: expected {expected_mime} but got {mime_type}",
                    "educational": {
                        "title": "🎭 File Type Spoofing",
                        "explanation": "The file's declared type doesn't match its extension, suggesting an attempt to bypass security filters.",
                        "tips": [
                            "This could indicate content manipulation",
                            "Email filters may be deceived by type mismatches",
                            "Always verify file authenticity before opening"
                        ]
                    }
                })
                logger.warning(f"MIME mismatch for {filename}: expected {expected_mime}, got {mime_type}")
    
    # 6. SUSPICIOUS FILENAME PATTERNS
    suspicious_patterns = [
        (r'invoice.*\.(html|exe|js)', "Fake invoice file"),
        (r'receipt.*\.(html|exe|js)', "Fake receipt file"),
        (r'payment.*\.(html|exe|js)', "Fake payment file"),
        (r'order.*\.(html|exe|js)', "Fake order file"),
        (r'document.*\.(html|exe|js)', "Suspicious document file"),
        (r'secure.*\.(html|exe|js)', "Fake secure file"),
        (r'statement.*\.(html|exe|js)', "Fake statement file"),
    ]
    
    for pattern, description in suspicious_patterns:
        if re.search(pattern, filename_lower, re.IGNORECASE):
            details["suspicious_patterns"].append(description)
            if score < 50:  # Only add if not already flagged high
                score += 15
                findings.append({
                    "risk_score": 15,
                    "category": "suspicious_filename",
                    "detail": f"{description}: {filename}",
                    "educational": {
                        "title": "📎 Suspicious Filename",
                        "explanation": "This filename matches common phishing patterns used to trick users into opening malicious files.",
                        "tips": [
                            "Phishers use familiar names like 'invoice' or 'receipt'",
                            "Verify expected file type for the claimed content",
                            "Contact sender through official channels if unsure"
                        ]
                    }
                })
                break  # Only flag once
    
    # 7. SIZE CHECK (if provided)
    # Suspiciously small "documents" might be HTML redirectors
    if size is not None and file_ext in SAFE_EXTENSIONS:
        if size < 1024:  # Less than 1KB
            score += 10
            findings.append({
                "risk_score": 10,
                "category": "suspicious_size",
                "detail": f"Unusually small file size ({size} bytes) for a {file_ext} document",
                "educational": {
                    "title": "📏 Suspicious File Size",
                    "explanation": "Real documents are typically larger. Small files may be malicious redirectors.",
                    "tips": [
                        "Legitimate PDF/Office files are usually several KB or larger",
                        "Tiny files may contain only malicious code or links",
                        "Verify file authenticity if size seems unusual"
                    ]
                }
            })
    
    # Cap score at 100
    final_score = min(score, 100)
    
    return {
        "attachment_score": final_score,
        "attachment_details": details,
        "findings": findings,
        "filename": filename,
        "file_extension": file_ext,
        "declared_mime": mime_type,
        "file_size": size
    }


def get_risk_level(score: int) -> str:
    """
    Determine risk level based on attachment score.
    
    Args:
        score: Attachment risk score (0-100)
        
    Returns:
        Risk level string: "LOW", "MEDIUM", or "HIGH"
    """
    if score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    else:
        return "LOW"


# Educational tips for attachment analysis
ATTACHMENT_TIPS = {
    "safe_practices": [
        "Always verify sender identity before opening attachments",
        "Use antivirus software to scan all attachments",
        "Be wary of unexpected attachments, even from known contacts",
        "Check file extensions carefully - show hidden extensions in Windows",
        "When in doubt, contact the sender through official channels",
        "Never enable macros in documents from untrusted sources"
    ],
    "red_flags": [
        "Multiple file extensions (e.g., document.pdf.exe)",
        "Executable files (.exe, .bat, .js) in business emails",
        "HTML files pretending to be documents",
        "Urgent requests to open attachments immediately",
        "Mismatched file types and MIME declarations",
        "Suspiciously small file sizes for claimed document types"
    ]
}


if __name__ == "__main__":
    # Test cases
    test_cases = [
        ("invoice.pdf.exe", "application/pdf", 1500),
        ("report.docx.html", "text/html", 800),
        ("presentation.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation", 50000),
        ("document.pdf.js", None, 500),
        ("receipt.html", "text/html", 1200),
        ("normal_file.pdf", "application/pdf", 150000),
    ]
    
    print("="*70)
    print("Attachment Analysis Module - Test Cases")
    print("="*70)
    
    for filename, mime, size in test_cases:
        result = analyze_attachment(filename, mime, size)
        print(f"\nFile: {filename}")
        print(f"Score: {result['attachment_score']} ({get_risk_level(result['attachment_score'])})")
        print(f"Details: {result['attachment_details']}")
        print(f"Findings: {len(result['findings'])} detected")
        for finding in result['findings']:
            print(f"  - {finding['category']}: {finding['detail']}")
