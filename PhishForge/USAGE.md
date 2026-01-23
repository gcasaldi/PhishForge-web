# 🚀 How to Use PhishForge

## Quick Start

```bash
./demo.sh              # 📺 See examples
./interactive.sh       # 🎯 Guided analysis (PRODUCTION)
./analyze.sh --body-file email.txt  # 🔍 Quick analysis
./test.sh              # 🧪 Run tests
```

---

## 🎯 Interactive Mode - PRODUCTION

```bash
./interactive.sh
```

Guides you through:
1. Email body (paste text OR file path)
2. Subject line
3. Sender info  
4. Output format (human/JSON)
5. Auto-analyze

---

## 🔍 Quick Mode

```bash
# Minimal
./analyze.sh --body-file email.txt

# Full details
./analyze.sh --subject "..." --sender "..." --body-file email.txt

# JSON output
./analyze.sh --body-file email.txt --json

# Help
./analyze.sh --help
```

---

## 📺 Demo Mode

```bash
./demo.sh  # Shows pre-analyzed examples (HIGH/LOW risk)
```

## 🧪 Test Mode

```bash
./test.sh  # Runs automated tests, shows pass/fail
```

---

## 📋 Manual Analysis Steps

1. Save email body: `nano email.txt`
2. Run: `./analyze.sh --subject "..." --sender "..." --body-file email.txt`
3. Review: Risk score, signals, explanations

## 💻 Direct Python

```bash
python "PhishForge Detector.py" --subject "..." --sender "..." --body-file email.txt
```

---

## 💡 Tips

- Include complete email body
- Provide accurate sender (name + email)
- Use exact subject line
- Test with known phishing/legitimate emails first

See [README_USAGE.md](README_USAGE.md) for education, [DEMO_OUTPUT.txt](DEMO_OUTPUT.txt) for examples.
