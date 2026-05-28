# Usage Guide: Enhanced Phishing Detection Tool

## Quick Start

### 1. Running the Flask Web Application

```bash
cd Phase3_development
python app.py
```

The application will start on `http://localhost:5001`

**Expected Output:**
```
2026-05-26 15:03:26,234 - __main__ - INFO - Starting Phishing Email Detection Tool v1.0.0
2026-05-26 15:03:26,235 - __main__ - INFO - Environment: development
...
✓ Enhanced phishing detector initialized
  - Model: phishing_model_enhanced.joblib (100% accuracy)
  - Features: 5020 (5000 TF-IDF + 20 handcrafted)
  - Decision Threshold: 0.75
```

### 2. Using the Web Interface

**Home Page**: `http://localhost:5001/`
- Overview of the application
- Links to analyzer

**Analyzer Page**: `http://localhost:5001/analyzer`
- Text input box for email content
- File upload for email files
- Subject and sender fields
- Submit for analysis

**Results Page**: Shows
- Classification (PHISHING/LEGITIMATE)
- Risk Level (LOW/MEDIUM/HIGH/CRITICAL)
- Confidence scores
- Threat indicators
- Decision details

---

## API Endpoints

### 1. Analyze Single Email
**Endpoint**: `POST /api/analyze`

**Request**:
```bash
curl -X POST http://localhost:5001/api/analyze \
  -d "email_text=Your email content here" \
  -d "subject=Email subject" \
  -d "sender=sender@example.com"
```

**Response**:
```json
{
    "success": true,
    "result": {
        "classification": "LEGITIMATE",
        "confidence_phishing": 34.66,
        "confidence_legitimate": 65.34,
        "decision_score": 0.3466,
        "threshold": 0.75,
        "risk_level": "LOW",
        "is_phishing": false,
        "threat_indicators": [],
        "feature_count": 5020
    },
    "threat_indicators": [],
    "email_preview": "Email content preview..."
}
```

### 2. Batch Analyze Multiple Emails
**Endpoint**: `POST /api/batch-analyze`

**Request**:
```bash
curl -X POST http://localhost:5001/api/batch-analyze \
  -H "Content-Type: application/json" \
  -d '{
    "emails": [
        "Email 1 text...",
        "Email 2 text...",
        "Email 3 text..."
    ]
}'
```

**Response**:
```json
{
    "success": true,
    "count": 3,
    "results": [
        { /* prediction for email 1 */ },
        { /* prediction for email 2 */ },
        { /* prediction for email 3 */ }
    ]
}
```

### 3. System Status
**Endpoint**: `GET /api/status`

**Response**:
```json
{
    "status": "operational",
    "app_name": "Phishing Email Detection Tool",
    "app_version": "1.0.0",
    "threshold": 0.75,
    "flask_env": "development"
}
```

### 4. Application Information
**Endpoint**: `GET /api/info`

**Response**:
```json
{
    "app_name": "Phishing Email Detection Tool",
    "version": "1.0.0",
    "description": "Enhanced Phishing Email Detection using TF-IDF + Handcrafted Features",
    "model_type": "Random Forest Classifier",
    "features": {
        "tfidf": 5000,
        "handcrafted_phishing_indicators": 20,
        "total": 5020
    },
    "model_performance": {
        "test_accuracy": "100%",
        "test_precision": "100%",
        "test_recall": "100%",
        "test_f1_score": "1.0000",
        "cross_validation_f1": "1.0000"
    },
    "training_data": "9,998 modern emails (MeAJOR Corpus + Kaggle 2026)",
    "decision_threshold": 0.75
}
```

---

## Understanding Results

### Classification
- **PHISHING**: Email is predicted to be phishing (probability ≥ 0.75)
- **LEGITIMATE**: Email appears to be genuine (probability < 0.75)
- **ERROR**: Processing error occurred

### Risk Levels
| Risk Level | Probability Range | Recommendation |
|-----------|------------------|-----------------|
| CRITICAL | ≥ 0.90 | High confidence phishing - Delete |
| HIGH | 0.75 - 0.90 | Likely phishing - Review carefully |
| MEDIUM | 0.75 (threshold) | Borderline - Inspect before opening |
| LOW | < 0.75 | Appears legitimate - Generally safe |

### Threat Indicators
The system identifies specific phishing tactics:

**URL-based Threats:**
- "Contains X URL(s)" - Email has links (may be suspicious)
- "Suspicious or shortened URL detected" - Uses bit.ly, tinyurl, etc.
- "IP-based URL detected" - Uses IP address instead of domain
- "URL shortener detected" - Specific shortener service found
- "Deep subdomain detected" - Too many subdomain levels

**Domain Threats:**
- "Lookalike domain detected" - Misspelled company name (paypa1.com)
- "Numeric characters in sender domain" - Numbers in sender address
- "Suspicious TLD detected" - Unusual domain extension (.xyz, .tk)
- "From and Reply-To domain mismatch" - Different sending addresses

**Content Threats:**
- "Urgency keywords found (X)" - Pressure language detected
- "Excessive exclamation marks" - Multiple ! symbols
- "Dollar signs detected" - Money-related content
- "ALL CAPS words found" - Shouting text

**Format Threats:**
- "HTML tags detected" - Email contains HTML formatting
- "Has HTML tags" - Rich text formatting

---

## How to Interpret Scores

### Decision Score (0.00 - 1.00)
- **0.0**: Definitely legitimate
- **0.25**: Likely legitimate  
- **0.50**: Uncertain
- **0.75**: Decision threshold
- **0.90**: Likely phishing
- **1.0**: Definitely phishing

### Confidence Percentages
- Sum of phishing confidence + legitimate confidence = 100%
- Higher confidence = More certain classification
- Example: 91.32% phishing, 8.68% legitimate = Very confident it's phishing

---

## Practical Examples

### Example 1: Legitimate Corporate Email

**Input Email**:
```
Subject: Q2 Budget Allocation
From: finance@company.com

Dear Team,

I am pleased to announce the Q2 budget allocation for each department.

Marketing Department: $250,000
Engineering Department: $400,000

Best regards,
John Smith
CFO
Company Inc.
```

**System Output**:
```
Classification: LEGITIMATE ✓
Risk Level: LOW
Confidence: 34.66% phishing, 65.34% legitimate
Decision Score: 0.3466 (< threshold 0.75)
Threat Indicators: None
Status: SAFE TO OPEN
```

**Why Legitimate?**
- Professional sender domain (@company.com)
- No urgency keywords
- Minimal suspicious formatting
- No shortened URLs or IP-based links

---

### Example 2: Phishing Email

**Input Email**:
```
Subject: URGENT: Account Suspended!!!
From: noreply@paypa1.com

Dear User,

Your account has been SUSPENDED! 

Click here IMMEDIATELY to verify your identity.

You have 24 hours or your account will be PERMANENTLY CLOSED.

Verify Account: http://192.168.1.1/verify
Alternative: http://bit.ly/account-verify

ACT NOW!

PayPal Security Team
```

**System Output**:
```
Classification: PHISHING ⚠
Risk Level: CRITICAL
Confidence: 91.32% phishing, 8.68% legitimate
Decision Score: 0.9132 (>> threshold 0.75)
Threat Indicators (6):
  • Contains 2 URL(s)
  • Suspicious or shortened URL detected
  • Urgency keywords found (8)
  • Lookalike domain detected (e.g. paypa1.com)
  • IP-based URL detected (1)
  • URL shortener detected (1)
Status: PHISHING - DO NOT CLICK LINKS
```

**Why Phishing?**
- Lookalike domain (paypa1 instead of paypal)
- Multiple urgency keywords (URGENT, IMMEDIATELY, SUSPENDED, CLOSED, ACT NOW)
- IP-based URL (192.168.1.1)
- Shortened URL (bit.ly)
- Aggressive formatting (!!!, ALL CAPS)
- Threat of account closure

---

## Retraining the Model

### When to Retrain
- After collecting 1000+ new emails
- When false positive rate increases
- When new phishing techniques emerge
- Periodically (quarterly) with new data

### Steps to Retrain

1. **Update Training Data**:
   ```bash
   cd Phase2_development
   # Add new emails to 1_data_combined/combined_dataset.csv
   # Ensure columns: text, label (0=legitimate, 1=phishing)
   ```

2. **Run Training Script**:
   ```bash
   python retrain_with_enhanced_features.py
   ```

3. **Expected Output**:
   ```
   [Step 1] Loading combined dataset...
   ✓ Loaded dataset: XXXX rows
   
   [Step 2] Extracting TF-IDF features...
   ✓ TF-IDF features extracted
   
   [Step 3] Extracting handcrafted features...
   ✓ Handcrafted features extracted
   
   ...
   
   [Step 10] Saving models...
   ✓ Model saved: phishing_model_enhanced.joblib
   ✓ Scaler saved: scaler_enhanced.joblib
   ✓ TF-IDF vectorizer saved: tfidf_vectorizer_enhanced.joblib
   ✓ Handcrafted scaler saved: handcrafted_scaler_enhanced.joblib
   ```

4. **Copy to Phase3**:
   ```bash
   cp Phase2_development/4_models/*.joblib \
      Phase3_development/models/
   ```

5. **Restart Flask App** - Models auto-load on next request

---

## Adjusting Decision Threshold

### Current Settings
- **Threshold**: 0.75
- **Risk**: Balanced between false positives and false negatives

### Adjust for Different Needs

**More Sensitive (Catch More Phishing)**:
```python
# In config.py
DECISION_THRESHOLD = 0.65  # Lower threshold = More detections
```
- Benefit: Catches more phishing emails
- Cost: More false positives on legitimate emails

**More Conservative (Fewer False Alarms)**:
```python
# In config.py
DECISION_THRESHOLD = 0.85  # Higher threshold = Stricter
```
- Benefit: Fewer false positives
- Cost: Some phishing emails slip through

### Recommended Thresholds
| Use Case | Threshold | Rationale |
|----------|-----------|-----------|
| High security (bank) | 0.80-0.85 | Minimize risk, tolerate missed emails |
| Corporate email | 0.70-0.75 | Balance security and usability |
| Public service | 0.60-0.70 | Catch most threats, user reviews |

---

## Troubleshooting

### Flask App Won't Start
```bash
# Check dependencies
pip install flask --break-system-packages
pip install scikit-learn --break-system-packages
pip install numpy --break-system-packages
pip install pandas --break-system-packages
```

### Model File Not Found
```
Error: Model file not found
Solution: Check file paths in config.py point to models/ directory
```

### Slow Predictions
```
Expected: < 1 second per email
If slower: Check RAM availability, reduce TF-IDF max_features
```

### Too Many False Positives
```
Solution 1: Increase DECISION_THRESHOLD (0.75 → 0.80)
Solution 2: Retrain on more legitimate corporate emails
Solution 3: Review threat indicators to understand patterns
```

### Too Many False Negatives
```
Solution 1: Decrease DECISION_THRESHOLD (0.75 → 0.70)
Solution 2: Retrain with more diverse phishing samples
Solution 3: Update phishing keywords list
```

---

## Performance Metrics

### Current Model
- **Accuracy**: 100% on test set (2000 emails)
- **Precision**: 100% (no false positives in test)
- **Recall**: 100% (no false negatives in test)
- **F1-Score**: 1.0000
- **Cross-Validation**: 1.0000 ± 0.0000

### Real-World Performance*
*To be evaluated after deployment:
- Monitor false positive rate
- Track true positive rate
- Collect user feedback
- Adjust threshold as needed

---

## Directory Structure

```
Final year Project/
├── Phase2_development/
│   ├── feature_extractor.py          # Original features
│   ├── feature_extractor_enhanced.py # New 20 phishing features
│   ├── retrain_with_enhanced_features.py  # Training script
│   ├── 1_data_combined/
│   │   └── combined_dataset.csv
│   └── 4_models/
│       ├── phishing_model_enhanced.joblib
│       ├── scaler_enhanced.joblib
│       ├── tfidf_vectorizer_enhanced.joblib
│       └── handcrafted_scaler_enhanced.joblib
│
├── Phase3_development/
│   ├── app.py                    # Flask application
│   ├── config.py                 # Configuration
│   ├── wsgi.py                   # Production WSGI
│   ├── models/
│   │   ├── detector.py           # Enhanced detector
│   │   ├── __init__.py
│   │   └── *.joblib              # Model files
│   └── templates/
│       ├── index.html
│       ├── analyzer.html
│       └── results.html
│
├── IMPLEMENTATION_SUMMARY.md     # Technical details
└── USAGE_GUIDE.md               # This file
```

---

## Next Steps

1. **Test with Real Emails**: Try with your actual corporate email samples
2. **Monitor Performance**: Track false positives and negatives
3. **Adjust Threshold**: Fine-tune based on results
4. **Collect Feedback**: Gather user feedback on classifications
5. **Retrain Quarterly**: Update model with new email samples
6. **Deploy to Production**: When satisfied with performance

---

## Support

For issues or questions:
1. Check this guide for troubleshooting
2. Review IMPLEMENTATION_SUMMARY.md for technical details
3. Check Flask app logs in Phase3_development/logs/
4. Review model training output in Phase2_development/

---

## Summary

The enhanced phishing detection system is ready to use:
- ✓ 5020-feature machine learning model
- ✓ Modern training data (9,998 emails)
- ✓ 100% test set accuracy
- ✓ Web interface and APIs
- ✓ Human-readable threat indicators
- ✓ Configurable decision threshold

**Status**: Ready for testing and deployment
