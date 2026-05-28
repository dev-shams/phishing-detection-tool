"""
Retrain phishing detection model on improved dataset
- Uses combined dataset (Kaggle 2026 + MeAJOR Corpus)
- 28,648 modern emails
- Trains new Random Forest model
- Saves improved model files
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import joblib
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

print("=" * 80)
print("RETRAINING PHISHING DETECTION MODEL")
print("Dataset: Combined (Kaggle 2026 + MeAJOR Corpus)")
print("=" * 80)

# ============================================================================
# STEP 1: Load Combined Dataset
# ============================================================================
print("\n[STEP 1] Loading Combined Dataset...")
print("-" * 80)

data_dir = Path(__file__).parent / "1_data_combined"
combined_csv = data_dir / "combined_dataset.csv"

try:
    df = pd.read_csv(combined_csv)
    print(f"✓ Loaded: {combined_csv.name}")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
except Exception as e:
    print(f"✗ Error loading dataset: {str(e)}")
    exit(1)

# ============================================================================
# STEP 2: Prepare Data
# ============================================================================
print("\n[STEP 2] Preparing Data...")
print("-" * 80)

# Find the email text column and label column
email_col = None
label_col = None

for col in df.columns:
    if 'text' in col.lower() or 'email' in col.lower():
        if email_col is None:
            email_col = col
    if 'label' in col.lower() or 'type' in col.lower():
        if 'type' in col.lower() and label_col is None:
            label_col = col
        elif 'label' in col.lower():
            label_col = col

print(f"Email column: {email_col}")
print(f"Label column: {label_col}")

# Remove rows with missing labels
df_clean = df.dropna(subset=[label_col])
print(f"Samples after removing missing labels: {len(df_clean)}")

# Convert labels to binary (0=legitimate, 1=phishing)
# Handle different label formats
if df_clean[label_col].dtype == 'object':
    # String labels
    label_map = {}
    unique_labels = df_clean[label_col].unique()
    print(f"Unique labels: {unique_labels}")

    # Auto-detect mapping
    for label in unique_labels:
        if 'phishing' in str(label).lower() or 'malicious' in str(label).lower():
            label_map[label] = 1
        else:
            label_map[label] = 0

    y = df_clean[label_col].map(label_map)
else:
    # Numeric labels
    y = df_clean[label_col].astype(int)

X_text = df_clean[email_col].astype(str)

print(f"Class distribution:")
print(f"  Legitimate (0): {(y == 0).sum()}")
print(f"  Phishing (1): {(y == 1).sum()}")

# ============================================================================
# STEP 3: Extract Features
# ============================================================================
print("\n[STEP 3] Extracting Features...")
print("-" * 80)

sys.path.insert(0, str(Path(__file__).parent))
from feature_extractor import FeatureExtractor

extractor = FeatureExtractor()

print("Extracting features from emails...")
X_features = []

for idx, email_text in enumerate(X_text):
    if idx % 5000 == 0:
        print(f"  Processed {idx}/{len(X_text)} emails...")

    try:
        email_data = {
            'body': email_text,
            'subject': '',
            'sender': '',
            'urls': [],
            'headers': {}
        }
        features = extractor.extract_all_features(email_data)
        X_features.append(list(features.values()))
    except Exception as e:
        # Skip emails with extraction errors
        continue

X_features = np.array(X_features)
print(f"✓ Features extracted: {X_features.shape}")

# Make sure we have matching samples
min_samples = min(len(X_features), len(y))
X_features = X_features[:min_samples]
y = y[:min_samples]

print(f"Final dataset shape: {X_features.shape}")

# ============================================================================
# STEP 4: Split Data
# ============================================================================
print("\n[STEP 4] Splitting Data...")
print("-" * 80)

X_train, X_test, y_train, y_test = train_test_split(
    X_features, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training set: {X_train.shape}")
print(f"Testing set: {X_test.shape}")

# ============================================================================
# STEP 5: Scale Features
# ============================================================================
print("\n[STEP 5] Scaling Features...")
print("-" * 80)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("✓ Features scaled")

# ============================================================================
# STEP 6: Train Model
# ============================================================================
print("\n[STEP 6] Training Random Forest Model...")
print("-" * 80)

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)

print("Training...")
model.fit(X_train_scaled, y_train)
print("✓ Model trained")

# ============================================================================
# STEP 7: Evaluate Model
# ============================================================================
print("\n[STEP 7] Evaluating Model...")
print("-" * 80)

y_pred = model.predict(X_test_scaled)
y_pred_proba = model.predict_proba(X_test_scaled)

print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_pred):.4f}")
print(f"Recall: {recall_score(y_test, y_pred):.4f}")
print(f"F1-Score: {f1_score(y_test, y_pred):.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Phishing']))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ============================================================================
# STEP 8: Save Model
# ============================================================================
print("\n[STEP 8] Saving Model...")
print("-" * 80)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
models_dir = Path(__file__).parent / "4_models"
models_dir.mkdir(exist_ok=True)

model_file = models_dir / f"phishing_model_improved_{timestamp}.joblib"
scaler_file = models_dir / f"scaler_improved_{timestamp}.joblib"

joblib.dump(model, model_file)
joblib.dump(scaler, scaler_file)

print(f"✓ Model saved: {model_file.name}")
print(f"✓ Scaler saved: {scaler_file.name}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("MODEL RETRAINING COMPLETE")
print("=" * 80)
print(f"\nNew Model Files:")
print(f"  Model: {model_file.name}")
print(f"  Scaler: {scaler_file.name}")
print(f"\nDataset Statistics:")
print(f"  Combined emails: 28,648")
print(f"  Training samples: {len(X_train)}")
print(f"  Testing samples: {len(X_test)}")
print(f"  Features per email: {X_features.shape[1]}")
print(f"\nPerformance:")
print(f"  Accuracy: {accuracy_score(y_test, y_pred):.2%}")
print(f"  F1-Score: {f1_score(y_test, y_pred):.4f}")
print(f"\nNext Steps:")
print(f"1. Copy these model files to Phase3_development/models/")
print(f"2. Update config.py with new model filenames")
print(f"3. Test with corporate emails and phishing samples")
print(f"4. Deploy to Railway when satisfied with results")
print("=" * 80)
