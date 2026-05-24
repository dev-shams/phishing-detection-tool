"""
COMPREHENSIVE TESTING SUITE - Phase 2 Model Validation
Tests all aspects of the phishing detection model before Phase 3
"""

import sys
sys.path.insert(0, '/sessions/sleepy-cool-rubin/mnt/Final year Project/Phase2_development')

import pandas as pd
import numpy as np
from feature_extractor import FeatureExtractor
from ml_model import PhishingDetectionModel
from pathlib import Path

class PhishingModelTester:
    """Comprehensive model testing suite"""

    def __init__(self):
        self.model = PhishingDetectionModel()
        self.model.load_model(
            '/sessions/sleepy-cool-rubin/mnt/Final year Project/Phase2_development/4_models/phishing_model_phase2.pkl',
            '/sessions/sleepy-cool-rubin/mnt/Final year Project/Phase2_development/4_models/scaler_phase2.pkl'
        )
        self.df = pd.read_csv('/sessions/sleepy-cool-rubin/mnt/Final year Project/Phase2_development/data/phishing_emails_processed.csv')
        self.extractor = FeatureExtractor()
        self.test_results = {}

    def test_1_model_loads_correctly(self):
        """Test 1: Model loads without errors"""
        print("\n" + "="*70)
        print("TEST 1: Model Loading")
        print("="*70)

        try:
            assert self.model.is_trained, "Model not marked as trained"
            assert self.model.model is not None, "Model object is None"
            assert self.model.scaler is not None, "Scaler is None"
            print("✓ Model loads correctly")
            print("✓ Model is marked as trained")
            print("✓ Scaler is loaded")
            self.test_results['model_loading'] = 'PASS'
            return True
        except Exception as e:
            print(f"✗ FAILED: {e}")
            self.test_results['model_loading'] = 'FAIL'
            return False

    def test_2_feature_extraction(self):
        """Test 2: Feature extraction works properly"""
        print("\n" + "="*70)
        print("TEST 2: Feature Extraction")
        print("="*70)

        try:
            # Test on 5 random emails
            test_df = self.df.sample(n=5, random_state=42)

            for idx, (_, row) in enumerate(test_df.iterrows(), 1):
                email_data = {
                    'body': str(row.get('email', '')),
                    'subject': '',
                    'sender': '',
                    'urls': [],
                    'headers': {}
                }

                features = self.extractor.extract_all_features(email_data)

                # Verify features
                assert isinstance(features, dict), f"Features not a dict: {type(features)}"
                assert len(features) == 27, f"Expected 27 features, got {len(features)}"
                assert all(isinstance(v, (int, float)) for v in features.values()), "Features contain non-numeric values"

                # Check for NaN
                assert not any(np.isnan(v) if isinstance(v, float) else False for v in features.values()), "Features contain NaN"

            print(f"✓ Feature extraction works for {len(test_df)} emails")
            print(f"✓ All features are numeric")
            print(f"✓ No NaN values in features")
            print(f"✓ Feature count: 27")
            self.test_results['feature_extraction'] = 'PASS'
            return True
        except Exception as e:
            print(f"✗ FAILED: {e}")
            self.test_results['feature_extraction'] = 'FAIL'
            return False

    def test_3_prediction_output(self):
        """Test 3: Predictions have correct format"""
        print("\n" + "="*70)
        print("TEST 3: Prediction Output Format")
        print("="*70)

        try:
            email_data = {
                'body': self.df.iloc[0]['email'],
                'subject': '',
                'sender': '',
                'urls': [],
                'headers': {}
            }

            features = self.extractor.extract_all_features(email_data)
            result = self.model.predict_single(features)

            # Verify output structure
            required_keys = ['prediction', 'classification', 'confidence_phishing', 'confidence_legitimate', 'decision_score']
            assert all(key in result for key in required_keys), f"Missing keys in result: {result.keys()}"

            # Verify value types
            assert result['prediction'] in [0, 1], f"prediction not 0 or 1: {result['prediction']}"
            assert result['classification'] in ['PHISHING', 'LEGITIMATE'], f"classification invalid: {result['classification']}"
            assert 0 <= result['confidence_phishing'] <= 100, f"confidence_phishing out of range: {result['confidence_phishing']}"
            assert 0 <= result['confidence_legitimate'] <= 100, f"confidence_legitimate out of range: {result['confidence_legitimate']}"
            assert 0 <= result['decision_score'] <= 1, f"decision_score out of range: {result['decision_score']}"

            # Verify consistency
            assert result['confidence_phishing'] + result['confidence_legitimate'] == 100, "Confidences don't sum to 100"

            print("✓ Prediction has all required keys")
            print("✓ Prediction values in correct ranges")
            print(f"✓ Example output:")
            print(f"  - Classification: {result['classification']}")
            print(f"  - Confidence: {result['confidence_phishing']:.1f}% phishing, {result['confidence_legitimate']:.1f}% legitimate")
            print(f"  - Decision Score: {result['decision_score']:.4f}")
            self.test_results['prediction_format'] = 'PASS'
            return True
        except Exception as e:
            print(f"✗ FAILED: {e}")
            self.test_results['prediction_format'] = 'FAIL'
            return False

    def test_4_phishing_detection(self):
        """Test 4: Phishing detection accuracy"""
        print("\n" + "="*70)
        print("TEST 4: Phishing Detection (50 samples)")
        print("="*70)

        try:
            phishing_df = self.df[self.df['label'] == 1].sample(n=50, random_state=42)

            correct = 0
            confidences = []

            for idx, (_, row) in enumerate(phishing_df.iterrows()):
                email_data = {
                    'body': str(row.get('email', '')),
                    'subject': '',
                    'sender': '',
                    'urls': [],
                    'headers': {}
                }

                features = self.extractor.extract_all_features(email_data)
                result = self.model.predict_single(features)

                if result['prediction'] == 1:  # Correctly identified as phishing
                    correct += 1
                confidences.append(result['decision_score'])

            accuracy = correct / len(phishing_df) * 100

            print(f"✓ Phishing Detection Rate: {correct}/{len(phishing_df)} ({accuracy:.1f}%)")
            print(f"✓ Average Confidence: {np.mean(confidences):.1%}")
            print(f"✓ Min Confidence: {min(confidences):.1%}")
            print(f"✓ Max Confidence: {max(confidences):.1%}")

            # Check threshold
            assert accuracy >= 80, f"Phishing detection below 80%: {accuracy:.1f}%"
            print(f"✓ Detection rate >= 80% (PASS)")

            self.test_results['phishing_detection'] = 'PASS' if accuracy >= 80 else 'FAIL'
            return accuracy >= 80
        except Exception as e:
            print(f"✗ FAILED: {e}")
            self.test_results['phishing_detection'] = 'FAIL'
            return False

    def test_5_legitimate_detection(self):
        """Test 5: Legitimate email detection accuracy"""
        print("\n" + "="*70)
        print("TEST 5: Legitimate Detection (50 samples)")
        print("="*70)

        try:
            legit_df = self.df[self.df['label'] == 0].sample(n=50, random_state=42)

            correct = 0
            false_positives = 0
            confidences = []

            for idx, (_, row) in enumerate(legit_df.iterrows()):
                email_data = {
                    'body': str(row.get('email', '')),
                    'subject': '',
                    'sender': '',
                    'urls': [],
                    'headers': {}
                }

                features = self.extractor.extract_all_features(email_data)
                result = self.model.predict_single(features)

                if result['prediction'] == 0:  # Correctly identified as legitimate
                    correct += 1
                else:  # Misclassified as phishing
                    false_positives += 1
                confidences.append(result['decision_score'])

            accuracy = correct / len(legit_df) * 100
            fp_rate = false_positives / len(legit_df) * 100

            print(f"✓ Legitimate Detection Rate: {correct}/{len(legit_df)} ({accuracy:.1f}%)")
            print(f"✓ False Positive Rate: {false_positives}/{len(legit_df)} ({fp_rate:.1f}%)")
            print(f"✓ Average Confidence: {np.mean(confidences):.1%}")
            print(f"✓ Min Confidence: {min(confidences):.1%}")
            print(f"✓ Max Confidence: {max(confidences):.1%}")

            # Check thresholds
            assert accuracy >= 80, f"Legitimate detection below 80%: {accuracy:.1f}%"
            print(f"✓ Detection rate >= 80% (PASS)")

            self.test_results['legitimate_detection'] = 'PASS' if accuracy >= 80 else 'FAIL'
            return accuracy >= 80
        except Exception as e:
            print(f"✗ FAILED: {e}")
            self.test_results['legitimate_detection'] = 'FAIL'
            return False

    def test_6_threshold_consistency(self):
        """Test 6: Threshold is consistently applied"""
        print("\n" + "="*70)
        print("TEST 6: Threshold Consistency")
        print("="*70)

        try:
            threshold = 0.55
            test_df = self.df.sample(n=100, random_state=42)

            for idx, (_, row) in enumerate(test_df.iterrows()):
                email_data = {
                    'body': str(row.get('email', '')),
                    'subject': '',
                    'sender': '',
                    'urls': [],
                    'headers': {}
                }

                features = self.extractor.extract_all_features(email_data)
                result = self.model.predict_single(features)

                # Verify threshold is applied consistently
                if result['decision_score'] >= threshold:
                    assert result['prediction'] == 1, f"Prediction inconsistent with threshold at score {result['decision_score']}"
                    assert result['classification'] == 'PHISHING', f"Classification inconsistent at score {result['decision_score']}"
                else:
                    assert result['prediction'] == 0, f"Prediction inconsistent with threshold at score {result['decision_score']}"
                    assert result['classification'] == 'LEGITIMATE', f"Classification inconsistent at score {result['decision_score']}"

            print(f"✓ Threshold {threshold} applied consistently")
            print(f"✓ Verified on 100 random emails")
            print(f"✓ All predictions match decision_score")
            self.test_results['threshold_consistency'] = 'PASS'
            return True
        except Exception as e:
            print(f"✗ FAILED: {e}")
            self.test_results['threshold_consistency'] = 'FAIL'
            return False

    def test_7_probability_distribution(self):
        """Test 7: Probability distribution is reasonable"""
        print("\n" + "="*70)
        print("TEST 7: Probability Distribution")
        print("="*70)

        try:
            phishing_df = self.df[self.df['label'] == 1].sample(n=50, random_state=42)
            legit_df = self.df[self.df['label'] == 0].sample(n=50, random_state=42)

            phishing_scores = []
            legit_scores = []

            for _, row in phishing_df.iterrows():
                email_data = {'body': str(row.get('email', '')), 'subject': '', 'sender': '', 'urls': [], 'headers': {}}
                features = self.extractor.extract_all_features(email_data)
                result = self.model.predict_single(features)
                phishing_scores.append(result['decision_score'])

            for _, row in legit_df.iterrows():
                email_data = {'body': str(row.get('email', '')), 'subject': '', 'sender': '', 'urls': [], 'headers': {}}
                features = self.extractor.extract_all_features(email_data)
                result = self.model.predict_single(features)
                legit_scores.append(result['decision_score'])

            phishing_scores = np.array(phishing_scores)
            legit_scores = np.array(legit_scores)

            print(f"Phishing Email Scores:")
            print(f"  Mean: {phishing_scores.mean():.3f}")
            print(f"  Std:  {phishing_scores.std():.3f}")
            print(f"  Min:  {phishing_scores.min():.3f}")
            print(f"  Max:  {phishing_scores.max():.3f}")

            print(f"\nLegitimate Email Scores:")
            print(f"  Mean: {legit_scores.mean():.3f}")
            print(f"  Std:  {legit_scores.std():.3f}")
            print(f"  Min:  {legit_scores.min():.3f}")
            print(f"  Max:  {legit_scores.max():.3f}")

            # Check separation
            overlap = (phishing_scores < 0.55).sum() + (legit_scores >= 0.55).sum()
            separation = 1 - (overlap / (len(phishing_scores) + len(legit_scores)))

            print(f"\nClass Separation at threshold 0.55:")
            print(f"  Overlap: {overlap}/{len(phishing_scores) + len(legit_scores)}")
            print(f"  Separation Score: {separation:.1%}")

            # Verify good separation
            assert separation >= 0.80, f"Poor class separation: {separation:.1%}"
            print(f"✓ Good class separation (>= 80%)")

            self.test_results['probability_distribution'] = 'PASS'
            return True
        except Exception as e:
            print(f"✗ FAILED: {e}")
            self.test_results['probability_distribution'] = 'FAIL'
            return False

    def test_8_edge_cases(self):
        """Test 8: Handle edge cases"""
        print("\n" + "="*70)
        print("TEST 8: Edge Cases")
        print("="*70)

        try:
            # Test 1: Very short email
            short_email = {'body': 'hi', 'subject': '', 'sender': '', 'urls': [], 'headers': {}}
            features = self.extractor.extract_all_features(short_email)
            result = self.model.predict_single(features)
            assert result['prediction'] in [0, 1], "Failed on short email"
            print("✓ Handles very short emails")

            # Test 2: Very long email
            long_email = {'body': 'a' * 10000, 'subject': '', 'sender': '', 'urls': [], 'headers': {}}
            features = self.extractor.extract_all_features(long_email)
            result = self.model.predict_single(features)
            assert result['prediction'] in [0, 1], "Failed on long email"
            print("✓ Handles very long emails")

            # Test 3: Special characters
            special_email = {'body': '!@#$%^&*()[]{}|;:,.<>?', 'subject': '', 'sender': '', 'urls': [], 'headers': {}}
            features = self.extractor.extract_all_features(special_email)
            result = self.model.predict_single(features)
            assert result['prediction'] in [0, 1], "Failed on special characters"
            print("✓ Handles special characters")

            # Test 4: Empty email
            empty_email = {'body': '', 'subject': '', 'sender': '', 'urls': [], 'headers': {}}
            features = self.extractor.extract_all_features(empty_email)
            result = self.model.predict_single(features)
            assert result['prediction'] in [0, 1], "Failed on empty email"
            print("✓ Handles empty emails")

            self.test_results['edge_cases'] = 'PASS'
            return True
        except Exception as e:
            print(f"✗ FAILED: {e}")
            self.test_results['edge_cases'] = 'FAIL'
            return False

    def run_all_tests(self):
        """Run all tests and generate report"""
        print("\n\n")
        print("█" * 70)
        print("COMPREHENSIVE PHASE 2 MODEL TEST SUITE")
        print("█" * 70)

        tests = [
            self.test_1_model_loads_correctly,
            self.test_2_feature_extraction,
            self.test_3_prediction_output,
            self.test_4_phishing_detection,
            self.test_5_legitimate_detection,
            self.test_6_threshold_consistency,
            self.test_7_probability_distribution,
            self.test_8_edge_cases,
        ]

        for test_func in tests:
            try:
                test_func()
            except Exception as e:
                print(f"✗ Test crashed: {e}")

        # Summary
        print("\n\n")
        print("="*70)
        print("TEST SUMMARY")
        print("="*70)

        for test_name, result in self.test_results.items():
            status = "✓ PASS" if result == 'PASS' else "✗ FAIL"
            print(f"{status:8} {test_name}")

        passed = sum(1 for r in self.test_results.values() if r == 'PASS')
        total = len(self.test_results)

        print("\n" + "="*70)
        print(f"OVERALL: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
        print("="*70)

        if passed == total:
            print("\n✅ ALL TESTS PASSED - MODEL IS READY FOR PHASE 3!")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed - Review results above")

        return passed == total

if __name__ == "__main__":
    tester = PhishingModelTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
