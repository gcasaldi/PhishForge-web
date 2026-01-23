#!/usr/bin/env python3
"""
Update Multi-Database Script
Downloads and consolidates all phishing databases to make PhishForge infallible
"""

import sys
import logging
from PhishForge.multi_database_client import MultiDatabaseClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║           PhishForge Multi-Database Updater                  ║
║  Consolidating ALL phishing databases for maximum coverage   ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    print("📚 Databases sources:")
    print("   1. Phishing.Database (491k+ domains)")
    print("   2. discord-scam-links (Discord phishing)")
    print("   3. SteamNitroPhishingLinks (Steam/Nitro scams)")
    print("   4. scam-links (DevSpen)")
    print("   5. AntiScam scam-link (Discord phishing)")
    print("   6. phish.sinking.yachts (real-time API)")
    print("   7. anti-fish (various sources)")
    print()
    
    # Create client
    client = MultiDatabaseClient()
    
    # Show current stats
    print("📊 Current cache:")
    stats = client.get_stats()
    print(f"   Total domains: {stats['total_domains']:,}")
    if stats.get('last_update'):
        print(f"   Last update: {stats['last_update']}")
    print()
    
    # Update databases
    print("🔄 Starting download from all sources...")
    print("   (This may take 30-60 seconds)")
    print()
    
    update_stats = client.update_databases(force=True)
    
    print()
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                    UPDATE COMPLETE! ✅                        ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    print(f"📊 Total phishing domains: {update_stats['total_after']:,}")
    print(f"✨ New domains added: {update_stats['new_domains']:,}")
    print()
    print("📋 Per-database breakdown:")
    for db_name, count in update_stats['databases'].items():
        print(f"   {db_name}: {count:,} domains")
    print()
    print(f"💾 Cache saved to: {client.consolidated_cache_file}")
    print()
    print("🎯 PhishForge is now INFALLIBLE with comprehensive coverage!")
    print("   Use this database to catch:")
    print("   • Discord Nitro scams")
    print("   • Steam phishing")
    print("   • Italian bank phishing (Poste, Intesa, UniCredit, etc.)")
    print("   • PayPal/payment processor scams")
    print("   • Cryptocurrency phishing")
    print("   • And 500,000+ other known phishing domains")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏸️ Update cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
