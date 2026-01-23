# 🛡️ PhishForge Detector - User Guide

**Educational phishing detector** - Analyzes emails and **explains why** they're dangerous.

## 📊 Risk Levels

- 🚨 **HIGH RISK** (30+): Likely phishing - DO NOT interact
- ⚠️ **MEDIUM RISK** (15-29): Suspicious - verify carefully  
- ✅ **LOW RISK** (0-14): No obvious signals, stay vigilant

## 🔍 What It Checks

1. **Sender** - Display name vs actual email
2. **URLs** - Shortened/suspicious links, HTTP
3. **Language** - Alarming words, urgency
4. **Credentials** - Login requests
5. **Domains** - Risky TLDs, punycode

## 🎓 Common Phishing Signals

- **Sender Mismatch**: "Microsoft Support" but email is @suspicious.xyz
- **Shortened URLs**: bit.ly links hide real destination
- **Alarming Language**: "URGENT!!! Account will be CLOSED!!!"

## 💡 Quick Tips

**DO**: Verify sender, go to sites manually, contact company directly, take time

**DON'T**: Click suspicious links, provide passwords via email, let yourself be rushed

## 🔧 Customization

Edit `PhishForge Detector.py`:
- `SUSPICIOUS_KEYWORDS` - Add phishing words
- `SUSPICIOUS_TLDS` - Add risky domains
- `trusted_domains` - Add your org domains

## 📱 JSON Output

```bash
./analyze.sh --body-file email.txt --json
```

## ⚠️ Important

**Educational tool only** - Does NOT replace antivirus, spam filters, or common sense. Always use caution.

## 📚 Learn More

- [US CISA - Phishing Guide](https://www.cisa.gov/phishing)
- Search "how to recognize phishing"

---

**Remember**: The best defense against phishing is knowledge! 🧠🛡️
