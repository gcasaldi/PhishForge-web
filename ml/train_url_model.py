#!/usr/bin/env python3
"""
Machine Learning Training Script for URL Phishing Detection

This script trains a binary classification model to distinguish between
phishing and legitimate URLs using character-level n-grams.

Architecture:
- TfidfVectorizer with character n-grams (3-5)
- LogisticRegression classifier
- Full pipeline saved as joblib

Usage:
    python ml/train_url_model.py
"""

import os
import sys
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Determine base directory
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

# File paths
PHISHING_FILE = DATA_DIR / "phishing_urls.txt"
LEGIT_FILE = DATA_DIR / "legit_urls.txt"
MODEL_FILE = MODEL_DIR / "url_phishing_model.joblib"


def load_training_data():
    """
    Load training data from text files.
    
    Returns:
        tuple: (urls, labels) where labels are 1 for phishing, 0 for legit
    """
    urls = []
    labels = []
    
    # Load phishing URLs (label = 1)
    if not PHISHING_FILE.exists():
        print(f"ERROR: Phishing data file not found: {PHISHING_FILE}")
        sys.exit(1)
        
    with open(PHISHING_FILE, 'r', encoding='utf-8') as f:
        phishing_urls = [line.strip() for line in f if line.strip()]
        urls.extend(phishing_urls)
        labels.extend([1] * len(phishing_urls))
    
    print(f"Loaded {len(phishing_urls)} phishing URLs")
    
    # Load legitimate URLs (label = 0)
    if not LEGIT_FILE.exists():
        print(f"ERROR: Legitimate data file not found: {LEGIT_FILE}")
        sys.exit(1)
        
    with open(LEGIT_FILE, 'r', encoding='utf-8') as f:
        legit_urls = [line.strip() for line in f if line.strip()]
        urls.extend(legit_urls)
        labels.extend([0] * len(legit_urls))
    
    print(f"Loaded {len(legit_urls)} legitimate URLs")
    print(f"Total dataset size: {len(urls)} URLs")
    
    return urls, labels


def train_model(urls, labels):
    """
    Train the phishing detection model.
    
    Args:
        urls: List of URL strings
        labels: List of binary labels (1=phishing, 0=legit)
        
    Returns:
        Pipeline: Trained scikit-learn pipeline
    """
    # Split data into train/test sets
    X_train, X_test, y_train, y_test = train_test_split(
        urls, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print(f"\nTraining set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Create pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            analyzer='char',
            ngram_range=(3, 5),
            max_features=5000,
            lowercase=True
        )),
        ('classifier', LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight='balanced'
        ))
    ])
    
    print("\nTraining model...")
    pipeline.fit(X_train, y_train)
    
    # Evaluate on test set
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n{'='*60}")
    print(f"Model Training Complete")
    print(f"{'='*60}")
    print(f"Test Accuracy: {accuracy:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Legit', 'Phishing']))
    
    return pipeline


def save_model(pipeline):
    """
    Save trained pipeline to disk.
    
    Args:
        pipeline: Trained scikit-learn pipeline
    """
    # Ensure model directory exists
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save model
    joblib.dump(pipeline, MODEL_FILE)
    print(f"\n✅ Model saved to: {MODEL_FILE}")
    print(f"File size: {MODEL_FILE.stat().st_size / 1024:.1f} KB")


def main():
    """Main training workflow."""
    print("="*60)
    print("PhishForge ML - URL Phishing Detection Training")
    print("="*60)
    
    # Load data
    urls, labels = load_training_data()
    
    if len(urls) < 10:
        print("\n⚠️  WARNING: Dataset too small for meaningful training")
        print("Please add more training examples to ml/data/")
        sys.exit(1)
    
    # Train model
    pipeline = train_model(urls, labels)
    
    # Save model
    save_model(pipeline)
    
    print("\n✨ Training complete! Model ready for deployment.")
    print("\nTo use the model, import ml_model and call ml_score_url(url)")


if __name__ == "__main__":
    main()
