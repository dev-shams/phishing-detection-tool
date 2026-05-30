#!/usr/bin/env python3
"""
Train with Probability Calibration to Fix Overconfidence

The model achieved 100% on training data, so it learned extreme confidence.
This script adds CalibratedClassifierCV to make probabilities realistic.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import re
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from scipy.sparse import hstack, csr_matrix
import warnings

warnings.filterwarnings('ignore')

print("\n" + "="*80)
print("CALIBRATED TRAINING: Fix Probability Overconfidence")
print("="*80)

# Feature extraction function (same as before)
URGENCY_KEYWORDS = [
    'urgent', 'immediately', 'action required', 'verify', 'confirm',
    'account suspended', 'click here', 'limited time', 'expire',
    'won', 'winner', 'prize', 'claim', 'free', 'congratulations',
    'password', 'bank', 'wire transfer', 'invoice', 'update your',
    'dear customer', 'dear user', 'suspended', 'security alert'
]

def extract_handcrafted_features(text):
    t = str(text)
    tl = t.lower()
    PHISHING_DOMAINS = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly', 'tiny.cc', 'is.gd', 'cli.gs']
    SUSPICIOUS_TLDS = ['.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', '.ru', '.cn']

    p1_features = [
        len(re.findall(r'http[s]?://\S+', t)),
        len(re.findall(r'http[s]?://(?:\d{1,3}\.){3}\d{1,3}|bit\.ly|tinyurl|goo\.gl', t)),
        sum(1 for kw in URGENCY_KEYWORDS if kw in tl),
        t.count('!'), t.count('$'),
        len(re.findall(r'\b[A-Z]{3,}\b', t)),
        len(t), len(t.split()),
        1 if re.search(r'<[a-z]+[\s/>]', tl) else 0,
        1 if 'reply-to' in tl else 0,
    ]

    fm = re.search(r'from:\s*[\w\.\-]+@([\w\.\-]+)', tl)
    rm = re.search(r'reply-to:\s*[\w\.\-]+@([\w\.\-]+)', tl)
    fd = fm.group(1) if fm else ''
    rd = rm.group(1) if rm else ''

    header_features = [
        1 if (fd and rd and fd != rd) else 0,
        1 if re.search(r'(paypa[^l]|micros[^o]ft|app[^l]e|go{3,}gle|amaz[^o]n)', tl) else 0,
        1 if (fd and re.search(r'\d', fd)) else 0,
        1 if any(tld in (fd + ' ' + rd) for tld in SUSPICIOUS_TLDS) else 0,
    ]

    urls = re.findall(r'http[s]?://\S+', t)
    if not urls:
        url_features = [0, 0, 0, 0, 0, 0]
    else:
        url_features = [
            sum(1 for u in urls if re.search(r'http[s]?://(?:\d{1,3}\.){3}\d{1,3}', u)),
            sum(1 for u in urls if any(d in u for d in PHISHING_DOMAINS)),
            float(np.mean([len(u) for u in urls])) if urls else 0,
            sum(1 for u in urls if u.count('.') > 3),
            sum(1 for u in urls if any(tld in u for tld in SUSPICIOUS_TLDS)),
            sum(1 for u in urls if '@' in u),
        ]
    return p1_features + header_features + url_features

# Load data
print("\n[1/6] Loading data...")
possible_paths = [
    'Phase2_development/1_data_combined/meajor_corpus.csv',
    'Phase2_development/1_data_combined/combined_dataset.csv',
]

data_file = None
for p in possible_paths:
    if Path(p).exists():
        data_file = Path(p)
        break

if data_file is None:
    print("✗ Data not found")
    sys.exit(1)

df = pd.read_csv(data_file)
for col in df.columns:
    col_lower = col.lower()
    if 'text' in col_lower or 'email' in col_lower or 'body' in col_lower:
        text_col = col
    if 'label' in col_lower or 'type' in col_lower or 'class' in col_lower:
        label_col = col

df = df[[text_col, label_col]].dropna()
df.columns = ['text', 'label']
if df['label'].dtype == 'object':
    df['label'] = df['label'].apply(lambda x: 1 if 'phish' in str(x).lower() else 0)

print(f"  ✓ Loaded {len(df):,} emails")

# Extract features
print("\n[2/6] Extracting features...")
hc_features = np.array([extract_handcrafted_features(t) for t in df['text']])
tfidf = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1,2), min_df=2)
X_tfidf = tfidf.fit_transform(df['text'])
X_combined = hstack([X_tfidf, csr_matrix(hc_features)])
y = df['label'].values
print(f"  ✓ Combined shape: {X_combined.shape}")

# Split data
print("\n[3/6] Splitting data (80/20)...")
X_train, X_test, y_train, y_test = train_test_split(
    X_combined, y, test_size=0.2, random_state=42, stratify=y
)
X_train_dense = X_train.toarray() if hasattr(X_train, 'toarray') else X_train
X_test_dense = X_test.toarray() if hasattr(X_test, 'toarray') else X_test

# Scale
print("\n[4/6] Scaling features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_dense)
X_test_scaled = scaler.transform(X_test_dense)

# Train with calibration
print("\n[5/6] Training with probability calibration...")

# Step 1: Train base Logistic Regression on training set
base_model = LogisticRegression(C=10.0, max_iter=1000, random_state=42, class_weight='balanced')

# Step 2: Use CalibratedClassifierCV with sigmoid method
# This recalibrates probabilities using a held-out set
calibrated_model = CalibratedClassifierCV(base_model, method='sigmoid', cv=5)
calibrated_model.fit(X_train_scaled, y_train)

# Evaluate
print("\n[6/6] Evaluating...")
y_pred = calibrated_model.predict(X_test_scaled)
y_pred_proba = calibrated_model.predict_proba(X_test_scaled)[:, 1]

print(f"\n  Accuracy:  {accuracy_score(y_test, y_pred)*100:.2f}%")
print(f"  Precision: {precision_score(y_test, y_pred)*100:.2f}%")
print(f"  Recall:    {recall_score(y_test, y_pred)*100:.2f}%")
print(f"  F1-Score:  {f1_score(y_test, y_pred)*100:.2f}%")

# Check probability distribution
print(f"\n  Probability Distribution:")
print(f"    Min phishing prob: {y_pred_proba.min():.4f}")
print(f"    Max phishing prob: {y_pred_proba.max():.4f}")
print(f"    Mean phishing prob: {y_pred_proba.mean():.4f}")
print(f"    Median phishing prob: {np.median(y_pred_proba):.4f}")

# Save
print("\n  Saving calibrated model...")
models_dir = Path('Phase3_development/models')
models_dir.mkdir(exist_ok=True)

joblib.dump(calibrated_model, models_dir / 'phishing_model_enhanced.joblib')
joblib.dump(tfidf, models_dir / 'tfidf_vectorizer_enhanced.joblib')
joblib.dump(scaler, models_dir / 'scaler_enhanced.joblib')

config = {
    'best_model': 'Logistic Regression (Calibrated)',
    'calibration_method': 'sigmoid',
    'cv_folds': 5,
    'test_accuracy': float(accuracy_score(y_test, y_pred)),
    'note': 'Uses CalibratedClassifierCV to fix probability overconfidence'
}

with open(models_dir / 'config.json', 'w') as f:
    json.dump(config, f, indent=2)

print(f"  ✓ Saved to {models_dir}")

print("\n" + "="*80)
print("✅ CALIBRATED TRAINING COMPLETE")
print("="*80)
print("\nFix Applied:")
print("  - Added CalibratedClassifierCV with sigmoid method")
print("  - Recalibrates probabilities to realistic values")
print("  - Should fix 100% phishing predictions")
print("\nRun: python Phase3_development/test_enhanced_model.py")
print("="*80 + "\n")
