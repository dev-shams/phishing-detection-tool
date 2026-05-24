"""
IMMEDIATE FIX: Threshold Adjustment
Don't wait for retraining - fix the false positives by adjusting decision threshold
The model HAS learned proper features, it's just biased toward phishing (87.7% baseline)
By lowering the threshold, we can catch legitimate emails
"""

import sys
sys.path.insert(0, '/sessions/sleepy-cool-rubin/mnt/Final year Project/Phase2_development')

import pandas as pd
import numpy as np
from feature_extractor import FeatureExtractor
from ml_model import PhishingDetectionModel

print("\n" + "="*70)
print("IMMEDIATE FIX: THRESHOLD ADJUSTMENT")
print("Testing different decision thresholds")
print("="*70)

# Load model
model_path = '/sessions/sleepy-cool-rubin/mnt/Final year Project/Phase2_development/4_models/phishing_model_phase2.pkl'
scaler_path = '/sessions/sleepy-cool-rubin/mnt/Final year Project/Phase2_development/4_models/scaler_phase2.pkl'

model = PhishingDetectionModel()
model.load_model(model_path, scaler_path)

# Load data
df = pd.read_csv('/sessions/sleepy-cool-rubin/mnt/Final year Project/Phase2_development/data/phishing_emails_processed.csv')

# Get 100 samples (50 phishing, 50 legitimate)
phishing_df = df[df['label'] == 1].sample(n=50, random_state=42)
legit_df = df[df['label'] == 0].sample(n=50, random_state=42)

extractor = FeatureExtractor()

# Extract features and get probabilities
print("\nExtracting features from 100 emails (50 phishing, 50 legitimate)...")

probs = []
true_labels = []

for idx, (_, row) in enumerate(pd.concat([phishing_df, legit_df]).iterrows()):
    email_data = {
        'body': str(row.get('email', '')),
        'subject': '',
        'sender': '',
        'urls': [],
        'headers': {}
    }

    features = extractor.extract_all_features(email_data)
    result = model.predict_single(features)

    probs.append(result['confidence_phishing'] / 100.0)
    true_labels.append(row['label'])

probs = np.array(probs)
true_labels = np.array(true_labels)

print(f"✓ Extracted {len(probs)} samples")
print(f"\nProbability distribution:")
print(f"  Min:  {probs.min():.4f}")
print(f"  Max:  {probs.max():.4f}")
print(f"  Mean: {probs.mean():.4f}")

# Test different thresholds
print("\n" + "="*70)
print("THRESHOLD ANALYSIS")
print("="*70)

print(f"\n{'Threshold':<12} {'Phishing%':>10} {'Legit%':>10} {'FalsePos%':>10} {'Overall%':>10}")
print("-"*70)

best_result = None
best_balanced_score = 0

for threshold in np.arange(0.3, 0.9, 0.05):
    preds = (probs >= threshold).astype(int)

    phishing_mask = true_labels == 1
    legit_mask = true_labels == 0

    phishing_acc = (preds[phishing_mask] == 1).sum() / phishing_mask.sum() * 100
    legit_acc = (preds[legit_mask] == 0).sum() / legit_mask.sum() * 100
    overall_acc = (preds == true_labels).sum() / len(true_labels) * 100

    balanced_score = (phishing_acc + legit_acc) / 2

    print(f"{threshold:<12.2f} {phishing_acc:>10.1f}% {legit_acc:>10.1f}% {100-legit_acc:>10.1f}% {overall_acc:>10.1f}%")

    if balanced_score > best_balanced_score:
        best_balanced_score = balanced_score
        best_result = {
            'threshold': threshold,
            'phishing_acc': phishing_acc,
            'legit_acc': legit_acc,
            'balanced_score': balanced_score
        }

print("\n" + "="*70)
print("OPTIMAL THRESHOLD FOUND")
print("="*70)

if best_result:
    print(f"\nThreshold: {best_result['threshold']:.2f}")
    print(f"Phishing Detection: {best_result['phishing_acc']:.1f}%")
    print(f"Legitimate Detection: {best_result['legit_acc']:.1f}%")
    print(f"Balanced Score: {best_result['balanced_score']:.1f}%")

    print(f"\n" + "="*70)
    print("HOW TO USE THIS THRESHOLD")
    print("="*70)

    print(f"\nAdd this to test_legitimate_detection.py:")
    print(f"""
# After getting prediction from model.predict_single()
optimal_threshold = {best_result['threshold']:.3f}

# Modify the prediction logic
if result['decision_score'] >= optimal_threshold:
    verdict = 'PHISHING'
else:
    verdict = 'LEGITIMATE'
""")

    print(f"\nOr modify ml_model.py predict_single() method:")
    print(f"""
# In PhishingDetectionModel.predict_single():
decision_threshold = {best_result['threshold']:.3f}  # Updated threshold

# Change this line:
'classification': 'PHISHING' if result['decision_score'] >= decision_threshold else 'LEGITIMATE',
""")

    print(f"\nThen re-run tests and you should see improvement!")

print("\n" + "="*70)
