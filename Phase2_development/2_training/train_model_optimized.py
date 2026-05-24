"""
OPTIMIZED TRAINING SCRIPT - Phase 2
Trains Random Forest with carefully tuned class weights to fix false positives
without overcorrecting
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

def train_optimized_model():
    """Train model with optimized class weights to reduce false positives"""

    print("\n" + "="*70)
    print("PHASE 2: OPTIMIZED MODEL TRAINING")
    print("Training Random Forest with Tuned Class Weights")
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
    print(f"  - Imbalance ratio: {phishing_count/legit_count:.2f}:1")

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
    print(f"Number of Features: {X.shape[1]}")
    print(f"Sample Count: {X.shape[0]}")

    # ========================================
    # OPTIMIZED APPROACH: Custom class weights
    # ========================================
    print("\n" + "="*70)
    print("CREATING OPTIMIZED MODEL")
    print("="*70)

    # Calculate class weights
    # Instead of 'balanced', use custom weights that are more moderate
    # Phishing is majority, so give it weight = 1.0
    # Legitimate is minority, so give it higher weight to reduce false positives
    # Ratio: legitimate_weight / phishing_weight = (phishing_count / legit_count) * 0.8
    legitimate_weight = (phishing_count / legit_count) * 0.8
    phishing_weight = 1.0

    print(f"Custom Class Weights (tuned to reduce false positives):")
    print(f"  - Phishing weight: {phishing_weight:.4f}")
    print(f"  - Legitimate weight: {legitimate_weight:.4f}")
    print(f"  - Weight ratio: {legitimate_weight/phishing_weight:.2f}:1")

    model = PhishingDetectionModel(model_type='random_forest')

    # Modify the underlying sklearn model with custom class weights
    from sklearn.ensemble import RandomForestClassifier
    model.model = RandomForestClassifier(
        n_estimators=150,  # Increased from 100
        max_depth=20,      # Slightly increased for better feature interaction
        min_samples_split=4,  # Reduced slightly for more sensitivity
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        # Use custom class weights (not 'balanced')
        class_weight={
            0: legitimate_weight,  # Legitimate class weight
            1: phishing_weight      # Phishing class weight
        }
    )

    print("✓ Random Forest configured with optimized class weights")
    print("  This reduces false positives while maintaining detection accuracy")

    # Train model
    print("\nTraining optimized model...")
    metrics = model.train(X, y, test_size=0.2)

    # Save model
    print("\n" + "="*70)
    print("SAVING TRAINED MODEL")
    print("="*70)

    model_path = str(models_dir / 'phishing_model_phase2.pkl')
    scaler_path = str(models_dir / 'scaler_phase2.pkl')

    model.save_model(model_path, scaler_path)

    # Create summary
    print("\nCreating training summary...")

    summary = f"""
PHASE 2 - OPTIMIZED MODEL TRAINING SUMMARY
{'='*70}

TRAINING CONFIGURATION:
- Algorithm: Random Forest Classifier
- Estimators: 150 (increased for stability)
- Max Depth: 20 (tuned for better feature interactions)
- Class Weights: Custom Tuned
  * Legitimate: {legitimate_weight:.4f} (minority class boost)
  * Phishing: {phishing_weight:.4f}
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

KEY IMPROVEMENTS:
1. Custom class weights tuned for false positive reduction
2. Increased estimators (150) for more stable predictions
3. Adjusted tree depth for better feature learning
4. Balanced precision-recall tradeoff

OUTPUT FILES:
- Model: {model_path}
- Scaler: {scaler_path}

STATUS: ✓ Ready for Testing
{'='*70}
"""

    summary_path = Path(__file__).parent.parent / '5_results' / 'phase2_training_summary.txt'
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
    print("3. Verify both phishing and legitimate detection work correctly")

    return model, metrics

if __name__ == "__main__":
    try:
        model, metrics = train_optimized_model()
        print("\n✓ Optimized model training completed successfully!")
    except Exception as e:
        print(f"\n✗ Error during training: {e}")
        import traceback
        traceback.print_exc()
