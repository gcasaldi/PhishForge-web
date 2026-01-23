"""
Phishing.Database Integration Module

This module provides integration with the Phishing.Database project 
(https://github.com/mitchellkrogza/Phishing.Database) to check URLs 
and domains against a continuously updated list of known phishing sites.
"""

import urllib.request
import urllib.parse
import urllib.error
import os
import time
import re
from typing import Set, Optional
from pathlib import Path


class PhishingDatabaseClient:
    """
    Client for checking URLs/domains against the Phishing.Database.
    
    Features:
    - Downloads and caches known phishing domains locally
    - Automatic cache refresh after configurable interval
    - Graceful fallback if database is unreachable
    - Fast in-memory lookup with set-based matching
    """
    
    # Default configuration
    DEFAULT_DATABASE_URL = "https://raw.githubusercontent.com/mitchellkrogza/Phishing.Database/master/phishing-domains-ACTIVE.txt"
    DEFAULT_CACHE_DIR = Path(__file__).parent / "cache"
    DEFAULT_CACHE_FILENAME = "phishing_domains.txt"
    DEFAULT_CACHE_TTL = 43200  # 12 hours in seconds (12 * 60 * 60)
    
    def __init__(
        self, 
        database_url: Optional[str] = None,
        cache_dir: Optional[Path] = None,
        cache_ttl: int = DEFAULT_CACHE_TTL
    ):
        """
        Initialize the Phishing.Database client.
        
        Args:
            database_url: URL to download phishing domains list (default: Phishing.Database ACTIVE list)
            cache_dir: Directory to store cached domain list (default: ./cache)
            cache_ttl: Time-to-live for cache in seconds (default: 24 hours)
        """
        self.database_url = database_url or self.DEFAULT_DATABASE_URL
        self.cache_dir = cache_dir or self.DEFAULT_CACHE_DIR
        self.cache_ttl = cache_ttl
        self.cache_file = self.cache_dir / self.DEFAULT_CACHE_FILENAME
        
        # In-memory set for fast lookups
        self._phishing_domains: Set[str] = set()
        self._last_update: float = 0
        self._initialized = False
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid based on TTL."""
        if not self.cache_file.exists():
            return False
        
        cache_age = time.time() - self.cache_file.stat().st_mtime
        return cache_age < self.cache_ttl
    
    def _download_database(self) -> bool:
        """
        Download the phishing domains database from remote URL.
        
        Returns:
            True if download successful, False otherwise (graceful fallback)
        """
        try:
            print(f"[PhishingDB] Attempting database download (timeout: 5s)...")
            
            # Download with SHORT timeout to avoid blocking
            req = urllib.request.Request(
                self.database_url,
                headers={'User-Agent': 'PhishForge/1.0'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                content = response.read().decode('utf-8')
            
            # Save to cache file
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"[PhishingDB] ✓ Database updated ({len(content)} bytes)")
            return True
            
        except urllib.error.URLError as e:
            print(f"[PhishingDB] ✗ Network unavailable (using cached/offline mode)")
            return False
        except Exception as e:
            print(f"[PhishingDB] ✗ Download failed (using cached/offline mode)")
            return False
    
    def _load_from_cache(self) -> bool:
        """
        Load phishing domains from cache file into memory.
        
        Returns:
            True if load successful, False otherwise
        """
        try:
            if not self.cache_file.exists():
                print("[PhishingDB] No cache file found")
                return False
            
            print(f"[PhishingDB] Loading domains from cache: {self.cache_file}")
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                domains = {
                    line.strip().lower() 
                    for line in f 
                    if line.strip() and not line.startswith('#')
                }
            
            self._phishing_domains = domains
            self._last_update = time.time()
            print(f"[PhishingDB] Loaded {len(self._phishing_domains):,} phishing domains")
            return True
            
        except Exception as e:
            print(f"[PhishingDB] Failed to load cache: {e}")
            return False
    
    def initialize(self) -> bool:
        """
        Initialize the client by loading or downloading the database.
        Uses graceful fallback - ALWAYS allows system to continue working.
        NEVER blocks or raises exceptions.
        
        Returns:
            True always (system continues even if database unavailable)
        """
        try:
            if self._initialized and self._is_cache_valid():
                return True
            
            # Try to load from valid cache first (fastest)
            if self._is_cache_valid():
                if self._load_from_cache():
                    self._initialized = True
                    print("[PhishingDB] ✓ Using cached database")
                    return True
            
            # Cache invalid or missing, try quick download (5s timeout)
            try:
                if self._download_database():
                    if self._load_from_cache():
                        self._initialized = True
                        return True
            except Exception:
                pass  # Silent failure, continue to fallback
            
            # Download failed, try to load expired cache as fallback
            if self.cache_file.exists():
                print("[PhishingDB] ⚠ Using expired cache (offline mode)")
                if self._load_from_cache():
                    self._initialized = True
                    return True
            
            # No cache available at all
            print("[PhishingDB] ⚠ Running in offline mode (heuristics only)")
            self._initialized = True
            return True
            
        except Exception as e:
            # CRITICAL: Catch ALL exceptions to ensure system never fails
            print(f"[PhishingDB] ⚠ Initialization error (continuing anyway): {e}")
            self._initialized = True
            return True
    
    def extract_domain_from_url(self, url: str) -> Optional[str]:
        """
        Extract domain from a URL.
        
        Args:
            url: Full URL or domain string
            
        Returns:
            Extracted domain in lowercase, or None if invalid
        """
        try:
            # Add scheme if missing for proper parsing
            if not url.startswith(('http://', 'https://', '//')):
                url = 'http://' + url
            
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc or parsed.path.split('/')[0]
            
            # Remove port if present
            domain = domain.split(':')[0]
            
            # Remove www. prefix for better matching
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain.lower() if domain else None
            
        except Exception:
            return None
    
    def is_phishing_url(self, url: str) -> bool:
        """
        Check if a URL or domain is in the phishing database.
        NEVER fails or blocks - returns False on any error.
        
        Args:
            url: URL or domain to check
            
        Returns:
            True if found in database, False otherwise (graceful fallback)
        """
        try:
            # Ensure initialized (non-blocking with error handling)
            if not self._initialized:
                self.initialize()
            
            # If no domains loaded, return False (system still works with heuristics)
            if not self._phishing_domains:
                return False
            
            # Extract domain from URL
            domain = self.extract_domain_from_url(url)
            if not domain:
                return False
            
            # Check exact match
            if domain in self._phishing_domains:
                return True
            
            # Check parent domains (e.g., "evil.com" matches "sub.evil.com")
            parts = domain.split('.')
            for i in range(len(parts)):
                parent_domain = '.'.join(parts[i:])
                if parent_domain in self._phishing_domains:
                    return True
            
            return False
            
        except Exception as e:
            # CRITICAL: Never fail, always return False to allow system to continue
            print(f"[PhishingDB] ✗ Check failed (continuing): {e}")
            return False
    
    def check_multiple_urls(self, urls: list[str]) -> dict:
        """
        Check multiple URLs against the database.
        
        Args:
            urls: List of URLs to check
            
        Returns:
            Dict with 'found' (list of phishing URLs) and 'checked' (total count)
        """
        found_phishing = []
        
        for url in urls:
            if self.is_phishing_url(url):
                found_phishing.append(url)
        
        return {
            'found': found_phishing,
            'checked': len(urls),
            'phishing_count': len(found_phishing)
        }
    
    def get_stats(self) -> dict:
        """
        Get statistics about the loaded database.
        
        Returns:
            Dict with database statistics
        """
        return {
            'initialized': self._initialized,
            'domain_count': len(self._phishing_domains),
            'cache_file': str(self.cache_file),
            'cache_valid': self._is_cache_valid(),
            'last_update': self._last_update,
            'database_url': self.database_url
        }


# Global singleton instance
_client_instance: Optional[PhishingDatabaseClient] = None


def get_client() -> PhishingDatabaseClient:
    """
    Get the global PhishingDatabaseClient singleton instance.
    
    Returns:
        Initialized PhishingDatabaseClient instance
    """
    global _client_instance
    
    if _client_instance is None:
        _client_instance = PhishingDatabaseClient()
        _client_instance.initialize()
    
    return _client_instance


def is_url_in_phishing_database(url: str) -> bool:
    """
    Convenience function to check if a URL is in the phishing database.
    
    Args:
        url: URL or domain to check
        
    Returns:
        True if found in database, False otherwise
    """
    client = get_client()
    return client.is_phishing_url(url)
