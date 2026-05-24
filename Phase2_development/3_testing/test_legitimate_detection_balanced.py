"""
Test Legitimate Email Detection - Balanced Model
Tests if the balanced model correctly identifies legitimate emails (zero false positives)
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from feature_extractor import FeatureExtractor
from ml_model import PhishingDetectionModel

# Sample legitimate emails (from various sources)
LEGITIMATE_SAMPLES = [
    {
        'subject': 'Project Status Update - Q2 Report',
        'body': '''Hi Team,

I wanted to provide an update on our Q2 project progress.

Key Achievements:
- Completed phase 1 deliverables on schedule
- Team productivity increased by 15%
- All stakeholder reviews completed successfully

Next Steps:
- Phase 2 kicks off next Monday
- Please review the attached timeline
- Schedule 1:1 meetings with your team lead

Let me know if you have any questions.

Best regards,
John Smith
Project Manager
john.smith@company.com''',
        'sender': 'john.smith@company.com'
    },
    {
        'subject': 'Meeting Agenda - Tuesday 2:00 PM',
        'body': '''Hello Everyone,

Our regular team sync meeting is scheduled for:

Date: Tuesday, May 28th
Time: 2:00 PM - 2:45 PM
Location: Conference Room B

Agenda:
1. Project Updates (15 min)
2. Technical Discussion (20 min)
3. Open Q&A (10 min)

Please come prepared with your updates.

Thanks,
Sarah Johnson
Team Lead
sarah@company.com''',
        'sender': 'sarah@company.com'
    },
    {
        'subject': 'Code Review Ready for PR #1523',
        'body': '''Hi Alex,

Your pull request is ready for review. I've completed the initial assessment:

✓ Code style looks good
✓ Tests are comprehensive
✓ Documentation is clear
- One minor suggestion: simplify the error handling in line 245

Overall, this is solid work. A few team members have requested to review as well.

Let me know when you've addressed the comment.

Thanks,
Mike Chen
Senior Engineer
mike.chen@company.com''',
        'sender': 'mike.chen@company.com'
    },
    {
        'subject': 'Quarterly Budget Review Complete',
        'body': '''Team,

The Q3 budget review has been finalized. Here's the summary:

Budget Allocations:
- Development: $250,000
- Operations: $100,000
- Marketing: $75,000
- Infrastructure: $50,000

All departments have been notified of their allocations.

Finance will be reaching out with next steps for expense tracking.

Best regards,
Lisa Wong
Finance Director
lisa.wong@company.com''',
        'sender': 'lisa.wong@company.com'
    },
    {
        'subject': 'Client Feedback Summary - Positive Response',
        'body': '''Dear Team,

I wanted to share the feedback we received from our client meeting yesterday.

Highlights:
- Client very satisfied with our deliverables
- Requested timeline for Phase 3 acceleration
- Interested in expanding partnership to 3 more projects
- Praised team professionalism and communication

Next Steps:
- I'll coordinate with Sales on the expansion opportunities
- Technical team can expect a detailed requirements document by Friday
- Please start planning capacity for Q3

This is great momentum for the company!

Warm regards,
Emma Rodriguez
Account Manager
emma.rodriguez@company.com''',
        'sender': 'emma.rodriguez@company.com'
    }
]

def test_legitimate_detection():
    """Test if the balanced model correctly identifies legitimate emails"""

    print("\n" + "="*70)
    print("LEGITIMATE EMAIL DETECTION TEST - BALANCED MODEL")
    print("Testing on 5 legitimate email samples")
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
        return False

    # Create feature extractor
    extractor = FeatureExtractor()

    # Test each sample
    correct_count = 0
    false_positives = 0
    results = []

    print("\nTesting legitimate emails:")
    print("="*70)

    for i, sample in enumerate(LEGITIMATE_SAMPLES, 1):
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

        # Check if correctly identified as legitimate
        is_correct = result['prediction'] == 0
        correct_count += is_correct

        # Check for false positive
        if result['prediction'] == 1:
            false_positives += 1

        status = "✓" if is_correct else "✗"
        verdict = "LEGITIMATE" if result['prediction'] == 0 else "PHISHING"
        error_type = "" if is_correct else " (FALSE POSITIVE)" if result['prediction'] == 1 else ""

        print(f"\nEmail {i}:")
        print(f"  Subject: {sample['subject'][:50]}...")
        print(f"  Verdict: {status} {verdict}{error_type}")
        print(f"  Confidence: {result['confidence_legitimate']:.1f}%")
        print(f"  Score: {result['decision_score']:.4f}")

        results.append({
            'email': i,
            'correct': is_correct,
            'prediction': verdict,
            'confidence': result['confidence_legitimate']
        })

    # Summary
    print("\n" + "="*70)
    print("LEGITIMATE DETECTION RESULTS")
    print("="*70)
    print(f"Correctly Identified: {correct_count}/{len(LEGITIMATE_SAMPLES)}")
    print(f"Detection Rate: {correct_count/len(LEGITIMATE_SAMPLES)*100:.1f}%")
    print(f"False Positives: {false_positives}/{len(LEGITIMATE_SAMPLES)}")

    if correct_count == len(LEGITIMATE_SAMPLES) and false_positives == 0:
        status = "✓ PERFECT"
    elif correct_count >= len(LEGITIMATE_SAMPLES) * 0.8 and false_positives <= 1:
        status = "✓ GOOD"
    else:
        status = "⚠ NEEDS IMPROVEMENT"

    print(f"Status: {status}")
    print("="*70)

    # Save results
    results_file = Path(__file__).parent.parent / '5_results' / 'legitimate_detection_results_balanced.txt'
    results_file.parent.mkdir(parents=True, exist_ok=True)

    with open(results_file, 'w') as f:
        f.write("LEGITIMATE EMAIL DETECTION TEST RESULTS - BALANCED MODEL\n")
        f.write("="*70 + "\n\n")
        f.write(f"Total Tests: {len(LEGITIMATE_SAMPLES)}\n")
        f.write(f"Correct Identifications: {correct_count}\n")
        f.write(f"Detection Rate: {correct_count/len(LEGITIMATE_SAMPLES)*100:.1f}%\n")
        f.write(f"False Positives: {false_positives}\n")
        f.write(f"Status: {status}\n\n")
        f.write("Detailed Results:\n")
        f.write("-"*70 + "\n")
        for result in results:
            f.write(f"Email {result['email']}: {result['prediction']} (Confidence: {result['confidence']:.1f}%)\n")

    print(f"\n✓ Results saved to {results_file}")

    return correct_count == len(LEGITIMATE_SAMPLES) and false_positives == 0

if __name__ == "__main__":
    success = test_legitimate_detection()
    if success:
        print("\n✓ Legitimate detection test PASSED - No false positives!")
    else:
        print("\n⚠ Legitimate detection test needs improvement")
