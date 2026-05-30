#!/usr/bin/env python3
"""
Debug script to trace through the prediction step by step
"""

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from models.detector import PhishingDetector
from config import (
    MODEL_PATH, SCALER_PATH, TFIDF_VECTORIZER_PATH,
    HANDCRAFTED_SCALER_PATH, FEATURE_EXTRACTOR_PATH, DECISION_THRESHOLD
)

import joblib

# Initialize
detector = PhishingDetector(
    model_path=str(MODEL_PATH),
    scaler_path=str(SCALER_PATH),
    feature_extractor_path=str(FEATURE_EXTRACTOR_PATH),
    tfidf_vectorizer_path=str(TFIDF_VECTORIZER_PATH),
    handcrafted_scaler_path=str(HANDCRAFTED_SCALER_PATH),
    threshold=DECISION_THRESHOLD
)

# Test email
test_email = {
    'subject': 'Project Status Update',
    'body': 'Hi team, please find attached the quarterly project status report. Please review and provide feedback by Friday. Best regards, Sarah',
    'sender': 'sarah.johnson@company.com',
}

print("\n" + "="*80)
print("DEBUG: Tracing Prediction for Legitimate Email")
print("="*80)

# Extract handcrafted features
print("\nStep 1: Extract Handcrafted Features")
hc_raw = detector._extract_handcrafted_features(test_email)
print(f"  Shape: {hc_raw.shape}")
print(f"  Values: {hc_raw}")
print(f"  Min: {hc_raw.min()}, Max: {hc_raw.max()}")

# Scale handcrafted features
print("\nStep 2: Scale Handcrafted Features")
hc_scaled = detector.handcrafted_scaler.transform(hc_raw)
print(f"  Shape: {hc_scaled.shape}")
print(f"  Values: {hc_scaled}")
print(f"  Min: {hc_scaled.min()}, Max: {hc_scaled.max()}")

# Extract TF-IDF features
print("\nStep 3: Extract TF-IDF Features")
tfidf_features = detector.tfidf_vectorizer.transform([test_email['body']]).toarray()
print(f"  Shape: {tfidf_features.shape}")
print(f"  Values: {tfidf_features}")
print(f"  Min: {tfidf_features.min()}, Max: {tfidf_features.max()}")

# Combine
print("\nStep 4: Combine Features")
from scipy.sparse import hstack, csr_matrix
combined = np.hstack([tfidf_features, hc_scaled])
print(f"  Shape: {combined.shape}")
print(f"  Values: {combined}")

# Scale combined
print("\nStep 5: Scale Combined Features")
combined_scaled = detector.scaler.transform(combined)
print(f"  Shape: {combined_scaled.shape}")
print(f"  Values: {combined_scaled}")
print(f"  Min: {combined_scaled.min()}, Max: {combined_scaled.max()}")

# Predict
print("\nStep 6: Make Prediction")
proba = detector.model.predict_proba(combined_scaled)
pred = detector.model.predict(combined_scaled)
print(f"  Probability: {proba}")
print(f"  Phishing prob: {proba[0, 1]:.6f}")
print(f"  Prediction: {pred}")

# Decision
is_phishing = proba[0, 1] >= DECISION_THRESHOLD
print(f"\nFinal Decision: {'PHISHING' if is_phishing else 'LEGITIMATE'}")
print(f"  Threshold: {DECISION_THRESHOLD}")
print(f"  Probability: {proba[0, 1]:.6f}")

print("\n" + "="*80)

# Now test with a phishing email
test_email_phish = {
    'subject': 'URGENT: Account Suspended - Verify Now!',
    'body': 'Dear Customer, your account has been suspended due to suspicious activity. Click here immediately to verify your identity: http://bit.ly/verify-account or your account will be permanently closed. Click now!!!',
    'sender': 'support@paypa1.com',
}

print("\nDEBUG: Tracing Prediction for Phishing Email")
print("="*80)

hc_raw = detector._extract_handcrafted_features(test_email_phish)
print(f"\nHandcrafted features raw: {hc_raw}")

hc_scaled = detector.handcrafted_scaler.transform(hc_raw)
print(f"Handcrafted features scaled: {hc_scaled}")

tfidf_features = detector.tfidf_vectorizer.transform([test_email_phish['body']]).toarray()
print(f"TF-IDF features: {tfidf_features}")

combined = np.hstack([tfidf_features, hc_scaled])
combined_scaled = detector.scaler.transform(combined)

proba = detector.model.predict_proba(combined_scaled)
pred = detector.model.predict(combined_scaled)

is_phishing = proba[0, 1] >= DECISION_THRESHOLD
print(f"\nFinal Decision: {'PHISHING' if is_phishing else 'LEGITIMATE'}")
print(f"  Probability: {proba[0, 1]:.6f}")

print("\n" + "="*80)
