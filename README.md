# Phishing Email Detection Tool

A web application that classifies email messages as **phishing** or **legitimate** using a calibrated Logistic Regression model trained on 25,116 emails. Built as a Final Year Project for the BSc (Hons) Cyber Security programme at De Montfort University Dubai.

A live deployment is available at:
**https://phishing-detection-tool-production.up.railway.app**

If you would rather run it on your own computer, the rest of this README walks you through the setup from scratch.

---

## What you need before you start

You need three things installed on your machine. If you already have them, jump straight to **Setup**.

1. **Python 3.10 or newer**
   Check by opening a terminal and running:
   ```bash
   python3 --version
   ```
   If the command is not found or the version is older than 3.10, download an installer from https://www.python.org/downloads/.

2. **Git**
   Check by running:
   ```bash
   git --version
   ```
   If it is missing, download it from https://git-scm.com/downloads.

3. **Visual Studio Code** (recommended editor, but any will do)
   Download from https://code.visualstudio.com/. After installing, also install the **Python extension** from the Extensions side panel — it gives you the run button, integrated terminal and auto-formatting.

---

## Setup (one-time, takes about five minutes)

### Step 1 — clone the repository

Open a terminal in the folder where you keep your projects and run:

```bash
git clone https://github.com/dev-shams/phishing-detection-tool.git
cd phishing-detection-tool
```

### Step 2 — open the project in VS Code

From the same terminal:

```bash
code .
```

(or open VS Code first, then **File → Open Folder…** and select the freshly-cloned folder).

### Step 3 — open the integrated terminal in VS Code

Use the menu **Terminal → New Terminal** (shortcut: `Ctrl + ~` on Windows/Linux, `Cmd + ~` on macOS). All subsequent commands should be run in this terminal.

### Step 4 — create a Python virtual environment

A virtual environment keeps this project's dependencies isolated from the rest of your system:

```bash
python3 -m venv phishing_env
```

Activate it:

| OS              | Command                                     |
|-----------------|---------------------------------------------|
| macOS / Linux   | `source phishing_env/bin/activate`          |
| Windows (cmd)   | `phishing_env\Scripts\activate.bat`         |
| Windows (PS)    | `phishing_env\Scripts\Activate.ps1`         |

You should see `(phishing_env)` appear at the start of your terminal prompt.

### Step 5 — install all dependencies

```bash
pip install -r requirements.txt
```

This installs Flask, scikit-learn, joblib, pandas, NumPy, gunicorn and a few smaller libraries. It takes about a minute on a normal internet connection.

If pip says "command not found", try `python3 -m pip install -r requirements.txt` instead.

---

## Running the application

With the virtual environment still activated:

```bash
cd Phase3_development
python app.py
OR
python3 app.py
```

The first time the app boots it loads the trained model into memory. You should see output ending with:

```
* Running on http://127.0.0.1:5001
* Running on http://192.168.x.x:5001
Press CTRL+C to quit
```

Open your browser and visit **http://127.0.0.1:5001/**.

### Using the web interface

1. Click **Analyzer** in the navigation bar (or visit `/analyzer` directly).
2. Either paste a raw email into the text area, or upload an email file (`.eml`, `.txt` or `.msg`).
3. Click **Analyze Email**.
4. The result page shows the verdict (`PHISHING` or `LEGITIMATE`), a calibrated confidence score, and a list of any threat indicators that fired.

To stop the server, press `Ctrl + C` in the terminal.

---

## Project structure

```
phishing-detection-tool/
|
|-- Phase1_development/        Initial baseline (parser + 24-feature extractor + RF)
|
|-- Phase2_development/
|   |-- 1_data_combined/       Training datasets (CSV)
|   |-- 2_training/            retrain_phase3_model.py, evaluate_phase3_model.py
|   |-- 3_testing/             quick_test_suite.py
|   `-- feature_extractor_enhanced.py
|
|-- Phase3_development/        Production web application
|   |-- app.py                 Flask routes
|   |-- config.py              Configuration (paths, decision threshold, logging)
|   |-- wsgi.py                Production WSGI entry point
|   |-- models/
|   |   |-- detector.py        PhishingDetector class (load + predict)
|   |   |-- *.joblib           Saved model artefacts
|   |   `-- config.json        Model metadata
|   |-- static/                CSS and JavaScript
|   `-- templates/             HTML pages (index, analyzer, error pages)
|
|-- Procfile                   Production entry point (for Railway / Heroku)
|-- requirements.txt           Python dependencies
|-- runtime.txt                Python version pin (3.10.13)
|-- mise.toml                  Railway build settings
`-- README.md                  This file
```

---

## How the detection works

The classifier looks at every email through two complementary lenses:

- **5,000 TF-IDF features** — the 5,000 most class-distinguishing 1-to-2 word phrases learned automatically from the training corpus.
- **20 handcrafted phishing indicators** — domain-expert features such as IP-literal hosts in URLs, URL shortener use, look-alike domain detection (paypa1, micros0ft, …), suspicious TLDs (`.tk`, `.xyz`, …), urgency keywords, credential-request phrases and structural metrics.

These are concatenated into a 5,020-dimensional vector that is fed to a Logistic Regression classifier wrapped in scikit-learn's `CalibratedClassifierCV` (sigmoid calibration, 5-fold cross-validation).

Two production safety nets sit on top of the model:

- A **sender-reputation allowlist** of well-known transactional domains (GitHub, Amazon, Microsoft, etc.) downgrades the verdict to *legitimate* when no hard phishing signal fires. Free webmail providers are intentionally excluded so Business Email Compromise from a Gmail address is still caught.
- A **hard-signal escalation rule** upgrades the verdict to *phishing* when a non-allowlisted sender triggers any high-signal indicator (lookalike domain, brand-subdomain spoofing, IP-literal URL, URL shortener, suspicious TLD).

The decision threshold is set to `0.35` in `Phase3_development/config.py`.

---

## Reported performance

Measured on a stratified 5,024-email held-out test set:

| Metric    | Value   |
|-----------|---------|
| Accuracy  | 98.77 % |
| Precision | 98.57 % |
| Recall    | 98.96 % |
| F1-score  | 98.77 % |
| ROC-AUC   | 99.77 % |

Mean inference latency is approximately 2–3 ms per email on a laptop-class CPU.

---

## Re-training and re-evaluating the model

Everything is reproducible from the bundled datasets.

```bash
cd Phase2_development/2_training
python3 retrain_phase3_model.py        # writes new joblib files to Phase3_development/models/
python3 evaluate_phase3_model.py       # writes confusion_matrix.png and roc_pr_curves.png
```

To run the end-to-end test suite:

```bash
cd ../3_testing
python3 quick_test_suite.py
```

---

## Troubleshooting

**`python3: command not found`**
Install Python 3.10+ from https://www.python.org/downloads/ and reopen your terminal.

**`pip: command not found`**
Use `python3 -m pip install -r requirements.txt` instead.

**`ModuleNotFoundError: No module named 'flask'`**
The virtual environment is not activated. Re-run the activation command from Step 4.

**`Port 5001 is already in use`**
Another process is using the port. Either close the other process or change the port in `Phase3_development/config.py` (look for `PORT`).

**The browser shows "This site can't be reached"**
Make sure the Flask server is still running in the terminal. If you closed the terminal, the server stopped — restart it with `python3 app.py`.

**The model is slow on the very first request**
This is normal. The model loads into memory on the first request after startup (≈1 second) and stays cached afterwards.

---

## Licence and acknowledgements

This project was developed as part of the BSc (Hons) Cyber Security Final Year Project at De Montfort University Dubai, academic year 2025/26.

Training data sources:
- **MeAJOR Corpus** — publicly available phishing-email corpus.
- **Kaggle phishing-vs-legitimate 10k dataset** — https://www.kaggle.com/.

The project is released under the MIT licence (see `LICENSE` if present in the repository, otherwise treat as MIT for non-commercial academic re-use).
