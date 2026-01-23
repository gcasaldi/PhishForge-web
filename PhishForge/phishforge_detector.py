import re
from urllib.parse import urlparse
from email.utils import parseaddr
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Import Phishing.Database integration
try:
    from .phishing_database_client import get_client, PhishingDatabaseClient
    PHISHING_DB_AVAILABLE = True
except ImportError:
    # Graceful fallback if module not available
    PHISHING_DB_AVAILABLE = False
    get_client = None  # Define as None when import fails
    print("[PhishForge] Phishing.Database integration not available")

# Import Multi-Database integration (Discord, Steam, AntiScam, phish.sinking.yachts, etc.)
try:
    from .multi_database_client import get_client as get_multi_db_client
    MULTI_DB_AVAILABLE = True
except ImportError:
    MULTI_DB_AVAILABLE = False
    print("[PhishForge] Multi-Database integration not available")

def is_url_in_phishing_database(url: str) -> bool:
    """
    Check if a URL is in the Phishing.Database.
    NEVER fails - returns False on any error.
    
    Args:
        url: URL to check
        
    Returns:
        True if found in database, False otherwise (including if database unavailable)
    """
    if not PHISHING_DB_AVAILABLE or get_client is None:
        return False
    
    try:
        db_client = get_client()
        return db_client.is_phishing_url(url)
    except Exception:
        # Silent failure - system continues with heuristics
        return False
        return False


def is_url_in_multi_database(url: str) -> bool:
    """
    Check if URL is in consolidated multi-database (Discord, Steam, AntiScam, phish.sinking.yachts, etc.)
    NEVER fails - returns False on any error.
    
    Args:
        url: URL to check
        
    Returns:
        True if found in any database, False otherwise
    """
    if not MULTI_DB_AVAILABLE:
        return False
    
    try:
        # Extract domain from URL
        parsed = urlparse(url if url.startswith('http') else f'http://{url}')
        domain = parsed.netloc or parsed.path.split('/')[0]
        
        # Safe import - already checked MULTI_DB_AVAILABLE above
        from .multi_database_client import get_client as get_multi_db_client
        multi_db = get_multi_db_client()
        return multi_db.is_phishing(domain)
    except Exception as e:
        logger.debug(f"Multi-database check failed: {e}")
        return False


def normalize_for_fuzzy_match(text: str) -> str:
    """
    Normalize text for fuzzy matching by replacing visually similar characters.
    Catches advanced phishing techniques like:
    - rn → m (visual similarity: "arnazon" → "amazon")
    - vv → w ("vvebsite" → "website")
    - cl → d ("paypa1cl" → "paypald")
    - 0 → o, 1 → l/i, 5 → s, etc.
    
    Args:
        text: Text to normalize (domain, path, etc.)
    
    Returns:
        Normalized text with substitutions applied
    """
    text = text.lower()
    
    # Multi-character visual substitutions (ORDER MATTERS - do these first!)
    visual_tricks = [
        ('rn', 'm'),   # rn looks like m: "arnazon" → "amazon"
        ('vv', 'w'),   # vv looks like w: "vvebsite" → "website"  
        ('cl', 'd'),   # cl looks like d (in some fonts)
        ('nn', 'u'),   # nn can look like u
        ('ii', 'u'),   # ii looks like u (in some fonts)
        ('oo', 'oo'),  # Keep oo but normalize digits below
    ]
    
    for original, replacement in visual_tricks:
        text = text.replace(original, replacement)
    
    # Single character substitutions (numbers/symbols → letters)
    substitutions = {
        # Numbers that look like letters
        '0': 'o',
        '1': 'i',  # Also covers l → i (1 looks like l or i)
        '3': 'e',
        '4': 'a',
        '5': 's',
        '6': 'b',
        '7': 't',
        '8': 'b',
        '9': 'g',
        
        # Symbols that look like letters
        '@': 'a',
        '$': 's',
        '!': 'i',
        '|': 'i',
        '(': 'c',
        ')': 'c',
        '[': 'c',
        ']': 'c',
        '{': 'c',
        '}': 'c',
        
        # Remove common separators (treat domain-name and domainname the same)
        '-': '',
        '_': '',
        '.': '',  # Normalize subdomains
    }
    
    for char, replacement in substitutions.items():
        text = text.replace(char, replacement)
    
    return text


def check_fuzzy_brand_match(domain: str, known_brands: dict) -> tuple:
    """
    Check if domain fuzzy-matches a known brand using assonance detection.
    Catches advanced phishing like:
    - paypa1 → paypal (1→l)
    - arnazon → amazon (rn→m visual trick)
    - micr0s0ft → microsoft (0→o)
    - g00gle → google (00→oo)
    
    Args:
        domain: Domain to check
        known_brands: Dictionary of {brand: [official_domains]}
    
    Returns:
        Tuple of (is_fuzzy_match: bool, matched_brand: str or None, normalized_domain: str)
    """
    normalized_domain = normalize_for_fuzzy_match(domain)
    
    for brand, official_domains in known_brands.items():
        normalized_brand = normalize_for_fuzzy_match(brand)
        
        # Check if normalized brand appears in normalized domain
        if normalized_brand in normalized_domain:
            # But it's NOT an official domain
            if not any(official in domain.lower() for official in official_domains):
                return (True, brand, normalized_domain)
    
    return (False, None, normalized_domain)


# Phishing keywords (case-insensitive matching) - each adds ~10 points
PHISHING_KEYWORDS = [
    # Urgency & Action
    "verify", "confirm", "update", "limited", "suspended",
    "urgent", "immediately", "expire", "expires", "expired",
    "act now", "click here", "click now", "action required",
    "immediate action", "respond now", "time sensitive",
    "final notice", "last warning", "last chance",
    
    # Account Status
    "blocked account", "locked", "locked account", "frozen",
    "account suspension", "deactivated", "disabled",
    "unusual activity", "suspicious activity", "unauthorized",
    "unauthorized access", "security alert", "security breach",
    "restore", "reactivate", "unlock",
    
    # Verification & Authentication
    "authenticate", "validate", "validation", "verification",
    "confirm identity", "verify identity", "verify account",
    "token leak", "credential leak", "data breach",
    
    # Payment & Financial
    "payment failed", "payment declined", "billing problem",
    "refund", "claim refund", "unclaimed refund",
    "invoice attached", "overdue payment", "outstanding balance",
    "wire transfer", "bank transfer", "update payment",
    
    # Security & Password
    "reset password", "change password", "password expired",
    "security code", "verification code", "one-time code",
    "2fa", "two-factor", "mfa", "multi-factor",
    
    # Prize/Reward Scams
    "congratulations", "you won", "winner", "prize",
    "claim prize", "lottery", "jackpot", "reward",
    
    # Italian specific
    "verifica", "conferma", "scaduto", "urgente",
    "conto bloccato", "sospeso", "attività sospetta"
]

# Phishing phrases (case-insensitive) - each adds ~20-25 points (more weight than single keywords)
PHISHING_PHRASES = [
    # Account threats
    "your account has been limited",
    "your account will be blocked",
    "your account will be closed",
    "your account has been suspended",
    "your account is locked",
    "temporarily suspended",
    "permanently suspended",
    "account termination",
    
    # Verification demands
    "confirm your identity",
    "verify your account",
    "verify your identity now",
    "restore access to your account",
    "reactivate your account",
    "unlock your account",
    
    # Time pressure
    "within 24 hours",
    "within 48 hours",
    "within 30 minutes",
    "expires in 24 hours",
    "expires today",
    "act immediately",
    "respond within",
    
    # Security alerts
    "unusual activity detected",
    "suspicious activity detected",
    "unauthorized access detected",
    "security alert",
    "security breach",
    "unauthorized login attempt",
    "someone tried to access",
    "we detected a login",
    
    # Action demands
    "verify now",
    "confirm now",
    "click here to verify",
    "click here to confirm",
    "immediate action required",
    "action required immediately",
    "urgent action required",
    
    # Password/Credentials
    "reset your password",
    "change your password immediately",
    "update your information",
    "confirm your password",
    "verify your credentials",
    
    # Data breach claims
    "we detected a token leak",
    "token leak detected",
    "credential leak detected",
    "your data has been compromised",
    "password breach detected",
    
    # Consequences
    "failure to act may result",
    "account will be closed",
    "will lose access",
    "account will be terminated",
    
    # Security settings
    "review your security settings",
    "review your security settings immediately",
    "update security information",
    
    # Payment/Refund
    "payment failed",
    "payment could not be processed",
    "billing information outdated",
    "claim your refund",
    "unclaimed refund",
    "pending refund",
    "refund available",
    
    # Prize/Reward scams
    "you have won",
    "congratulations you won",
    "claim your prize",
    "you are a winner",
    "selected as winner",
    
    # Italian phrases
    "il tuo account è stato limitato",
    "il tuo account sarà bloccato",
    "verifica la tua identità",
    "conferma i tuoi dati",
    "attività sospetta rilevata",
    "accesso non autorizzato",
    "entro 24 ore",
    "azione richiesta"
]

# Legacy comprehensive keywords for educational tips (not used in scoring)
SUSPICIOUS_KEYWORDS = [
    # Verification & Confirmation
    "verify", "verification", "verify your account", "verify now",
    "confirm", "confirmation", "confirm your identity", "confirm your account",
    "validate", "validation", "authenticate",
    
    # Account Status
    "account locked", "account suspended", "account blocked", "account disabled",
    "suspended", "blocked account", "locked account", "deactivated",
    "unusual activity", "suspicious activity", "unauthorized access",
    "unauthorized", "unauthorized transaction",
    
    # Urgency & Time Pressure
    "urgent", "urgently", "immediately", "immediate action",
    "act now", "respond now", "time sensitive", "limited time",
    "expire", "expires", "expiring", "expired",
    "deadline", "final notice", "last chance", "24 hours",
    
    # Security
    "security alert", "security warning", "security notification",
    "security update", "security breach", "compromised",
    "password", "password reset", "reset password", "change password",
    "security code", "verification code", "one-time code", "otp", "mfa",
    
    # Account Actions
    "update", "update your account", "update information",
    "restore", "restore account", "restore access", "reactivate",
    "unlock", "unlock account",
    
    # Financial
    "invoice", "payment", "refund", "transaction", "billing",
    "bank", "credit card", "paypal", "account details",
    "social security", "ssn", "tax", "irs",
    
    # Call to Action
    "click here", "click now", "click below", "download",
    "open attachment", "verify here", "login here",
    "update here", "confirm here"
]

# Educational explanations for each risk type
EDUCATIONAL_TIPS = {
    "suspicious_keywords": {
        "title": "📚 Alarming Language",
        "explanation": "Phishers use words that create urgency or fear to make you act without thinking.",
        "tips": [
            "Real companies rarely use such urgent tones",
            "Always take time to verify",
            "No legitimate service will make you lose your account in hours"
        ]
    },
    "url_shortener": {
        "title": "🔗 Shortened URLs",
        "explanation": "URL shorteners hide the real destination of the link.",
        "tips": [
            "Banks and official services use their full domains",
            "You can expand shortened URLs with services like unshorten.it",
            "When in doubt, go directly to the official site without clicking the link"
        ]
    },
    "http_insecure": {
        "title": "🔓 Insecure Connection",
        "explanation": "URLs starting with 'http' (without 's') are not encrypted.",
        "tips": [
            "Legitimate sites handling sensitive data always use HTTPS",
            "Look for the padlock in the browser's address bar",
            "Never enter credentials on HTTP sites"
        ]
    },
    "suspicious_tld": {
        "title": "🌍 Suspicious Domain",
        "explanation": "Some top-level domains (TLDs) are more commonly used for fraudulent activities.",
        "tips": [
            "Always verify the company's complete domain",
            "Example: 'amazon-verify.xyz' is NOT Amazon",
            "When in doubt, search for the official domain on Google"
        ]
    },
    "sender_mismatch": {
        "title": "👤 Suspicious Sender",
        "explanation": "The display name doesn't match the actual email address.",
        "tips": [
            "Click on the sender to see the full address",
            "'Microsoft Support <hacker@suspicious.com>' is NOT Microsoft",
            "Companies use their official domains"
        ]
    },
    "generic_sender": {
        "title": "⚠️ Generic Sender",
        "explanation": "Email from generic support/security addresses that can't be verified.",
        "tips": [
            "Verify the domain: it must match the company",
            "Compare with official emails received in the past",
            "Look for the official contact on the company's website"
        ]
    },
    "credential_request": {
        "title": "🔑 Credential Request",
        "explanation": "You're being asked to log in or provide sensitive information.",
        "tips": [
            "NEVER click links to log in from emails",
            "Go manually to the official site and log in from there",
            "Serious companies don't ask for passwords via email"
        ]
    },
    "known_phishing_url": {
        "title": "🚫 Known Phishing URL Detected",
        "explanation": "This URL or domain has been confirmed as phishing by the Phishing.Database.",
        "tips": [
            "DO NOT click on this link under any circumstances",
            "This domain has been reported and verified as malicious",
            "Delete this email immediately and report it as spam",
            "If you already clicked, change your passwords immediately and scan for malware"
        ]
    },
    "excessive_urgency": {
        "title": "‼️ Excessive Urgency",
        "explanation": "Excessive use of exclamation marks to create pressure.",
        "tips": [
            "Haste is the enemy of security",
            "Criminals want you to act impulsively",
            "Take time to verify"
        ]
    },
    "punycode": {
        "title": "🔤 Deceptive Characters",
        "explanation": "Use of similar-looking characters to imitate legitimate domains.",
        "tips": [
            "Example: 'аmazon.com' uses a Cyrillic 'a', not Latin",
            "These attacks are called 'homograph attacks'",
            "Always check the URL carefully"
        ]
    }
}

# Domains or TLDs often appearing in spam/phishing
SUSPICIOUS_TLDS = [
    # High-risk TLDs (frequently abused)
    ".xyz", ".top", ".tk", ".ml", ".ga", ".cf", ".gq",
    ".pw", ".cc", ".ws", ".buzz", ".loan", ".download",
    ".click", ".link", ".racing", ".review", ".stream",
    ".win", ".bid", ".trade", ".accountant", ".science",
    ".work", ".party", ".gdn", ".mom", ".xin",
    ".live", ".support", ".center",  # Added: commonly used in phishing
    
    # Country codes often abused
    ".ru", ".cn", ".tk", ".kim", ".icu",
    
    # New gTLDs with high abuse rates
    ".online", ".site", ".website", ".space", ".host",
    ".press", ".news", ".info"  # Added .info - very common in phishing
]

# Common URL shorteners (all major services)
URL_SHORTENERS = [
    # Major platforms
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly",
    "buff.ly", "is.gd", "cutt.ly", "rebrand.ly",
    
    # Additional services
    "short.io", "tiny.cc", "lnkd.in", "s.id", "clck.ru",
    "v.gd", "tr.im", "x.co", "1url.com", "2.gp",
    "6.ly", "7.ly", "a.co", "b.link", "bl.ink",
    "budurl.com", "chilp.it", "cli.gs", "db.tt",
    "doiop.com", "ff.im", "goo.by", "hyperurl.co",
    "jmp2.net", "kl.am", "mcaf.ee", "merky.de",
    "migre.me", "o-x.fr", "pd.am", "po.st",
    "q.gs", "qr.ae", "qr.net", "rb.gy", "s2r.co",
    "scrnch.me", "short.ie", "shorturl.at", "soo.gd",
    "su.pr", "t.cn", "tcrn.ch", "tgr.ph", "tinycc.com",
    "tiny.pl", "tr.my", "tweez.me", "u.to", "v.ht",
    "vzturl.com", "wp.me", "x.co", "y.ahoo.it", "yep.it",
    "zi.ma", "zipmex.me", "➡.ws", "✩.ws", "★.ws"
]


# ========================================================
# ENTERPRISE-GRADE HEURISTICS (SOC-LEVEL)
# ========================================================

def has_char_substitution(domain: str) -> bool:
    """
    Detect character substitution (typosquatting).
    
    Common substitutions:
    - 0 → o
    - 1 → l / i
    - 3 → e
    - 5 → s
    
    Examples:
    - "paypa1.com" (1 instead of l)
    - "micr0soft.com" (0 instead of o)
    - "g00gle.com" (00 instead of oo)
    - "amaz0n.com" (0 instead of o)
    
    Args:
        domain: Domain name to check
        
    Returns:
        bool: True if character substitution detected
    """
    if not domain:
        return False
    
    domain_lower = domain.lower()
    
    # Patterns indicating typosquatting
    suspicious_patterns = [
        # Major brands with digit substitutions
        r'paypa1', r'paypa11', r'p4ypal', r'payp4l',  # PayPal
        r'micr0soft', r'micros0ft', r'micr0s0ft',     # Microsoft
        r'g00gle', r'g0ogle', r'go0gle', r'g00g1e', r'goog1e',   # Google
        r'amaz0n', r'amaz00n', r'4mazon',             # Amazon
        r'app1e', r'appl3', r'4pple',                 # Apple
        r'netf1ix', r'netf11x', r'n3tflix',           # Netflix
        r'faceb00k', r'faceb0ok', r'f4cebook',        # Facebook
        r'tw1tter', r'twitt3r', r'tw1tt3r',           # Twitter
        r'1inkedin', r'link3din', r'linked1n',        # LinkedIn
        r'1nstagram', r'instag4am', r'inst4gram',     # Instagram
        r'wha+sapp', r'whats4pp', r'what5app',        # WhatsApp
        r'del0itte', r'd3loitte', r'de10itte',        # Deloitte (Added)
        
        # Italian banks
        r'int3sa', r'intes4', r'1ntesa',              # Intesa
        r'unic4edit', r'unicr3dit', r'un1credit',     # UniCredit
        r'p0ste', r'p0steitaliane', r'po5te',         # Poste
        r'p0st3', r'post3italiane',                   # Poste variations
        r'1nps', r'inp5',                             # INPS (Added)
        r'b4nca', r'b4nk', r'b0nk',                   # Banca/Bank
        r'sanpa0lo', r'sanpa010',                      # Sanpaolo
        
        # Italian words commonly used in phishing (CRITICAL)
        r'r1mbors0', r'r1mborso', r'rimb0rso', r'r1mb0rs0',  # rimborso
        r'ver1f1ca', r'ver1fica', r'verif1ca', r'v3rifica',  # verifica
        r'c0nferma', r'conf3rma', r'c0nf3rma',        # conferma
        r'paag4mento', r'pag4mento', r'pagam3nto',    # pagamento
        r'acc3ss0', r'acc3sso', r'acce5so', r'4ccesso', # accesso
        r'cl1ente', r'cli3nte', r'cl13nte',           # cliente
        r'serv1z1o', r'serv1zio', r'serviz1o',        # servizio
        r's1curezza', r'sicur3zza', r's1cur3zza',     # sicurezza
        r'b0ll3tta', r'bolletta', r'b0lletta',        # bolletta
        r'fatt4ra', r'fattur4', r'f4ttura',           # fattura
        r'c0nt0', r'cont0', r'c0nto',                 # conto
        r'bl0cc0', r'blocc0', r'bl0cco',              # blocco
        r'sb1occa', r'sbl0cca', r'sb10cca',           # sblocca
        r'att1va', r'attiv4', r'4ttiva',              # attiva
        r'r1attiva', r'riatt1va', r'r14ttiva',        # riattiva
        
        # Financial brands
        r'payp0l', r'v1sa', r'v15a', r'masterc4rd',   # Payment
        r'c0inbase', r'bin4nce', r'chas3',            # Crypto/Bank
        r'we11sfargo', r'wel1sfargo',                 # Wells Fargo
        r'b0famerica', r'bankofamer1ca',              # Bank of America
        
        # Tech platforms
        r'dr0pbox', r'dr0pb0x',                       # Dropbox
        r'slac1k', r'sl4ck',                          # Slack
        r'z00m', r'z0om',                             # Zoom
        r'0utlook', r'outlo0k', r'0utl00k',          # Outlook
        r'yah00', r'yaho0',                           # Yahoo
        
        # Generic patterns: letter + digit + letter
        r'[a-z]0[a-z]',  # a0b pattern (o→0)
        r'[a-z]1[a-z]',  # a1b pattern (l/i→1)
        r'[a-z]3[a-z]',  # a3b pattern (e→3)
        r'[a-z]4[a-z]',  # a4b pattern (a→4)
        r'[a-z]5[a-z]',  # a5b pattern (s→5)
        r'[a-z]7[a-z]',  # a7b pattern (t→7)
        r'[a-z]8[a-z]',  # a8b pattern (b→8)
        r'[a-z]9[a-z]',  # a9b pattern (g→9)
        
        # Common words with substitutions
        r'acc0unt', r'acc0un7', r'4ccount',           # account
        r'secur3', r'secur1ty', r's3curity',          # secure/security
        r'ver1fy', r'v3rify', r'verif1',              # verify
        r'updat3', r'upd4te', r'upd473',              # update
        r'conf1rm', r'c0nfirm', r'conf1r7',           # confirm
        r'l0gin', r'l0g1n', r'10gin',                 # login
        r'b4nk', r'b4nking', r'b0nk',                 # bank
        r'supp0rt', r'supp0r7', r'5upport',           # support
        r'serv1ce', r's3rvice', r'serv1c3',           # service
        r'cust0mer', r'cu5tomer', r'cust0m3r',        # customer
        r'val1date', r'v4lidate', r'validat3',        # validate
        r'4uth', r'auth3nticate', r'4uthenticate',    # auth
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, domain_lower):
            return True
    
    # RILEVAMENTO GENERALE: numeri mescolati con lettere in modo sospetto
    # Rimuovi parti legittime (anni, numeri alla fine, TLD)
    domain_parts = domain_lower.replace('.com', '').replace('.net', '').replace('.org', '').replace('.info', '').replace('.co', '').replace('.io', '')
    
    # Rimuovi anni comuni (2020-2025, 365, etc)
    domain_cleaned = re.sub(r'(19|20)\d{2}', '', domain_parts)
    domain_cleaned = re.sub(r'365', '', domain_cleaned)  # office365, etc.
    
    # Conta cifre e lettere
    digit_count = sum(c.isdigit() for c in domain_cleaned)
    letter_count = sum(c.isalpha() for c in domain_cleaned)
    
    # Se ci sono lettere E numeri mescolati nel dominio (dopo aver rimosso eccezioni legittime)
    if letter_count > 0 and digit_count >= 1:
        # Verifica se i numeri sono MESCOLATI con le lettere (non solo alla fine)
        # Pattern sospetto: lettere, poi cifra, poi ancora lettere (es: micr0soft, supp0rt)
        if re.search(r'[a-z]+\d+[a-z]+', domain_cleaned):
            return True
        
        # Pattern sospetto: cifra all'inizio seguita da lettere (es: 1nstagram, 5ecure)
        if re.search(r'^\d[a-z]+', domain_cleaned):
            return True
    
    # Check per numeri multipli in mezzo al testo (es: micr0s0ft, g00gle)
    if digit_count >= 2 and letter_count > 0:
        # Eccezione: non segnalare se i numeri sono TUTTI alla fine (es: server123)
        if not re.search(r'^[a-z]+\d+$', domain_cleaned):
            return True
    
    return False


def has_double_extension(filename: str) -> bool:
    """
    Detect double file extensions (classic malware delivery).
    
    Patterns:
    - .pdf.exe
    - .docx.exe
    - .pptx.html
    - .xlsx.html
    - .invoice.pdf.exe
    
    Args:
        filename: Filename to check
        
    Returns:
        bool: True if double extension detected
    """
    if not filename:
        return False
    
    filename_lower = filename.lower()
    
    # Critical double extension patterns
    double_ext_patterns = [
        # Document + executable
        '.pdf.exe', '.doc.exe', '.docx.exe',
        '.xls.exe', '.xlsx.exe', '.ppt.exe', '.pptx.exe',
        
        # Document + HTML (phishing pages disguised as documents)
        '.pdf.html', '.doc.html', '.docx.html',
        '.xls.html', '.xlsx.html', '.ppt.html', '.pptx.html',
        
        # Image + executable
        '.jpg.exe', '.png.exe', '.gif.exe', '.bmp.exe',
        
        # Archive + executable
        '.zip.exe', '.rar.exe', '.7z.exe',
        
        # Common filenames with double extensions
        '.invoice.pdf.exe', '.receipt.doc.exe', '.document.pdf.exe',
        '.contract.docx.exe', '.report.xlsx.exe', '.presentation.pptx.exe',
        
        # HTML disguises
        '.invoice.html', '.receipt.html', '.document.html',
        
        # Other dangerous combinations
        '.txt.exe', '.rtf.exe', '.csv.exe'
    ]
    
    return any(pattern in filename_lower for pattern in double_ext_patterns)


def extract_urls(text: str):
    """
    Extract http/https URLs from text with improved pattern matching.
    Handles URLs in various contexts (plain text, HTML, encoded, etc.)
    """
    if not text:
        return []
    
    # Multiple patterns to catch different URL formats
    patterns = [
        # Standard URLs
        r'https?://[^\s<>"\')\]\}]+',
        # URLs with common delimiters
        r'https?://[^\s<>"\']+(?=[.,;:!?)\]])',
        # URLs that might be URL-encoded
        r'https?%3A%2F%2F[^\s<>"\']+',
    ]
    
    urls = []
    for pattern in patterns:
        found = re.findall(pattern, text, re.IGNORECASE)
        urls.extend(found)
    
    # Deduplicate while preserving order
    seen = set()
    unique_urls = []
    for url in urls:
        # Clean up trailing punctuation
        url = url.rstrip('.,;:!?)')
        if url and url not in seen:
            seen.add(url)
            unique_urls.append(url)
    
    return unique_urls


def score_url(url: str):
    """
    Score a single URL for phishing risk with tuned scoring rules.
    
    Returns a dict with:
    - risk_score: int (0-100)
    - risk_level: str (LOW/MEDIUM/HIGH)
    - indicators: list of findings
    - from_phishing_database: bool
    - url: str
    """
    indicators = []
    score = 0
    from_phishing_database = False
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        
        # HEURISTICS - ALWAYS RUN THESE CHECKS FIRST
        # The database check will be done at the END as a BONUS signal
        
        # 1) Brand impersonation in domain (but not official)
        known_brands = {
            "paypal": ["paypal.com"],
            "amazon": ["amazon.com", "amazon.co.uk", "amazon.de"],
            "microsoft": ["microsoft.com", "live.com", "outlook.com"],
            "google": ["google.com", "gmail.com", "drive.google.com"],
            "apple": ["apple.com", "icloud.com"],
            "facebook": ["facebook.com"],
            "netflix": ["netflix.com"],
            "ebay": ["ebay.com"],
            "bank": ["chase.com", "bankofamerica.com", "wellsfargo.com"],
            "bankofamerica": ["bankofamerica.com"],  # ADDED
            "fedex": ["fedex.com", "fedex.co.uk"],  # ADDED
            "drive": ["drive.google.com", "google.com"],  # ADDED (Google Drive)
            "accounts": ["accounts.google.com", "google.com"],  # ADDED (Google Accounts)
            "github": ["github.com"],
            "intesa": ["intesasanpaolo.com"],
            "intesasanpaolo": ["intesasanpaolo.com"],
            "deloitte": ["deloitte.com"],
            "ups": ["ups.com"],
            "poste": ["poste.it", "posteitaliane.it"],
            "inps": ["inps.it"],
            "office": ["office.com", "microsoft.com"],
            "icloud": ["icloud.com", "apple.com"]
        }
        
        for brand, official_domains in known_brands.items():
            if brand in domain:
                # Check if it's NOT an official domain
                is_official = any(official in domain for official in official_domains)
                if not is_official:
                    score += 55  # Increased from 40 - high penalty for brand impersonation
                    indicators.append({
                        "risk_score": 55,
                        "category": "brand_impersonation",
                        "detail": f"Domain mentions '{brand}' but is not official {brand} domain",
                        "educational": {
                            "title": "🎭 Brand Impersonation",
                            "explanation": "Phishers use brand names in fake domains to trick users.",
                            "tips": [
                                f"Official {brand} domains: {', '.join(official_domains)}",
                                "Always check the exact domain name",
                                "Go directly to official sites, don't click email links"
                            ]
                        }
                    })
                    break
        
        # 2) URL Shorteners (hide real destination)
        if any(short in domain for short in URL_SHORTENERS):
            score += 40  # CRITICAL - shortened URLs are major phishing vector
            indicators.append({
                "risk_score": 40,
                "category": "url_shortener",
                "detail": f"🚨 CRITICAL: Shortened URL hides real destination: {domain}",
                "educational": EDUCATIONAL_TIPS["url_shortener"]
            })
        
        # 3) Plain IP address in domain
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        if re.match(ip_pattern, domain):
            # Check if path contains login/update
            if any(suspicious in path for suspicious in ['/login', '/update', '/verify', '/account', '/auth', '/signin', '/reset']):
                score += 60  # CRITICAL: IP + sensitive path = molto sospetto
                indicators.append({
                    "risk_score": 60,
                    "category": "ip_with_sensitive_path",
                    "detail": f"🚨 CRITICAL: IP address with login/auth path: {domain}{path}",
                    "educational": {
                        "title": "🔢 IP Address + Login Path",
                        "explanation": "Legitimate sites use domain names, not raw IPs for login pages.",
                        "tips": [
                            "Banks and services NEVER use IP addresses",
                            "This is a major red flag",
                            "Do not enter any credentials"
                        ]
                    }
                })
            else:
                score += 20  # IP alone is suspicious
                indicators.append({
                    "risk_score": 20,
                    "category": "ip_address",
                    "detail": f"URL uses IP address instead of domain: {domain}",
                    "educational": {
                        "title": "🔢 Raw IP Address",
                        "explanation": "Professional sites use domain names, not IP addresses.",
                        "tips": [
                            "Legitimate companies use domains like 'example.com'",
                            "IP addresses in URLs are often suspicious",
                            "Verify the sender before clicking"
                        ]
                    }
                })
        
        # 4) HTTP (insecure) adds penalty
        if parsed.scheme == "http":
            score += 25  # Increased from 18 - significant penalty for no HTTPS
            indicators.append({
                "risk_score": 25,
                "category": "http_insecure",
                "detail": "Insecure HTTP connection (no encryption)",
                "educational": EDUCATIONAL_TIPS["http_insecure"]
            })
        
        # 5) Suspicious TLDs
        for tld in SUSPICIOUS_TLDS:
            if domain.endswith(tld):
                score += 30  # CRITICAL - suspicious TLDs like .ru, .tk, .xyz are major red flags
                indicators.append({
                    "risk_score": 30,
                    "category": "suspicious_tld",
                    "detail": f"🚨 CRITICAL: Domain uses high-risk extension {tld}: {domain}",
                    "educational": EDUCATIONAL_TIPS["suspicious_tld"]
                })
                break
        
        # 6) Punycode/IDN homograph attack o caratteri Unicode sospetti
        if 'xn--' in domain:
            score += 65  # CRITICAL - sophisticated attack con punycode
            indicators.append({
                "risk_score": 65,
                "category": "punycode",
                "detail": "🚨 CRITICAL: Domain uses punycode (homograph attack)",
                "educational": EDUCATIONAL_TIPS["punycode"]
            })
        # Controlla caratteri Unicode sospetti (non-ASCII) che potrebbero essere IDN homograph
        elif any(ord(c) > 127 for c in domain):
            score += 70  # CRITICAL - caratteri Unicode nel dominio (possibile homograph)
            indicators.append({
                "risk_score": 70,
                "category": "unicode_homograph",
                "detail": f"🚨 CRITICAL: Domain contains Unicode/non-ASCII characters (IDN homograph attack): {domain}",
                "educational": {
                    "title": "🔤 IDN Homograph Attack",
                    "explanation": "Domain uses Unicode characters that look like ASCII to impersonate legitimate sites.",
                    "tips": [
                        "Example: Cyrillic 'а' (U+0430) looks identical to Latin 'a'",
                        "'аррӏеid.com' uses Cyrillic letters to mimic 'appleid.com'",
                        "This is an extremely sophisticated phishing technique",
                        "Always verify the domain in the browser address bar",
                        "NEVER click on such links"
                    ]
                }
            })
        
        # 7) Character substitution (typosquatting) in domain
        if has_char_substitution(domain):
            score += 50  # High penalty for typosquatting
            indicators.append({
                "risk_score": 50,
                "category": "typosquatting",
                "detail": f"Character substitution detected (typosquatting): {domain}",
                "educational": {
                    "title": "🚨 Typosquatting Attack",
                    "explanation": "Domain uses digit substitutions to imitate legitimate sites.",
                    "tips": [
                        "Examples: 'paypa1' (1→l), 'micr0soft' (0→o), 'goog1e' (1→l)",
                        "Common: 0→o, 1→l/i, 5→s, 3→e, 4→a",
                        "This is a STRONG phishing indicator",
                        "NEVER trust URLs with digit substitutions"
                    ]
                }
            })
        
        # 8) Phishing keywords in URL - scoring progressivo per keyword multiple
        url_lower = url.lower()
        domain_lower = domain.lower()
        
        # Conta keyword critiche nel dominio (più grave)
        critical_keywords = ['login', 'verify', 'secure', 'update', 'account', 'auth', 'signin', 'reset', 'confirm', 'security', 'verification', 'authentication']
        domain_keyword_matches = [kw for kw in critical_keywords if kw in domain_lower]
        
        # Conta tutte le keyword nell'URL
        url_keyword_matches = [kw for kw in PHISHING_KEYWORDS if kw in url_lower]
        
        # Penalità progressiva basata sul numero di keyword nel dominio
        if len(domain_keyword_matches) >= 3:
            # CRITICAL: 3+ keyword phishing nel dominio (es: login-update-secure-service.com)
            keyword_score = 60
            indicators.append({
                "risk_score": keyword_score,
                "category": "excessive_phishing_keywords",
                "detail": f"🚨 CRITICAL: Domain contains {len(domain_keyword_matches)} security keywords: {', '.join(domain_keyword_matches)}",
                "educational": {
                    "title": "🎣 Excessive Phishing Keywords",
                    "explanation": "Domain stacks multiple security terms - obvious phishing pattern.",
                    "tips": [
                        "Legitimate sites use simple domains (e.g., 'paypal.com')",
                        "Phishers add keywords like 'login-secure-verify' to seem legitimate",
                        "'login-update-secure-service.com' is obviously fake",
                        "NEVER trust domains with 3+ security keywords"
                    ]
                }
            })
            score += keyword_score
        elif len(domain_keyword_matches) == 2:
            # Moderato: 2 keyword nel dominio
            keyword_score = 25
            indicators.append({
                "risk_score": keyword_score,
                "category": "multiple_phishing_keywords",
                "detail": f"Domain contains multiple security keywords: {', '.join(domain_keyword_matches)}",
                "educational": {
                    "title": "🎣 Multiple Phishing Keywords",
                    "explanation": "Domain stacks security terms - suspicious pattern.",
                    "tips": [
                        "Legitimate sites use simple domains",
                        "Real security pages are at official domains, not keyword-stuffed domains"
                    ]
                }
            })
            score += keyword_score
        elif url_keyword_matches:
            # Scoring per keyword nell'intero URL (non solo dominio)
            if len(url_keyword_matches) >= 3:
                keyword_score = 35  # Molte keyword
            elif len(url_keyword_matches) >= 2:
                keyword_score = 20  # Alcune keyword
            else:
                keyword_score = 10  # Poche keyword
            
            score += keyword_score
            indicators.append({
                "risk_score": keyword_score,
                "category": "phishing_keywords_in_url",
                "detail": f"URL contains {len(url_keyword_matches)} phishing keyword(s): {', '.join(url_keyword_matches[:5])}",
                "educational": {
                    "title": "🎣 Phishing Keywords in URL",
                    "explanation": "Phishers use security words to appear legitimate.",
                    "tips": [
                        "Real security URLs don't advertise with keywords",
                        "Access security features directly from official sites",
                        "Be suspicious of 'verify', 'secure', 'login' in URLs"
                    ]
                }
            })
        
        # 9) PHISHING.DATABASE CHECK (BONUS SIGNAL)
        # This is checked AFTER all heuristics so both systems contribute
        # Database hit is a STRONG signal but not the only one
        if is_url_in_phishing_database(url):
            from_phishing_database = True
            database_bonus = 70  # Strong bonus to ensure HIGH risk (typically pushes to 90-100)
            score += database_bonus
            indicators.insert(0, {  # Add as first indicator (highest priority)
                "risk_score": database_bonus,
                "category": "known_phishing_url",
                "detail": "🚨 CRITICAL: URL found in Phishing.Database (491,010+ known phishing domains)",
                "educational": EDUCATIONAL_TIPS["known_phishing_url"]
            })
            print(f"[PhishForge] 🚨 Database hit: {url} (heuristic: {score-database_bonus}, +{database_bonus} DB bonus = {score} total)")
        
        # 10) MULTI-DATABASE CHECK (Discord, Steam, AntiScam, phish.sinking.yachts, anti-fish, etc.)
        # Additional check against consolidated databases for maximum coverage
        if not from_phishing_database and is_url_in_multi_database(url):
            from_phishing_database = True  # Treat as database hit
            multi_db_bonus = 75  # VERY STRONG signal - these are known active phishing sites
            score += multi_db_bonus
            indicators.insert(0, {
                "risk_score": multi_db_bonus,
                "category": "known_phishing_multidatabase",
                "detail": "🚨 CRITICAL: URL found in consolidated phishing databases (Discord/Steam/AntiScam/phish.sinking.yachts/anti-fish)",
                "educational": {
                    "title": "🚨 Known Phishing Site",
                    "explanation": "This URL appears in multiple specialized phishing databases including Discord scams, Steam/Nitro phishing, and real-time phishing feeds.",
                    "tips": [
                        "Do NOT click or visit this URL",
                        "These databases track active phishing campaigns",
                        "Commonly used for Discord Nitro scams, Steam account theft",
                        "Report to your security team immediately",
                        "Delete the message containing this link"
                    ]
                }
            })
            print(f"[PhishForge] 🚨 Multi-DB hit: {url} (heuristic: {score-multi_db_bonus}, +{multi_db_bonus} Multi-DB bonus = {score} total)")
        
        # Cap score at 100
        final_score = min(score, 100)
        
        # Determine risk level based on tuned thresholds
        # 0-25 → LOW, 26-55 → MEDIUM, 56-100 → HIGH
        if final_score >= 56:
            risk_level = "HIGH"
        elif final_score >= 26:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "url": url,
            "risk_score": final_score,
            "risk_level": risk_level,
            "indicators": indicators,
            "from_phishing_database": from_phishing_database
        }
    
    except Exception as e:
        print(f"[PhishForge] Error scoring URL {url}: {e}")
        return {
            "url": url,
            "risk_score": 0,
            "risk_level": "LOW",
            "indicators": [],
            "from_phishing_database": False,
            "error": str(e)
        }


def analyze_sender(sender: str):
    """Analyze sender to detect discrepancies."""
    display_name, email_addr = parseaddr(sender)
    issues = []
    
    if not email_addr:
        return issues, display_name, email_addr
    
    email_lower = email_addr.lower()
    display_lower = display_name.lower() if display_name else ""
    
    # Extract domain
    if '@' in email_addr:
        domain = email_addr.split('@')[1].lower()
    else:
        domain = ""
    
    # Check if display name suggests a company
    # but domain doesn't match
    known_companies = [
        "paypal", "amazon", "microsoft", "google", "apple", "facebook",
        "instagram", "netflix", "ebay", "linkedin", "twitter", "bank",
        "poste", "inps", "agenzia entrate", "unicredit", "intesa"
    ]
    
    for company in known_companies:
        if company in display_lower:
            # Display name mentions the company
            if company not in domain:
                issues.append({
                    "type": "sender_mismatch",
                    "company": company,
                    "display": display_name,
                    "email": email_addr
                })
    
    # Check for suspicious characters (punycode/IDN)
    if 'xn--' in domain:
        issues.append({
            "type": "punycode",
            "domain": domain
        })
    
    return issues, display_name, email_addr


def score_email(subject: str, sender: str, body: str):
    """
    Calculate phishing risk score with tuned scoring rules.
    Scores are calibrated so typical phishing scores 80+, marketing 20-40, normal < 15.
    
    ALWAYS returns a valid dict, even if internal errors occur.
    Implements robust error handling with graceful fallback.
    """
    # Initialize fallback for error cases
    fallback_result = {
        "score": 0,
        "label": "✅ LOW RISK",
        "risk_level": "LOW",
        "findings": [],
        "urls": [],
        "sender_info": {"display_name": "", "email": sender if sender else ""},
        "from_phishing_database": False
    }
    
    try:
        findings = []
        score = 0
        from_phishing_database = False

        full_text = f"{subject}\n{body}".lower()

        # Sender analysis
        sender_issues, display_name, email_addr = analyze_sender(sender)
        for issue in sender_issues:
            if issue["type"] == "sender_mismatch":
                score += 25  # Increased from 15
                findings.append({
                    "risk_score": 25,
                    "category": "sender_mismatch",
                    "detail": f"Display name '{issue['display']}' mentions '{issue['company']}' but email is {issue['email']}",
                    "educational": EDUCATIONAL_TIPS["sender_mismatch"]
                })
            elif issue["type"] == "punycode":
                score += 35  # Increased from 20
                findings.append({
                    "risk_score": 35,
                    "category": "punycode",
                    "detail": f"Domain {issue['domain']} uses encoded characters (punycode) - possible impersonation",
                    "educational": EDUCATIONAL_TIPS["punycode"]
                })

        # 1) Check for phishing PHRASES first (higher weight: ~15-20 points each)
        phrase_hits = [phrase for phrase in PHISHING_PHRASES if phrase in full_text]
        if phrase_hits:
            phrase_score = min(len(phrase_hits) * 18, 55)  # Reduced from 22, cap at 55 points
            score += phrase_score
            findings.append({
                "risk_score": phrase_score,
                "category": "phishing_phrases",
                "detail": f"Found {len(phrase_hits)} phishing phrases: {', '.join(phrase_hits[:3])}",
                "educational": EDUCATIONAL_TIPS["suspicious_keywords"]
            })

        # 2) Check for individual phishing KEYWORDS (~5 points each, reduced from 10)
        # Only count if 2+ keywords found (reduce false positives from single common words)
        keyword_hits = [kw for kw in PHISHING_KEYWORDS if kw in full_text]
        if len(keyword_hits) >= 2:  # Require at least 2 keywords
            keyword_score = min(len(keyword_hits) * 5, 30)  # Reduced from 10 points each, cap at 30
            score += keyword_score
            findings.append({
                "risk_score": keyword_score,
                "category": "phishing_keywords",
                "detail": f"Found {len(keyword_hits)} phishing keywords: {', '.join(keyword_hits[:5])}",
                "educational": EDUCATIONAL_TIPS["suspicious_keywords"]
            })

        # 3) URLs in body - ALWAYS run heuristic analysis on ALL URLs
        urls = extract_urls(body)
    
        # Brand impersonation check - comprehensive list
        known_brands = {
            # Payment platforms
            "paypal": ["paypal.com", "paypal.it"],
            "stripe": ["stripe.com"],
            "revolut": ["revolut.com"],
            "wise": ["wise.com", "transferwise.com"],
            
            # E-commerce
            "amazon": ["amazon.com", "amazon.it", "amazon.co.uk", "amazon.de", "amazon.fr", "amazon.es"],
            "ebay": ["ebay.com", "ebay.it"],
            "alibaba": ["alibaba.com"],
            
            # Tech giants
            "microsoft": ["microsoft.com", "live.com", "outlook.com", "office.com", "onedrive.com"],
            "google": ["google.com", "gmail.com", "google.it"],
            "apple": ["apple.com", "icloud.com", "me.com"],
            "meta": ["facebook.com", "meta.com", "instagram.com"],
            "facebook": ["facebook.com", "fb.com"],
            "instagram": ["instagram.com"],
            "whatsapp": ["whatsapp.com"],
            "twitter": ["twitter.com", "x.com"],
            "linkedin": ["linkedin.com"],
            "github": ["github.com"],
            "dropbox": ["dropbox.com"],
            "zoom": ["zoom.us"],
            
            # Streaming
            "netflix": ["netflix.com"],
            "spotify": ["spotify.com"],
            "disney": ["disneyplus.com", "disney.com"],
            
            # Italian banks
            "intesa": ["intesasanpaolo.com"],
            "intesasanpaolo": ["intesasanpaolo.com"],
            "sanpaolo": ["intesasanpaolo.com"],
            "unicredit": ["unicredit.it"],
            "bancaintesa": ["intesasanpaolo.com"],
            "poste": ["poste.it", "posteitaliane.it"],
            "postepay": ["poste.it", "posteitaliane.it"],
            "posteitaliane": ["poste.it", "posteitaliane.it"],
            "bnl": ["bnl.it"],
            "mps": ["mps.it", "montepaschi.it"],
            "bper": ["bper.it"],
            "credem": ["credem.it"],
            "banco": ["bancobpm.it"],
            
            # International banks
            "chase": ["chase.com"],
            "bankofamerica": ["bankofamerica.com"],
            "wellsfargo": ["wellsfargo.com"],
            "citi": ["citi.com", "citibank.com"],
            "hsbc": ["hsbc.com"],
            "barclays": ["barclays.co.uk"],
            "santander": ["santander.com"],
            "ing": ["ing.com", "ing.it"],
            
            # Crypto
            "coinbase": ["coinbase.com"],
            "binance": ["binance.com"],
            "kraken": ["kraken.com"],
            
            # Generic banking keywords
            "bank": ["chase.com", "bankofamerica.com", "wellsfargo.com"],
            "banking": ["chase.com", "bankofamerica.com"],
            "banca": ["intesasanpaolo.com", "unicredit.it"]
        }
        
        # HEURISTIC URL ANALYSIS - runs independently of database
        for url in urls:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                path = parsed.path.lower()
                
                # Brand impersonation detection
                for brand, official_domains in known_brands.items():
                    if brand in domain and not any(official in domain for official in official_domains):
                        score += 45  # Increased from 40
                        findings.append({
                            "risk_score": 45,
                            "category": "brand_impersonation_url",
                            "detail": f"URL impersonates '{brand}' but isn't official domain: {domain}",
                            "url": url,
                            "educational": {
                                "title": "🎭 Fake Brand URL",
                                "explanation": "Domain pretends to be a known brand but isn't official.",
                                "tips": [
                                    "Always verify the exact domain name",
                                    "Go to official sites directly, don't click email links",
                                    "Phishers register similar-looking domains"
                                ]
                            }
                        })
                        break
                
                # FUZZY BRAND MATCHING - Catches assonance and visual tricks
                # Examples: arnazon→amazon (rn→m), paypa1→paypal (1→l), g00gle→google (0→o)
                is_fuzzy_match, matched_brand, normalized_domain = check_fuzzy_brand_match(domain, known_brands)
                if is_fuzzy_match:
                    score += 60  # VERY HIGH - advanced phishing technique
                    findings.append({
                        "risk_score": 60,
                        "category": "fuzzy_brand_impersonation",
                        "detail": f"🚨 CRITICAL: Domain uses visual tricks to impersonate '{matched_brand}': {domain}",
                        "url": url,
                        "educational": {
                            "title": "🚨 Advanced Brand Impersonation",
                            "explanation": f"Domain uses character substitutions to look like '{matched_brand}'. "
                                          f"Visual tricks detected: {domain} → {normalized_domain}",
                            "tips": [
                                "Examples: 'rn' looks like 'm' (arnazon→amazon)",
                                "'vv' looks like 'w' (vvebsite→website)",
                                "'0' looks like 'o' (micr0soft→microsoft)",
                                "'1' looks like 'l' or 'i' (paypa1→paypal)",
                                "This is EXTREMELY sophisticated phishing",
                                "NEVER trust these domains",
                                "Legitimate companies use correct spelling"
                            ]
                        }
                    })
                
                # SPECIAL CHECK: posteitaliane variations (CRITICAL for Italy)
                poste_fake_patterns = [
                    r'poste.*italiane', r'p0ste', r'po5te', r'post3',
                    r'posteitalian[^e]', r'posteitalia[^n]'
                ]
                is_fake_poste = any(re.search(pattern, domain, re.IGNORECASE) for pattern in poste_fake_patterns)
                is_real_poste = any(official in domain for official in ["poste.it", "posteitaliane.it"])
                
                if is_fake_poste and not is_real_poste:
                    score += 55  # VERY HIGH penalty
                    findings.append({
                        "risk_score": 55,
                        "category": "fake_posteitaliane",
                        "detail": f"🚨 CRITICAL: Fake Poste Italiane domain: {domain}",
                        "url": url,
                        "educational": {
                            "title": "🚨 ATTENZIONE: Poste Italiane FALSO",
                            "explanation": "Questo NON è il vero sito di Poste Italiane. Domini ufficiali: poste.it, posteitaliane.it",
                            "tips": [
                                "Poste Italiane usa SOLO poste.it o posteitaliane.it",
                                "Qualsiasi variazione è FALSA (posteitaliane-xyz.it, ecc.)",
                                "Non inserire MAI credenziali o dati bancari",
                                "Segnala immediatamente a Poste Italiane"
                            ]
                        }
                    })
                
                # Character substitution in domain OR PATH
                domain_and_path = domain + path  # Check both!
                if has_char_substitution(domain_and_path):
                    score += 50  # CRITICAL: Increased from 35 to 50
                    findings.append({
                        "risk_score": 50,
                        "category": "typosquatting_url",
                        "detail": f"CRITICAL: Character substitution detected (typosquatting): {url}",
                        "url": url,
                        "educational": {
                            "title": "🚨 CRITICAL: Typosquatting Attack",
                            "explanation": f"URL uses digit substitutions to imitate legitimate sites. Detected in: {domain_and_path}",
                            "tips": [
                                "Examples: 'r1mbors0' (rimborso), 'ver1f1ca' (verifica), 'paypa1' (paypal)",
                                "Common: 0→o, 1→l/i, 5→s, 3→e, 4→a",
                                "This is a STRONG phishing indicator",
                                "NEVER trust URLs with digit substitutions",
                                "Legitimate companies use correct spelling"
                            ]
                        }
                    })

                # URL Shortener
                if any(short in domain for short in URL_SHORTENERS):
                    score += 30
                    findings.append({
                        "risk_score": 30,
                        "category": "url_shortener",
                        "detail": f"Shortened URL hides destination: {domain}",
                        "url": url,
                        "educational": EDUCATIONAL_TIPS["url_shortener"]
                    })

                # IP address in URL
                ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
                if re.match(ip_pattern, domain):
                    score += 25
                    findings.append({
                        "risk_score": 25,
                        "category": "ip_address_url",
                        "detail": f"URL uses IP address instead of domain: {domain}",
                        "url": url,
                        "educational": {
                            "title": "🚨 IP Address URL",
                            "explanation": "Legitimate websites use domain names, not IP addresses.",
                            "tips": [
                                "This is a major red flag",
                                "Phishers use IPs to avoid domain detection",
                                "Never trust IP-based URLs for sensitive actions"
                            ]
                        }
                    })
                    # Extra penalty if login/sensitive path
                    sensitive_paths = [
                        '/login', '/signin', '/sign-in', '/log-in',
                        '/auth', '/authenticate', '/sso',
                        '/account', '/myaccount', '/my-account',
                        '/verify', '/verification', '/validate',
                        '/update', '/confirm', '/reset',
                        '/password', '/reset-password', '/change-password',
                        '/secure', '/security', '/2fa', '/mfa',
                        '/payment', '/checkout', '/billing',
                        '/wallet', '/banking', '/transfer'
                    ]
                    if any(s in path for s in sensitive_paths):
                        score += 25  # Increased penalty
                        findings.append({
                            "risk_score": 25,
                            "category": "ip_with_sensitive_path",
                            "detail": f"CRITICAL: IP address with sensitive path: {url}",
                            "url": url,
                            "educational": {
                                "title": "🚨 CRITICAL: IP + Sensitive Action",
                                "explanation": "Legitimate sites NEVER use IP addresses for login/payment/account pages.",
                                "tips": [
                                    "This is an extremely strong phishing indicator",
                                    "Do NOT enter any credentials or payment info",
                                    "Report to security team immediately",
                                    "Real banks/services always use proper domains"
                                ]
                            }
                        })

                # Insecure HTTP
                if parsed.scheme == "http":
                    score += 18
                    findings.append({
                        "risk_score": 18,
                        "category": "http_insecure",
                        "detail": f"Insecure HTTP link (no encryption): {url}",
                        "url": url,
                        "educational": EDUCATIONAL_TIPS["http_insecure"]
                    })

                # Suspicious TLDs
                for tld in SUSPICIOUS_TLDS:
                    if domain.endswith(tld):
                        score += 12
                        findings.append({
                            "risk_score": 12,
                            "category": "suspicious_tld",
                            "detail": f"Risky domain extension {tld}: {domain}",
                            "url": url,
                            "educational": EDUCATIONAL_TIPS["suspicious_tld"]
                        })
                        break
                
                # Dangerous file extensions in URL path
                dangerous_extensions = [
                    '.exe', '.scr', '.bat', '.cmd', '.com', '.pif',
                    '.js', '.jse', '.vbs', '.vbe', '.jar',
                    '.msi', '.reg', '.ps1', '.apk'
                ]
                if any(path.endswith(ext) for ext in dangerous_extensions):
                    score += 30
                    findings.append({
                        "risk_score": 30,
                        "category": "dangerous_file_url",
                        "detail": f"URL points to dangerous executable file: {url}",
                        "url": url,
                        "educational": {
                            "title": "🚨 Dangerous File Link",
                            "explanation": "URL links to executable file that can install malware.",
                            "tips": [
                                "Never download executables from emails",
                                "Legitimate companies don't send .exe files",
                                "This could install ransomware or steal data",
                                "Delete email immediately"
                            ]
                        }
                    })
                
                # Double extension detection in URL
                double_ext_patterns = [
                    '.pdf.exe', '.doc.exe', '.docx.exe', '.xls.exe',
                    '.pdf.html', '.docx.html', '.xlsx.html'
                ]
                if any(pattern in path.lower() for pattern in double_ext_patterns):
                    score += 40  # Very high penalty
                    findings.append({
                        "risk_score": 40,
                        "category": "double_extension_url",
                        "detail": f"CRITICAL: Double extension in URL (malware technique): {url}",
                        "url": url,
                        "educational": {
                            "title": "🚨 CRITICAL: Double Extension",
                            "explanation": "Double extensions (.pdf.exe) are classic malware delivery technique.",
                            "tips": [
                                "This is a known malware distribution method",
                                "Real documents don't need .exe extension",
                                "Do NOT click or download",
                                "Report to security team"
                            ]
                        }
                    })
                        
            except Exception as e:
                # Don't fail on single URL parsing error
                logger.warning(f"Error analyzing URL {url}: {e}")
                continue

        # ========================================================
        # ENTERPRISE HEURISTICS: Typosquatting Detection
        # ========================================================
        # Check sender domain for character substitution
        if email_addr and '@' in email_addr:
            sender_domain = email_addr.split('@')[1] if '@' in email_addr else ""
            if has_char_substitution(sender_domain):
                score += 20
                findings.append({
                    "risk_score": 20,
                    "category": "typosquatting",
                    "detail": f"Domain contains character substitution (typosquatting): {sender_domain}",
                    "educational": {
                        "title": "🔤 Typosquatting Attack",
                        "explanation": "Attackers use digit substitutions (0→O, 1→l, 5→S) to create fake domains.",
                        "tips": [
                            "Example: 'paypa1.com' uses '1' instead of 'l'",
                            "Always verify domain spelling carefully",
                            "Legitimate companies don't use digits in brand names",
                            "Contact company through official channels to verify"
                        ]
                    }
                })
        
        # ========================================================
        # 4) Generic security sender
        # ========================================================
        sender_lower = sender.lower()
        if any(x in sender_lower for x in ["support", "helpdesk", "security", "noreply"]):
            trusted = False
            if email_addr:
                domain = email_addr.split('@')[1].lower() if '@' in email_addr else ""
                trusted_domains = ["yourcompany.com", "azienda.it", "google.com", "microsoft.com"]
                trusted = any(td in domain for td in trusted_domains)
        
            if not trusted:
                score += 8  # Increased from 5
                findings.append({
                    "risk_score": 8,
                    "category": "generic_sender",
                    "detail": f"Generic support/security sender: {email_addr or sender}",
                    "educational": EDUCATIONAL_TIPS["generic_sender"]
                })

        # 5) Credential request
        credential_keywords = ["login", "sign in", "password", "username", "credentials"]
        if any(kw in full_text for kw in credential_keywords):
            score += 12  # Increased from 5
            findings.append({
                "risk_score": 12,
                "category": "credential_request",
                "detail": "Email requests login or credentials",
                "educational": EDUCATIONAL_TIPS["credential_request"]
            })
        
        # 5.5) Dangerous attachment filenames mentioned in body/subject
        # Detect double extensions and suspicious file mentions
        dangerous_attachment_patterns = [
            # Double extensions (classic malware technique)
            r'\b\w+\.pdf\.exe\b', r'\b\w+\.doc\.exe\b', r'\b\w+\.docx\.exe\b',
            r'\b\w+\.xls\.exe\b', r'\b\w+\.xlsx\.exe\b', r'\b\w+\.txt\.exe\b',
            r'\b\w+\.pdf\.html\b', r'\b\w+\.doc\.html\b', r'\b\w+\.docx\.html\b',
            r'\b\w+\.xls\.html\b', r'\b\w+\.xlsx\.html\b',
            r'\b\w+\.pdf\.scr\b', r'\b\w+\.doc\.scr\b',
            r'\b\w+\.pdf\.js\b', r'\b\w+\.doc\.js\b',
            # Typosquatted extensions  
            r'\b\w+\.xlxs\b',  # xlsx misspelled
            r'\b\w+\.docm\b', r'\b\w+\.xlsm\b',  # Macro-enabled (dangerous)
            # Executable attachments (specific dangerous ones only)
            r'\b\w+\.exe\b', r'\b\w+\.scr\b', r'\b\w+\.bat\b',
            r'\b\w+\.cmd\b', r'\b\w+\.pif\b',  # removed .com (too generic)
            r'\b\w+\.vbs\b', r'\b\w+\.js\b', r'\b\w+\.jse\b',
            r'\b\w+\.jar\b', r'\b\w+\.msi\b', r'\b\w+\.apk\b'
        ]
        
        attachment_matches = []
        for pattern in dangerous_attachment_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            attachment_matches.extend(matches)
        
        if attachment_matches:
            # Higher penalty for double extensions
            is_double_ext = any('.' in match[:-4] and '.' in match[-4:] for match in attachment_matches)
            penalty = 55 if is_double_ext else 35
            
            score += penalty
            findings.append({
                "risk_score": penalty,
                "category": "dangerous_attachment",
                "detail": f"{'CRITICAL' if is_double_ext else 'WARNING'}: Dangerous attachment(s) mentioned: {', '.join(attachment_matches[:3])}",
                "educational": {
                    "title": "🚨 Malicious Attachment Detected" if is_double_ext else "⚠️ Suspicious Attachment",
                    "explanation": "Double extensions (.pdf.exe) are a classic malware delivery technique." if is_double_ext else "Executable attachments can install malware.",
                    "tips": [
                        "DO NOT open these attachments under any circumstances" if is_double_ext else "Be very cautious with executable files",
                        "Real PDFs/documents don't have .exe, .html, or .scr extensions",
                        "Delete the email immediately and report as spam",
                        "Scan your computer if you already opened it"
                    ] if is_double_ext else [
                        "Legitimate companies rarely send executables",
                        "Verify with sender through another channel",
                        "Scan with antivirus before opening"
                    ]
                }
            })

        # 6) Phishing.Database check - BONUS signal (checked AFTER all heuristics)
        # Check ALL extracted URLs against the database
        if urls:  # Only check if there are URLs
            phishing_urls_found = []
            for url in urls:
                if is_url_in_phishing_database(url):
                    phishing_urls_found.append(url)
        
            if phishing_urls_found:
                from_phishing_database = True
                database_bonus = 70  # Strong bonus to push into HIGH risk
                score += database_bonus
                
                findings.insert(0, {  # Add as first finding (highest priority)
                    "risk_score": database_bonus,
                    "category": "known_phishing_url",
                    "detail": f"🚨 CRITICAL: {len(phishing_urls_found)} URL(s) found in Phishing.Database: {', '.join(phishing_urls_found[:2])}",
                    "urls": phishing_urls_found,
                    "educational": EDUCATIONAL_TIPS["known_phishing_url"]
                })
                
                print(f"[PhishForge] 🚨 Database hit in email: {phishing_urls_found} (added +{database_bonus} points)")

        # Cap score at 100
        final_score = min(score, 100)

        # Final decision based on tuned thresholds
        # 0-25 → LOW, 26-55 → MEDIUM, 56-100 → HIGH
        if final_score >= 56 or from_phishing_database:
            label = "🚨 HIGH RISK - Likely Phishing"
            risk_level = "HIGH"
        elif final_score >= 26:
            label = "⚠️ MEDIUM RISK - Suspicious Email"
            risk_level = "MEDIUM"
        else:
            label = "✅ LOW RISK"
            risk_level = "LOW"

        return {
            "score": final_score,
            "label": label,
            "risk_level": risk_level,
            "findings": findings,
            "urls": urls,
            "sender_info": {
                "display_name": display_name,
                "email": email_addr
            },
            "from_phishing_database": from_phishing_database
        }
        
    except Exception as e:
        # Log error and return fallback
        print(f"[PhishForge] Error in score_email: {e}")
        import traceback
        traceback.print_exc()
        return fallback_result


def analyze_email_content(subject: str, body: str, sender: str = None):
    """
    Wrapper function for score_email - returns dict with risk_score and findings.
    Compatible with local_api.py expectations.
    """
    result = score_email(subject, sender or "", body)
    return {
        "risk_score": result["score"],
        "risk_level": result["risk_level"],
        "findings": result["findings"],
        "urls": result["urls"],
        "sender_info": result["sender_info"],
        "from_phishing_database": result.get("from_phishing_database", False)
    }


def analyze_url(url: str):
    """
    Analyze a single URL for phishing indicators.
    """
    findings = []
    score = 0
    
    try:
        # Check phishing databases first
        if is_url_in_phishing_database(url):
            score += 90
            findings.append({
                "risk_score": 90,
                "category": "known_phishing_url",
                "detail": f"URL found in Phishing.Database",
                "educational": EDUCATIONAL_TIPS.get("known_phishing_url", {
                    "title": "🚨 Known Phishing URL",
                    "explanation": "This URL is in known phishing databases",
                    "tips": ["Do not visit this URL", "Report it to authorities"]
                })
            })
            return {
                "risk_score": score,
                "risk_level": "HIGH",
                "findings": findings,
                "urls": [{"url": url, "risk_score": score}]
            }
        
        if is_url_in_multi_database(url):
            score += 85
            findings.append({
                "risk_score": 85,
                "category": "known_phishing_url",
                "detail": f"URL found in multi-database check",
                "educational": EDUCATIONAL_TIPS.get("known_phishing_url", {
                    "title": "🚨 Known Phishing URL",
                    "explanation": "This URL is in known phishing databases",
                    "tips": ["Do not visit this URL", "Report it to authorities"]
                })
            })
            return {
                "risk_score": score,
                "risk_level": "HIGH",
                "findings": findings,
                "urls": [{"url": url, "risk_score": score}]
            }
        
        # Heuristic analysis
        parsed = urlparse(url if url.startswith('http') else f'http://{url}')
        domain = parsed.netloc or parsed.path.split('/')[0]
        
        # Check for suspicious TLDs
        tld = domain.split('.')[-1] if '.' in domain else ''
        if tld in HIGH_RISK_TLDS:
            score += 20
            findings.append({
                "risk_score": 20,
                "category": "suspicious_tld",
                "detail": f"High-risk TLD: .{tld}",
                "educational": EDUCATIONAL_TIPS.get("suspicious_tld", {
                    "title": "⚠️ Suspicious Domain Extension",
                    "explanation": f"The .{tld} extension is commonly used in phishing",
                    "tips": ["Verify the URL through official channels"]
                })
            })
        
        # Check for URL shorteners
        if domain in URL_SHORTENERS:
            score += 15
            findings.append({
                "risk_score": 15,
                "category": "url_shortener",
                "detail": f"URL shortener detected: {domain}",
                "educational": EDUCATIONAL_TIPS.get("url_shorteners", {
                    "title": "⚠️ URL Shortener",
                    "explanation": "Shortened URLs hide the real destination",
                    "tips": ["Use a URL expander service first", "Never click unknown shortened links"]
                })
            })
        
        # Determine risk level
        if score >= 56:
            risk_level = "HIGH"
        elif score >= 26:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "risk_score": score,
            "risk_level": risk_level,
            "findings": findings,
            "urls": [{"url": url, "risk_score": score}]
        }
        
    except Exception as e:
        logger.error(f"Error analyzing URL: {e}")
        return {
            "risk_score": 0,
            "risk_level": "LOW",
            "findings": [],
            "urls": [{"url": url, "risk_score": 0}]
        }


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="PhishForge Detector - Simple rule-based phishing detector."
    )
    parser.add_argument("--subject", type=str, help="Email subject")
    parser.add_argument("--sender", type=str, help="Sender (From: ...)")
    parser.add_argument(
        "--body-file",
        type=str,
        help="Path to file containing email body (plain text)",
    )

    args = parser.parse_args()

    if not (args.subject and args.sender and args.body_file):
        print("Usage: python 'PhishForge Detector.py' --subject \"...\" --sender \"...\" --body-file email.txt")
        sys.exit(1)

    with open(args.body_file, "r", encoding="utf-8", errors="ignore") as f:
        body = f.read()

    result = score_email(args.subject, args.sender, body)

    print("\n" + "="*70)
    print("🛡️  PHISHFORGE DETECTOR - Email Security Analysis")
    print("="*70)
    
    print(f"\n📧 SENDER: {result['sender_info']['email'] or args.sender}")
    if result['sender_info']['display_name']:
        print(f"   Display name: {result['sender_info']['display_name']}")
    print(f"📨 SUBJECT: {args.subject}")
    
    print("\n" + "-"*70)
    print(f"\n🎯 RESULT: {result['label']}")
    print(f"📊 Risk score: {result['score']}/100")
    print("\n" + "-"*70)
    
    if result["findings"]:
        print("\n⚠️  DANGER SIGNALS DETECTED:\n")
        
        for i, finding in enumerate(result["findings"], 1):
            print(f"\n{i}. {finding['educational']['title']}")
            print(f"   Risk: +{finding['risk_score']} points")
            print(f"   🔍 Found: {finding['detail']}")
            print(f"\n   💡 {finding['educational']['explanation']}")
            print("\n   📚 What to do:")
            for tip in finding['educational']['tips']:
                print(f"      • {tip}")
            print("\n   " + "-"*66)
    else:
        print("\n✅ No obvious danger signals detected.")
        print("   Remember: even seemingly safe emails can be dangerous.")
    
    if result["urls"]:
        print("\n🔗 URLS DETECTED IN EMAIL:")
        for url in result["urls"]:
            print(f"   • {url}")
        print("\n   ⚠️ WARNING: Don't click links in suspicious emails!")
    
    print("\n" + "="*70)
    print("\n💡 GENERAL SECURITY ADVICE:")
    
    if result["risk_level"] == "high":
        print("""
   ⛔ This email shows strong phishing signals:
   • DO NOT click any links
   • DO NOT provide personal information
   • Delete this email
   • If it concerns a service you use, contact them directly
         (search for the official contact on their website)
        """)
    elif result["risk_level"] == "medium":
        print("""
   ⚠️ This email has some suspicious elements:
   • Verify carefully before interacting
   • Contact the company directly if in doubt
   • Don't trust the email's appearance alone
   • Go manually to the official site without clicking links
        """)
    else:
        print("""
   ✅ The email shows no obvious signals, but stay vigilant:
   • Always verify the sender's identity
   • Don't blindly trust even seemingly legitimate emails
   • For unusual requests, verify through official channels
        """)
    
    print("="*70 + "\n")
    
    # Optional JSON output for integration with other tools
    if "--json" in sys.argv:
        print("\n\n=== JSON OUTPUT ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))