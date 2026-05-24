"""
Test Model on Real Kaggle Data
Tests phishing detection on actual emails from the training dataset
This ensures features match training characteristics
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from feature_extractor import FeatureExtractor
from ml_model import PhishingDetectionModel

def test_on_real_data():
    """Test model on real emails from Kaggle dataset"""

    print("\n" + "="*70)
    print("TESTING ON REAL KAGGLE DATA")
    print("Testing phishing and legitimate emails from actual dataset")
    print("="*70)

    # Load data
    data_path = Path(__file__).parent.parent / 'data' / 'phishing_emails_processed.csv'
    print(f"\nLoading dataset from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} emails")

    # Load model
    model_path = Path(__file__).parent.parent / '4_models' / 'phishing_model_phase2.pkl'
    scaler_path = Path(__file__).parent.parent / '4_models' / 'scaler_phase2.pkl'

    print("\nLoading model...")
    model = PhishingDetectionModel()
    model.load_model(str(model_path), str(scaler_path))
    print("✓ Model loaded")

    # Create feature extractor
    extractor = FeatureExtractor()

    # Test on phishing emails
    print("\n" + "="*70)
    print("TEST 1: PHISHING EMAILS (from Kaggle dataset)")
    print("="*70)

    phishing_df = df[df['label'] == 1].sample(n=min(10, (df['label'] == 1).sum()), random_state=42)
    phishing_correct = 0

    for idx, (_, row) in enumerate(phishing_df.iterrows(), 1):
        email_data = {
            'body': str(row.get('email_text', '')),
            'subject': str(row.get('subject', '')),
            'sender': str(row.get('sender', '')),
            'urls': [],
            'headers': {}
        }

        features = extractor.extract_all_features(email_data)
        result = model.predict_single(features)

        is_correct = result['prediction'] == 1
        phishing_correct += is_correct

        status = "✓" if is_correct else "✗"
        print(f"\n{idx}. {status} Predicted: {'PHISHING' if result['prediction'] == 1 else 'LEGITIMATE'}")
        print(f"   Confidence: {result['confidence_phishing']:.1f}%")
        print(f"   Subject: {row.get('subject', 'N/A')[:60]}...")

    phishing_rate = phishing_correct / len(phishing_df)
    print(f"\nPhishing Detection: {phishing_correct}/{len(phishing_df)} ({phishing_rate*100:.1f}%)")

    # Test on legitimate emails
    print("\n" + "="*70)
    print("TEST 2: LEGITIMATE EMAILS (from Kaggle dataset)")
    print("="*70)

    legit_df = df[df['label'] == 0].sample(n=min(10, (df['label'] == 0).sum()), random_state=42)
    legit_correct = 0
    false_positives = 0

    for idx, (_, row) in enumerate(legit_df.iterrows(), 1):
        email_data = {
            'body': str(row.get('email_text', '')),
            'subject': str(row.get('subject', '')),
            'sender': str(row.get('sender', '')),
            'urls': [],
            'headers': {}
        }

        features = extractor.extract_all_features(email_data)
        result = model.predict_single(features)

        is_correct = result['prediction'] == 0
        legit_correct += is_correct

        if result['prediction'] == 1:
            false_positives += 1

        status = "✓" if is_correct else "✗"
        verdict = "LEGITIMATE" if result['prediction'] == 0 else "PHISHING (FALSE POSITIVE)"
        print(f"\n{idx}. {status} Predicted: {verdict}")
        print(f"   Confidence (Legit): {result['confidence_legitimate']:.1f}%")
        print(f"   Subject: {row.get('subject', 'N/A')[:60]}...")

    legit_rate = legit_correct / len(legit_df)
    fp_rate = false_positives / len(legit_df)

    print(f"\nLegitimate Detection: {legit_correct}/{len(legit_df)} ({legit_rate*100:.1f}%)")
    print(f"False Positives: {false_positives}/{len(legit_df)} ({fp_rate*100:.1f}%)")

    # Overall summary
    print("\n" + "="*70)
    print("OVERALL PERFORMANCE")
    print("="*70)
    print(f"\nPhishing Detection Rate:    {phishing_rate*100:6.1f}%  ({phishing_correct}/{len(phishing_df)})")
    print(f"Legitimate Detection Rate:  {legit_rate*100:6.1f}%  ({legit_correct}/{len(legit_df)})")
    print(f"False Positive Rate:        {fp_rate*100:6.1f}%  ({false_positives}/{len(legit_df)})")

    # Determine status
    print("\n" + "="*70)
    if phishing_rate >= 0.8 and legit_rate >= 0.8 and fp_rate <= 0.2:
        status = "✓ EXCELLENT"
    elif phishing_rate >= 0.7 and legit_rate >= 0.7 and fp_rate <= 0.3:
        status = "✓ GOOD"
    elif phishing_rate >= 0.6 and legit_rate >= 0.6:
        status = "⚠ ACCEPTABLE"
    else:
        status = "✗ NEEDS IMPROVEMENT"

    print(f"Status: {status}")
    print("="*70)

    # Save results
    results_path = Path(__file__).parent.parent / '5_results' / 'real_data_test_results.txt'
    results_path.parent.mkdir(parents=True, exist_ok=True)

    with open(results_path, 'w') as f:
        f.write("PHASE 2 - REAL DATA TEST RESULTS\n")
        f.write("="*70 + "\n\n")
        f.write(f"Phishing Detection Rate:    {phishing_rate*100:6.1f}%  ({phishing_correct}/{len(phishing_df)})\n")
        f.write(f"Legitimate Detection Rate:  {legit_rate*100:6.1f}%  ({legit_correct}/{len(legit_df)})\n")
        f.write(f"False Positive Rate:        {fp_rate*100:6.1f}%  ({false_positives}/{len(legit_df)})\n")
        f.write(f"\nStatus: {status}\n")

    print(f"\n✓ Results saved to {results_path}")

    return phishing_rate, legit_rate, fp_rate

if __name__ == "__main__":
    try:
        phishing_rate, legit_rate, fp_rate = test_on_real_data()
        print("\n✓ Testing complete!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
