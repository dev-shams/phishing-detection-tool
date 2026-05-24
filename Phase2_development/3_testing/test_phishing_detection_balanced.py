"""
Test Phishing Detection - Balanced Model
Tests if the balanced model correctly identifies phishing emails
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from feature_extractor import FeatureExtractor
from ml_model import PhishingDetectionModel

# Sample phishing emails (with suspicious characteristics)
PHISHING_SAMPLES = [
    {
        'subject': 'URGENT: Confirm Your Apple ID Account Immediately',
        'body': '''Dear Customer,

We detected unusual activity on your Apple ID account. Your account has been temporarily locked for security reasons.

CLICK HERE IMMEDIATELY to verify your account and restore access:
https://apple-security-verify.tk/confirm

Do not delay - your account will be permanently closed in 24 hours if you do not act now.

Click here: apple-verify-now.bit.ly/security

Regards,
Apple Security Team''',
        'sender': 'security@apple-verify.tk'
    },
    {
        'subject': 'PayPal Account Update Required - Action Needed NOW',
        'body': '''Hello,

Your PayPal account requires immediate verification due to suspicious login attempts.

Please confirm your login credentials and banking information:
http://paypal-secure-login.ga/verify-account

This is urgent - your account will be restricted if not verified within 24 hours.

Act Now: https://bit.ly/paypal-verify

Best regards,
PayPal Security Department''',
        'sender': 'noreply@paypal-security.ml'
    },
    {
        'subject': 'ALERT: Unauthorized Access to Your Bank Account',
        'body': '''Warning!!!

We detected multiple failed login attempts on your bank account.

IMMEDIATE ACTION REQUIRED:
Click below to secure your account and reset your password:
https://bank-security.tk/reset-password?token=xyz123

Failure to act within 2 hours will result in account suspension.

CLICK HERE NOW: https://tinyurl.com/banksecurity

Your Bank Security Team''',
        'sender': 'alert@secure-banking.ml'
    },
    {
        'subject': 'Verify Your Amazon Account Immediately',
        'body': '''Dear Amazon Customer,

We need to confirm your identity to prevent account suspension.

URGENT: Update your account information NOW:
https://amazon-account-verify.ga/login

Verification required:
- Full Name
- Email Address
- Phone Number
- Credit Card Details

Do this within 24 hours or lose access to your account!

CLICK NOW: amazon-verify-24.bit.ly

Amazon Security''',
        'sender': 'verify@amazon-account.tk'
    },
    {
        'subject': 'Microsoft Account Security Alert - Verify Now',
        'body': '''Hello User,

SECURITY ALERT: Your Microsoft account shows suspicious activity.

You must verify your account immediately to prevent unauthorized access.

VERIFY ACCOUNT: https://micro-soft-verify.ga/signin
UPDATE SECURITY: https://windows-security-alert.tk/update

Username:
Password:
Recovery Email:

If you do not verify within 12 hours, your account will be closed.

Microsoft Security Team''',
        'sender': 'noreply@microsoft-verify.ml'
    }
]

def test_phishing_detection():
    """Test if the balanced model correctly detects phishing emails"""

    print("\n" + "="*70)
    print("PHISHING DETECTION TEST - BALANCED MODEL")
    print("Testing on 5 phishing email samples")
    print("="*70)

    # Load model
    model_path = Path(__file__).parent.parent / '4_models' / 'phishing_model_phase2_balanced.pkl'
    scaler_path = Path(__file__).parent.parent / '4_models' / 'scaler_phase2_balanced.pkl'

    print("\nLoading balanced model...")
    model = PhishingDetectionModel()

    try:
        model.load_model(str(model_path), str(scaler_path))
        print(f"✓ Model loaded from {model_path}")
    except FileNotFoundError:
        print(f"✗ Model file not found: {model_path}")
        print("Please run: python 2_training/train_model_balanced.py")
        return

    # Create feature extractor
    extractor = FeatureExtractor()

    # Test each sample
    correct_count = 0
    results = []

    print("\nTesting phishing emails:")
    print("="*70)

    for i, sample in enumerate(PHISHING_SAMPLES, 1):
        email_data = {
            'body': sample['body'],
            'subject': sample['subject'],
            'sender': sample['sender'],
            'urls': [],
            'headers': {}
        }

        # Extract features
        features = extractor.extract_all_features(email_data)
        result = model.predict_single(features)

        # Check if correctly identified as phishing
        is_correct = result['prediction'] == 1
        correct_count += is_correct

        status = "✓" if is_correct else "✗"
        verdict = "PHISHING" if result['prediction'] == 1 else "LEGITIMATE"

        print(f"\nEmail {i}:")
        print(f"  Subject: {sample['subject'][:50]}...")
        print(f"  Verdict: {status} {verdict}")
        print(f"  Confidence: {result['confidence_phishing']:.1f}%")
        print(f"  Score: {result['decision_score']:.4f}")

        results.append({
            'email': i,
            'correct': is_correct,
            'prediction': verdict,
            'confidence': result['confidence_phishing']
        })

    # Summary
    print("\n" + "="*70)
    print("PHISHING DETECTION RESULTS")
    print("="*70)
    print(f"Correctly Identified: {correct_count}/{len(PHISHING_SAMPLES)}")
    print(f"Detection Rate: {correct_count/len(PHISHING_SAMPLES)*100:.1f}%")

    if correct_count == len(PHISHING_SAMPLES):
        status = "✓ PERFECT"
    elif correct_count >= len(PHISHING_SAMPLES) * 0.8:
        status = "✓ GOOD"
    else:
        status = "⚠ NEEDS IMPROVEMENT"

    print(f"Status: {status}")
    print("="*70)

    # Save results
    results_file = Path(__file__).parent.parent / '5_results' / 'phishing_detection_results_balanced.txt'
    results_file.parent.mkdir(parents=True, exist_ok=True)

    with open(results_file, 'w') as f:
        f.write("PHISHING DETECTION TEST RESULTS - BALANCED MODEL\n")
        f.write("="*70 + "\n\n")
        f.write(f"Total Tests: {len(PHISHING_SAMPLES)}\n")
        f.write(f"Correct Detections: {correct_count}\n")
        f.write(f"Detection Rate: {correct_count/len(PHISHING_SAMPLES)*100:.1f}%\n")
        f.write(f"Status: {status}\n\n")
        f.write("Detailed Results:\n")
        f.write("-"*70 + "\n")
        for result in results:
            f.write(f"Email {result['email']}: {result['prediction']} (Confidence: {result['confidence']:.1f}%)\n")

    print(f"\n✓ Results saved to {results_file}")

    return correct_count == len(PHISHING_SAMPLES)

if __name__ == "__main__":
    success = test_phishing_detection()
    if success:
        print("\n✓ Phishing detection test PASSED!")
    else:
        print("\n⚠ Phishing detection test needs improvement")
