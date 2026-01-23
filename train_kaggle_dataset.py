#!/usr/bin/env python3
"""
Download and prepare Kaggle Phishing Email Dataset
Dataset: https://www.kaggle.com/datasets/naserabdullahalam/phishing-email-dataset

This script:
1. Downloads the dataset from Kaggle
2. Cleans and preprocesses the data
3. Trains a new ML model with real phishing emails
4. Saves the improved model
"""

import os
import sys
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import re

print("="*60)
print("PhishForge - Kaggle Dataset Training")
print("="*60)
print()

# Step 1: Install kagglehub if needed
print("📦 Installing dependencies...")
os.system("pip install -q kagglehub pandas scikit-learn joblib")
print("✅ Dependencies installed\n")

# Step 2: Download dataset using Kaggle API
print("📥 Downloading Kaggle dataset...")
print("   Dataset: naserabdullahalam/phishing-email-dataset")
print()

try:
    import kaggle
    
    # Download dataset
    dataset_name = "naserabdullahalam/phishing-email-dataset"
    download_path = "./kaggle_data"
    
    os.makedirs(download_path, exist_ok=True)
    
    kaggle.api.dataset_download_files(
        dataset_name,
        path=download_path,
        unzip=True
    )
    
    # Find CSV file
    csv_files = list(Path(download_path).glob("*.csv"))
    
    if not csv_files:
        raise FileNotFoundError("No CSV files found in downloaded dataset")
    
    csv_file = csv_files[0]
    print(f"✅ Dataset downloaded: {csv_file.name}")
    
    # Load CSV
    df = pd.read_csv(csv_file)
    
    print(f"✅ Dataset loaded successfully!")
    print(f"   Total records: {len(df):,}")
    print()
    
except Exception as e:
    print(f"❌ Error downloading dataset: {e}")
    print()
    print("🔧 Make sure you have Kaggle API configured:")
    print("   1. Go to https://www.kaggle.com/settings/account")
    print("   2. Create API token (downloads kaggle.json)")
    print("   3. Place in ~/.kaggle/kaggle.json")
    print("   4. chmod 600 ~/.kaggle/kaggle.json")
    sys.exit(1)

# Step 3: Inspect dataset
print("📊 Dataset structure:")
print(df.head())
print()
print("Columns:", df.columns.tolist())
print()
print("Data types:")
print(df.dtypes)
print()
print("Missing values:")
print(df.isnull().sum())
print()

# Step 4: Prepare data
print("🔧 Preparing data for training...")

# Identify text and label columns
# Common column names in phishing datasets
text_columns = ['email', 'Email Text', 'text', 'body', 'content', 'message']
label_columns = ['label', 'Email Type', 'type', 'class', 'is_phishing']

text_col = None
label_col = None

# Find text column
for col in text_columns:
    if col in df.columns:
        text_col = col
        break

# Find label column  
for col in label_columns:
    if col in df.columns:
        label_col = col
        break

if not text_col or not label_col:
    print(f"❌ Could not find text or label columns")
    print(f"   Available columns: {df.columns.tolist()}")
    print()
    print("Please specify manually:")
    text_col = input("Text column name: ").strip()
    label_col = input("Label column name: ").strip()

print(f"✅ Using columns:")
print(f"   Text: {text_col}")
print(f"   Label: {label_col}")
print()

# Extract text and labels
X = df[text_col].fillna('').astype(str)
y = df[label_col]

# Normalize labels (handle different formats)
# Convert to binary: 1 = phishing, 0 = legitimate
print("📋 Label distribution:")
print(y.value_counts())
print()

# Map common label formats to binary
label_mapping = {
    'Phishing Email': 1,
    'Safe Email': 0,
    'phishing': 1,
    'legitimate': 0,
    'spam': 1,
    'ham': 0,
    1: 1,
    0: 0,
    '1': 1,
    '0': 0
}

y_binary = y.map(label_mapping)

# If mapping failed, try to infer
if y_binary.isnull().any():
    print("⚠️ Some labels couldn't be mapped, inferring...")
    # Assume first unique value is phishing (usually listed first)
    unique_labels = y.unique()
    y_binary = (y == unique_labels[0]).astype(int)

print("✅ Binary label distribution:")
print(f"   Phishing (1): {(y_binary == 1).sum():,}")
print(f"   Legitimate (0): {(y_binary == 0).sum():,}")
print()

# Step 5: Train/test split
print("🔀 Splitting dataset (80/20)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y_binary, 
    test_size=0.2, 
    random_state=42,
    stratify=y_binary
)

print(f"✅ Training set: {len(X_train):,} emails")
print(f"✅ Test set: {len(X_test):,} emails")
print()

# Step 6: Vectorize with TF-IDF
print("🔤 Creating TF-IDF vectorizer...")
vectorizer = TfidfVectorizer(
    max_features=5000,  # Top 5000 words
    ngram_range=(1, 2),  # Unigrams and bigrams
    min_df=2,  # Ignore terms that appear in less than 2 documents
    max_df=0.95,  # Ignore terms that appear in more than 95% of documents
    strip_accents='unicode',
    lowercase=True,
    token_pattern=r'\b[a-zA-Z]{2,}\b'  # Only words with 2+ letters
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

print(f"✅ Vocabulary size: {len(vectorizer.vocabulary_):,} terms")
print()

# Step 7: Train Logistic Regression model
print("🤖 Training Logistic Regression model...")
model = LogisticRegression(
    max_iter=1000,
    C=1.0,
    class_weight='balanced',  # Handle class imbalance
    random_state=42,
    n_jobs=-1  # Use all CPU cores
)

model.fit(X_train_vec, y_train)
print("✅ Model trained!")
print()

# Step 8: Evaluate model
print("📊 Evaluating model...")
y_pred = model.predict(X_test_vec)
y_pred_proba = model.predict_proba(X_test_vec)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Accuracy: {accuracy*100:.2f}%")
print()

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print()

print("Classification Report:")
print(classification_report(y_test, y_pred, 
                          target_names=['Legitimate', 'Phishing']))
print()

# Step 9: Save model
print("💾 Saving model and vectorizer...")

# Create models directory
models_dir = Path(__file__).parent / "ml" / "models"
models_dir.mkdir(parents=True, exist_ok=True)

# Save vectorizer and model
vectorizer_path = models_dir / "email_vectorizer.joblib"
model_path = models_dir / "email_model.joblib"

joblib.dump(vectorizer, vectorizer_path)
joblib.dump(model, model_path)

print(f"✅ Vectorizer saved: {vectorizer_path}")
print(f"✅ Model saved: {model_path}")
print()

# Step 10: Test with example emails
print("🧪 Testing with example emails...")
print()

test_examples = [
    {
        "text": "Urgent! Your account will be closed. Click here to verify: http://paypal-verify.ru",
        "expected": "PHISHING"
    },
    {
        "text": "Hi, meeting tomorrow at 2pm in conference room B. See you there!",
        "expected": "LEGITIMATE"
    },
    {
        "text": "WINNER! You've won $1,000,000! Click here to claim your prize now!!!",
        "expected": "PHISHING"
    },
    {
        "text": "Your Amazon order #12345 has shipped. Track your package at amazon.com",
        "expected": "LEGITIMATE"
    }
]

for i, example in enumerate(test_examples, 1):
    text = example["text"]
    expected = example["expected"]
    
    # Predict
    text_vec = vectorizer.transform([text])
    proba = model.predict_proba(text_vec)[0][1]
    prediction = "PHISHING" if proba > 0.5 else "LEGITIMATE"
    
    # Display
    status = "✅" if prediction == expected else "❌"
    print(f"{status} Test {i}: {prediction} (confidence: {proba*100:.1f}%)")
    print(f"   Expected: {expected}")
    print(f"   Text: {text[:60]}...")
    print()

print("="*60)
print("✅ TRAINING COMPLETE!")
print("="*60)
print()
print("📋 Summary:")
print(f"   Dataset: {len(df):,} emails")
print(f"   Accuracy: {accuracy*100:.2f}%")
print(f"   Model: {model_path}")
print(f"   Vectorizer: {vectorizer_path}")
print()
print("🚀 The new model is ready to use!")
print("   Restart the API to load the improved model:")
print("   uvicorn api:app --reload")
print()
