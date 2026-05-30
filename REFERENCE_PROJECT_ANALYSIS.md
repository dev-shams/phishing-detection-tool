# Phishing Detection Model Analysis: Reference Project vs Your Implementation

## Executive Summary

The reference project achieves superior accuracy due to **5 critical technical differences**. The most important is **feature scaling**, which you're missing entirely. Without it, your raw numerical handcrafted features overwhelm the sparse TF-IDF matrix, causing severe probability calibration issues.

---

## Critical Difference #1: Feature Scaling ⚠️ MOST IMPORTANT

### Reference Project (Phase 2)
```python
from sklearn.preprocessing import MinMaxScaler

# STEP: Scale handcrafted features to [0,1] before combining with TF-IDF
scaler = MinMaxScaler()
handcrafted_scaled = np.clip(scaler.fit_transform(handcrafted_raw), 0, 1)

X_tfidf = tfidf.fit_transform(df['text'])
X_combined = hstack([X_tfidf, csr_matrix(handcrafted_scaled)])
```

### Your Implementation
```python
# Your code (in detector.py) - NO SCALING
X_tfidf = tfidf.fit_transform(email_text)
X_combined = hstack([X_tfidf, csr_matrix(handcrafted)])
```

### Why This Matters
- **TF-IDF values**: Typically range from 0 to 1 (sparse)
- **Handcrafted features WITHOUT scaling**: Raw counts like `url_count=5`, `urgency_keywords=3` (can be 10+)
- **Result**: Raw numerical features dominate the TF-IDF weights by orders of magnitude
- **Consequence**: Model relies almost entirely on raw features, ignoring learned text patterns
- **Symptom**: Your model flags ~50% of legitimate emails as phishing (probability calibration broken)

### Fix for Your Project
```python
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
handcrafted_scaled = np.clip(scaler.fit_transform(handcrafted_features), 0, 1)
X_combined = hstack([X_tfidf, csr_matrix(handcrafted_scaled)])
```

---

## Critical Difference #2: Model Selection

### Reference Project
```python
models = {
    'Naive Bayes': MultinomialNB(alpha=0.1),
    'Logistic Regression': LogisticRegression(C=1.0, max_iter=1000),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100)
}
# RESULT: Logistic Regression selected as best model
```

### Your Implementation
```python
model = RandomForestClassifier(
    n_estimators=300, 
    max_depth=25, 
    class_weight='balanced'
)
```

### Why Logistic Regression Wins
1. **Better Calibration**: Logistic Regression produces properly calibrated probabilities
2. **Simpler Decision Boundary**: Linear model fits phishing detection better
3. **Fewer Hyperparameters**: Less prone to overfitting
4. **Stable with Scaled Features**: Works optimally when features are normalized

### Why Your Random Forest Fails
1. **Overconfidence**: Random Forest learns training set too perfectly
2. **Poor Probability Calibration**: Probabilities don't reflect true confidence
3. **Deeper Trees + More Estimators**: Settings (depth=25, n_estimators=300) lead to overfitting
4. **Unscaled Features Issue Amplified**: Random Forest magnifies the feature scaling problem

### Reference's Hyperparameters (Phase 2)
```python
RandomForestClassifier(n_estimators=200, max_depth=20, random_state=42)
GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
LogisticRegression(C=10.0, max_iter=1000, random_state=42)  # ← BEST
```

---

## Critical Difference #3: Feature Engineering Quality

### Reference Project Features (20 total)

**Phase 1 Features (10):**
```
1. url_count - Number of URLs in email
2. suspicious_url - IP-based URLs, bit.ly, tinyurl, goo.gl
3. urgency_keywords - 24 predefined keywords
4. exclamation_marks - Count of !
5. dollar_signs - Count of $
6. caps_words - Words with 3+ consecutive capitals
7. text_length - Total character count
8. word_count - Total words
9. has_html - Binary: HTML tags present?
10. has_reply_to - Binary: Reply-To header present?
```

**Phase 2 Additional Features (10 more):**

**Email Header Analysis (4):**
```
11. domain_mismatch - From domain ≠ Reply-To domain
12. lookalike_domain - Patterns like "paypa[^l]", "app[^l]e"
13. numeric_in_domain - Digits in sender domain (123.com)
14. suspicious_tld_header - TLDs like .xyz, .tk, .ml, .ga, .cf, .gq, .ru, .cn
```

**URL Structure Analysis (6):**
```
15. ip_url_count - URLs with IP addresses instead of domains
16. shortener_url_count - bit.ly, tinyurl, goo.gl, t.co, etc.
17. avg_url_length - Average URL length in email
18. deep_subdomain_count - URLs with >3 dots (deep subdomains)
19. suspicious_tld_url - Suspicious TLDs in URLs
20. at_in_url - @ symbol in URLs (credential stealing attempt)
```

### Your Features
You have the same 20 features, BUT your feature extraction might differ:

**Check your feature extraction for:**
1. Are you detecting lookalike domains correctly? (Pattern matching)
2. Are your URL shortener lists complete?
3. Are your suspicious TLD lists up-to-date?

---

## Critical Difference #4: Model Evaluation & Selection

### Reference Project
```python
from sklearn.model_selection import cross_val_score

# 5-fold cross-validation to select best model
cv_results = {}
for name, model in models.items():
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1')
    cv_results[name] = scores.mean()

best_name = max(cv_results, key=lambda k: cv_results[k])
best_model = models[best_name]  # Logistic Regression
best_model.fit(X_train, y_train)
```

### Your Implementation
```python
# Single train/test split - no cross-validation
X_train, X_test, y_train, y_test = train_test_split(
    X_combined, y, test_size=0.2, random_state=42, stratify=y
)
model.fit(X_train, y_train)
```

### Impact
- **Reference**: Robust model selection across multiple folds
- **Your approach**: Could select a model that's lucky on THIS specific split
- **Better practice**: Use cross-validation for final model selection

---

## Critical Difference #5: Training Methodology

### Reference Project - Iterative Approach

**Phase 1**: Build foundation with 10 simple features + 3 models, select best
```
Baseline accuracy established with Logistic Regression
```

**Phase 2**: Add 10 advanced features + 4 models, improve further
```
Features: +10 (header analysis, URL analysis)
Models: +Gradient Boosting option
Result: Logistic Regression still best, but with richer features
```

**Phase 3**: Deploy winning model from Phase 2 unchanged
```
Same model, same features, same scaler
Flask wrapper around proven system
```

### Your Implementation - Direct to Complex

- Started with Phase 3 (web deployment) immediately
- Didn't validate Phase 1 (basic features) first
- Used unproven feature combinations
- No iterative validation at each step

---

## Quantitative Comparison

| Aspect | Reference | Your Implementation |
|--------|-----------|-------------------|
| **Best Model** | Logistic Regression | Random Forest |
| **Model Hyperparameters** | C=10.0 | n_estimators=300, depth=25 |
| **Feature Scaling** | ✅ MinMaxScaler | ❌ None |
| **Cross-Validation** | ✅ 5-fold | ❌ Single split |
| **Features Count** | 5020 (5000 TF-IDF + 20) | 5020 (5000 TF-IDF + 20) |
| **TF-IDF Params** | (1,2)-grams, min_df=2 | (1,2)-grams, min_df=2 |
| **Reported Accuracy** | ~95%+ | ~50% (2/4 emails) |

---

## Step-by-Step Fix for Your Model

### Step 1: Add Feature Scaling
```python
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
handcrafted_scaled = np.clip(scaler.fit_transform(handcrafted_features), 0, 1)

# Save scaler
joblib.dump(scaler, 'models/scaler_enhanced.joblib')

# Use scaled features
X_combined = hstack([X_tfidf, csr_matrix(handcrafted_scaled)])
```

### Step 2: Switch Model Selection
```python
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

# Train multiple models
models = {
    'Logistic Regression': LogisticRegression(C=10.0, max_iter=1000, random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=20, random_state=42),
}

# Select via cross-validation
best_name = None
best_score = 0
for name, model in models.items():
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1')
    if scores.mean() > best_score:
        best_score = scores.mean()
        best_name = name

best_model = models[best_name]
best_model.fit(X_train, y_train)
```

### Step 3: Load Scaler in Prediction
```python
class PhishingDetector:
    def __init__(self):
        self.model = joblib.load('models/phishing_model_enhanced.joblib')
        self.tfidf = joblib.load('models/tfidf_vectorizer_enhanced.joblib')
        self.scaler = joblib.load('models/scaler_enhanced.joblib')  # NEW
    
    def predict(self, text):
        X_tfidf = self.tfidf.transform([text])
        hc_raw = np.array([self.extract_features(text)])
        hc_scaled = np.clip(self.scaler.transform(hc_raw), 0, 1)  # SCALE HERE
        X = hstack([X_tfidf, csr_matrix(hc_scaled)])
        return self.model.predict_proba(X)
```

### Step 4: Adjust Decision Threshold
```python
# With Logistic Regression and proper scaling, default 0.5 should work
# If needed, tune to 0.45-0.55 range (not 0.60)
decision_threshold = 0.5
```

---

## Why Reference Project Succeeds

1. **Proper Feature Representation**: Scaled features work harmoniously with TF-IDF
2. **Appropriate Algorithm**: Logistic Regression's linear boundary fits this problem
3. **Robust Validation**: Cross-validation confirms generalization
4. **Iterative Refinement**: Features evolved from 10→20 with validation at each step
5. **Clean Probability Calibration**: Model confidence scores accurately reflect true precision

---

## Why Your Model Fails

1. **Unscaled Features Overwhelm TF-IDF**: Raw counts dominate decision-making
2. **Random Forest Overfitting**: Too complex for this relatively simple problem
3. **Poor Probability Calibration**: Model thinks it's more confident than it should be
4. **Symptom Match**: ~50% incorrect = model making near-random guesses
5. **No Validation Loop**: Hyperparameters never validated against diverse data

---

## Recommended Actions

### Immediate (Quick Win)
1. Add MinMaxScaler to your detector.py
2. Retrain model with scaled features
3. Test locally - should see significant improvement

### Short-term (Proper Implementation)
1. Switch to Logistic Regression as primary model
2. Implement 5-fold cross-validation
3. Compare all 3-4 models systematically
4. Retrain and save new model

### Long-term (Production Ready)
1. Document your feature engineering choices
2. Add unit tests for feature extraction
3. Keep PhaseX notebooks documenting progression
4. Deploy tested, validated model

---

## Files to Modify in Your Project

1. **Phase2_development/model_training.ipynb** or Python script
   - Add MinMaxScaler import
   - Add 5-fold cross-validation
   - Test Logistic Regression vs Random Forest

2. **Phase3_development/models/detector.py**
   - Load scaler in __init__
   - Apply scaling in predict method

3. **Phase3_development/config.py**
   - Update DECISION_THRESHOLD if needed (0.50 with Logistic Regression)

---

## Success Metrics

**Before Fix (Current State):**
- 2/4 emails correct (50% accuracy)
- High false positive rate
- Model confidence unreliable

**After Fix (Expected):**
- 4/4 emails correct (100% accuracy on test set)
- Proper calibration
- Confidence scores meaningful
- Ready for submission

---

## Conclusion

Your model architecture (5000 TF-IDF + 20 features) is correct. The problem is in the implementation details:

1. **Missing feature scaling** is the #1 issue
2. **Wrong model choice** (RF instead of LR) amplifies the problem
3. **Lack of validation** prevents you from catching these issues

Implement the three suggested fixes above, and your model should perform comparably to the reference project. The foundation is sound—the execution needs refinement.
