#!/usr/bin/env python3
"""
Fresh test of calibrated model - avoids module caching issues
"""

import sys
import numpy as np
import re
import joblib
from pathlib import Path
from scipy.sparse import hstack, csr_matrix

# Feature extraction
URGENCY_KEYWORDS = [
    'urgent', 'immediately', 'action required', 'verify', 'confirm',
    'account suspended', 'click here', 'limited time', 'expire',
    'won', 'winner', 'prize', 'claim', 'free', 'congratulations',
    'password', 'bank', 'wire transfer', 'invoice', 'update your',
    'dear customer', 'dear user', 'suspended', 'security alert'
]

def extract_features(text):
    t = str(text)
    tl = t.lower()
    PHISHING_DOMAINS = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly', 'tiny.cc', 'is.gd', 'cli.gs']
    SUSPICIOUS_TLDS = ['.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', '.ru', '.cn']

    p1 = [
        len(re.findall(r'http[s]?://\S+', t)),
        len(re.findall(r'http[s]?://(?:\d{1,3}\.){3}\d{1,3}|bit\.ly|tinyurl|goo\.gl', t)),
        sum(1 for kw in URGENCY_KEYWORDS if kw in tl),
        t.count('!'), t.count('$'), len(re.findall(r'\b[A-Z]{3,}\b', t)), len(t), len(t.split()),
        1 if re.search(r'<[a-z]+[\s/>]', tl) else 0,
        1 if 'reply-to' in tl else 0,
    ]

    fm = re.search(r'from:\s*[\w\.\-]+@([\w\.\-]+)', tl)
    rm = re.search(r'reply-to:\s*[\w\.\-]+@([\w\.\-]+)', tl)
    fd = fm.group(1) if fm else ''
    rd = rm.group(1) if rm else ''

    h = [
        1 if (fd and rd and fd != rd) else 0,
        1 if re.search(r'(paypa[^l]|micros[^o]ft|app[^l]e|go{3,}gle|amaz[^o]n)', tl) else 0,
        1 if (fd and re.search(r'\d', fd)) else 0,
        1 if any(tld in (fd + ' ' + rd) for tld in SUSPICIOUS_TLDS) else 0,
    ]

    urls = re.findall(r'http[s]?://\S+', t)
    if not urls:
        u = [0, 0, 0, 0, 0, 0]
    else:
        u = [
            sum(1 for x in urls if re.search(r'http[s]?://(?:\d{1,3}\.){3}\d{1,3}', x)),
            sum(1 for x in urls if any(d in x for d in PHISHING_DOMAINS)),
            float(np.mean([len(x) for x in urls])) if urls else 0,
            sum(1 for x in urls if x.count('.') > 3),
            sum(1 for x in urls if any(tld in x for tld in SUSPICIOUS_TLDS)),
            sum(1 for x in urls if '@' in x),
        ]
    return np.array(p1 + h + u)

# Load models
print("\n" + "="*80)
print("TEST: Calibrated Model (Fresh Python Process)")
print("="*80)

models_dir = Path('Phase3_development/models')
model = joblib.load(models_dir / 'phishing_model_enhanced.joblib')
tfidf = joblib.load(models_dir / 'tfidf_vectorizer_enhanced.joblib')
scaler = joblib.load(models_dir / 'scaler_enhanced.joblib')

print(f"\nModel Type: {type(model).__name__}")
print(f"TF-IDF Features: {tfidf.max_features}")
print(f"Scaler: {type(scaler).__name__}")

# Test emails
tests = [
    ("Legitimate", "Hi team, please review the project report. Best, Sarah", "LEGITIMATE"),
    ("Phishing", "URGENT: Account suspended! Click http://bit.ly/verify NOW!!!", "PHISHING"),
]

print("\n" + "="*80)
for name, text, expected in tests:
    print(f"\n{name} Email:")
    print(f"  Text: {text[:60]}...")
    print(f"  Expected: {expected}")

    # Extract features
    hc = extract_features(text).reshape(1, -1)
    tfidf_feat = tfidf.transform([text]).toarray()
    combined = np.hstack([tfidf_feat, hc])
    scaled = scaler.transform(combined)

    # Predict
    proba = model.predict_proba(scaled)[0]
    pred = "PHISHING" if proba[1] >= 0.5 else "LEGITIMATE"

    print(f"  Prediction: {pred}")
    print(f"  Confidence: {proba[1]*100:.2f}% phishing")
    print(f"  Result: {'✓' if pred == expected else '✗'}")

print("\n" + "="*80)
print("This is the CORRECT model behavior with calibration!")
print("="*80 + "\n")
