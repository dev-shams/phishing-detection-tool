#!/usr/bin/env python3
"""
Phase 2: Test Phishing Email Detection

Tests the trained model on sample phishing emails.
Verifies the model correctly identifies phishing emails.
"""

import sys
import pickle
import numpy as np
import pandas as pd
from pathlib import Path

print("\n" + "="*70)
print("PHASE 2: TEST PHISHING EMAIL DETECTION")
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

# Sample phishing emails
phishing_emails = [
    """Dear Customer,

Your account has been locked due to suspicious activity.
Click here immediately to verify your identity: http://192.168.1.1/verify

URGENT: Do not delay or your account will be permanently closed!

Best regards,
Security Team""",

    """VERIFY YOUR AMAZON ACCOUNT NOW!

We detected unusual activity on your account.
You must confirm your payment information immediately.

Click: https://bit.ly/amazon-confirm

Act now to prevent account suspension!""",

    """Alert: Update Required

Your banking credentials need to be updated for security.
Visit: http://malicious-bank-update.tk/verify-now

Time is running out! Update immediately!""",

    """PayPal Account Under Review

Your account has been flagged for suspicious transactions.
CONFIRM YOUR IDENTITY: https://verify-paypal.xyz/login

Failure to comply will result in permanent account closure.""",

    """Microsoft Account Security Alert

IMMEDIATE ACTION REQUIRED!
Unusual sign-in activity detected.

Verify your password: http://192.168.0.1/msaccount

Click immediately to secure your account!"""
]

print(f"\nTesting {len(phishing_emails)} phishing emails...")
print("="*70)

correct_detections = 0

for idx, email_text in enumerate(phishing_emails, 1):
    # Extract features
    email_data = {
        'sender': 'attacker@suspicious.tk',
        'sender_domain': 'suspicious.tk',
        'to': 'user@gmail.com',
        'subject': 'URGENT: Action Required',
        'reply_to': '',
        'body': email_text,
        'urls': ['http://192.168.1.1/verify', 'https://bit.ly/amazon-confirm'],
        'headers': {}
    }

    features = extractor.extract_all_features(email_data)
    feature_values = np.array([list(features.values())]).reshape(1, -1)

    # Scale and predict
    X_scaled = scaler.transform(feature_values)
    prediction = model.predict(X_scaled)[0]
    probabilities = model.predict_proba(X_scaled)[0]
    confidence = probabilities[1]  # Confidence in phishing class

    is_phishing = prediction == 1
    verdict = "✓ PHISHING DETECTED" if is_phishing else "✗ FALSE NEGATIVE"

    print(f"\nEmail {idx}:")
    print(f"  Verdict: {verdict}")
    print(f"  Confidence: {confidence*100:.1f}%")
    print(f"  Phishing score: {probabilities[1]:.4f}")
    print(f"  Legitimate score: {probabilities[0]:.4f}")

    if is_phishing:
        correct_detections += 1

print("\n" + "="*70)
print(f"PHISHING DETECTION RESULTS")
print("="*70)
print(f"Detected: {correct_detections}/{len(phishing_emails)}")
print(f"Detection Rate: {(correct_detections/len(phishing_emails))*100:.1f}%")

if correct_detections == len(phishing_emails):
    print("✓ ALL PHISHING EMAILS DETECTED CORRECTLY!")
    status = "✓ PASS"
else:
    missed = len(phishing_emails) - correct_detections
    print(f"⚠ {missed} phishing email(s) not detected")
    status = "⚠ PARTIAL"

print("="*70)
print(f"Status: {status}")
print("="*70)

print("\nNext: python 3_testing/test_legitimate_detection.py")
print("="*70 + "\n")
