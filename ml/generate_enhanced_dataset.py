#!/usr/bin/env python3
"""
Enhanced Dataset Generator for Phishing Detection
Genera un dataset completo e bilanciato per il training del modello ML

Caratteristiche:
- Dataset esteso con migliaia di esempi
- Pattern realistici di phishing
- Bilanciamento tra classi
- Integrazione con database PhishTank
"""

import random
import string
from typing import List, Tuple
from pathlib import Path

# Domini legittimi comuni
LEGIT_DOMAINS = [
    # Tech giants
    "google.com", "facebook.com", "amazon.com", "microsoft.com", "apple.com",
    "twitter.com", "linkedin.com", "youtube.com", "instagram.com", "netflix.com",
    
    # Banche italiane
    "intesasanpaolo.com", "unicredit.it", "bancobpm.it", "mps.it", "ubi.com",
    "poste.it", "postepay.it", "intesasanpaolo.com",
    
    # Banche internazionali
    "paypal.com", "chase.com", "wellsfargo.com", "bankofamerica.com",
    "hsbc.com", "barclays.co.uk", "santander.com",
    
    # E-commerce
    "ebay.com", "alibaba.com", "walmart.com", "target.com", "bestbuy.com",
    "amazon.it", "amazon.co.uk", "amazon.de", "amazon.fr",
    
    # Servizi cloud e email
    "dropbox.com", "icloud.com", "outlook.com", "gmail.com", "yahoo.com",
    "onedrive.com", "drive.google.com", "mail.google.com",
    
    # Utility e servizi
    "adobe.com", "zoom.us", "slack.com", "github.com", "stackoverflow.com",
    "wikipedia.org", "reddit.com", "medium.com",
    
    # Governo e istituzioni
    "gov.it", "agenziaentrate.gov.it", "inps.it", "gov.uk", "irs.gov",
    
    # Telecomunicazioni
    "vodafone.it", "tim.it", "wind.it", "iliad.it", "fastweb.it"
]

# Pattern comuni di phishing
PHISHING_PATTERNS = [
    # Tipologie di attacco
    "verify", "secure", "update", "confirm", "validate", "authentication",
    "suspended", "locked", "expired", "urgent", "alert", "warning",
    "security", "payment", "billing", "account", "login", "signin",
    "recover", "restore", "reactivate", "unlock", "claim", "prize",
    
    # Azioni
    "click-here", "verify-now", "update-now", "confirm-identity",
    "reset-password", "confirm-payment", "validate-account",
    
    # Termini ingannevoli
    "support", "help", "service", "customer", "team", "official",
    "secure-login", "safe-payment", "protected", "verified"
]

# TLD sospetti
SUSPICIOUS_TLDS = [
    ".tk", ".ml", ".ga", ".cf", ".gq",  # Freenom domains
    ".xyz", ".top", ".club", ".online", ".site", ".win",
    ".info", ".biz", ".pw", ".cc", ".ws"
]

# TLD legittimi
LEGIT_TLDS = [
    ".com", ".org", ".net", ".edu", ".gov",
    ".it", ".uk", ".de", ".fr", ".es",
    ".io", ".co"
]

def generate_legit_urls(count: int = 5000) -> List[str]:
    """Genera URL legittimi realistici"""
    urls = []
    
    # URL diretti a domini legittimi
    for domain in LEGIT_DOMAINS:
        urls.append(f"https://{domain}")
        urls.append(f"https://www.{domain}")
        
        # Sottopagine comuni
        paths = [
            "/login", "/account", "/profile", "/settings", "/support",
            "/products", "/services", "/about", "/contact", "/help",
            "/search", "/dashboard", "/home", "/index"
        ]
        
        for path in random.sample(paths, min(3, len(paths))):
            urls.append(f"https://{domain}{path}")
            urls.append(f"https://www.{domain}{path}")
    
    # Sottodomini legittimi
    legit_subdomains = [
        "mail", "www", "login", "account", "secure", "support",
        "help", "app", "mobile", "api", "cloud", "drive"
    ]
    
    for _ in range(count // 4):
        domain = random.choice(LEGIT_DOMAINS)
        subdomain = random.choice(legit_subdomains)
        path = random.choice(["", "/login", "/account", "/dashboard"])
        urls.append(f"https://{subdomain}.{domain}{path}")
    
    # Rimuovi duplicati e limita
    urls = list(set(urls))
    return urls[:count]

def generate_phishing_urls(count: int = 5000) -> List[str]:
    """Genera URL di phishing realistici"""
    urls = []
    
    # Pattern 1: Typosquatting
    for domain in random.sample(LEGIT_DOMAINS, min(50, len(LEGIT_DOMAINS))):
        base = domain.split('.')[0]
        
        # Sostituzioni comuni
        typos = [
            base.replace('o', '0'),
            base.replace('i', 'l'),
            base.replace('l', '1'),
            base + random.choice(['1', '2', '3', '-secure', '-verify']),
            base.replace('e', '3'),
            base[::-1],  # Reverse
        ]
        
        for typo in typos:
            tld = random.choice(SUSPICIOUS_TLDS)
            urls.append(f"http://{typo}{tld}/login")
            urls.append(f"http://{typo}{tld}/verify")
    
    # Pattern 2: Sottodomini ingannevoli
    for domain in random.sample(LEGIT_DOMAINS, min(40, len(LEGIT_DOMAINS))):
        for pattern in random.sample(PHISHING_PATTERNS, 5):
            fake_domain = random.choice([
                "security.tk", "verify.ml", "support.xyz",
                "account.club", "login.online", "secure.site"
            ])
            # Dominio legittimo come sottodominio
            urls.append(f"http://{domain}.{fake_domain}/verify")
            urls.append(f"http://{pattern}-{domain}.{fake_domain}/login")
    
    # Pattern 3: Homograph attacks (IDN)
    homographs = {
        'a': ['а', 'ɑ'],  # Cyrillic a
        'e': ['е', 'ė'],  # Cyrillic e
        'o': ['о', 'ο'],  # Cyrillic o
        'p': ['р'],       # Cyrillic p
        'c': ['с'],       # Cyrillic c
    }
    
    for domain in random.sample(LEGIT_DOMAINS, min(30, len(LEGIT_DOMAINS))):
        base = domain.split('.')[0]
        # Sostituisci un carattere
        if len(base) > 3:
            for orig, replacements in homographs.items():
                if orig in base:
                    for repl in replacements:
                        fake = base.replace(orig, repl, 1)
                        urls.append(f"http://{fake}.com/login")
                        break
                    break
    
    # Pattern 4: URL con pattern di phishing
    for _ in range(count // 3):
        pattern = random.choice(PHISHING_PATTERNS)
        brand = random.choice(LEGIT_DOMAINS).split('.')[0]
        tld = random.choice(SUSPICIOUS_TLDS)
        
        variations = [
            f"http://{brand}-{pattern}{tld}",
            f"http://{pattern}-{brand}{tld}",
            f"http://{brand}{pattern}{tld}",
            f"http://secure-{brand}-{pattern}{tld}",
            f"http://{brand}.{pattern}{tld}",
        ]
        
        url = random.choice(variations)
        path = random.choice(["/login", "/verify", "/account", "/confirm", "/update"])
        urls.append(f"{url}{path}")
    
    # Pattern 5: IP addresses
    for _ in range(50):
        ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
        path = random.choice(["/login", "/verify", "/secure", "/account"])
        urls.append(f"http://{ip}{path}")
    
    # Pattern 6: URL con redirect e parametri sospetti
    for _ in range(100):
        legit = random.choice(LEGIT_DOMAINS)
        params = random.choice([
            "?redirect=", "?return=", "?next=", "?url=", "?goto="
        ])
        fake_site = f"{random.choice(PHISHING_PATTERNS)}{random.choice(SUSPICIOUS_TLDS)}"
        urls.append(f"http://{fake_site}/fake{params}http://{legit}")
    
    # Pattern 7: URL troppo lunghi con encoding
    for _ in range(100):
        brand = random.choice(LEGIT_DOMAINS).split('.')[0]
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=40))
        urls.append(f"http://{brand}-verify.tk/{random_str}/login")
    
    # Rimuovi duplicati e limita
    urls = list(set(urls))
    return urls[:count]

def save_dataset(output_dir: Path):
    """Genera e salva il dataset completo"""
    print("🔧 Generazione dataset esteso per PhishForge...")
    print("=" * 50)
    
    # Genera dataset
    print("\n📊 Generazione URL legittimi...")
    legit_urls = generate_legit_urls(5000)
    print(f"✓ Generati {len(legit_urls)} URL legittimi")
    
    print("\n🎣 Generazione URL di phishing...")
    phishing_urls = generate_phishing_urls(5000)
    print(f"✓ Generati {len(phishing_urls)} URL di phishing")
    
    # Crea directory se non esiste
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Salva file
    legit_file = output_dir / "legit_urls.txt"
    phishing_file = output_dir / "phishing_urls.txt"
    
    print(f"\n💾 Salvataggio dataset...")
    
    with open(legit_file, 'w') as f:
        f.write('\n'.join(legit_urls))
    print(f"✓ Salvati URL legittimi: {legit_file}")
    
    with open(phishing_file, 'w') as f:
        f.write('\n'.join(phishing_urls))
    print(f"✓ Salvati URL phishing: {phishing_file}")
    
    print(f"\n✅ Dataset generato con successo!")
    print(f"   - URL legittimi: {len(legit_urls)}")
    print(f"   - URL phishing: {len(phishing_urls)}")
    print(f"   - Totale: {len(legit_urls) + len(phishing_urls)}")
    print(f"\n🚀 Pronto per il training con: python ml/train_url_model.py")

if __name__ == "__main__":
    # Directory di output
    data_dir = Path(__file__).parent / "data"
    save_dataset(data_dir)
