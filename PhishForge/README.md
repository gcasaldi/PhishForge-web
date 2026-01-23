# 🛡️ PhishForge Detector

**An educational tool to detect phishing emails and learn how to recognize them.**

PhishForge analyzes emails for phishing signals and explains **why** each signal is dangerous, helping you learn to identify threats on your own.

---

## 🚀 Quick Start

### 📺 See Demo Examples
```bash
./demo.sh
```

### 🎯 Analyze Your Email (Interactive - PRODUCTION)
```bash
./interactive.sh
```
Paste your email directly or provide a file path - the tool guides you step-by-step.

### 🔍 Quick Analysis (Direct)
```bash
./analyze.sh --body-file your_email.txt
```

### 🧪 Run Tests
```bash
./test.sh
```

---

## 🎯 Features

- **🔍 Smart Detection**: Analyzes sender, URLs, language, and more
- **📚 Educational**: Explains each danger signal in detail
- **💡 Actionable Advice**: Tells you exactly what to do
- **🎓 Learn by Example**: Demo mode shows real analyses
- **⚡ Easy to Use**: Simple command-line interface

---

## 📊 What It Detects

| Signal | What It Checks |
|--------|----------------|
| 👤 **Sender Mismatch** | Display name vs actual email address |
| 🔗 **Suspicious URLs** | Shortened links, unsafe domains, HTTP |
| 📝 **Alarming Language** | Urgent words, excessive punctuation |
| 🔑 **Credential Requests** | Asking for login or sensitive info |
| 🌍 **Risky Domains** | Suspicious TLDs, punycode attacks |

---

## 💻 Usage Modes

### 1️⃣ Demo Mode - Learn by Example

See pre-analyzed emails:
```bash
./demo.sh
```

Shows:
- ✅ High-risk phishing example (62 points)
- ✅ Low-risk legitimate example (5 points)
- Educational explanations for every signal

Perfect for: Training, demonstrations, understanding how it works

---

### 2️⃣ Interactive Mode - Guided Analysis (PRODUCTION)

Step-by-step guided analysis:
```bash
./interactive.sh
```

The tool will ask you for:
- 📝 Email body (paste directly OR file path)
- 📧 Subject line
- 👤 Sender information
- 📊 Output format (human or JSON)

Then analyzes and shows results with educational explanations.

Perfect for: **Production use**, first-time users, training

---

### 2️⃣.1 Quick Mode - Direct Command-Line

For experienced users who want speed:

Quick analysis:
```bash
./analyze.sh --body-file email.txt
```

Full analysis:
```bash
./analyze.sh \
  --subject "Email Subject" \
  --sender "Name <email@domain.com>" \
  --body-file email.txt
```

JSON output:
```bash
./analyze.sh --body-file email.txt --json > result.json
```

Perfect for: Scripts, automation, experienced users

---

### 3️⃣ Test Mode - Verify Installation

Run automated tests:
```bash
./test.sh
```

Verifies:
- ✅ Detector correctly identifies high-risk emails
- ✅ Detector correctly identifies low-risk emails
- ✅ All components working properly

Perfect for: Installation verification, development, CI/CD

---

## 📖 Documentation

- **[USAGE.md](USAGE.md)** - Complete usage guide with examples
- **[README_USAGE.md](README_USAGE.md)** - Educational content and learning resources
- **[DEMO_OUTPUT.txt](DEMO_OUTPUT.txt)** - Example analysis output

---

## 🎓 Example Output

```
🛡️  PHISHFORGE DETECTOR - Email Security Analysis

📧 SENDER: hacker@paypal-verify.xyz
   Display name: PayPal Security

🎯 RESULT: 🚨 HIGH RISK - Likely Phishing
📊 Risk score: 62/100

⚠️  DANGER SIGNALS DETECTED:

1. 📚 Alarming Language
   Risk: +20 points
   🔍 Found: verify, urgent, immediately, suspended
   
   💡 Phishers use words that create urgency or fear...
   
   📚 What to do:
      • Real companies rarely use such urgent tones
      • Always take time to verify
      • No legitimate service will make you lose your account in hours
```

---

## 🔧 Customization

Edit `PhishForge Detector.py` to customize:

- **`SUSPICIOUS_KEYWORDS`**: Add words common in scams you see
- **`SUSPICIOUS_TLDS`**: Add risky domain extensions
- **`trusted_domains`**: Add your organization's domains
- **`EDUCATIONAL_TIPS`**: Add custom explanations

---

## ⚠️ Important Notes

PhishForge is an **educational tool**. It does NOT replace:
- Professional antivirus software
- Email provider spam filters
- Your judgment and common sense

**Always exercise caution** - even low-risk emails can be dangerous.

---

## 📚 Learn More About Phishing

- [US CISA - Phishing Guide](https://www.cisa.gov/news-events/news/avoiding-social-engineering-and-phishing-attacks)
- [Anti-Phishing Working Group](https://apwg.org/)
- Search "how to recognize phishing" for current guides

---

## 🤝 Contributing

Ideas for improvement:

1. Add new detection rules in `score_email()`
2. Expand keyword lists with terms you encounter
3. Add educational content in `EDUCATIONAL_TIPS`
4. Report issues or suggest features

---

## 📄 License

See [LICENSE](LICENSE) file for details.

---

## 🛡️ Stay Safe!

**Remember**: The best defense against phishing is knowledge. Use PhishForge to learn, practice, and protect yourself and others.

---

**Quick Reference**:
- `./demo.sh` - See examples (demo mode)
- `./interactive.sh` - **Guided analysis (PRODUCTION)**
- `./analyze.sh --body-file <file>` - Quick analysis
- `./test.sh` - Run tests
- `./analyze.sh --help` - Show help