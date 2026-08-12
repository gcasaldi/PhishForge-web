# PhishForge 🎣

PhishForge is an AI-powered phishing detection system built to analyze suspicious emails and URLs in a practical, explainable, and privacy-conscious way. It combines classic rule-based detection, machine learning models, and live phishing feed checks to produce a final risk score that is useful both for automated filtering and for human review.

The project was designed to be useful in real-world scenarios: a user can paste an email, inspect a message, or check a URL and get a fast risk assessment without losing transparency. Every result explains what triggered the score, which is important because phishing detection is not only about a binary answer but also about understanding why something looks dangerous.

## What this project does

PhishForge evaluates:
- sender identity and email metadata
- subject and body language
- urgency and manipulation patterns
- suspicious links and malicious domains
- known phishing database hits
- ML-based risk estimation
- attachment-related risk indicators

The system produces a score from 0 to 100, along with a risk label, findings, and recommended action.

## Why it was built this way

Phishing is constantly evolving. Attackers do not rely on a single pattern. They combine urgency, fake brand impersonation, short links, social engineering, and brand spoofing. That means a detector that only checks one rule is not enough.

This project combines multiple layers:
- heuristic signal detection for language and patterns
- URL/domain analysis and normalization
- fuzzy brand checks to catch lookalike domains
- known phishing list matching from public feeds
- ML classification as an additional signal

This layered approach is more resilient than relying on a single model or a single blacklist.

## Architecture

The system is structured into a few clear parts:

- Frontend: static web interface for email and URL analysis
- Backend API: FastAPI service to process requests and return scores
- Detection engine: heuristic + URL risk logic
- ML layer: trained models for phishing classification
- Threat feeds: public phishing databases refreshed periodically
- Cache layer: local storage for metadata and consolidated domains

In practical terms, the app works like this:
1. The user submits an email or URL.
2. The backend extracts the relevant signals.
3. Rule-based checks look for suspicious patterns and known malicious domains.
4. The ML model gives an extra probability score.
5. Threat feed checks add a strong signal when a domain is known to be malicious.
6. The final risk score is built and returned to the frontend.

## Risk scoring model

The score is not just a simple yes/no flag. It is a weighted combination of multiple signals, including:
- suspicious phrasing like "verify your account" or "limited time only"
- URL shorteners and odd TLDs
- impersonation of known brands
- unusual sender domains
- malicious keyword stacking in URLs
- database hits from phishing feeds
- machine learning confidence score

The result is then mapped into a risk label such as SAFE, LOW, MEDIUM, HIGH, or CRITICAL depending on the final value.

## Threat feeds and phishing database coverage

PhishForge is designed to stay current by checking multiple public phishing sources instead of relying on a single database. In addition to local heuristics, the project uses known public threat feeds for URL/domain validation.

This matters because attackers move quickly. If a domain appears in an active phishing feed, that is a strong signal and should significantly increase the risk score. The system treats database hits as high-confidence evidence, but it still keeps heuristics in the loop so the detector is not overly dependent on one list.

## AI model update policy

This project is designed to evolve with the threat landscape. The default policy is:

- retrain the model every 15 days
- refresh the public phishing feeds more frequently when possible
- run a full retraining cycle whenever the data source changes significantly or false positives increase

If no active retraining pipeline is configured, the recommended minimum is a scheduled refresh every 15 days. That keeps the model from drifting too far from the latest phishing patterns while still keeping the workflow manageable in production.

A practical cadence is:
- every 15 days: model retraining + validation
- after major feed updates: quick evaluation pass
- when the false positive rate increases: immediate review and retraining

This is the recommended default for a project like this because phishing patterns shift faster than most traditional models. Waiting too long means the model becomes stale, while retraining too often without new data wastes effort and adds little value.

## Training workflow

The model can be retrained with the repository scripts, which are intended to keep the learning pipeline controlled and reproducible.

Typical workflow:

```bash
python train_models.py
```

To refresh the phishing feeds and local cached data:

```bash
python update_databases.py
```

or the multi-feed variant:

```bash
python update_multi_databases.py
```

This helps keep the system aligned with recent phishing campaigns while preserving the full detection pipeline.

## Local setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the local API

```bash
bash start_local_api.sh
```

or directly:

```bash
python local_api.py
```

### 3. Open the app

```text
http://127.0.0.1:8000
```

## Usage

### Email analysis

1. Open the Email tab.
2. Enter the sender, subject, and message body.
3. Click Analyze.
4. Review the score, findings, and recommendations.

### URL analysis

1. Open the URL tab.
2. Paste the link to inspect.
3. Click Analyze.
4. Check whether the URL is safe or suspicious and why.

## Main files

- `local_api.py` — local FastAPI application
- `index.html` — main frontend interface
- `script.js` — client-side logic and API calls
- `style.css` — application styling
- `email_predictor.py` — email analysis logic
- `ml/` — training data and model artifacts
- `PhishForge/` — phishing detection engine, feed client, and database helpers
- `update_databases.py` — database refresh script
- `train_models.py` — model training entry point

## Technology stack

- Python
- FastAPI
- Scikit-learn
- JavaScript / HTML / CSS
- public phishing feeds and cached domain lists

## Security and privacy

PhishForge is designed to be local-first and transparent. The analysis is done in the application environment, and the project is structured to keep the workflow understandable and inspectable.

Key principles:
- no hidden black-box decisioning
- explainable suspicious indicators
- local analysis where possible
- clear detection logic instead of opaque single-score behavior

## License

This project is released under the MIT License.

## Contribution

Contributions are welcome. If you want to improve detection quality, add better threat feeds, improve the model, or reduce false positives, please open an issue or submit a pull request.

---

PhishForge is meant to be practical: useful in the real world, transparent in its decisions, and flexible enough to evolve as phishing tactics change. The important part is not only the model itself, but the fact that it is built around a repeatable update rhythm so it stays relevant over time.


