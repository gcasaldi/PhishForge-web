#!/usr/bin/env python3
"""
Multi-Database Phishing Client
Integrates multiple phishing databases for maximum coverage:
- Phishing.Database (491k+ domains)
- discord-scam-links (Discord phishing)
- SteamNitroPhishingLinks (Steam/Nitro scams)
- scam-links (general scams)
- AntiScam scam-link
- Phishing Domain API
- phish.sinking.yachts (real-time API)
- anti-fish
"""

import requests
import os
import logging
from typing import Set, Dict, List
from datetime import datetime, timedelta
import json
import re

logger = logging.getLogger(__name__)

class MultiDatabaseClient:
    """Consolidates multiple phishing databases for comprehensive protection"""
    
    # Database sources
    DATABASES = {
        "phishing_database": {
            "url": "https://raw.githubusercontent.com/mitchellkrogza/Phishing.Database/master/phishing-domains-ACTIVE.txt",
            "timeout": 5,
            "type": "list"
        },
        "discord_scam_links": {
            "url": "https://raw.githubusercontent.com/nikolaischunk/discord-scam-links/main/src/links.json",
            "timeout": 5,
            "type": "json"
        },
        "steam_nitro_phishing": {
            "url": "https://raw.githubusercontent.com/SteamDatabase/SteamTracking/master/Random/SteamNitroPhishing.txt",
            "timeout": 5,
            "type": "list"
        },
        "antiscam_scamlink": {
            "url": "https://raw.githubusercontent.com/Dogino/Discord-Phishing-URLs/main/scam-urls.txt",
            "timeout": 5,
            "type": "list"
        },
        "scam_links_main": {
            "url": "https://raw.githubusercontent.com/DevSpen/scam-links/master/src/links.txt",
            "timeout": 5,
            "type": "list"
        },
        "phish_sinking_yachts": {
            "url": "https://phish.sinking.yachts/v2/all",
            "timeout": 5,
            "type": "json_array"
        }
    }
    
    def __init__(self, cache_dir: str | None = None):
        """
        Initialize multi-database client
        
        Args:
            cache_dir: Directory for caching database files
        """
        if cache_dir is None:
            cache_dir = os.path.join(os.path.dirname(__file__), "cache")
        
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        self.consolidated_cache_file = os.path.join(cache_dir, "consolidated_phishing_domains.txt")
        self.metadata_file = os.path.join(cache_dir, "database_metadata.json")
        
        self.phishing_domains: Set[str] = set()
        self.metadata: Dict = {}
        
        # Load cached data
        self._load_from_cache()
    
    def _load_from_cache(self) -> bool:
        """Load consolidated domains from cache"""
        try:
            if os.path.exists(self.consolidated_cache_file):
                with open(self.consolidated_cache_file, 'r', encoding='utf-8') as f:
                    self.phishing_domains = set(line.strip().lower() for line in f if line.strip())
                
                if os.path.exists(self.metadata_file):
                    with open(self.metadata_file, 'r') as f:
                        self.metadata = json.load(f)
                
                logger.info(f"✅ Loaded {len(self.phishing_domains)} phishing domains from cache")
                return True
        except Exception as e:
            logger.warning(f"Could not load cache: {e}")
        
        return False
    
    def _save_to_cache(self):
        """Save consolidated domains to cache"""
        try:
            # Save domains
            with open(self.consolidated_cache_file, 'w', encoding='utf-8') as f:
                for domain in sorted(self.phishing_domains):
                    f.write(f"{domain}\n")
            
            # Save metadata
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            
            logger.info(f"💾 Saved {len(self.phishing_domains)} domains to cache")
        except Exception as e:
            logger.error(f"Could not save cache: {e}")
    
    def _download_database(self, name: str, config: Dict) -> Set[str]:
        """Download and parse a single database"""
        domains = set()
        
        try:
            logger.info(f"📥 Downloading {name}...")
            response = requests.get(
                config["url"],
                timeout=config["timeout"],
                headers={"User-Agent": "PhishForge/1.0"}
            )
            response.raise_for_status()
            
            # Parse based on type
            if config["type"] == "list":
                # Plain text list of domains
                for line in response.text.split('\n'):
                    line = line.strip().lower()
                    if line and not line.startswith('#'):
                        # Extract domain (remove http://, https://, etc.)
                        domain = re.sub(r'^https?://', '', line)
                        domain = domain.split('/')[0]  # Remove path
                        domain = domain.split(':')[0]  # Remove port
                        if domain and '.' in domain:
                            domains.add(domain)
            
            elif config["type"] == "json":
                # Discord scam links format
                data = response.json()
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, str):
                            domain = re.sub(r'^https?://', '', item)
                            domain = domain.split('/')[0]
                            if domain and '.' in domain:
                                domains.add(domain.lower())
                        elif isinstance(item, dict):
                            url = item.get('url') or item.get('domain') or item.get('link')
                            if url:
                                domain = re.sub(r'^https?://', '', url)
                                domain = domain.split('/')[0]
                                if domain and '.' in domain:
                                    domains.add(domain.lower())
            
            elif config["type"] == "json_array":
                # phish.sinking.yachts format
                data = response.json()
                if isinstance(data, list):
                    for domain in data:
                        if isinstance(domain, str) and '.' in domain:
                            domains.add(domain.lower())
            
            logger.info(f"✅ {name}: {len(domains)} domains")
            return domains
        
        except requests.Timeout:
            logger.warning(f"⏱️ Timeout downloading {name}")
        except requests.RequestException as e:
            logger.warning(f"❌ Failed to download {name}: {e}")
        except Exception as e:
            logger.error(f"❌ Error parsing {name}: {e}")
        
        return domains
    
    def update_databases(self, force: bool = False) -> Dict:
        """
        Update all phishing databases
        
        Args:
            force: Force update even if cache is recent
        
        Returns:
            Dictionary with update statistics
        """
        # Check if update is needed
        if not force and self.metadata.get("last_update"):
            last_update = datetime.fromisoformat(self.metadata["last_update"])
            if datetime.now() - last_update < timedelta(hours=6):
                logger.info(f"⏭️ Cache is recent ({last_update}), skipping update")
                return {
                    "status": "skipped",
                    "reason": "cache_recent",
                    "total_domains": len(self.phishing_domains)
                }
        
        logger.info("🔄 Starting multi-database update...")
        
        all_domains = set()
        stats = {
            "databases": {},
            "total_before": len(self.phishing_domains),
            "total_after": 0,
            "new_domains": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Download all databases
        for name, config in self.DATABASES.items():
            domains = self._download_database(name, config)
            all_domains.update(domains)
            stats["databases"][name] = len(domains)
        
        # Update consolidated set
        stats["new_domains"] = len(all_domains - self.phishing_domains)
        self.phishing_domains.update(all_domains)
        stats["total_after"] = len(self.phishing_domains)
        
        # Save metadata
        self.metadata = {
            "last_update": stats["timestamp"],
            "total_domains": stats["total_after"],
            "database_stats": stats["databases"]
        }
        
        # Save to cache
        self._save_to_cache()
        
        logger.info(f"""
🎉 Update complete!
   Total domains: {stats['total_after']:,}
   New domains: {stats['new_domains']:,}
   Databases: {len(stats['databases'])}
""")
        
        return stats
    
    def is_phishing(self, domain: str) -> bool:
        """
        Check if domain is in phishing databases
        
        Args:
            domain: Domain to check (e.g., "example.com")
        
        Returns:
            True if domain is known phishing, False otherwise
        """
        if not domain:
            return False
        
        domain = domain.lower().strip()
        
        # Remove protocol if present
        domain = re.sub(r'^https?://', '', domain)
        domain = domain.split('/')[0]  # Remove path
        domain = domain.split(':')[0]  # Remove port
        
        # Check exact match
        if domain in self.phishing_domains:
            return True
        
        # Check subdomains (e.g., www.phishing.com -> phishing.com)
        parts = domain.split('.')
        if len(parts) > 2:
            parent_domain = '.'.join(parts[-2:])
            if parent_domain in self.phishing_domains:
                return True
        
        return False
    
    def check_url(self, url: str) -> Dict:
        """
        Check URL against all databases
        
        Args:
            url: Full URL to check
        
        Returns:
            Dictionary with check results
        """
        # Extract domain
        domain = re.sub(r'^https?://', '', url)
        domain = domain.split('/')[0]
        domain = domain.split(':')[0]
        domain = domain.lower()
        
        result = {
            "url": url,
            "domain": domain,
            "is_phishing": self.is_phishing(domain),
            "total_databases": len(self.phishing_domains),
            "checked_at": datetime.now().isoformat()
        }
        
        return result
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        return {
            "total_domains": len(self.phishing_domains),
            "last_update": self.metadata.get("last_update"),
            "databases": self.metadata.get("database_stats", {}),
            "cache_file": self.consolidated_cache_file
        }


# Singleton instance
_client_instance = None

def get_client() -> MultiDatabaseClient:
    """Get or create singleton client instance"""
    global _client_instance
    if _client_instance is None:
        _client_instance = MultiDatabaseClient()
    return _client_instance


def is_phishing(domain: str) -> bool:
    """
    Quick check if domain is phishing
    
    Args:
        domain: Domain to check
    
    Returns:
        True if phishing, False otherwise (never raises exceptions)
    """
    try:
        client = get_client()
        return client.is_phishing(domain)
    except Exception as e:
        logger.error(f"Error checking domain: {e}")
        return False  # Fail open - don't block on errors


if __name__ == "__main__":
    # Test the multi-database client
    logging.basicConfig(level=logging.INFO)
    
    client = MultiDatabaseClient()
    
    print("📊 Current stats:")
    stats = client.get_stats()
    print(f"   Total domains: {stats['total_domains']:,}")
    print(f"   Last update: {stats['last_update']}")
    
    print("\n🔄 Updating databases...")
    update_stats = client.update_databases(force=True)
    print(f"\n✅ Update complete!")
    print(f"   Total domains: {update_stats['total_after']:,}")
    print(f"   New domains: {update_stats['new_domains']:,}")
    
    print("\n🔍 Testing detection:")
    test_urls = [
        "https://posteitaliane-r1mbors0.it/refund",
        "https://paypa1-secure.com/login",
        "https://google.com",
        "https://discord-nitro-free.ru",
        "https://steam-free-nitro.com"
    ]
    
    for url in test_urls:
        result = client.check_url(url)
        status = "🚨 PHISHING" if result["is_phishing"] else "✅ Safe"
        print(f"   {status}: {result['domain']}")
