"""
Test with Threshold Optimization
Automatically find the best decision threshold to balance
phishing detection and legitimate email accuracy
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from feature_extractor import FeatureExtractor
from ml_model import PhishingDetectionModel

def test_with_threshold_optimization():
    """Find optimal threshold for balanced detection"""

    print("\n" + "="*70)
    print("THRESHOLD OPTIMIZATION")
    print("Finding optimal decision threshold for model predictions")
    print("="*70)

    # Load data
    data_path = Path(__file__).parent.parent / 'data' / 'phishing_emails_processed.csv'
    print(f"\nLoading dataset...")
    df = pd.read_csv(data_path)

    # Load model
    model_path = Path(__file__).parent.parent / '4_models' / 'phishing_model_phase2.pkl'
    scaler_path = Path(__file__).parent.parent / '4_models' / 'scaler_phase2.pkl'

    print("Loading model...")
    model = PhishingDetectionModel()
    model.load_model(str(model_path), str(scaler_path))

    # Create feature extractor
    extractor = FeatureExtractor()

    # Get validation set (use a larger sample for threshold optimization)
    print("\nExtracting features for validation set (500 emails)...")

    # Sample 250 phishing and 250 legitimate
    phishing_df = df[df['label'] == 1].sample(n=min(250, (df['label'] == 1).sum()), random_state=42)
    legit_df = df[df['label'] == 0].sample(n=min(250, (df['label'] == 0).sum()), random_state=42)

    val_df = pd.concat([phishing_df, legit_df])

    probabilities = []
    true_labels = []

    for idx, (_, row) in enumerate(val_df.iterrows()):
        if (idx + 1) % 50 == 0:
            print(f"  Processed {idx + 1}/{len(val_df)} emails...")

        email_data = {
            'body': str(row.get('email_text', '')),
            'subject': str(row.get('subject', '')),
            'sender': str(row.get('sender', '')),
            'urls': [],
            'headers': {}
        }

        features = extractor.extract_all_features(email_data)
        result = model.predict_single(features)

        probabilities.append(result['decision_score'])
        true_labels.append(row['label'])

    probabilities = np.array(probabilities)
    true_labels = np.array(true_labels)

    print(f"✓ Extracted features from {len(probabilities)} validation emails")

    # Test different thresholds
    print("\n" + "="*70)
    print("THRESHOLD ANALYSIS")
    print("="*70)

    thresholds = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    results = []

    print("\nTesting thresholds:")
    print(f"{'Threshold':<12} {'Phishing':>12} {'Legitimate':>12} {'Overall':>12}")
    print("-"*70)

    for threshold in thresholds:
        predictions = (probabilities >= threshold).astype(int)

        # Calculate accuracies
        phishing_acc = np.mean(predictions[true_labels == 1] == 1)
        legit_acc = np.mean(predictions[true_labels == 0] == 0)
        overall_acc = np.mean(predictions == true_labels)

        results.append({
            'threshold': threshold,
            'phishing_acc': phishing_acc,
            'legit_acc': legit_acc,
            'overall_acc': overall_acc,
            'balanced_score': (phishing_acc + legit_acc) / 2
        })

        print(f"{threshold:<12.1f} {phishing_acc:>11.1%} {legit_acc:>12.1%} {overall_acc:>12.1%}")

    # Find best threshold (balanced score)
    best_result = max(results, key=lambda x: x['balanced_score'])

    print("\n" + "="*70)
    print("OPTIMAL THRESHOLD")
    print("="*70)
    print(f"\nThreshold: {best_result['threshold']:.1f}")
    print(f"Phishing Detection: {best_result['phishing_acc']*100:.1f}%")
    print(f"Legitimate Detection: {best_result['legit_acc']*100:.1f}%")
    print(f"Overall Accuracy: {best_result['overall_acc']*100:.1f}%")
    print(f"Balanced Score: {best_result['balanced_score']*100:.1f}%")

    # Test final model with best threshold
    print("\n" + "="*70)
    print("FINAL PERFORMANCE (with optimized threshold)")
    print("="*70)

    final_predictions = (probabilities >= best_result['threshold']).astype(int)

    phishing_mask = true_labels == 1
    legit_mask = true_labels == 0

    phishing_correct = np.sum(final_predictions[phishing_mask] == 1)
    legit_correct = np.sum(final_predictions[legit_mask] == 0)
    false_positives = np.sum(final_predictions[legit_mask] == 1)

    print(f"\nPhishing Detection: {phishing_correct}/{np.sum(phishing_mask)} ({np.sum(phishing_mask & (final_predictions == 1))/np.sum(phishing_mask)*100:.1f}%)")
    print(f"Legitimate Detection: {legit_correct}/{np.sum(legit_mask)} ({legit_correct/np.sum(legit_mask)*100:.1f}%)")
    print(f"False Positives: {false_positives}/{np.sum(legit_mask)} ({false_positives/np.sum(legit_mask)*100:.1f}%)")

    # Save optimal threshold
    config_path = Path(__file__).parent.parent / '4_models' / 'optimal_threshold.txt'
    with open(config_path, 'w') as f:
        f.write(f"OPTIMAL DECISION THRESHOLD\n")
        f.write(f"{'='*40}\n\n")
        f.write(f"Threshold: {best_result['threshold']:.2f}\n\n")
        f.write(f"Performance:\n")
        f.write(f"  Phishing Detection: {best_result['phishing_acc']*100:.1f}%\n")
        f.write(f"  Legitimate Detection: {best_result['legit_acc']*100:.1f}%\n")
        f.write(f"  Overall Accuracy: {best_result['overall_acc']*100:.1f}%\n")

    print(f"\n✓ Optimal threshold saved to {config_path}")

    return best_result

if __name__ == "__main__":
    try:
        result = test_with_threshold_optimization()
        print("\n✓ Threshold optimization complete!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
