"""
Script to setup Kaggle credentials and download dataset.

Instructions:
1. Go to https://www.kaggle.com/settings
2. Scroll to "API" section
3. Click "Create New Token" - downloads kaggle.json
4. Run this script and paste the contents when prompted

Or manually place kaggle.json at ~/.kaggle/kaggle.json
"""

import os
import json
from pathlib import Path

def setup_kaggle_credentials():
    """Interactive setup for Kaggle credentials."""
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_file = kaggle_dir / "kaggle.json"
    
    if kaggle_file.exists():
        print("✅ Kaggle credentials already configured")
        return True
    
    print("="*60)
    print("Kaggle API Setup")
    print("="*60)
    print("\nKaggle credentials not found.")
    print("\nTo get your credentials:")
    print("1. Go to: https://www.kaggle.com/settings")
    print("2. Scroll to 'API' section")
    print("3. Click 'Create New Token'")
    print("4. This will download kaggle.json")
    print("\nOption 1: Paste kaggle.json content below")
    print("Option 2: Manually copy kaggle.json to ~/.kaggle/")
    print("-"*60)
    
    choice = input("\nEnter '1' to paste content, '2' to skip: ").strip()
    
    if choice == '1':
        print("\nPaste the content of kaggle.json (format: {\"username\":\"...\",\"key\":\"...\"}):")
        try:
            content = input().strip()
            data = json.loads(content)
            
            # Validate format
            if 'username' not in data or 'key' not in data:
                print("❌ Invalid format. Must contain 'username' and 'key'")
                return False
            
            # Create directory and save file
            kaggle_dir.mkdir(parents=True, exist_ok=True)
            with open(kaggle_file, 'w') as f:
                json.dump(data, f)
            
            # Set permissions (Kaggle requires 600)
            kaggle_file.chmod(0o600)
            
            print(f"✅ Credentials saved to: {kaggle_file}")
            return True
            
        except json.JSONDecodeError:
            print("❌ Invalid JSON format")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    else:
        print("\nPlease manually copy kaggle.json to ~/.kaggle/kaggle.json")
        return False

if __name__ == "__main__":
    setup_kaggle_credentials()
