#!/bin/bash

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "🚀 Starting PhishForge ML training..."
cd "$PROJECT_ROOT"
python ml/train_url_model.py

if [ $? -ne 0 ]; then
  echo "❌ Training failed. Aborting."
  exit 1
fi

echo "📦 Adding updated model to Git..."
git add ml/models/url_phishing_model.joblib

echo "📝 Committing changes..."
git commit -m "Train: Updated phishing model with new data"

echo "⬆️ Pushing to main branch..."
git push origin main

echo "🔥 Done! Render will now detect the push and redeploy automatically."
