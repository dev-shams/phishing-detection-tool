# Phishing Email Detection Tool

Final Year Project, BSc (Hons) Cyber Security
School of Computer Science and Informatics
De Montfort University, Dubai — Academic Year 2025/26

A machine-learning based web tool that classifies a submitted email as
either *phishing* or *legitimate*, reports a calibrated confidence score
and surfaces the human-interpretable indicators that drove the decision.

---

## Overview

The system combines 5,000 TF-IDF text features (1–2 word n-grams over the
email body) with 20 handcrafted phishing indicators drawn from the cyber
security literature (URL signals, header anomalies, content cues,
structural metrics). The 5,020-dimensional feature vector is fed to a
Logistic Regression classifier wrapped in `CalibratedClassifierCV`
(sigmoid calibration, 5-fold cross-validation) and trained on a balanced
corpus of 25,116 emails assembled from the MeAJOR Corpus and a publicly
available Kaggle phishing-vs-legitimate dataset.

The Phase 3 deployment adds two production-oriented behaviours:

- a **sender-reputation allowlist override** that downgrades the verdict
  to *legitimate* when the From-domain belongs to a known transactional
  sender and no high-signal handcrafted indicator fires; and
- a **hard-signal escalation rule** (the inverse) that upgrades the
  verdict to *phishing* when a non-allowlisted sender triggers one of
  the high-signal indicators (lookalike domain, IP-literal host, URL
  shortener, suspicious TLD, brand-subdomain spoofing).

Free webmail providers are deliberately excluded from the allowlist
because Business Email Compromise attacks are commonly delivered from
free webmail addresses impersonating executives.

---

## Repository layout

```
Final year Project/
|
|-- Phase1_development/        Foundational parser, 24-feature extractor and
|                              Random Forest baseline (synthetic data).
|
|-- Phase2_development/
|   |-- 1_data_combined/       Source datasets used for training.
|   |-- 2_training/            Production retraining and evaluation scripts.
|   |-- 3_testing/             Quick test suite exercising the deployed model.
|   |-- feature_extractor.py
|   |-- feature_extractor_enhanced.py
|   |-- ml_model.py
|   `-- README.md
|
|-- Phase3_development/        Deployed web application.
|   |-- app.py                 Flask routes, request handling, JSON API.
|   |-- config.py              Production settings (paths, threshold, logging).
|   |-- wsgi.py                WSGI entry point used by Gunicorn.
|   |-- models/
|   |   |-- detector.py        PhishingDetector class (load + predict).
|   |   |-- *.joblib           Trained model artefacts.
|   |   `-- config.json        Model metadata.
|   |-- static/                CSS and JavaScript for the web UI.
|   |-- templates/             Jinja2 templates (index, analyzer, errors).
|   `-- requirements.txt
|
|-- Procfile                   Railway / Heroku-style web entry point.
|-- requirements.txt           Top-level dependency list (Railway uses this).
|-- runtime.txt                Pinned Python version (3.10.13).
|-- mise.toml                  Build-tool settings for the Railway image.
`-- README.md                  This file.
```

---

## Running the application locally

The project was developed and tested on macOS with Python 3.10. The
commands below assume that pattern; Linux is equivalent.

```bash
# 1. Create and activate a virtual environment (first time only)
python3 -m venv phishing_env
source phishing_env/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the Flask development server
cd Phase3_development
python3 app.py
```

The application listens on `http://127.0.0.1:5001` and exposes the
following routes:

| Route               | Purpose                                                |
|---------------------|--------------------------------------------------------|
| `GET /`             | Landing page with project overview and statistics      |
| `GET /analyzer`     | Submission form (paste text or upload `.eml/.txt/.msg`)|
| `POST /api/analyze` | JSON-returning REST endpoint for integration           |
| `GET /api/status`   | Returns the detector readiness state                   |

For production deployment the entry point is `gunicorn wsgi:app`.

---

## Retraining the model

Retraining is fully reproducible from the bundled datasets:

```bash
cd Phase2_development/2_training
python3 retrain_phase3_model.py
```

The script performs an 80/20 stratified split, fits a 5,000-feature
TF-IDF vectoriser on the training portion, extracts the 20 handcrafted
indicators, runs a 5-fold cross-validation comparison across five
classifiers (Multinomial Naive Bayes, Decision Tree, Linear SVM, Random
Forest, Logistic Regression), trains the chosen calibrated Logistic
Regression model and writes the four joblib artefacts plus an updated
`config.json` to `Phase3_development/models/`.

To re-evaluate the saved model on the held-out test set:

```bash
python3 evaluate_phase3_model.py
```

This prints aggregate metrics and writes `confusion_matrix.png` and
`roc_pr_curves.png` to the same directory.

To run the end-to-end test suite against the deployed `PhishingDetector`:

```bash
cd ../3_testing
python3 quick_test_suite.py
```

---

## Reported performance

On a stratified 5,024-email held-out test set drawn from the same
combined corpus, the production model achieves:

| Metric    | Value   |
|-----------|---------|
| Accuracy  | 98.77 % |
| Precision | 98.57 % |
| Recall    | 98.96 % |
| F1-score  | 98.77 % |
| ROC-AUC   | 99.77 % |

Mean inference latency is approximately 2–3 milliseconds per email on a
laptop-class CPU. The decision threshold is set to 0.35 to capture
business-email-compromise and brand-impersonation messages whose
calibrated probability falls in the 0.35–0.50 borderline zone; the
allowlist override and hard-signal escalation rule in `detector.py`
handle the false-positive trade-off this lowered threshold would
otherwise introduce.

---

## Limitations

- The headline metrics above are an in-domain estimate. Real-world
  accuracy will differ; temporal cross-validation is identified as
  future work in the project report.
- Attachment-based malware delivery (e.g. a ZIP or PDF payload with
  no URLs in the body) is out of scope for a content-only classifier
  and is documented as a known gap.
- The TF-IDF block is English-dominant; non-English emails may degrade
  in accuracy and will tend to fall through the out-of-distribution
  safety path in `detector.py`.

---

## Privacy

All analysis is performed in memory. Submitted email text is never
written to durable storage and uploaded files are deleted after parsing.
Logs do not contain message bodies.

---

## Deployment

The project deploys to Railway via the bundled `Procfile`. The build
pipeline:

1. Installs the Python version pinned in `runtime.txt`
   (`python-3.10.13`) using `mise`. The `mise.toml` file disables
   GitHub artifact attestation verification, which is required because
   no attestations are published for that specific patch release.
2. Runs `pip install -r requirements.txt` at the repository root.
3. Boots the production server with
   `gunicorn app:app --workers 2 --threads 2 --worker-class gthread`
   from inside `Phase3_development/`.

---

## Repository

Source code: `https://github.com/dev-shams/phishing-detection-tool`
