# 🛡️ PhishForge Lite — AI-Powered Phishing Detection

PhishForge Lite is a lightweight phishing detection engine that analyzes URLs and emails using a multi-layer approach combining heuristics, threat-intelligence rules, and a versioned Machine Learning model.

Its goal is simple: **provide fast, explainable, and reliable phishing detection for real-world scenarios**.

---

## ⚙️ Architecture Overview

### **Frontend**
- Hosted on GitHub Pages  
- Clean and simple UI for URL/email analysis  
- Direct communication with backend via Fetch API  

### **Backend**
- FastAPI running on Render  
- `/analyze` endpoint returning a combined phishing risk score  
- ML model loaded once at startup (cached in memory)

### **Machine Learning Engine**
- Model: `url_phishing_model.joblib`  
- Pipeline: `TfidfVectorizer` + `LogisticRegression`  
- Fully versioned  
- Deterministic loading  
- Designed for safe, controlled updates

The model does **not** retrain itself.  
It is intentionally static to ensure security, consistency, and explainability.

---

## 🚀 Key Features

- Real-time URL analysis  
- Email analysis (subject, sender, body)  
- Combined scoring (0–100)  
- Deterministic ML inference  
- Auto-deployment on Render after each push  
- Zero secrets in the frontend (safe)

---

## 📈 Example Scores

| Input | Score | Classification |
|-------|-------|----------------|
| `paypal-verify-account.xyz` | 66/100 | Phishing |
| `bit.ly/free-money` | 66/100 | Phishing |
| `www.google.com` | 27/100 | Legitimate |
| Suspicious email | 70–95/100 | Phishing |

---

## 🤖 ML Versioning & Update Process

The ML model is **versioned and static in production**.  
It does **not** train itself on live traffic and does **not** store or learn from user inputs.

This is intentional to avoid:
- data poisoning,
- unstable behaviour,
- and inconsistent scoring.

### Update Workflow

When you want to improve the model, the update is explicit and controlled:

1. **Update or extend the training data**  
   - e.g. add new phishing/legit URLs under `ml/data/`

2. **Train a new model locally**
   ```bash
   python ml/train_url_model.py
