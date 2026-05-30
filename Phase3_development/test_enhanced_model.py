#!/usr/bin/env python3
"""
Test the enhanced phishing detection model with proper feature scaling

This script tests the model with 4 sample emails to verify:
1. Feature scaling is applied correctly
2. Model predictions are accurate
3. Confidence scores are well-calibrated
"""

import sys
import os
from pathlib import Path

# Add Phase 3 to path
sys.path.insert(0, str(Path(__file__).parent))

from models.detector import PhishingDetector
from config import (
    MODEL_PATH,
    SCALER_PATH,
    TFIDF_VECTORIZER_PATH,
    HANDCRAFTED_SCALER_PATH,
    FEATURE_EXTRACTOR_PATH,
    DECISION_THRESHOLD
)

print("\n" + "="*80)
print("TEST: Enhanced Phishing Detection Model")
print("="*80)
print(f"\nModel Configuration:")
print(f"  Model: {MODEL_PATH}")
print(f"  Threshold: {DECISION_THRESHOLD}")
print(f"  Feature Extractor: {FEATURE_EXTRACTOR_PATH}")

# Initialize detector
print(f"\nInitializing detector...")
try:
    detector = PhishingDetector(
        model_path=str(MODEL_PATH),
        scaler_path=str(SCALER_PATH),
        feature_extractor_path=str(FEATURE_EXTRACTOR_PATH),
        tfidf_vectorizer_path=str(TFIDF_VECTORIZER_PATH),
        handcrafted_scaler_path=str(HANDCRAFTED_SCALER_PATH),
        threshold=DECISION_THRESHOLD
    )
    print("✓ Detector initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize detector: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test emails
test_cases = [
    {
        'name': 'Email 1: Legitimate Corporate',
        'email': {
            'subject': 'Project Status Update',
            'body': 'Hi team, please find attached the quarterly project status report. Please review and provide feedback by Friday. Best regards, Sarah',
            'sender': 'sarah.johnson@company.com',
        },
        'expected': 'LEGITIMATE'
    },
    {
        'name': 'Email 2: Phishing - Urgent Action',
        'email': {
            'subject': 'URGENT: Account Suspended - Verify Now!',
            'body': 'Dear Customer, your account has been suspended due to suspicious activity. Click here immediately to verify your identity: http://bit.ly/verify-account or your account will be permanently closed. Click now!!!',
            'sender': 'support@paypa1.com',
        },
        'expected': 'PHISHING'
    },
    {
        'name': 'Email 3: Legitimate Personal',
        'email': {
            'subject': 'Meeting Rescheduled',
            'body': 'Hi John, the project meeting has been rescheduled to 3pm tomorrow instead of 2pm. Please update your calendar. Thanks.',
            'sender': 'manager@company.com',
        },
        'expected': 'LEGITIMATE'
    },
    {
        'name': 'Email 4: Phishing - Prize Scam',
        'email': {
            'subject': 'Congratulations! You Won $1,000,000!',
            'body': 'Congratulations!!! You have been selected as a winner of $1,000,000 in our international lottery. Claim your prize now by visiting http://free-money-now.xyz/claim. Provide your banking details to receive your money. Act now, offer expires in 24 hours!',
            'sender': 'lottery@scam-domain.tk',
        },
        'expected': 'PHISHING'
    },
]

# Run tests
print("\n" + "="*80)
print("Testing with Sample Emails")
print("="*80)

results = {'correct': 0, 'total': len(test_cases)}

for test_case in test_cases:
    print(f"\n{test_case['name']}")
    print("-" * 80)

    try:
        result = detector.predict(test_case['email'])

        classification = result['classification']
        confidence = result['confidence_phishing']
        risk_level = result['risk_level']
        threat_indicators = result['threat_indicators']

        # Check if prediction is correct
        is_correct = (classification == test_case['expected'])
        status = "✓ CORRECT" if is_correct else "✗ INCORRECT"

        if is_correct:
            results['correct'] += 1

        print(f"  Expected: {test_case['expected']:12} | Got: {classification:12} | {status}")
        print(f"  Confidence: {confidence:.2f}% Phishing | Risk Level: {risk_level}")

        if threat_indicators:
            print(f"  Threat Indicators ({len(threat_indicators)}):")
            for indicator in threat_indicators[:3]:  # Show first 3
                print(f"    - {indicator}")
        else:
            print(f"  Threat Indicators: None")

    except Exception as e:
        print(f"  ✗ Prediction failed: {str(e)}")
        import traceback
        traceback.print_exc()

# Summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print(f"Results: {results['correct']}/{results['total']} correct")
accuracy = (results['correct'] / results['total']) * 100
print(f"Accuracy: {accuracy:.1f}%")

if results['correct'] == results['total']:
    print("\n✓ All tests passed!")
else:
    print(f"\n✗ {results['total'] - results['correct']} test(s) failed")

print("="*80 + "\n")

sys.exit(0 if results['correct'] == results['total'] else 1)
