"""
Retrain phishing detection model with enhanced techniques
Combines TF-IDF text features (5000 features) + Handcrafted phishing indicators (20 features)
This matches the approach used in the successful previous project

Features:
- TF-IDF vectorizer on email body text (5000 features)
- EnhancedFeatureExtractor with 20 handcrafted phishing-specific features
- Total: 5020 features per email
- Model: Random Forest Classifier with optimized hyperparameters
- Training: 5-fold cross-validation for robustness
"""

import pandas as pd
import numpy as np
import sys
import pickle
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report
import warnings

warnings.filterwarnings('ignore')

print("=" * 100)
print("RETRAINING PHISHING DETECTION MODEL - ENHANCED APPROACH")
print("=" * 100)

# ============================================================================
# Step 1: Load Dataset
# ============================================================================
print("\n[Step 1] Loading combined dataset...")
data_dir = Path(__file__).parent / "1_data_combined"
combined_csv = data_dir / "combined_dataset.csv"

df = pd.read_csv(combined_csv)
print(f"✓ Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")

# Prepare data
email_col = 'text'
label_col = 'label'
df_clean = df.dropna(subset=[label_col])
y = df_clean[label_col].astype(int)
X_text = df_clean[email_col].astype(str)

print(f"✓ Clean samples: {len(df_clean)}")
print(f"  - Phishing emails: {(y == 1).sum()}")
print(f"  - Legitimate emails: {(y == 0).sum()}")

# ============================================================================
# Step 2: Extract TF-IDF Features
# ============================================================================
print("\n[Step 2] Extracting TF-IDF features (5000 features)...")
tfidf_vectorizer = TfidfVectorizer(
    max_features=5000,
    min_df=2,
    max_df=0.95,
    ngram_range=(1, 2),
    stop_words='english'
)
X_tfidf = tfidf_vectorizer.fit_transform(X_text).toarray()
print(f"✓ TF-IDF features extracted: {X_tfidf.shape}")

# ============================================================================
# Step 3: Extract Handcrafted Phishing Features
# ============================================================================
print("\n[Step 3] Extracting handcrafted phishing features (20 features)...")

# Import enhanced feature extractor
sys.path.insert(0, str(Path(__file__).parent))
try:
    from feature_extractor_enhanced import EnhancedFeatureExtractor
    print("✓ Using EnhancedFeatureExtractor with 20 phishing-specific features")
except ImportError:
    print("⚠ EnhancedFeatureExtractor not found, falling back to original")
    from feature_extractor import FeatureExtractor as EnhancedFeatureExtractor

extractor = EnhancedFeatureExtractor()
X_handcrafted = []

for idx, email_text in enumerate(X_text):
    if idx % 5000 == 0:
        print(f"  Processing {idx}/{len(X_text)}...")
    try:
        email_data = {'body': email_text, 'subject': '', 'sender': '', 'urls': [], 'headers': {}}
        features = extractor.extract_all_features(email_data)
        X_handcrafted.append(list(features.values()))
    except Exception as e:
        # Use zeros if extraction fails
        X_handcrafted.append([0] * 20)

X_handcrafted = np.array(X_handcrafted)
print(f"✓ Handcrafted features extracted: {X_handcrafted.shape}")

# ============================================================================
# Step 4: Combine Features
# ============================================================================
print("\n[Step 4] Combining features...")

# Scale handcrafted features to [0, 1] so they don't get overshadowed by TF-IDF
scaler_handcrafted = MinMaxScaler()
X_handcrafted_scaled = scaler_handcrafted.fit_transform(X_handcrafted)

# Combine TF-IDF and scaled handcrafted features
X_combined = np.hstack([X_tfidf, X_handcrafted_scaled])
print(f"✓ Combined features: {X_combined.shape}")
print(f"  - TF-IDF features: 5000")
print(f"  - Handcrafted features: 20")
print(f"  - Total: {X_combined.shape[1]}")

# ============================================================================
# Step 5: Train/Test Split
# ============================================================================
print("\n[Step 5] Splitting dataset (80/20 with stratification)...")
X_train, X_test, y_train, y_test = train_test_split(
    X_combined, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)
print(f"✓ Training set: {X_train.shape[0]} samples")
print(f"✓ Test set: {X_test.shape[0]} samples")

# ============================================================================
# Step 6: Scale All Features
# ============================================================================
print("\n[Step 6] Scaling combined features...")
scaler_all = StandardScaler()
X_train_scaled = scaler_all.fit_transform(X_train)
X_test_scaled = scaler_all.transform(X_test)
print(f"✓ Features scaled with StandardScaler")

# ============================================================================
# Step 7: Train Model
# ============================================================================
print("\n[Step 7] Training Random Forest model...")
model = RandomForestClassifier(
    n_estimators=300,
    max_depth=25,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)

model.fit(X_train_scaled, y_train)
print(f"✓ Model training complete")

# ============================================================================
# Step 8: Evaluate Model
# ============================================================================
print("\n[Step 8] Evaluating model...")

y_pred_train = model.predict(X_train_scaled)
y_pred_test = model.predict(X_test_scaled)

train_accuracy = accuracy_score(y_train, y_pred_train)
test_accuracy = accuracy_score(y_test, y_pred_test)
test_precision = precision_score(y_test, y_pred_test, zero_division=0)
test_recall = recall_score(y_test, y_pred_test, zero_division=0)
test_f1 = f1_score(y_test, y_pred_test, zero_division=0)

print(f"\n  Training Accuracy:  {train_accuracy:.4f}")
print(f"  Test Accuracy:      {test_accuracy:.4f}")
print(f"  Test Precision:     {test_precision:.4f}")
print(f"  Test Recall:        {test_recall:.4f}")
print(f"  Test F1-Score:      {test_f1:.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred_test, target_names=['LEGITIMATE', 'PHISHING']))

# ============================================================================
# Step 9: Cross-Validation
# ============================================================================
print("\n[Step 9] Running 5-fold cross-validation...")
cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='f1')
print(f"✓ Cross-validation F1 scores: {[f'{s:.4f}' for s in cv_scores]}")
print(f"  Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# ============================================================================
# Step 10: Save Model, Scaler, TF-IDF Vectorizer, and Handcrafted Scaler
# ============================================================================
print("\n[Step 10] Saving models and components...")

models_dir = Path(__file__).parent / "4_models"
models_dir.mkdir(exist_ok=True)

# Save model
model_file = models_dir / "phishing_model_enhanced.joblib"
joblib.dump(model, model_file)
print(f"✓ Model saved: {model_file.name}")

# Save scaler for combined features
scaler_file = models_dir / "scaler_enhanced.joblib"
joblib.dump(scaler_all, scaler_file)
print(f"✓ Scaler saved: {scaler_file.name}")

# Save TF-IDF vectorizer
tfidf_file = models_dir / "tfidf_vectorizer_enhanced.joblib"
joblib.dump(tfidf_vectorizer, tfidf_file)
print(f"✓ TF-IDF vectorizer saved: {tfidf_file.name}")

# Save handcrafted features scaler
handcrafted_scaler_file = models_dir / "handcrafted_scaler_enhanced.joblib"
joblib.dump(scaler_handcrafted, handcrafted_scaler_file)
print(f"✓ Handcrafted features scaler saved: {handcrafted_scaler_file.name}")

# ============================================================================
# Step 11: Also save as pickle for compatibility
# ============================================================================
print("\n[Step 11] Saving backup pickle format...")

model_pkl_file = models_dir / "phishing_model_enhanced.pkl"
scaler_pkl_file = models_dir / "scaler_enhanced.pkl"
tfidf_pkl_file = models_dir / "tfidf_vectorizer_enhanced.pkl"
handcrafted_pkl_file = models_dir / "handcrafted_scaler_enhanced.pkl"

with open(model_pkl_file, 'wb') as f:
    pickle.dump(model, f)
with open(scaler_pkl_file, 'wb') as f:
    pickle.dump(scaler_all, f)
with open(tfidf_pkl_file, 'wb') as f:
    pickle.dump(tfidf_vectorizer, f)
with open(handcrafted_pkl_file, 'wb') as f:
    pickle.dump(scaler_handcrafted, f)

print(f"✓ Pickle format backups saved")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 100)
print("TRAINING COMPLETE - SUMMARY")
print("=" * 100)
print(f"""
Dataset:
  - Total samples: {len(df_clean)}
  - Phishing: {(y == 1).sum()}, Legitimate: {(y == 0).sum()}

Features:
  - TF-IDF text features: 5,000
  - Handcrafted phishing indicators: 20
  - Total features: 5,020

Model Performance:
  - Test Accuracy: {test_accuracy:.2%}
  - Test Precision: {test_precision:.2%}
  - Test Recall: {test_recall:.2%}
  - Test F1-Score: {test_f1:.4f}
  - Cross-validation F1: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}

Saved Files (in 4_models/):
  - phishing_model_enhanced.joblib
  - scaler_enhanced.joblib
  - tfidf_vectorizer_enhanced.joblib
  - handcrafted_scaler_enhanced.joblib
  - (+ .pkl backup versions)

Next Steps:
  1. Update Phase3_development/config.py to point to new models:
     - MODEL_PATH = 'models/phishing_model_enhanced.joblib'
     - SCALER_PATH = 'models/scaler_enhanced.joblib'
     - Update references to tfidf_vectorizer_enhanced.joblib and handcrafted_scaler_enhanced.joblib

  2. Update Phase3_development/models/detector.py to:
     - Use EnhancedFeatureExtractor
     - Load and use TF-IDF vectorizer
     - Combine TF-IDF features with handcrafted features
     - Include threat_indicators in results

  3. Test with the corporate emails that were failing before
""")
print("=" * 100)
