"""
Debug Probability Distribution
Analyze what probability scores the model is actually producing
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from feature_extractor import FeatureExtractor
from ml_model import PhishingDetectionModel

print("\n" + "="*70)
print("PROBABILITY DISTRIBUTION ANALYSIS")
print("="*70)

# Load data
data_path = Path(__file__).parent / 'data' / 'phishing_emails_processed.csv'
df = pd.read_csv(data_path)

# Load model
model_path = Path(__file__).parent / '4_models' / 'phishing_model_phase2.pkl'
scaler_path = Path(__file__).parent / '4_models' / 'scaler_phase2.pkl'

print(f"\nLoading model from {model_path}...")
model = PhishingDetectionModel()
model.load_model(str(model_path), str(scaler_path))

# Test on a sample
extractor = FeatureExtractor()

print("\nExtracting features from 50 sample emails...")
probabilities_phishing = []
probabilities_legitimate = []
emails_tested = 0

for idx, (_, row) in enumerate(df.sample(n=50, random_state=42).iterrows()):
    email_data = {
        'body': str(row.get('email_text', '')),
        'subject': str(row.get('subject', '')),
        'sender': str(row.get('sender', '')),
        'urls': [],
        'headers': {}
    }

    features = extractor.extract_all_features(email_data)
    result = model.predict_single(features)

    probabilities_phishing.append(result['confidence_phishing'] / 100.0)
    probabilities_legitimate.append(result['confidence_legitimate'] / 100.0)
    emails_tested += 1

print(f"✓ Extracted features from {emails_tested} emails")

probabilities_phishing = np.array(probabilities_phishing)
probabilities_legitimate = np.array(probabilities_legitimate)

print("\n" + "="*70)
print("PROBABILITY STATISTICS")
print("="*70)

print(f"\nPhishing Probabilities:")
print(f"  Min:    {probabilities_phishing.min():.6f}")
print(f"  Max:    {probabilities_phishing.max():.6f}")
print(f"  Mean:   {probabilities_phishing.mean():.6f}")
print(f"  Std:    {probabilities_phishing.std():.6f}")
print(f"  Unique values: {len(np.unique(probabilities_phishing))}")

print(f"\nLegitimate Probabilities:")
print(f"  Min:    {probabilities_legitimate.min():.6f}")
print(f"  Max:    {probabilities_legitimate.max():.6f}")
print(f"  Mean:   {probabilities_legitimate.mean():.6f}")
print(f"  Std:    {probabilities_legitimate.std():.6f}")
print(f"  Unique values: {len(np.unique(probabilities_legitimate))}")

print(f"\nUnique probability pairs found:")
unique_pairs = {}
for p_phish, p_legit in zip(probabilities_phishing, probabilities_legitimate):
    key = (round(p_phish, 4), round(p_legit, 4))
    unique_pairs[key] = unique_pairs.get(key, 0) + 1

for (p_phish, p_legit), count in sorted(unique_pairs.items()):
    print(f"  Phishing: {p_phish:.4f}, Legitimate: {p_legit:.4f} (count: {count})")

print("\n" + "="*70)
print("DIAGNOSIS")
print("="*70)

if len(np.unique(probabilities_phishing)) <= 3:
    print("\n⚠ WARNING: Model is producing very few unique probability values")
    print("This suggests the model may not be properly trained or is stuck")
    print("at a specific decision boundary.")
else:
    print("\n✓ Model is producing varied probability outputs")

print("\nModel Feature Importance:")
try:
    importances = model.get_feature_importance(top_n=10)
    for name, importance in importances:
        print(f"  {name:.<40} {importance:.4f}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "="*70)
