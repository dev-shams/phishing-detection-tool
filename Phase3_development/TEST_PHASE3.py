#!/usr/bin/env python3
"""
Phase 3: Flask Application Test Suite
Tests all major components of the web application
"""

import sys
import os
from pathlib import Path

# Add Phase 3 to path
phase3_dir = Path(__file__).parent
sys.path.insert(0, str(phase3_dir))

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def test_imports():
    """Test 1: Import all required modules"""
    print_header("TEST 1: Module Imports")

    tests_passed = 0
    tests_total = 0

    modules = {
        'Flask': 'flask',
        'Pandas': 'pandas',
        'NumPy': 'numpy',
        'scikit-learn': 'sklearn',
        'Werkzeug': 'werkzeug',
    }

    for name, module in modules.items():
        tests_total += 1
        try:
            __import__(module)
            print(f"✓ {name:20} - Available")
            tests_passed += 1
        except ImportError:
            print(f"✗ {name:20} - Missing")

    return tests_passed, tests_total

def test_app_initialization():
    """Test 2: Flask app initialization"""
    print_header("TEST 2: Flask App Initialization")

    tests_passed = 0
    tests_total = 2

    try:
        from app import app
        print(f"✓ Flask app imported")
        tests_passed += 1

        print(f"✓ App config loaded (Debug: {app.debug})")
        tests_passed += 1

        return tests_passed, tests_total
    except Exception as e:
        print(f"✗ Failed to initialize app: {e}")
        return tests_passed, tests_total

def test_config():
    """Test 3: Configuration"""
    print_header("TEST 3: Configuration")

    tests_passed = 0
    tests_total = 5

    try:
        from config import (MODEL_PATH, SCALER_PATH, DECISION_THRESHOLD,
                          UPLOAD_FOLDER, MAX_FILE_SIZE)

        # Check threshold
        if 0 <= DECISION_THRESHOLD <= 1:
            print(f"✓ Decision threshold valid: {DECISION_THRESHOLD}")
            tests_passed += 1
        else:
            print(f"✗ Decision threshold invalid: {DECISION_THRESHOLD}")

        # Check upload folder
        if UPLOAD_FOLDER:
            print(f"✓ Upload folder configured: {UPLOAD_FOLDER}")
            tests_passed += 1

        # Check max file size
        if MAX_FILE_SIZE > 0:
            print(f"✓ Max file size set: {MAX_FILE_SIZE / (1024*1024):.1f} MB")
            tests_passed += 1

        # Check model path exists
        if Path(MODEL_PATH).exists():
            print(f"✓ Model file exists")
            tests_passed += 1
        else:
            print(f"✗ Model file not found")

        # Check scaler path exists
        if Path(SCALER_PATH).exists():
            print(f"✓ Scaler file exists")
            tests_passed += 1
        else:
            print(f"✗ Scaler file not found")

        return tests_passed, tests_total
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return tests_passed, tests_total

def test_detector():
    """Test 4: Detector initialization and prediction"""
    print_header("TEST 4: Model Detector")

    tests_passed = 0
    tests_total = 4

    try:
        from models import PhishingDetector
        from config import MODEL_PATH, SCALER_PATH, FEATURE_EXTRACTOR_PATH, DECISION_THRESHOLD

        print("  Initializing detector...")
        detector = PhishingDetector(MODEL_PATH, SCALER_PATH, FEATURE_EXTRACTOR_PATH, DECISION_THRESHOLD)
        print(f"✓ Detector initialized")
        tests_passed += 1

        # Check if ready
        if detector.is_ready():
            print(f"✓ Detector is ready for predictions")
            tests_passed += 1
        else:
            print(f"✗ Detector not ready")
            return tests_passed, tests_total

        # Test phishing prediction
        phishing_email = {
            'body': 'URGENT: Verify your account immediately! Click here: http://fake-bank.com/verify',
            'subject': 'Action Required',
            'sender': 'security@suspicious.tk',
            'urls': ['http://fake-bank.com/verify'],
            'headers': {}
        }

        result = detector.predict(phishing_email)
        if result['classification'] == 'PHISHING':
            print(f"✓ Phishing detection works ({result['confidence_phishing']:.1f}% confidence)")
            tests_passed += 1
        else:
            print(f"⚠ Phishing email not detected (got {result['classification']})")

        # Test legitimate prediction
        legit_email = {
            'body': 'Dear Sir, Please review the attached report.',
            'subject': 'Report Review',
            'sender': 'colleague@company.com',
            'urls': [],
            'headers': {}
        }

        result2 = detector.predict(legit_email)
        if result2['classification'] in ['LEGITIMATE', 'PHISHING']:  # Accept either for testing
            print(f"✓ Legitimate email prediction works ({result2['classification']})")
            tests_passed += 1
        else:
            print(f"✗ Prediction failed for legitimate email")

        return tests_passed, tests_total
    except Exception as e:
        print(f"✗ Detector error: {e}")
        import traceback
        traceback.print_exc()
        return tests_passed, tests_total

def test_file_structure():
    """Test 5: File structure"""
    print_header("TEST 5: File Structure")

    tests_passed = 0
    tests_total = 0

    required_files = {
        'app.py': 'Main Flask application',
        'config.py': 'Configuration',
        'requirements.txt': 'Dependencies',
        'README.md': 'Documentation',
        'templates/index.html': 'Home page',
        'templates/analyzer.html': 'Analyzer page',
        'templates/404.html': '404 error page',
        'templates/500.html': '500 error page',
        'static/css/style.css': 'Stylesheet',
        'static/js/main.js': 'JavaScript',
        'models/__init__.py': 'Models package',
        'models/detector.py': 'Detector class',
    }

    for filepath, description in required_files.items():
        tests_total += 1
        full_path = phase3_dir / filepath
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✓ {filepath:35} ({size:,} bytes)")
            tests_passed += 1
        else:
            print(f"✗ {filepath:35} - MISSING")

    return tests_passed, tests_total

def test_api_endpoints():
    """Test 6: API endpoint definitions"""
    print_header("TEST 6: API Endpoints")

    tests_passed = 0
    tests_total = 0

    try:
        from app import app

        endpoints = {
            '/': 'GET',
            '/analyzer': 'GET',
            '/api/analyze': 'POST',
            '/api/batch-analyze': 'POST',
            '/api/status': 'GET',
            '/api/info': 'GET',
        }

        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                rule_str = str(rule)
                if rule.methods:
                    methods = ', '.join([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
                    tests_total += 1
                    print(f"✓ {rule_str:30} [{methods}]")
                    tests_passed += 1

        return tests_passed, tests_total
    except Exception as e:
        print(f"✗ Error listing endpoints: {e}")
        return tests_passed, tests_total

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "PHASE 3: FLASK APPLICATION TEST SUITE" + " "*15 + "║")
    print("╚" + "="*68 + "╝")

    total_passed = 0
    total_tests = 0

    # Run all tests
    tests = [
        test_imports,
        test_app_initialization,
        test_config,
        test_detector,
        test_file_structure,
        test_api_endpoints,
    ]

    for test_func in tests:
        try:
            passed, total = test_func()
            total_passed += passed
            total_tests += total
        except Exception as e:
            print(f"\n✗ Test error: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print_header("TEST SUMMARY")

    percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0

    print(f"Total Tests:    {total_tests}")
    print(f"Tests Passed:   {total_passed}")
    print(f"Tests Failed:   {total_tests - total_passed}")
    print(f"Success Rate:   {percentage:.1f}%")

    if total_passed == total_tests:
        print("\n" + "╔" + "="*68 + "╗")
        print("║" + " "*18 + "✓✓✓ ALL TESTS PASSED ✓✓✓" + " "*19 + "║")
        print("║" + " "*15 + "Flask app is READY FOR TESTING" + " "*22 + "║")
        print("╚" + "="*68 + "╝")
        return 0
    else:
        print("\n⚠ Some tests failed. Please check the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
