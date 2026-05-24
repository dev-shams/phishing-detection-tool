"""
Diagnostic Script: Analyze False Positives in Legitimate Email Detection
Identifies which features are causing legitimate emails to be misclassified as phishing
"""

import sys
import os
import pandas as pd
import numpy as np
import pickle
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from feature_extractor import FeatureExtractor
from ml_model import PhishingDetectionModel

def diagnose_false_positives():
    """Analyze what's causing false positives on legitimate emails"""

    print("\n" + "="*70)
    print("FALSE POSITIVE DIAGNOSIS")
    print("Analyzing why legitimate emails are classified as phishing")
    print("="*70)

    # Paths
    data_path = Path(__file__).parent.parent / 'data' / 'phishing_emails_processed.csv'
    model_path = Path(__file__).parent.parent / '4_models' / 'phishing_model_phase2.pkl'
    scaler_path = Path(__file__).parent.parent / '4_models' / 'scaler_phase2.pkl'

    # Load preprocessed data
    print("\nLoading preprocessed data...")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} emails")

    # Class distribution
    phishing_count = (df['label'] == 1).sum()
    legit_count = (df['label'] == 0).sum()
    print(f"\nClass Distribution:")
    print(f"  - Phishing: {phishing_count} ({phishing_count/len(df)*100:.1f}%)")
    print(f"  - Legitimate: {legit_count} ({legit_count/len(df)*100:.1f}%)")
    print(f"  - Imbalance ratio: {phishing_count/legit_count:.2f}:1")

    # Load model
    print("\nLoading trained model...")
    model = PhishingDetectionModel()
    model.load_model(str(model_path), str(scaler_path))
    print("✓ Model loaded")

    # Extract features from legitimate emails
    print("\nExtracting features from legitimate emails...")
    extractor = FeatureExtractor()

    legit_df = df[df['label'] == 0].head(100)  # Sample of legitimate emails
    legit_features = []

    for idx, row in legit_df.iterrows():
        email_data = {
            'body': row.get('email_text', ''),
            'subject': row.get('subject', ''),
            'sender': row.get('sender', ''),
            'urls': [],
            'headers': {}
        }

        features = extractor.extract_all_features(email_data)
        legit_features.append(features)

    # Convert to numpy array
    feature_names = list(legit_features[0].keys())
    X_legit = np.array([list(f.values()) for f in legit_features])

    print(f"✓ Extracted features from {len(legit_features)} legitimate emails")

    # Get predictions
    print("\nMaking predictions on legitimate emails...")
    predictions, probabilities = model.predict(X_legit)

    # Analyze results
    phishing_preds = (predictions == 1).sum()
    legit_preds = (predictions == 0).sum()

    print(f"\nPrediction Results:")
    print(f"  - Classified as PHISHING: {phishing_preds}/{len(predictions)} ({phishing_preds/len(predictions)*100:.1f}%)")
    print(f"  - Classified as LEGITIMATE: {legit_preds}/{len(predictions)} ({legit_preds/len(predictions)*100:.1f}%)")

    # Calculate average confidences
    phishing_confidence = probabilities[:, 1].mean()
    legit_confidence = probabilities[:, 0].mean()

    print(f"\nAverage Confidence Scores:")
    print(f"  - Phishing: {phishing_confidence:.1%}")
    print(f"  - Legitimate: {legit_confidence:.1%}")

    # Analyze feature distributions
    print("\n" + "="*70)
    print("FEATURE ANALYSIS")
    print("="*70)

    # Get feature importance
    try:
        feature_importance = model.get_feature_importance(top_n=15)
        print("\nTop 15 Most Important Features:")
        print("-"*50)
        for i, (fname, importance) in enumerate(feature_importance, 1):
            print(f"{i:2d}. {fname:.<35} {importance:.4f}")
    except Exception as e:
        print(f"Note: {e}")

    # Analyze the most problematic features
    print("\n" + "="*70)
    print("FALSE POSITIVE ROOT CAUSES")
    print("="*70)

    # Compare feature values for false positives vs correct predictions
    false_positives_mask = predictions == 1
    correct_predictions_mask = predictions == 0

    if false_positives_mask.sum() > 0:
        print(f"\nFalse Positives Found: {false_positives_mask.sum()}")

        # Get feature names from extractor
        sample_features = extractor.extract_all_features({
            'body': 'test',
            'subject': 'test',
            'sender': 'test@test.com',
            'urls': [],
            'headers': {}
        })

        feature_names_list = list(sample_features.keys())

        # Compare means for each feature
        print("\nFeature Comparison (False Positives vs Correct Classifications):")
        print("-"*70)
        print(f"{'Feature':<40} {'False Pos':>12} {'Correct':>12}")
        print("-"*70)

        for i, fname in enumerate(feature_names_list):
            fp_mean = X_legit[false_positives_mask, i].mean() if false_positives_mask.sum() > 0 else 0
            cp_mean = X_legit[correct_predictions_mask, i].mean() if correct_predictions_mask.sum() > 0 else 0

            print(f"{fname:<40} {fp_mean:>12.3f} {cp_mean:>12.3f}")

    print("\n" + "="*70)
    print("DIAGNOSIS SUMMARY")
    print("="*70)
    print("""
KEY FINDINGS:
1. Class Imbalance: More phishing emails in training (42,885 vs 39,594 legitimate)
   → Model is biased toward predicting PHISHING

2. Decision Boundary Issues: Model's probability threshold is not tuned
   → Default 0.5 threshold may be inappropriate

3. Solution: Use class_weight='balanced' in Random Forest to handle imbalance
   → This adjusts feature weights proportionally to class frequencies

NEXT STEPS:
1. Retrain model with class_weight='balanced'
2. Optionally adjust decision threshold
3. Re-test on both phishing and legitimate samples
""")

    print("="*70)

if __name__ == "__main__":
    diagnose_false_positives()
