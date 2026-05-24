"""
Model Retraining Script
Trains the phishing detection model with real data from Kaggle datasets
"""

import os
import pandas as pd
import numpy as np
from feature_extractor import FeatureExtractor
from ml_model import PhishingDetectionModel
import json
from datetime import datetime

print("\n" + "="*70)
print("PHISHING DETECTOR - MODEL RETRAINING WITH REAL DATA")
print("="*70)

# Configuration
DATA_FOLDER = 'phishing_data'
EXPECTED_FILES = [
    'CEAS_08.csv',
    'Enron.csv',
    'Ling.csv',
    'Nazario.csv',
    'Nigerian_Fraud.csv',
    'SpamAssassin.csv',
    'phishing_email.csv'
]

print("\n[1/6] Checking data files...")
print(f"Looking for data in: {DATA_FOLDER}/")

available_files = []
for file in EXPECTED_FILES:
    path = os.path.join(DATA_FOLDER, file)
    if os.path.exists(path):
        size = os.path.getsize(path) / 1024 / 1024  # Size in MB
        print(f"  ✓ {file} ({size:.2f} MB)")
        available_files.append(path)
    else:
        print(f"  ✗ {file} (not found)")

if not available_files:
    print("\n✗ ERROR: No phishing data files found!")
    print(f"Make sure you unzipped the data into the '{DATA_FOLDER}' folder")
    exit(1)

print(f"\nFound {len(available_files)} data files")

# ============================================================================
# LOAD DATA
# ============================================================================

print("\n[2/6] Loading email data from CSV files...")

all_emails = []
email_labels = []

for filepath in available_files:
    print(f"  Loading {os.path.basename(filepath)}...", end=" ")
    try:
        df = pd.read_csv(filepath, on_bad_lines='skip')

        # Different files have different column names, so we need to handle them
        # Try to identify email text and label columns
        email_col = None
        label_col = None

        # Common column names
        for col in df.columns:
            col_lower = col.lower()
            if any(x in col_lower for x in ['text', 'email', 'body', 'message', 'content']):
                email_col = col
            if any(x in col_lower for x in ['label', 'class', 'phishing', 'spam']):
                label_col = col

        if email_col is None:
            # Use first text-like column
            email_col = df.columns[0]

        # Process emails
        for idx, row in df.iterrows():
            try:
                email_text = str(row[email_col]).strip()

                # Determine label
                label = 0  # Default to legitimate
                if label_col:
                    label_val = str(row[label_col]).lower()
                    if any(x in label_val for x in ['phishing', 'phish', '1', 'spam', 'malicious']):
                        label = 1

                if email_text and len(email_text) > 10:  # Only include meaningful emails
                    all_emails.append(email_text)
                    email_labels.append(label)
            except:
                continue

        print(f"✓ ({len(df)} rows)")
    except Exception as e:
        print(f"✗ Error: {e}")
        continue

print(f"\nTotal emails loaded: {len(all_emails)}")
print(f"  Phishing: {email_labels.count(1)}")
print(f"  Legitimate: {email_labels.count(0)}")

if len(all_emails) < 50:
    print("\n✗ ERROR: Not enough data to train (minimum 50 required)")
    exit(1)

# ============================================================================
# EXTRACT FEATURES
# ============================================================================

print("\n[3/6] Extracting features from emails...")
print("This may take a few minutes...")

extractor = FeatureExtractor()
features_list = []
processed_count = 0
error_count = 0

for i, email_text in enumerate(all_emails):
    if (i + 1) % 100 == 0:
        print(f"  Processed {i + 1}/{len(all_emails)} emails...")

    try:
        # Create minimal email data structure
        email_data = {
            'sender': 'unknown@example.com',
            'sender_domain': 'example.com',
            'subject': 'Email',
            'to': 'user@example.com',
            'reply_to': '',
            'body': email_text,
            'urls': extractor._extract_urls(email_text),
            'headers': {}
        }

        # Extract features
        features = extractor.extract_all_features(email_data)
        features_list.append(features)
        processed_count += 1
    except Exception as e:
        error_count += 1
        continue

print(f"  Successfully extracted features from {processed_count} emails")
if error_count > 0:
    print(f"  (Skipped {error_count} due to errors)")

if processed_count < 50:
    print("\n✗ ERROR: Not enough valid features extracted")
    exit(1)

# ============================================================================
# PREPARE DATA FOR TRAINING
# ============================================================================

print("\n[4/6] Preparing data for model training...")

# Convert to numpy array
feature_names = list(features_list[0].keys())
X = np.array([list(f.values()) for f in features_list])
y = np.array(email_labels[:len(features_list)])

print(f"  Feature matrix shape: {X.shape}")
print(f"  Features: {len(feature_names)}")
print(f"  Training samples: {len(y)}")
print(f"  Phishing samples: {(y == 1).sum()}")
print(f"  Legitimate samples: {(y == 0).sum()}")

# ============================================================================
# TRAIN NEW MODEL
# ============================================================================

print("\n[5/6] Training model with real data...")

new_model = PhishingDetectionModel(model_type='random_forest')
metrics = new_model.train(X, y)

print(f"\n  ✓ Model trained successfully!")
print(f"  Accuracy:  {metrics.get('accuracy', 0):.2%}")
print(f"  Precision: {metrics.get('precision', 0):.2%}")
print(f"  Recall:    {metrics.get('recall', 0):.2%}")
print(f"  F1 Score:  {metrics.get('f1', 0):.2%}")

# ============================================================================
# SAVE MODEL
# ============================================================================

print("\n[6/6] Saving new model...")

# Backup old model
old_model_path = 'phishing_model_backup.pkl'
old_scaler_path = 'scaler_backup.pkl'

if os.path.exists('phishing_model.pkl'):
    os.rename('phishing_model.pkl', old_model_path)
    print(f"  Backed up old model to {old_model_path}")

if os.path.exists('scaler.pkl'):
    os.rename('scaler.pkl', old_scaler_path)
    print(f"  Backed up old scaler to {old_scaler_path}")

# Save new model
new_model.save_model('phishing_model.pkl', 'scaler.pkl')

# Save training metrics
metadata = {
    'training_date': datetime.now().isoformat(),
    'data_source': 'Kaggle Phishing Email Dataset',
    'total_samples': len(y),
    'phishing_samples': int((y == 1).sum()),
    'legitimate_samples': int((y == 0).sum()),
    'features_extracted': len(feature_names),
    'model_type': 'random_forest',
    'accuracy': float(metrics.get('accuracy', 0)),
    'precision': float(metrics.get('precision', 0)),
    'recall': float(metrics.get('recall', 0)),
    'f1_score': float(metrics.get('f1', 0)),
    'feature_names': feature_names
}

with open('model_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"  Saved model metadata to model_metadata.json")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
print("✓ MODEL RETRAINING COMPLETE!")
print("="*70)

print(f"\nNew Model Performance:")
print(f"  Accuracy:  {metrics.get('accuracy', 0):.2%}")
print(f"  Precision: {metrics.get('precision', 0):.2%}")
print(f"  Recall:    {metrics.get('recall', 0):.2%}")
print(f"  F1 Score:  {metrics.get('f1', 0):.2%}")

print(f"\nTraining Data:")
print(f"  Total emails: {len(y)}")
print(f"  Phishing: {(y == 1).sum()}")
print(f"  Legitimate: {(y == 0).sum()}")

print(f"\nModel Files:")
print(f"  ✓ phishing_model.pkl (new model)")
print(f"  ✓ scaler.pkl (new scaler)")
print(f"  ✓ model_metadata.json (metrics)")
print(f"  ✓ {old_model_path} (backup)")

print(f"\nNext Steps:")
print(f"  1. Restart Flask: python app.py")
print(f"  2. Test with new model at http://127.0.0.1:5000")
print(f"  3. The accuracy should be much better!")

print("\n" + "="*70 + "\n")
