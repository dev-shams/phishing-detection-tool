#!/usr/bin/env python3
"""
Quick Test Suite — works against the Phase 3 deployed model.
=============================================================
Replaces the broken COMPREHENSIVE_TEST_SUITE.py which referenced files that
no longer exist. This script exercises the actual production PhishingDetector
class with a set of known-good and known-bad inputs and prints a PASS/FAIL
summary suitable for Figure 13 of the report.

Usage:
  cd Phase2_development/3_testing
  python3 quick_test_suite.py
"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Phase3_development"))
sys.path.insert(0, str(ROOT / "Phase3_development" / "models"))

# Import the deployed detector
from detector import PhishingDetector

# Build the detector with the actual production paths
MODELS = ROOT / "Phase3_development" / "models"
detector = PhishingDetector(
    model_path=str(MODELS / "phishing_model_enhanced.joblib"),
    scaler_path=str(MODELS / "scaler_enhanced.joblib"),
    feature_extractor_path=str(ROOT / "Phase2_development"),
    tfidf_vectorizer_path=str(MODELS / "tfidf_vectorizer_enhanced.joblib"),
    handcrafted_scaler_path=str(MODELS / "handcrafted_scaler_enhanced.joblib"),
    threshold=0.30,
)

print("=" * 70)
print("PHISHING DETECTION TOOL — QUICK TEST SUITE")
print("=" * 70)
print(f"Detector ready: {detector.is_ready()}")
print()

PHISHING_EMAILS = [
    ("T-01 PayPal lookalike", "security@paypa1-services.com",
     "URGENT — Unusual sign-in",
     "Dear Customer, We detected unusual activity. Verify immediately at https://paypa1-services.com/verify or your account will be suspended."),
    ("T-02 IP-literal URL",   "alert@bank-secure.com",
     "Action Required: Confirm Identity",
     "Confirm your wire transfer immediately: http://192.168.45.91/login. Failure to act will close your account."),
    ("T-03 URL shortener",    "noreply@invoice-bill.com",
     "Invoice #2387 overdue",
     "Your invoice is overdue. Pay now: https://bit.ly/x9k2 — limited time, password reset required."),
    ("T-04 Free TLD",         "admin@account-verify.tk",
     "Security alert",
     "Suspicious sign-in detected. Click here: https://verify-now.xyz/login to confirm your identity."),
    ("T-05 Urgency keywords", "winner@prize-claim.com",
     "Congratulations! You won",
     "URGENT! You are the winner of a free prize. Claim now or expire in 24 hours: https://claim-prize.ml/win"),
]

LEGITIMATE_EMAILS = [
    ("T-06 Personal note",   "ahmed@university.ac.ae",
     "Lunch tomorrow?",
     "Hey, are you free for lunch tomorrow around 1pm at the canteen? Let me know what you fancy. Cheers, Ahmed"),
    ("T-07 Calendar invite", "calendar-notification@google.com",
     "Reminder: Team standup at 10am",
     "This is a reminder that you have a meeting scheduled tomorrow at 10am. The room has been booked."),
    ("T-08 Conference CFP",  "chairs@acmccs.org",
     "ACM CCS 2026 call for papers",
     "Dear colleagues, ACM CCS 2026 will be held in November 2026 in Singapore. We invite original research contributions on all aspects of computer security. Submission deadline is May 15."),
    ("T-09 Recipe newsletter","weekly@bbcgoodfood.com",
     "Five quick weeknight dinners",
     "This week we look at five vegetarian recipes you can make in under thirty minutes. Pasta with roasted tomatoes, miso aubergine, and three more inside."),
    ("T-10 Open-source note","maintainer@example.org",
     "Thanks for your pull request",
     "Hi, thanks for the pull request on the parser module. The CI passed on all platforms. I have left a couple of minor style suggestions inline; otherwise it looks good. I will merge once the comments are addressed."),
]

results = []
print("RUNNING TESTS")
print("-" * 70)

import re

def run(label, sender, subject, body, expect):
    # detector.predict() expects a dict, not a string
    urls = re.findall(r"https?://\S+", body)
    email_data = {
        "sender": sender,
        "subject": subject,
        "body": body,
        "urls": urls,
        "headers": {"from": sender, "subject": subject},
    }
    t0 = time.time()
    try:
        out = detector.predict(email_data)
        latency = (time.time() - t0) * 1000
        # Detector returns various key names depending on version — handle all
        verdict = str(out.get("classification") or out.get("verdict") or out.get("prediction") or "?").upper()
        conf = out.get("confidence_phishing")
        if conf is None: conf = out.get("probability")
        if conf is None: conf = out.get("confidence", 0)
        try: conf = float(conf)
        except Exception: conf = 0.0
        ok = (expect == "PHISHING" and verdict == "PHISHING") or \
             (expect == "LEGITIMATE" and verdict in ("LEGITIMATE", "SAFE", "LEGIT"))
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {label:30s}  verdict={verdict:10s}  conf={conf:.2f}  ({latency:.0f} ms)")
        results.append((label, expect, verdict, ok))
    except Exception as e:
        print(f"  [ERR ] {label:30s}  exception: {type(e).__name__}: {e}")
        results.append((label, expect, "ERROR", False))

for label, sender, subject, body in PHISHING_EMAILS:
    run(label, sender, subject, body, "PHISHING")
for label, sender, subject, body in LEGITIMATE_EMAILS:
    run(label, sender, subject, body, "LEGITIMATE")

print("-" * 70)
passed = sum(1 for r in results if r[3])
total = len(results)
print(f"\nSUMMARY: {passed}/{total} passed ({100*passed/total:.0f}%)")
print("=" * 70)
