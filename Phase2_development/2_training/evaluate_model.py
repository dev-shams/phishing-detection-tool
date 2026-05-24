#!/usr/bin/env python3
"""
Phase 2: Evaluate Model Performance

Loads trained model and evaluates on test set.
Generates detailed metrics and creates evaluation report.

Input:
  - 4_models/phishing_model_phase2.pkl (trained model)
  - 4_models/scaler_phase2.pkl (scaler)
  - data/phishing_emails_processed.csv (test data)

Output:
  - 5_results/phase2_evaluation_report.txt (detailed metrics)
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score
)
import pickle

print("\n" + "="*70)
print("PHASE 2: EVALUATE MODEL PERFORMANCE")
print("="*70)

# Setup paths
phase2_dir = Path(__file__).parent.parent
sys.path.insert(0, str(phase2_dir))

# Import feature extractor
try:
    from feature_extractor import FeatureExtractor
    print("✓ Imported feature extractor")
except ImportError as e:
    print(f"✗ Failed to import: {str(e)}")
    sys.exit(1)

# Load model and scaler
models_dir = phase2_dir / "4_models"
model_path = models_dir / "phishing_model_phase2.pkl"
scaler_path = models_dir / "scaler_phase2.pkl"

if not model_path.exists() or not scaler_path.exists():
    print(f"\n✗ Model files not found")
    print(f"  Model: {model_path}")
    print(f"  Scaler: {scaler_path}")
    print("\nTrain model first: python 2_training/train_model.py")
    sys.exit(1)

print(f"\nLoading trained model...")
with open(model_path, 'rb') as f:
    model = pickle.load(f)
print(f"✓ Model loaded")

with open(scaler_path, 'rb') as f:
    scaler = pickle.load(f)
print(f"✓ Scaler loaded")

# Load data
data_file = phase2_dir / "data" / "phishing_emails_processed.csv"
if not data_file.exists():
    print(f"\n✗ Data file not found: {data_file}")
    sys.exit(1)

print(f"\nLoading test data...")
df = pd.read_csv(data_file)
print(f"  Loaded {len(df)} emails")

# Extract features
print(f"\nExtracting features from test data...")
extractor = FeatureExtractor()
features_list = []
labels_list = []

for idx, row in df.iterrows():
    if (idx + 1) % 5000 == 0:
        print(f"  Processed {idx + 1}/{len(df)} emails...")

    email_text = str(row['email'])
    label = int(row['label'])

    email_data = {
        'sender': '',
        'sender_domain': '',
        'to': '',
        'subject': '',
        'reply_to': '',
        'body': email_text,
        'urls': [],
        'headers': {}
    }

    try:
        features = extractor.extract_all_features(email_data)
        feature_values = [features[name] for name in extractor.get_feature_names()]
        features_list.append(feature_values)
        labels_list.append(label)
    except:
        continue

X = np.array(features_list)
y = np.array(labels_list)

print(f"  Extracted features from {len(X)} emails")

# Scale features
print(f"\nScaling features...")
X_scaled = scaler.transform(X)

# Split data
print(f"Splitting into train/test (80/20)...")
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

print(f"  Training samples: {len(X_train)}")
print(f"  Test samples: {len(X_test)}")

# Make predictions
print(f"\nMaking predictions...")
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

# Calculate metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)
roc_auc = roc_auc_score(y_test, y_pred_proba)
cm = confusion_matrix(y_test, y_pred)

# Print results
print("\n" + "="*70)
print("EVALUATION RESULTS")
print("="*70)

print(f"\nDataset:")
print(f"  Total samples: {len(X)}")
print(f"  Test samples: {len(X_test)}")
print(f"  Phishing in test: {(y_test == 1).sum()}")
print(f"  Legitimate in test: {(y_test == 0).sum()}")

print(f"\nPerformance Metrics:")
print(f"  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"  Precision: {precision:.4f} ({precision*100:.2f}%)")
print(f"  Recall:    {recall:.4f} ({recall*100:.2f}%)")
print(f"  F1-Score:  {f1:.4f}")
print(f"  ROC-AUC:   {roc_auc:.4f}")

print(f"\nConfusion Matrix:")
print(f"  True Negatives:  {cm[0,0]}")
print(f"  False Positives: {cm[0,1]}")
print(f"  False Negatives: {cm[1,0]}")
print(f"  True Positives:  {cm[1,1]}")

print(f"\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

# Save evaluation report
results_dir = phase2_dir / "5_results"
results_dir.mkdir(exist_ok=True)

report_file = results_dir / "phase2_evaluation_report.txt"

with open(report_file, 'w') as f:
    f.write("PHASE 2: MODEL EVALUATION REPORT\n")
    f.write("="*60 + "\n\n")
    f.write(f"Dataset: Kaggle Phishing Email Dataset\n")
    f.write(f"Total Samples: {len(X)}\n")
    f.write(f"Test Samples: {len(X_test)}\n")
    f.write(f"Features: {X.shape[1]}\n\n")

    f.write("PERFORMANCE METRICS:\n")
    f.write(f"  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)\n")
    f.write(f"  Precision: {precision:.4f} ({precision*100:.2f}%)\n")
    f.write(f"  Recall:    {recall:.4f} ({recall*100:.2f}%)\n")
    f.write(f"  F1-Score:  {f1:.4f}\n")
    f.write(f"  ROC-AUC:   {roc_auc:.4f}\n\n")

    f.write("CONFUSION MATRIX:\n")
    f.write(f"  True Negatives:  {cm[0,0]}\n")
    f.write(f"  False Positives: {cm[0,1]}\n")
    f.write(f"  False Negatives: {cm[1,0]}\n")
    f.write(f"  True Positives:  {cm[1,1]}\n\n")

    f.write("CLASSIFICATION REPORT:\n")
    f.write(classification_report(y_test, y_pred, zero_division=0))

print(f"\n✓ Report saved: {report_file.name}")

print("\n" + "="*70)
print("✓ EVALUATION COMPLETE")
print("="*70)

print("\nNext steps:")
print("1. python 3_testing/test_phishing_detection.py")
print("2. python 3_testing/test_legitimate_detection.py")
print("="*70 + "\n")
