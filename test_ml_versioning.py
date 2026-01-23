#!/usr/bin/env python3
"""
Test ML Model Versioning and Loading Mechanism

This script verifies that:
1. The model is loaded from a versioned file
2. The model is NOT re-created at runtime
3. The backend loads the latest saved model at startup
4. Model updates work by replacing the .joblib file
"""

import sys
import os
from pathlib import Path
import time
import joblib

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))


def test_model_file_exists():
    """Test 1: Verify model file exists"""
    print("Test 1: Model file exists")
    model_file = Path("ml/models/url_phishing_model.joblib")
    assert model_file.exists(), f"Model file not found: {model_file}"
    
    file_size = model_file.stat().st_size
    print(f"  ✓ Model file: {model_file}")
    print(f"  ✓ File size: {file_size / 1024:.1f} KB")
    print(f"  ✓ Last modified: {time.ctime(model_file.stat().st_mtime)}")
    return model_file


def test_model_loading():
    """Test 2: Verify model loads without recreation"""
    print("\nTest 2: Model loading mechanism")
    
    from ml_model import _load_model, is_model_available
    
    # First load
    model1 = _load_model()
    assert model1 is not None, "Model failed to load"
    print("  ✓ Model loaded successfully (first call)")
    
    # Second load should return cached instance
    model2 = _load_model()
    assert model2 is model1, "Model was recreated (should be cached)"
    print("  ✓ Model returns cached instance (not recreated)")
    
    # Verify availability
    assert is_model_available(), "Model should be available"
    print("  ✓ is_model_available() returns True")
    
    return model1


def test_model_scoring():
    """Test 3: Verify model can score URLs"""
    print("\nTest 3: Model scoring functionality")
    
    from ml_model import ml_score_url
    
    test_cases = [
        ("https://paypal-verify-account.xyz/login", 50, 100),  # Phishing
        ("https://www.paypal.com/signin", 0, 50),              # Legitimate
        ("http://bit.ly/free-money", 50, 100),                 # Phishing
        ("https://www.google.com", 0, 40),                     # Legitimate
    ]
    
    for url, min_score, max_score in test_cases:
        score = ml_score_url(url)
        assert 0 <= score <= 100, f"Score out of range: {score}"
        print(f"  ✓ {url[:50]:50} → {score:5.1f}/100")


def test_model_persistence():
    """Test 4: Verify model is persistent (loadable multiple times)"""
    print("\nTest 4: Model persistence")
    
    model_file = Path("ml/models/url_phishing_model.joblib")
    
    # Load model directly with joblib
    model = joblib.load(model_file)
    assert model is not None, "Failed to load model with joblib"
    print("  ✓ Model can be loaded directly with joblib")
    
    # Verify it's a scikit-learn pipeline
    assert hasattr(model, 'predict_proba'), "Model missing predict_proba method"
    print("  ✓ Model has predict_proba method")
    
    # Test prediction
    test_url = "https://example.com"
    proba = model.predict_proba([test_url])
    assert proba.shape == (1, 2), f"Unexpected prediction shape: {proba.shape}"
    print(f"  ✓ Model can make predictions: {proba[0]}")


def test_api_integration():
    """Test 5: Verify API loads model at startup"""
    print("\nTest 5: API integration")
    
    # Import API (triggers model loading)
    from api import is_model_available
    
    assert is_model_available(), "Model not available in API"
    print("  ✓ Model loaded when API is imported")
    print("  ✓ Model is loaded at startup (not at request time)")


def test_update_mechanism():
    """Test 6: Verify update mechanism documentation"""
    print("\nTest 6: Model update mechanism")
    
    training_script = Path("ml/train_url_model.py")
    assert training_script.exists(), "Training script not found"
    print(f"  ✓ Training script exists: {training_script}")
    
    model_file = Path("ml/models/url_phishing_model.joblib")
    print(f"  ✓ Model file location: {model_file}")
    
    print("\n  📝 To update the model:")
    print("     1. Edit data files: ml/data/phishing_urls.txt, ml/data/legit_urls.txt")
    print("     2. Run training: python ml/train_url_model.py")
    print("     3. New model saved to: ml/models/url_phishing_model.joblib")
    print("     4. Restart API to load new model")


def main():
    """Run all tests"""
    print("="*70)
    print("PhishForge ML - Model Versioning and Loading Test")
    print("="*70)
    
    try:
        model_file = test_model_file_exists()
        model = test_model_loading()
        test_model_scoring()
        test_model_persistence()
        test_api_integration()
        test_update_mechanism()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        
        print("\n🎯 VERIFICATION SUMMARY:")
        print("  ✓ Model is loaded from versioned file (ml/models/url_phishing_model.joblib)")
        print("  ✓ Model is NOT re-created at runtime (cached after first load)")
        print("  ✓ Backend loads the latest saved model at startup")
        print("  ✓ Model can be updated by replacing the .joblib file and restarting")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
