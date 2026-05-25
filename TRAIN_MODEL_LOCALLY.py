#!/usr/bin/env python3
"""
Train the phishing detection model locally
Run this on your Mac before pushing to GitHub

Usage:
    cd ~/Documents/Claude/Projects/'Final year Project'
    python3 TRAIN_MODEL_LOCALLY.py
"""

import sys
from pathlib import Path

# Add Phase2 to path
phase2_path = Path(__file__).parent.parent / "Documents/Claude/Projects/Final year Project/Phase2_development"
if not phase2_path.exists():
    phase2_path = Path.cwd() / "Phase2_development"

sys.path.insert(0, str(phase2_path))

# Change to Phase2 directory for relative imports
import os
os.chdir(phase2_path)

print("\n" + "="*70)
print("RETRAINING PHISHING DETECTION MODEL")
print("="*70)
print("This will create new .pkl files compatible with Railway")
print("Versions: numpy==1.24.3, pandas==1.5.3, scikit-learn==1.3.0")
print("="*70)

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import pickle
import time

# Import custom modules
from feature_extractor import FeatureExtractor

print("\n[Step 1/4] Loading data...")
start_time = time.time()
data_path = phase2_path / 'data' / 'phishing_emails_processed.csv'

if not data_path.exists():
    print(f"✗ Data file not found: {data_path}")
    print("  Run the preprocessing first:")
    print("    python3 Phase2_development/1_data/preprocess_data.py")
    sys.exit(1)

df = pd.read_csv(data_path)
print(f"✓ Loaded {len(df):,} emails")

phishing_count = (df['label'] == 1).sum()
legit_count = (df['label'] == 0).sum()
print(f"  Distribution:")
print(f"    Phishing:    {phishing_count:,} ({phishing_count/len(df)*100:.1f}%)")
print(f"    Legitimate:  {legit_count:,} ({legit_count/len(df)*100:.1f}%)")

print("\n[Step 2/4] Extracting features...")
print("  (This takes ~3-5 minutes depending on your hardware)")
extractor = FeatureExtractor()

features_list = []
labels_list = []

for idx, (_, row) in enumerate(df.iterrows()):
    if (idx + 1) % 10000 == 0:
        elapsed = time.time() - start_time
        rate = (idx + 1) / elapsed
        remaining = (len(df) - idx - 1) / rate / 60
        print(f"  Progress: {idx + 1:,}/{len(df):,} ({elapsed:.0f}s, ~{remaining:.1f}min remaining)")

    email_data = {
        'body': str(row.get('email', '')),
        'subject': '',
        'sender': '',
        'urls': [],
        'headers': {}
    }

    try:
        features = extractor.extract_all_features(email_data)
        features_list.append(features)
        labels_list.append(row['label'])
    except Exception as e:
        # Skip emails that fail feature extraction
        continue

if not features_list:
    print("✗ No features were extracted!")
    sys.exit(1)

feature_names = list(features_list[0].keys())
X = np.array([list(f.values()) for f in features_list])
y = np.array(labels_list)

print(f"✓ Extracted features: {X.shape[0]:,} emails × {X.shape[1]} features")
feature_variance = (X.var(axis=0) > 0).sum()
print(f"  Features with variance: {feature_variance}/{len(feature_names)}")

print("\n[Step 3/4] Training Random Forest model...")
print("  (This takes ~5-10 minutes)")

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

print(f"  Training set: {len(X_train):,} samples")
print(f"  Test set: {len(X_test):,} samples")

# Train with balanced class weights
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,  # Use all available cores
    class_weight='balanced'  # Handle class imbalance
)

train_start = time.time()
model.fit(X_train, y_train)
train_elapsed = time.time() - train_start
print(f"✓ Training complete in {train_elapsed:.1f}s")

print("\n[Step 4/4] Evaluating model...")
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)
roc_auc = roc_auc_score(y_test, y_pred_proba)

print("\n" + "="*70)
print("MODEL PERFORMANCE")
print("="*70)
print(f"Accuracy:  {accuracy:.2%}")
print(f"Precision: {precision:.2%}  (of predicted phishing, how many are correct)")
print(f"Recall:    {recall:.2%}   (of actual phishing, how many we catch)")
print(f"F1-Score:  {f1:.2%}   (harmonic mean)")
print(f"ROC-AUC:   {roc_auc:.2%}  (overall performance)")

print("\n" + "="*70)
print("SAVING MODEL FILES")
print("="*70)

models_dir = phase2_path / '4_models'
models_dir.mkdir(parents=True, exist_ok=True)

model_path = models_dir / 'phishing_model_phase2.pkl'
scaler_path = models_dir / 'scaler_phase2.pkl'

# Save with pickle
with open(model_path, 'wb') as f:
    pickle.dump(model, f)

with open(scaler_path, 'wb') as f:
    pickle.dump(scaler, f)

print(f"✓ Model saved:  {model_path.name} ({model_path.stat().st_size / 1024 / 1024:.1f} MB)")
print(f"✓ Scaler saved: {scaler_path.name} ({scaler_path.stat().st_size / 1024:.1f} KB)")

# Verify files can be loaded
print("\nVerifying files...")
try:
    with open(model_path, 'rb') as f:
        loaded_model = pickle.load(f)
    with open(scaler_path, 'rb') as f:
        loaded_scaler = pickle.load(f)
    print("✓ Files verified - can be loaded successfully")
except Exception as e:
    print(f"✗ Error loading files: {e}")
    sys.exit(1)

total_time = time.time() - start_time
print("\n" + "="*70)
print("DONE!")
print("="*70)
print(f"Total time: {total_time/60:.1f} minutes")
print("\nNext steps:")
print("  1. Commit and push to GitHub:")
print("       git add Phase2_development/4_models/phishing_model_phase2.pkl")
print("       git add Phase2_development/4_models/scaler_phase2.pkl")
print("       git commit -m 'Retrain model with compatible versions'")
print("       git push origin main")
print("\n  2. Railway will automatically redeploy")
print("  3. Test the analyzer at:")
print("     https://phishing-detection-tool-production.up.railway.app")
print("="*70 + "\n")
