"""
Retrain phishing detection model and save as PICKLE (.pkl) format
This avoids joblib version issues
"""

import pandas as pd
import numpy as np
import sys
import pickle
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import warnings

warnings.filterwarnings('ignore')

print("=" * 80)
print("RETRAINING AND SAVING AS PICKLE FORMAT")
print("=" * 80)

# Load combined dataset
data_dir = Path(__file__).parent / "1_data_combined"
combined_csv = data_dir / "combined_dataset.csv"

df = pd.read_csv(combined_csv)
print(f"✓ Loaded dataset: {df.shape}")

# Prepare data
email_col = 'text'
label_col = 'label'
df_clean = df.dropna(subset=[label_col])
y = df_clean[label_col].astype(int)
X_text = df_clean[email_col].astype(str)

print(f"Samples: {len(df_clean)}")

# Extract features
sys.path.insert(0, str(Path(__file__).parent))
from feature_extractor import FeatureExtractor

extractor = FeatureExtractor()
X_features = []

for idx, email_text in enumerate(X_text):
    if idx % 5000 == 0:
        print(f"  Processing {idx}/{len(X_text)}...")
    try:
        email_data = {'body': email_text, 'subject': '', 'sender': '', 'urls': [], 'headers': {}}
        features = extractor.extract_all_features(email_data)
        X_features.append(list(features.values()))
    except:
        continue

X_features = np.array(X_features)
min_samples = min(len(X_features), len(y))
X_features = X_features[:min_samples]
y = y[:min_samples]

print(f"✓ Features extracted: {X_features.shape}")

# Split and train
X_train, X_test, y_train, y_test = train_test_split(X_features, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = RandomForestClassifier(n_estimators=200, max_depth=20, min_samples_split=10, min_samples_leaf=5, random_state=42, n_jobs=-1, class_weight='balanced')
model.fit(X_train_scaled, y_train)

y_pred = model.predict(X_test_scaled)
print(f"✓ Model trained - Accuracy: {accuracy_score(y_test, y_pred):.4f}, F1: {f1_score(y_test, y_pred):.4f}")

# Save as PICKLE
models_dir = Path(__file__).parent / "4_models"
models_dir.mkdir(exist_ok=True)

model_file = models_dir / "phishing_model_improved.pkl"
scaler_file = models_dir / "scaler_improved.pkl"

with open(model_file, 'wb') as f:
    pickle.dump(model, f)

with open(scaler_file, 'wb') as f:
    pickle.dump(scaler, f)

print(f"✓ Model saved as pickle: {model_file.name}")
print(f"✓ Scaler saved as pickle: {scaler_file.name}")
