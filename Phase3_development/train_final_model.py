#!/usr/bin/env python3
"""
Final Training: Enhanced Phishing Detection Model (Simplified)

SIMPLIFIED APPROACH:
- Extract 20 handcrafted features
- Extract TF-IDF features
- Combine all features
- Apply StandardScaler to combined features (single unified scaling)
- Train Logistic Regression with cross-validation

This avoids the homogeneous data issue from separate scaling.
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
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
from scipy.sparse import hstack, csr_matrix
import warnings

warnings.filterwarnings('ignore')

print("\n" + "="*80)
print("FINAL TRAINING: Enhanced Phishing Detection Model (Simplified)")
print("="*80)

# Configuration
URGENCY_KEYWORDS = [
    'urgent', 'immediately', 'action required', 'verify', 'confirm',
    'account suspended', 'click here', 'limited time', 'expire',
    'won', 'winner', 'prize', 'claim', 'free', 'congratulations',
    'password', 'bank', 'wire transfer', 'invoice', 'update your',
    'dear customer', 'dear user', 'suspended', 'security alert'
]

def extract_handcrafted_features(text):
    """Extract 20 handcrafted phishing-specific features"""
    t = str(text)
    tl = t.lower()

    PHISHING_DOMAINS = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly', 'tiny.cc', 'is.gd', 'cli.gs']
    SUSPICIOUS_TLDS = ['.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', '.ru', '.cn']

    # Phase 1 Features (10)
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

    # Phase 2 Features (10)
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


# ============================================================================
# LOAD DATA
# ============================================================================
print("\n[1/7] Loading dataset...")

possible_paths = [
    'Phase2_development/1_data_combined/meajor_corpus.csv',
    'Phase2_development/1_data_combined/combined_dataset.csv',
    '1_data_combined/meajor_corpus.csv',
]

data_file = None
for path in possible_paths:
    if Path(path).exists():
        data_file = Path(path)
        break

if data_file is None:
    print("✗ Data file not found!")
    sys.exit(1)

df = pd.read_csv(data_file)

# Auto-detect columns
text_col = None
label_col = None
for col in df.columns:
    col_lower = col.lower()
    if any(k in col_lower for k in ['text', 'body', 'email', 'message']):
        text_col = col
    if any(k in col_lower for k in ['label', 'type', 'class', 'category']):
        label_col = col

if text_col is None or label_col is None:
    print(f"✗ Could not auto-detect columns! Found: {df.columns.tolist()}")
    sys.exit(1)

df = df[[text_col, label_col]].dropna()
df.columns = ['text', 'label']

if df['label'].dtype == 'object':
    df['label'] = df['label'].apply(lambda x: 1 if 'phish' in str(x).lower() else 0)

print(f"  ✓ Loaded {len(df):,} emails")
print(f"    Phishing: {(df['label']==1).sum():,}")
print(f"    Legitimate: {(df['label']==0).sum():,}")


# ============================================================================
# EXTRACT FEATURES
# ============================================================================
print("\n[2/7] Extracting features...")

# Handcrafted features
print("  Extracting handcrafted features...")
hc_features = np.array([extract_handcrafted_features(t) for t in df['text']])

# TF-IDF features
print("  Extracting TF-IDF features...")
tfidf = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1,2), min_df=2)
X_tfidf = tfidf.fit_transform(df['text'])

# Combine
X_combined = hstack([X_tfidf, csr_matrix(hc_features)])
y = df['label'].values

print(f"  ✓ Combined shape: {X_combined.shape}")


# ============================================================================
# TRAIN/TEST SPLIT
# ============================================================================
print("\n[3/7] Splitting data...")

X_train, X_test, y_train, y_test = train_test_split(
    X_combined, y, test_size=0.2, random_state=42, stratify=y
)

# Convert to dense for scaling
X_train_dense = X_train.toarray() if hasattr(X_train, 'toarray') else X_train
X_test_dense = X_test.toarray() if hasattr(X_test, 'toarray') else X_test

print(f"  ✓ Train: {X_train_dense.shape[0]:,} | Test: {X_test_dense.shape[0]:,}")


# ============================================================================
# SCALE & TRAIN MODELS
# ============================================================================
print("\n[4/7] Scaling features and training models...")

# Single unified scaling for all features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_dense)
X_test_scaled = scaler.transform(X_test_dense)

# Train multiple models
models = {
    'Logistic Regression': LogisticRegression(C=10.0, max_iter=1000, random_state=42, class_weight='balanced'),
    'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1),
}

print("\n  5-fold Cross-Validation:")
cv_results = {}
for name, model in models.items():
    scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='f1', n_jobs=-1)
    cv_results[name] = scores.mean()
    print(f"    {name:.<35} {scores.mean()*100:6.2f}%")

best_name = max(cv_results, key=cv_results.get)
print(f"\n  ✓ Best Model: {best_name}")


# ============================================================================
# EVALUATE
# ============================================================================
print("\n[5/7] Evaluating on test set...")

best_model = models[best_name]
best_model.fit(X_train_scaled, y_train)

y_pred = best_model.predict(X_test_scaled)
y_pred_proba = best_model.predict_proba(X_test_scaled)[:, 1]

print(f"\n  Accuracy:  {accuracy_score(y_test, y_pred)*100:.2f}%")
print(f"  Precision: {precision_score(y_test, y_pred)*100:.2f}%")
print(f"  Recall:    {recall_score(y_test, y_pred)*100:.2f}%")
print(f"  F1-Score:  {f1_score(y_test, y_pred)*100:.2f}%")

cm = confusion_matrix(y_test, y_pred)
print(f"\n  Confusion Matrix:")
print(f"    TN: {cm[0,0]:,} | FP: {cm[0,1]:,}")
print(f"    FN: {cm[1,0]:,} | TP: {cm[1,1]:,}")


# ============================================================================
# SAVE MODELS
# ============================================================================
print("\n[6/7] Saving models...")

models_dir = Path('Phase3_development/models')
models_dir.mkdir(exist_ok=True)

joblib.dump(best_model, models_dir / 'phishing_model_enhanced.joblib')
joblib.dump(tfidf, models_dir / 'tfidf_vectorizer_enhanced.joblib')
joblib.dump(scaler, models_dir / 'scaler_enhanced.joblib')

config = {
    'best_model': best_name,
    'cv_results': {k: float(v) for k, v in cv_results.items()},
    'test_accuracy': float(accuracy_score(y_test, y_pred)),
    'feature_count': X_combined.shape[1],
}

with open(models_dir / 'config.json', 'w') as f:
    json.dump(config, f, indent=2)

print(f"  ✓ Models saved to {models_dir}")


# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("✓ TRAINING COMPLETE")
print("="*80)
print(f"\nBest Model: {best_name}")
print(f"  CV F1-Score: {cv_results[best_name]*100:.2f}%")
print(f"  Test Accuracy: {accuracy_score(y_test, y_pred)*100:.2f}%")
print(f"\nKey Features:")
print(f"  ✓ StandardScaler for all {X_combined.shape[1]} features")
print(f"  ✓ Logistic Regression selected via cross-validation")
print(f"  ✓ {X_combined.shape[1]} total features (TF-IDF + handcrafted)")

print(f"\nNext: python Phase3_development/test_enhanced_model.py")
print("="*80 + "\n")
