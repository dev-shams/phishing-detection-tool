#!/usr/bin/env python3
"""
Phase 2: Train Model on Real Data

Loads preprocessed emails from Kaggle dataset and trains the model.
Uses feature extraction from Phase 1 to extract 24 features per email.

Input: data/phishing_emails_processed.csv
Output:
  - 4_models/phishing_model_phase2.pkl (trained model)
  - 4_models/scaler_phase2.pkl (feature scaler)
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

print("\n" + "="*70)
print("PHASE 2: TRAIN MODEL ON REAL DATA")
print("="*70)

# Add parent directory to path to import Phase 2 modules
phase2_dir = Path(__file__).parent.parent
sys.path.insert(0, str(phase2_dir))

# Import Phase 1 components
try:
    from feature_extractor import FeatureExtractor
    from ml_model import PhishingDetectionModel
    print("✓ Imported feature extractor and ML model")
except ImportError as e:
    print(f"✗ Failed to import modules: {str(e)}")
    print("Make sure feature_extractor.py and ml_model.py are in Phase2_development/")
    sys.exit(1)

# Load preprocessed data
data_file = phase2_dir / "data" / "phishing_emails_processed.csv"

if not data_file.exists():
    print(f"\n✗ Preprocessed data file not found: {data_file}")
    print("\nRun this first: python 1_data/preprocess_data.py")
    sys.exit(1)

print(f"\nLoading preprocessed emails...")
df = pd.read_csv(data_file)
print(f"  Loaded {len(df)} emails")
print(f"  Phishing: {(df['label'] == 1).sum()}")
print(f"  Legitimate: {(df['label'] == 0).sum()}")

# Extract features from all emails
print(f"\nExtracting features from emails...")
print("  (This may take 10-20 minutes for large datasets)")

extractor = FeatureExtractor()
features_list = []
labels_list = []
failed_count = 0

for idx, row in df.iterrows():
    if (idx + 1) % 1000 == 0:
        print(f"  Processed {idx + 1}/{len(df)} emails...")

    email_text = str(row['email'])
    label = int(row['label'])

    # Create email data dict for feature extractor
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
        # Extract features
        features = extractor.extract_all_features(email_data)

        # Convert to ordered list (same order as feature names)
        feature_values = [features[name] for name in extractor.get_feature_names()]
        features_list.append(feature_values)
        labels_list.append(label)

    except Exception as e:
        failed_count += 1
        if failed_count <= 5:  # Show first 5 errors
            print(f"  ⚠ Error extracting features for email {idx}: {str(e)}")
        continue

print(f"\n  Successfully processed {len(features_list)} emails")
if failed_count > 0:
    print(f"  Failed to process {failed_count} emails")

# Convert to numpy arrays
X = np.array(features_list)
y = np.array(labels_list)

print(f"\nDataset shape:")
print(f"  Samples: {X.shape[0]}")
print(f"  Features: {X.shape[1]}")
print(f"  Phishing labels: {(y == 1).sum()}")
print(f"  Legitimate labels: {(y == 0).sum()}")

# Check if we have enough data
if len(X) < 50:
    print("\n✗ Not enough samples for training (need at least 50)")
    sys.exit(1)

# Train model
print(f"\nTraining Random Forest model...")
model = PhishingDetectionModel(model_type='random_forest')
metrics = model.train(X, y, test_size=0.2)

# Save model
models_dir = phase2_dir / "4_models"
models_dir.mkdir(exist_ok=True)

model_path = models_dir / "phishing_model_phase2.pkl"
scaler_path = models_dir / "scaler_phase2.pkl"

print(f"\nSaving trained model...")
model.save_model(str(model_path), str(scaler_path))

# Show feature importance
print(f"\nTop 10 Important Features:")
print("="*50)
model.print_feature_importance(top_n=10)

print("\n" + "="*70)
print("✓ MODEL TRAINING COMPLETE")
print("="*70)
print(f"Model saved: {model_path.name}")
print(f"Scaler saved: {scaler_path.name}")
print("\nModel Performance:")
print(f"  Accuracy:  {metrics['accuracy']:.2%}")
print(f"  Precision: {metrics['precision']:.2%}")
print(f"  Recall:    {metrics['recall']:.2%}")
print(f"  F1-Score:  {metrics['f1']:.2%}")
print(f"  ROC-AUC:   {metrics['roc_auc']:.2%}")
print("="*70)

print("\nNext steps:")
print("1. python 2_training/evaluate_model.py - Evaluate on test set")
print("2. python 3_testing/test_phishing_detection.py - Test phishing detection")
print("3. python 3_testing/test_legitimate_detection.py - Test legitimate detection")
print("="*70 + "\n")
