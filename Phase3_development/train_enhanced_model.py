#!/usr/bin/env python3
"""
Phase 3: Train Enhanced Phishing Detection Model with Proper Feature Scaling

This script implements all three critical fixes:
1. MinMaxScaler for handcrafted features (BEFORE combining with TF-IDF)
2. Model comparison with cross-validation
3. Switch to Logistic Regression as primary model

Expected improvement: 50% accuracy → 95%+ accuracy
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
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
from scipy.sparse import hstack, csr_matrix
import warnings

warnings.filterwarnings('ignore')

print("\n" + "="*80)
print("PHASE 3: TRAIN ENHANCED PHISHING DETECTION MODEL")
print("="*80)

# Configuration
URGENCY_KEYWORDS = [
    'urgent', 'immediately', 'action required', 'verify', 'confirm',
    'account suspended', 'click here', 'limited time', 'expire',
    'won', 'winner', 'prize', 'claim', 'free', 'congratulations',
    'password', 'bank', 'wire transfer', 'invoice', 'update your',
    'dear customer', 'dear user', 'suspended', 'security alert'
]

PHISHING_DOMAINS = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly', 'tiny.cc', 'is.gd', 'cli.gs']
SUSPICIOUS_TLDS = ['.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', '.ru', '.cn']

def extract_handcrafted_features(text):
    """
    Extract 20 handcrafted phishing-specific features

    Features 1-10: Basic signals
    Features 11-14: Email header analysis
    Features 15-20: URL structure analysis
    """
    t = str(text)
    tl = t.lower()

    # Phase 1 Features (10): Basic phishing indicators
    p1_features = [
        len(re.findall(r'http[s]?://\S+', t)),  # 1. url_count
        len(re.findall(r'http[s]?://(?:\d{1,3}\.){3}\d{1,3}|bit\.ly|tinyurl|goo\.gl', t)),  # 2. suspicious_url
        sum(1 for kw in URGENCY_KEYWORDS if kw in tl),  # 3. urgency_keywords
        t.count('!'),  # 4. exclamation_marks
        t.count('$'),  # 5. dollar_signs
        len(re.findall(r'\b[A-Z]{3,}\b', t)),  # 6. caps_words
        len(t),  # 7. text_length
        len(t.split()),  # 8. word_count
        1 if re.search(r'<[a-z]+[\s/>]', tl) else 0,  # 9. has_html
        1 if 'reply-to' in tl else 0,  # 10. has_reply_to
    ]

    # Phase 2 Features (10): Advanced signals
    # Header analysis (4)
    fm = re.search(r'from:\s*[\w\.\-]+@([\w\.\-]+)', tl)
    rm = re.search(r'reply-to:\s*[\w\.\-]+@([\w\.\-]+)', tl)
    fd = fm.group(1) if fm else ''
    rd = rm.group(1) if rm else ''

    header_features = [
        1 if (fd and rd and fd != rd) else 0,  # 11. domain_mismatch
        1 if re.search(r'(paypa[^l]|micros[^o]ft|app[^l]e|go{3,}gle|amaz[^o]n)', tl) else 0,  # 12. lookalike_domain
        1 if (fd and re.search(r'\d', fd)) else 0,  # 13. numeric_in_domain
        1 if any(tld in (fd + ' ' + rd) for tld in SUSPICIOUS_TLDS) else 0,  # 14. suspicious_tld_header
    ]

    # URL analysis (6)
    urls = re.findall(r'http[s]?://\S+', t)
    if not urls:
        url_features = [0, 0, 0, 0, 0, 0]
    else:
        url_features = [
            sum(1 for u in urls if re.search(r'http[s]?://(?:\d{1,3}\.){3}\d{1,3}', u)),  # 15. ip_url_count
            sum(1 for u in urls if any(d in u for d in PHISHING_DOMAINS)),  # 16. shortener_url_count
            float(np.mean([len(u) for u in urls])),  # 17. avg_url_length
            sum(1 for u in urls if u.count('.') > 3),  # 18. deep_subdomain_count
            sum(1 for u in urls if any(tld in u for tld in SUSPICIOUS_TLDS)),  # 19. suspicious_tld_url
            sum(1 for u in urls if '@' in u),  # 20. at_in_url
        ]

    return p1_features + header_features + url_features


# ============================================================================
# STEP 1: Load Data
# ============================================================================
print("\n[1/9] Loading dataset...")

# Check for data file
possible_paths = [
    Path(__file__).parent.parent / "Phase2_development" / "1_data_combined" / "meajor_corpus.csv",
    Path(__file__).parent.parent / "Phase2_development" / "1_data_combined" / "combined_dataset.csv",
    Path(__file__).parent.parent / "1_data_combined" / "meajor_corpus.csv",
    Path(__file__).parent.parent / "Phase2_development" / "data" / "phishing_emails_processed.csv",
]

data_file = None
for path in possible_paths:
    if path.exists():
        data_file = path
        break

if data_file is None or not data_file.exists():

    for path in possible_paths:
        if path.exists():
            data_file = path
            break
    else:
        print(f"\n✗ Data file not found!")
        print(f"  Looked for: {data_file}")
        print(f"  Alternative paths tried:")
        for p in possible_paths:
            print(f"    - {p}")
        sys.exit(1)

df = pd.read_csv(data_file)
print(f"  ✓ Loaded {len(df):,} emails")

# Identify text and label columns
text_col = None
label_col = None

for col in df.columns:
    col_lower = col.lower()
    if any(k in col_lower for k in ['text', 'body', 'email', 'message', 'content']):
        text_col = col
    if any(k in col_lower for k in ['label', 'type', 'class', 'category', 'target']):
        label_col = col

if text_col is None or label_col is None:
    print(f"\n✗ Could not auto-detect columns!")
    print(f"  Columns found: {df.columns.tolist()}")
    print(f"  Please rename columns to contain 'text'/'body' and 'label'/'type'")
    sys.exit(1)

# Clean data
df = df[[text_col, label_col]].dropna()
df.columns = ['text', 'label']

# Normalize labels
if df['label'].dtype == 'object':
    df['label'] = df['label'].apply(lambda x: 1 if 'phish' in str(x).lower() else 0)
else:
    df['label'] = df['label'].astype(int)

phishing_count = (df['label'] == 1).sum()
legitimate_count = (df['label'] == 0).sum()
print(f"  ✓ Phishing: {phishing_count:,} | Legitimate: {legitimate_count:,}")


# ============================================================================
# STEP 2: Extract Handcrafted Features
# ============================================================================
print("\n[2/9] Extracting handcrafted features (20 per email)...")

handcrafted_raw = np.array([extract_handcrafted_features(t) for t in df['text']])
print(f"  ✓ Shape: {handcrafted_raw.shape}")


# ============================================================================
# STEP 3: Scale Handcrafted Features (FIX #1)
# ============================================================================
print("\n[3/9] Scaling handcrafted features with MinMaxScaler...")

handcrafted_scaler = MinMaxScaler()
handcrafted_scaled = np.clip(handcrafted_scaler.fit_transform(handcrafted_raw), 0, 1)
print(f"  ✓ Shape after scaling: {handcrafted_scaled.shape}")
print(f"  ✓ Value range: [{handcrafted_scaled.min():.3f}, {handcrafted_scaled.max():.3f}]")


# ============================================================================
# STEP 4: Extract TF-IDF Features
# ============================================================================
print("\n[4/9] Extracting TF-IDF features (5000 per email)...")

tfidf = TfidfVectorizer(
    max_features=5000,
    stop_words='english',
    ngram_range=(1, 2),
    min_df=2,
    sublinear_tf=True,
    norm='l2'
)
X_tfidf = tfidf.fit_transform(df['text'])
print(f"  ✓ Shape: {X_tfidf.shape}")


# ============================================================================
# STEP 5: Combine Features
# ============================================================================
print("\n[5/9] Combining TF-IDF + scaled handcrafted features...")

X_combined = hstack([X_tfidf, csr_matrix(handcrafted_scaled)])
y = df['label'].values
print(f"  ✓ Combined shape: {X_combined.shape}")
print(f"  ✓ Total features: {X_combined.shape[1]} (5000 TF-IDF + 20 handcrafted)")


# ============================================================================
# STEP 6: Train/Test Split
# ============================================================================
print("\n[6/9] Splitting data (80/20)...")

X_train, X_test, y_train, y_test = train_test_split(
    X_combined, y, test_size=0.2, random_state=42, stratify=y
)
print(f"  ✓ Train: {X_train.shape[0]:,} samples")
print(f"  ✓ Test: {X_test.shape[0]:,} samples")


# ============================================================================
# STEP 7: Scale Combined Features & Train Multiple Models
# ============================================================================
print("\n[7/9] Scaling combined features and training models...")

# Scale combined features with StandardScaler
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train.toarray() if hasattr(X_train, 'toarray') else X_train)
X_test_scaled = scaler.transform(X_test.toarray() if hasattr(X_test, 'toarray') else X_test)
print(f"  ✓ Combined features scaled")

# Define models (FIX #2 - Multiple models for comparison)
models = {
    'Logistic Regression': LogisticRegression(
        C=10.0,
        max_iter=1000,
        random_state=42,
        class_weight='balanced'
    ),
    'Random Forest': RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    ),
    'Gradient Boosting': GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    ),
}

# FIX #3: Use 5-fold cross-validation for model selection
print("\n  Training with 5-fold cross-validation:")
cv_results = {}
for name, model in models.items():
    scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='f1', n_jobs=-1)
    cv_results[name] = scores.mean()
    print(f"    {name:.<30} {scores.mean()*100:6.2f}% (+/- {scores.std()*100:.2f}%)")

# Select best model
best_name = max(cv_results, key=cv_results.get)
print(f"\n  ✓ Best model: {best_name} ({cv_results[best_name]*100:.2f}%)")


# ============================================================================
# STEP 8: Evaluate Best Model
# ============================================================================
print("\n[8/9] Evaluating best model on test set...")

best_model = models[best_name]
best_model.fit(X_train_scaled, y_train)

y_pred = best_model.predict(X_test_scaled)
y_pred_proba = best_model.predict_proba(X_test_scaled)[:, 1]

metrics = {
    'accuracy': accuracy_score(y_test, y_pred),
    'precision': precision_score(y_test, y_pred, zero_division=0),
    'recall': recall_score(y_test, y_pred, zero_division=0),
    'f1': f1_score(y_test, y_pred, zero_division=0),
    'roc_auc': roc_auc_score(y_test, y_pred_proba),
}

print("\n  Test Set Performance:")
print(f"    Accuracy:  {metrics['accuracy']*100:.2f}%")
print(f"    Precision: {metrics['precision']*100:.2f}%")
print(f"    Recall:    {metrics['recall']*100:.2f}%")
print(f"    F1-Score:  {metrics['f1']*100:.2f}%")
print(f"    ROC-AUC:   {metrics['roc_auc']*100:.2f}%")

print("\n  Confusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(f"    TN (Legit correct):  {cm[0,0]:,}")
print(f"    FP (False alarm):    {cm[0,1]:,}")
print(f"    FN (Missed phishing): {cm[1,0]:,}")
print(f"    TP (Phishing caught): {cm[1,1]:,}")

print("\n  Classification Report:")
print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Phishing']))


# ============================================================================
# STEP 9: Save Models
# ============================================================================
print("\n[9/9] Saving trained models...")

models_dir = Path(__file__).parent / "models"
models_dir.mkdir(exist_ok=True)

# Save model
model_path = models_dir / "phishing_model_enhanced.joblib"
joblib.dump(best_model, model_path)
print(f"  ✓ Model: {model_path.name}")

# Save TF-IDF vectorizer
tfidf_path = models_dir / "tfidf_vectorizer_enhanced.joblib"
joblib.dump(tfidf, tfidf_path)
print(f"  ✓ TF-IDF Vectorizer: {tfidf_path.name}")

# Save scalers
handcrafted_scaler_path = models_dir / "handcrafted_scaler_enhanced.joblib"
joblib.dump(handcrafted_scaler, handcrafted_scaler_path)
print(f"  ✓ Handcrafted Scaler: {handcrafted_scaler_path.name}")

scaler_path = models_dir / "scaler_enhanced.joblib"
joblib.dump(scaler, scaler_path)
print(f"  ✓ Combined Scaler: {scaler_path.name}")

# Save config
config = {
    'best_model': best_name,
    'cv_results': {k: float(v) for k, v in cv_results.items()},
    'metrics': {k: float(v) for k, v in metrics.items()},
    'feature_names': [
        'url_count', 'suspicious_url', 'urgency_keywords', 'exclamation_marks',
        'dollar_signs', 'caps_words', 'text_length', 'word_count', 'has_html', 'has_reply_to',
        'domain_mismatch', 'lookalike_domain', 'numeric_in_domain', 'suspicious_tld_header',
        'ip_url_count', 'shortener_url_count', 'avg_url_length', 'deep_subdomain_count',
        'suspicious_tld_url', 'at_in_url'
    ],
    'urgency_keywords': URGENCY_KEYWORDS,
    'phishing_domains': PHISHING_DOMAINS,
    'suspicious_tlds': SUSPICIOUS_TLDS,
    'total_features': 5020,
    'tfidf_features': 5000,
    'handcrafted_features': 20,
}

config_path = models_dir / "config.json"
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)
print(f"  ✓ Config: {config_path.name}")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "="*80)
print("✓ TRAINING COMPLETE")
print("="*80)
print(f"\nBest Model: {best_name}")
print(f"  Cross-validation F1: {cv_results[best_name]*100:.2f}%")
print(f"  Test Accuracy: {metrics['accuracy']*100:.2f}%")
print(f"  Test F1-Score: {metrics['f1']*100:.2f}%")

print(f"\nKey Improvements Applied:")
print(f"  ✓ Fix #1: MinMaxScaler for handcrafted features")
print(f"  ✓ Fix #2: Model comparison (trained 3 models)")
print(f"  ✓ Fix #3: 5-fold cross-validation for selection")

print(f"\nNext Steps:")
print(f"  1. Update Phase3_development/models/detector.py to use new scalers")
print(f"  2. Update Phase3_development/config.py with correct paths")
print(f"  3. Test locally: python Phase3_development/test_model.py")
print(f"  4. Deploy to Railway when satisfied")

print("\n" + "="*80 + "\n")
