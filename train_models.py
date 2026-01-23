#!/usr/bin/env python3
"""
PhishForge Continuous Model Training Script

This script trains/retrains all ML models used by PhishForge:
1. URL Phishing Detection Model
2. Email Phishing Detection Model

Can be run manually or scheduled via cron for periodic retraining.

Usage:
    python train_models.py [--url-only] [--email-only] [--force]

Options:
    --url-only      Train only URL model
    --email-only    Train only email model  
    --force         Force retrain even if models exist

Schedule with cron (weekly on Sunday at 2 AM):
    0 2 * * 0 cd /path/to/PhishForge-Lite && python train_models.py >> logs/training.log 2>&1
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
import subprocess

# Paths
BASE_DIR = Path(__file__).parent
ML_DIR = BASE_DIR / "ml"
MODELS_DIR = ML_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Model files
URL_MODEL_FILE = MODELS_DIR / "url_phishing_model.joblib"
EMAIL_PIPELINE_FILE = MODELS_DIR / "email_phishing_pipeline.joblib"

# Training scripts
URL_TRAIN_SCRIPT = ML_DIR / "train_url_model.py"
EMAIL_TRAIN_SCRIPT = ML_DIR / "train_email_model.py"


def print_header(title):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def check_model_exists(model_file):
    """Check if model file exists and get info"""
    if not model_file.exists():
        return False, "Not found"
    
    size_mb = model_file.stat().st_size / 1024 / 1024
    modified = datetime.fromtimestamp(model_file.stat().st_mtime)
    age_days = (datetime.now() - modified).days
    
    return True, f"{size_mb:.2f} MB, {age_days} days old"


def run_training_script(script_path, model_name):
    """Run a training script and capture output"""
    print(f"🚀 Starting {model_name} training...")
    print(f"   Script: {script_path}")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Run training script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {model_name} training completed successfully!")
            return True
        else:
            print(f"❌ {model_name} training failed (exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ {model_name} training timed out (>1 hour)")
        return False
    except Exception as e:
        print(f"❌ {model_name} training error: {e}")
        return False


def train_url_model(force=False):
    """Train URL phishing detection model"""
    print_header("URL Phishing Detection Model")
    
    # Check if model exists
    exists, info = check_model_exists(URL_MODEL_FILE)
    print(f"Current model status: {info}")
    
    if exists and not force:
        print("⏭️  Model exists. Use --force to retrain.\n")
        return True
    
    # Check if training script exists
    if not URL_TRAIN_SCRIPT.exists():
        print(f"❌ Training script not found: {URL_TRAIN_SCRIPT}\n")
        return False
    
    # Run training
    success = run_training_script(URL_TRAIN_SCRIPT, "URL Model")
    
    # Verify model was created
    if success:
        if URL_MODEL_FILE.exists():
            size_mb = URL_MODEL_FILE.stat().st_size / 1024 / 1024
            print(f"✅ Model saved: {URL_MODEL_FILE} ({size_mb:.2f} MB)")
        else:
            print(f"⚠️  Training succeeded but model file not found")
            success = False
    
    return success


def train_email_model(force=False):
    """Train Email phishing detection model"""
    print_header("Email Phishing Detection Model")
    
    # Check if model exists
    exists, info = check_model_exists(EMAIL_PIPELINE_FILE)
    print(f"Current model status: {info}")
    
    if exists and not force:
        print("⏭️  Model exists. Use --force to retrain.\n")
        return True
    
    # Check if training script exists
    if not EMAIL_TRAIN_SCRIPT.exists():
        print(f"❌ Training script not found: {EMAIL_TRAIN_SCRIPT}\n")
        return False
    
    # Check Kaggle credentials
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if not kaggle_json.exists():
        print("⚠️  Kaggle credentials not found!")
        print("   Email model training requires Kaggle API access.")
        print("   Setup: https://www.kaggle.com/docs/api")
        print("   Skipping email model training.\n")
        return False
    
    # Run training
    success = run_training_script(EMAIL_TRAIN_SCRIPT, "Email Model")
    
    # Verify model was created
    if success:
        if EMAIL_PIPELINE_FILE.exists():
            size_mb = EMAIL_PIPELINE_FILE.stat().st_size / 1024 / 1024
            print(f"✅ Model saved: {EMAIL_PIPELINE_FILE} ({size_mb:.2f} MB)")
        else:
            print(f"⚠️  Training succeeded but model file not found")
            success = False
    
    return success


def main():
    """Main training orchestration"""
    parser = argparse.ArgumentParser(
        description="PhishForge Continuous Model Training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python train_models.py                  # Train all models (skip existing)
  python train_models.py --force          # Force retrain all models
  python train_models.py --url-only       # Train only URL model
  python train_models.py --email-only --force  # Force retrain email model
        """
    )
    parser.add_argument('--url-only', action='store_true', help='Train only URL model')
    parser.add_argument('--email-only', action='store_true', help='Train only email model')
    parser.add_argument('--force', action='store_true', help='Force retrain even if models exist')
    
    args = parser.parse_args()
    
    # Ensure directories exist
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Print banner
    print(f"\n{'='*70}")
    print(f"  PhishForge Model Training Pipeline")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    results = {}
    
    # Train models
    if not args.email_only:
        results['url'] = train_url_model(force=args.force)
    
    if not args.url_only:
        results['email'] = train_email_model(force=args.force)
    
    # Print summary
    print_header("Training Summary")
    
    if 'url' in results:
        status = "✅ SUCCESS" if results['url'] else "❌ FAILED"
        print(f"URL Model:   {status}")
    
    if 'email' in results:
        status = "✅ SUCCESS" if results['email'] else "❌ FAILED"
        print(f"Email Model: {status}")
    
    # Overall success
    all_success = all(results.values())
    
    print(f"\n{'='*70}")
    if all_success:
        print("✅ All models trained successfully!")
    else:
        print("⚠️  Some models failed to train (see above)")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    return 0 if all_success else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
