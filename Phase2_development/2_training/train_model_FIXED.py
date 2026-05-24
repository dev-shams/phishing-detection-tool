"""
FIXED TRAINING SCRIPT - Phase 2
Uses correct column names from preprocessed CSV
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from feature_extractor import FeatureExtractor
from ml_model import PhishingDetectionModel

def train_fixed_model():
    """Train model with CORRECTED feature extraction"""

    print("\n" + "="*70)
    print("PHASE 2: FIXED MODEL TRAINING")
    print("Using correct column names from preprocessed CSV")
    print("="*70)

    # Paths
    data_path = Path(__file__).parent.parent / 'data' / 'phishing_emails_processed.csv'
    models_dir = Path(__file__).parent.parent / '4_models'
    models_dir.mkdir(parents=True, exist_ok=True)

    # Load preprocessed data
    print("\nLoading preprocessed data...")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} emails")
    print(f"  Columns: {df.columns.tolist()}")

    # Class distribution
    print("\nClass Distribution:")
    phishing_count = (df['label'] == 1).sum()
    legit_count = (df['label'] == 0).sum()
    total = len(df)
    print(f"  - Phishing emails: {phishing_count:,} ({phishing_count/total*100:.1f}%)")
    print(f"  - Legitimate emails: {legit_count:,} ({legit_count/total*100:.1f}%)")

    # Extract features
    print("\nExtracting features from all emails...")
    print("⚠ Using correct column name: 'email' (not 'email_text')")

    extractor = FeatureExtractor()

    features_list = []
    labels_list = []

    total_emails = len(df)
    for idx, row in df.iterrows():
        if (idx + 1) % 5000 == 0:
            print(f"  Processed {idx + 1}/{total_emails} emails...")

        # FIX: Use 'email' column instead of 'email_text'
        email_data = {
            'body': str(row.get('email', '')),
            'subject': '',  # Not available in CSV
            'sender': '',   # Not available in CSV
            'urls': [],
            'headers': {}
        }

        try:
            features = extractor.extract_all_features(email_data)
            features_list.append(features)
            labels_list.append(row['label'])
        except Exception as e:
            continue

    print(f"✓ Successfully extracted features from {len(features_list)} emails")

    # Convert to numpy arrays
    feature_names = list(features_list[0].keys())
    X = np.array([list(f.values()) for f in features_list])
    y = np.array(labels_list)

    print(f"\nFeature Matrix Shape: {X.shape}")
    print(f"Number of Features: {X.shape[1]}")
    print(f"Sample Count: {X.shape[0]}")

    # Verify features vary
    print(f"\nFeature Variance Check:")
    feature_vars = X.var(axis=0)
    non_zero_var = (feature_vars > 0).sum()
    print(f"  Features with variance: {non_zero_var}/{len(feature_names)}")
    print(f"  Features with zero variance: {len(feature_names) - non_zero_var}")

    if non_zero_var == 0:
        print("\n✗ ERROR: No features have variance! Feature extraction failed.")
        print("Aborting training.")
        return None, None

    # Train model
    print("\n" + "="*70)
    print("TRAINING MODEL")
    print("="*70)

    model = PhishingDetectionModel(model_type='random_forest')
    print("✓ Random Forest initialized")

    print("\nTraining model...")
    metrics = model.train(X, y, test_size=0.2)

    # Save model
    print("\n" + "="*70)
    print("SAVING TRAINED MODEL")
    print("="*70)

    model_path = str(models_dir / 'phishing_model_phase2.pkl')
    scaler_path = str(models_dir / 'scaler_phase2.pkl')

    model.save_model(model_path, scaler_path)

    # Create summary
    summary = f"""
PHASE 2 - FIXED MODEL TRAINING SUMMARY
{'='*70}

BUG FIX:
The previous training was using incorrect column name 'email_text'
instead of 'email', causing all features to be zero/identical.
This version uses the correct column name.

TRAINING CONFIGURATION:
- Algorithm: Random Forest Classifier
- Estimators: 100
- Max Depth: 15
- Min Samples Split: 5
- Min Samples Leaf: 2
- Class Weights: None (standard training)
- Random State: 42
- Test Size: 20%
- Cross-Validation: 5-fold

DATA STATISTICS:
- Total Emails: {len(df):,}
- Successfully Extracted: {X.shape[0]:,}
- Features per Email: {X.shape[1]}
- Features with variance: {non_zero_var}/{len(feature_names)}

CLASS DISTRIBUTION:
- Phishing Emails: {phishing_count:,} ({phishing_count/total*100:.1f}%)
- Legitimate Emails: {legit_count:,} ({legit_count/total*100:.1f}%)
- Imbalance Ratio: {phishing_count/legit_count:.2f}:1

MODEL PERFORMANCE:
- Accuracy:  {metrics['accuracy']:.2%}
- Precision: {metrics['precision']:.2%}
- Recall:    {metrics['recall']:.2%}
- F1-Score:  {metrics['f1']:.2%}
- ROC-AUC:   {metrics['roc_auc']:.2%}

OUTPUT FILES:
- Model: {model_path}
- Scaler: {scaler_path}

STATUS: ✓ Ready for Testing
{'='*70}
"""

    summary_path = Path(__file__).parent.parent / '5_results' / 'phase2_fixed_training_summary.txt'
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, 'w') as f:
        f.write(summary)

    print(f"✓ Summary saved to {summary_path}")

    print("\n" + "="*70)
    print("TRAINING COMPLETE")
    print("="*70)
    print("\nNext Steps:")
    print("1. Run: python 3_testing/test_phishing_detection.py")
    print("2. Run: python 3_testing/test_legitimate_detection.py")
    print("3. Verify detection works correctly")

    return model, metrics

if __name__ == "__main__":
    try:
        model, metrics = train_fixed_model()
        if model:
            print("\n✓ Fixed model training completed successfully!")
        else:
            print("\n✗ Training failed")
    except Exception as e:
        print(f"\n✗ Error during training: {e}")
        import traceback
        traceback.print_exc()
