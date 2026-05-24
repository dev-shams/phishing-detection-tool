"""
ORIGINAL TRAINING SCRIPT - Phase 2
Restores original training WITHOUT class weights (86% accuracy)
Will use post-hoc threshold adjustment for better legitimate detection
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from feature_extractor import FeatureExtractor
from ml_model import PhishingDetectionModel

def train_original_model():
    """Train original model with stable hyperparameters"""

    print("\n" + "="*70)
    print("PHASE 2: ORIGINAL MODEL TRAINING")
    print("Training Random Forest with original hyperparameters")
    print("="*70)

    # Paths
    data_path = Path(__file__).parent.parent / 'data' / 'phishing_emails_processed.csv'
    models_dir = Path(__file__).parent.parent / '4_models'
    models_dir.mkdir(parents=True, exist_ok=True)

    # Load preprocessed data
    print("\nLoading preprocessed data...")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} emails")

    # Class distribution
    print("\nClass Distribution:")
    phishing_count = (df['label'] == 1).sum()
    legit_count = (df['label'] == 0).sum()
    total = len(df)
    print(f"  - Phishing emails: {phishing_count:,} ({phishing_count/total*100:.1f}%)")
    print(f"  - Legitimate emails: {legit_count:,} ({legit_count/total*100:.1f}%)")

    # Extract features
    print("\nExtracting features from all emails...")
    extractor = FeatureExtractor()

    features_list = []
    labels_list = []

    total_emails = len(df)
    for idx, row in df.iterrows():
        if (idx + 1) % 5000 == 0:
            print(f"  Processed {idx + 1}/{total_emails} emails...")

        email_data = {
            'body': str(row.get('email_text', '')),
            'subject': str(row.get('subject', '')),
            'sender': str(row.get('sender', '')),
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

    # Train with ORIGINAL settings (no class weights)
    print("\n" + "="*70)
    print("TRAINING ORIGINAL MODEL")
    print("="*70)

    model = PhishingDetectionModel(model_type='random_forest')
    print("✓ Random Forest initialized with original hyperparameters")
    print("  No class weights - standard training")

    # Train
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
PHASE 2 - ORIGINAL MODEL TRAINING SUMMARY
{'='*70}

TRAINING CONFIGURATION:
- Algorithm: Random Forest Classifier (Original Settings)
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

APPROACH:
This is the original, stable training configuration. The model achieved
{metrics['accuracy']:.0%} accuracy during training.

For handling false positives on legitimate emails, we will use a
post-hoc DECISION THRESHOLD ADJUSTMENT rather than modifying training,
which preserves the model's learned probability distributions.

OUTPUT FILES:
- Model: {model_path}
- Scaler: {scaler_path}

STATUS: ✓ Ready for Testing & Threshold Tuning
{'='*70}
"""

    summary_path = Path(__file__).parent.parent / '5_results' / 'phase2_original_training_summary.txt'
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, 'w') as f:
        f.write(summary)

    print(f"✓ Summary saved to {summary_path}")

    print("\n" + "="*70)
    print("TRAINING COMPLETE")
    print("="*70)
    print("\nNext: Test with decision threshold adjustment")
    print("Run: python 3_testing/test_with_threshold_tuning.py")

    return model, metrics

if __name__ == "__main__":
    try:
        model, metrics = train_original_model()
        print("\n✓ Original model training completed successfully!")
    except Exception as e:
        print(f"\n✗ Error during training: {e}")
        import traceback
        traceback.print_exc()
