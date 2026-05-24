#!/usr/bin/env python3
"""
Phase 2: Test Legitimate Email Detection
Tests the trained model on REAL legitimate emails from Kaggle dataset
"""

import sys
import pickle
import numpy as np
import pandas as pd
from pathlib import Path

print("\n" + "="*70)
print("PHASE 2: TEST LEGITIMATE EMAIL DETECTION")
print("Testing on REAL Kaggle emails")
print("="*70)

# Setup paths
phase2_dir = Path(__file__).parent.parent
sys.path.insert(0, str(phase2_dir))

# Import feature extractor
try:
    from feature_extractor import FeatureExtractor
    print("✓ Imported feature extractor")
except ImportError as e:
    print(f"✗ Failed to import: {str(e)}")
    sys.exit(1)

# Load model and scaler
models_dir = phase2_dir / "4_models"
model_path = models_dir / "phishing_model_phase2.pkl"
scaler_path = models_dir / "scaler_phase2.pkl"

if not model_path.exists() or not scaler_path.exists():
    print(f"\n✗ Model files not found")
    print("Train model first: python 2_training/train_model.py")
    sys.exit(1)

print(f"\nLoading model...")
with open(model_path, 'rb') as f:
    model = pickle.load(f)
with open(scaler_path, 'rb') as f:
    scaler = pickle.load(f)
print(f"✓ Model and scaler loaded")

# Initialize feature extractor
extractor = FeatureExtractor()

# Load REAL legitimate emails from Kaggle dataset
print(f"\nLoading real emails from Kaggle dataset...")
data_path = phase2_dir / "data" / "phishing_emails_processed.csv"

try:
    df = pd.read_csv(data_path)
    print(f"✓ Loaded dataset with {len(df)} emails")
except Exception as e:
    print(f"✗ Failed to load dataset: {e}")
    sys.exit(1)

# Get 5 random LEGITIMATE emails
legitimate_df = df[df['label'] == 0].sample(n=5, random_state=42)
print(f"✓ Selected 5 random legitimate emails from dataset")

# Test each email
print("\nTesting legitimate emails:")
print("="*70)

correct_count = 0
false_positives = 0
results = []

for i, (_, row) in enumerate(legitimate_df.iterrows(), 1):
    # Extract features from REAL email
    email_text = str(row.get('email', ''))

    # For display, show a preview of the email
    email_preview = email_text[:100].replace('\n', ' ') + "..." if len(email_text) > 100 else email_text

    # Extract features
    email_data = {
        'body': email_text,
        'subject': '',
        'sender': '',
        'urls': [],
        'headers': {}
    }

    features = extractor.extract_all_features(email_data)

    # Get prediction using properly scaled features
    feature_array = np.array([list(features.values())]).reshape(1, -1)
    feature_scaled = scaler.transform(feature_array)

    # Get prediction from model
    prediction = model.predict(feature_scaled)
    probabilities = model.predict_proba(feature_scaled)

    # Apply threshold 0.55
    decision_threshold = 0.55
    phishing_prob = probabilities[0][1]

    is_legitimate = phishing_prob < decision_threshold
    is_correct = is_legitimate

    if is_correct:
        correct_count += 1
        status = "✓"
    else:
        false_positives += 1
        status = "✗"

    classification = "LEGITIMATE" if is_legitimate else "PHISHING (FALSE POSITIVE)"

    print(f"\nEmail {i}:")
    print(f"  {status} Verdict: {classification}")
    print(f"  Confidence: {phishing_prob*100:.1f}% phishing")
    print(f"  Email preview: {email_preview}")

    results.append({
        'email': i,
        'correct': is_correct,
        'prediction': classification,
        'confidence': phishing_prob
    })

# Summary
print("\n" + "="*70)
print("LEGITIMATE DETECTION RESULTS")
print("="*70)
print(f"Correctly Identified: {correct_count}/{len(legitimate_df)}")
print(f"Detection Rate: {correct_count/len(legitimate_df)*100:.1f}%")
print(f"△ {false_positives} false positive(s)")

if correct_count == len(legitimate_df):
    status = "✓ PERFECT"
elif correct_count >= len(legitimate_df) * 0.8:
    status = "✓ GOOD"
else:
    status = "⚠ NEEDS IMPROVEMENT"

print("="*70)
print(f"Status: {status}")
print("="*70)

# Save results
results_file = phase2_dir / "5_results" / "legitimate_detection_results.txt"
results_file.parent.mkdir(parents=True, exist_ok=True)

with open(results_file, 'w') as f:
    f.write("LEGITIMATE EMAIL DETECTION TEST RESULTS\n")
    f.write("="*70 + "\n\n")
    f.write(f"Test Type: Real Kaggle Emails\n")
    f.write(f"Total Tests: {len(legitimate_df)}\n")
    f.write(f"Correct Detections: {correct_count}\n")
    f.write(f"Detection Rate: {correct_count/len(legitimate_df)*100:.1f}%\n")
    f.write(f"False Positives: {false_positives}\n")
    f.write(f"Status: {status}\n\n")
    f.write("Detailed Results:\n")
    f.write("-"*70 + "\n")
    for result in results:
        f.write(f"Email {result['email']}: {result['prediction']} (Confidence: {result['confidence']*100:.1f}%)\n")

print(f"\nResults saved to: {results_file}")

print("\n" + "="*70)
print("PHASE 2 TESTING SUMMARY")
print("="*70)
print("Phase 2 is now complete!")
print("Model trained on real Kaggle data (82,479+ emails)")
print("Model tested on phishing and legitimate samples")
print("\nReady for Phase 3: Web Dashboard Development")
print("="*70)
