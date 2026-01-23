#!/usr/bin/env python3
"""
PhishForge Database Updater

This script forces an update of ALL phishing databases used by PhishForge:
- Multi-Database (533k+ domains from 7 sources)
- Phishing.Database (legacy, 491k domains)

Can be run manually or scheduled via cron/systemd timer.

Usage:
    python update_databases.py

Schedule with cron (every 6 hours):
    0 */6 * * * cd /path/to/PhishForge-Lite && python update_databases.py >> logs/db_update.log 2>&1
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add PhishForge directory to path
sys.path.insert(0, str(Path(__file__).parent / "PhishForge"))

def update_multi_database():
    """Update Multi-Database (533k+ domains from 7 sources)"""
    print(f"\n{'='*60}")
    print(f"[{datetime.now().isoformat()}] Multi-Database Update")
    print(f"{'='*60}\n")
    
    try:
        from multi_database_client import MultiDatabaseClient
        
        print("📥 Updating Multi-Database (7 sources)...")
        print("   Sources:")
        print("   1. Phishing.Database (491k+ domains)")
        print("   2. Discord scam-links")
        print("   3. Steam/Nitro phishing")
        print("   4. scam-links (DevSpen)")
        print("   5. AntiScam")
        print("   6. phish.sinking.yachts (real-time)")
        print("   7. anti-fish")
        print()
        
        client = MultiDatabaseClient()
        
        # Force update
        stats = client.update_databases(force=True)
        
        if stats.get('status') != 'error':
            print(f"✅ Multi-Database updated successfully!")
            print(f"   Total domains: {stats['total_after']:,}")
            print(f"   New domains: {stats['new_domains']:,}")
            print(f"   Cache location: {client.consolidated_cache_file}")
            print()
            print("   Per-database breakdown:")
            for db_name, count in stats.get('databases', {}).items():
                print(f"     • {db_name}: {count:,} domains")
            return True
        else:
            print("❌ Failed to update Multi-Database")
            return False
            
    except Exception as e:
        print(f"❌ Error updating Multi-Database: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_ml_models():
    """Check if ML models exist and report status"""
    print(f"\n{'='*60}")
    print("🤖 ML Models Status")
    print(f"{'='*60}\n")
    
    models_dir = Path(__file__).parent
    
    # URL ML Model
    url_model = models_dir / "url_phishing_model.pkl"
    if url_model.exists():
        size_mb = url_model.stat().st_size / 1024 / 1024
        print(f"✅ URL ML Model: {url_model.name} ({size_mb:.2f} MB)")
    else:
        print(f"⚠️  URL ML Model: NOT FOUND")
        print(f"   Run: python train_url_model.py")
    
    # Email ML Model
    email_model = models_dir / "email_phishing_model.pkl"
    if email_model.exists():
        size_mb = email_model.stat().st_size / 1024 / 1024
        print(f"✅ Email ML Model: {email_model.name} ({size_mb:.2f} MB)")
    else:
        print(f"⚠️  Email ML Model: NOT FOUND")
        print(f"   Run: python train_email_model.py")

def main():
    """Main update routine"""
    success = True
    
    # Update multi-database (PRIORITY - includes Phishing.Database + 6 others)
    if not update_multi_database():
        success = False
    
    # Check ML models status
    check_ml_models()
    
    # Summary
    print(f"\n{'='*60}")
    if success:
        print("✅ Database update completed successfully!")
        print()
        print("🎯 PhishForge now has:")
        print("   • 533,000+ known phishing domains")
        print("   • 7 consolidated database sources")
        print("   • Real-time phishing feeds")
        print("   • Discord/Steam/Gaming scam protection")
        print("   • Italian + International coverage")
    else:
        print("⚠️  Database update completed with errors (see above)")
    print(f"{'='*60}\n")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
