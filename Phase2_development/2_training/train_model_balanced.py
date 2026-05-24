"""
IMPROVED TRAINING SCRIPT - Phase 2
Trains Random Forest model on real Kaggle data WITH class imbalance handling
Fixes false positive issue on legitimate emails
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

def train_balanced_model():
    """Train model with balanced class weights to reduce false positives"""

    print("\n" + "="*70)
    print("PHASE 2: BALANCED MODEL TRAINING")
    print("Training Random Forest with Class Imbalance Handling")
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
    print(f"  - Phishing emails: {phishing_count:,}")
    print(f"  - Legitimate emails: {legit_count:,}")
    print(f"  - Imbalance ratio: {phishing_count/legit_count:.2f}:1")

    # Extract features
    print("\nExtracting features from all emails...")
    extractor = FeatureExtractor()

    features_list = []
    labels_list = []

    total = len(df)
    for idx, row in df.iterrows():
        if (idx + 1) % 5000 == 0:
            print(f"  Processed {idx + 1}/{total} emails...")

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
            # Skip problematic emails
            continue

    print(f"✓ Successfully extracted features from {len(features_list)} emails")

    # Convert to numpy arrays
    feature_names = list(features_list[0].keys())
    X = np.array([list(f.values()) for f in features_list])
    y = np.array(labels_list)

    print(f"\nFeature Matrix Shape: {X.shape}")
    print(f"Number of Features: {X.shape[1]}")
    print(f"Sample Count: {X.shape[0]}")

    # ========================================
    # KEY FIX: Create model with class_weight='balanced'
    # ========================================
    print("\n" + "="*70)
    print("CREATING BALANCED MODEL")
    print("="*70)

    model = PhishingDetectionModel(model_type='random_forest')

    # MODIFY the underlying sklearn model to use class weights
    from sklearn.ensemble import RandomForestClassifier
    model.model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'  # ← KEY FIX: Handle class imbalance
    )

    print("✓ Random Forest configured with class_weight='balanced'")
    print("  This penalizes misclassification of the minority class (legitimate)")
    print("  and reduces bias toward the majority class (phishing)")

    # Train model
    print("\nTraining balanced model...")
    metrics = model.train(X, y, test_size=0.2)

    # Save model
    print("\n" + "="*70)
    print("SAVING TRAINED MODEL")
    print("="*70)

    model_path = str(models_dir / 'phishing_model_phase2_balanced.pkl')
    scaler_path = str(models_dir / 'scaler_phase2_balanced.pkl')

    model.save_model(model_path, scaler_path)

    # Also create a backup comparison
    print("\nCreating comparison summary...")

    summary = f"""
PHASE 2 - BALANCED MODEL TRAINING SUMMARY
{'='*70}

TRAINING CONFIGURATION:
- Algorithm: Random Forest Classifier
- Estimators: 100
- Max Depth: 15
- Class Weight: BALANCED (new)
- Test Size: 20%
- Cross-Validation: 5-fold

DATA STATISTICS:
- Total Emails Processed: {len(df):,}
- Successfully Extracted: {X.shape[0]:,}
- Features per Email: {X.shape[1]}

CLASS DISTRIBUTION:
- Phishing Emails: {phishing_count:,} ({phishing_count/len(df)*100:.1f}%)
- Legitimate Emails: {legit_count:,} ({legit_count/len(df)*100:.1f}%)
- Imbalance Ratio: {phishing_count/legit_count:.2f}:1

MODEL PERFORMANCE:
- Accuracy:  {metrics['accuracy']:.2%}
- Precision: {metrics['precision']:.2%}
- Recall:    {metrics['recall']:.2%}
- F1-Score:  {metrics['f1']:.2%}
- ROC-AUC:   {metrics['roc_auc']:.2%}

KEY IMPROVEMENT:
The balanced model should reduce false positives on legitimate emails
by penalizing misclassification of the minority (legitimate) class.

OUTPUT FILES:
- Model: {model_path}
- Scaler: {scaler_path}

STATUS: ✓ Ready for Testing
{'='*70}
"""

    summary_path = Path(__file__).parent.parent / '5_results' / 'phase2_balanced_training_summary.txt'
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, 'w') as f:
        f.write(summary)

    print(f"✓ Summary saved to {summary_path}")

    print("\n" + "="*70)
    print("TRAINING COMPLETE")
    print("="*70)
    print("\nNext Steps:")
    print("1. Run: python 3_testing/test_phishing_detection_balanced.py")
    print("2. Run: python 3_testing/test_legitimate_detection_balanced.py")
    print("3. Verify both phishing and legitimate detection work correctly")

    return model, metrics

if __name__ == "__main__":
    try:
        model, metrics = train_balanced_model()
        print("\n✓ Balanced model training completed successfully!")
    except Exception as e:
        print(f"\n✗ Error during training: {e}")
        import traceback
        traceback.print_exc()
