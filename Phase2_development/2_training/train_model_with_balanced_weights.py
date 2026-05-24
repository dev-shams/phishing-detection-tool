"""
FINAL FIX: Train with Balanced Class Weights
NOW that features are extracting properly, properly handle class imbalance
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

sys.path.insert(0, str(Path(__file__).parent.parent))

from feature_extractor import FeatureExtractor
from ml_model import PhishingDetectionModel

def train_with_balanced_weights():
    """Train with PROPER balanced class weights (now that features work)"""

    print("\n" + "="*70)
    print("FINAL FIX: TRAINING WITH BALANCED CLASS WEIGHTS")
    print("="*70)

    # Paths
    data_path = Path(__file__).parent.parent / 'data' / 'phishing_emails_processed.csv'
    models_dir = Path(__file__).parent.parent / '4_models'
    models_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    print("\nLoading data...")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} emails")

    phishing_count = (df['label'] == 1).sum()
    legit_count = (df['label'] == 0).sum()

    print(f"\nClass Distribution:")
    print(f"  Phishing: {phishing_count:,} ({phishing_count/len(df)*100:.1f}%)")
    print(f"  Legitimate: {legit_count:,} ({legit_count/len(df)*100:.1f}%)")

    # Extract features (using FIXED column name 'email')
    print("\nExtracting features...")
    extractor = FeatureExtractor()

    features_list = []
    labels_list = []

    for idx, (_, row) in enumerate(df.iterrows()):
        if (idx + 1) % 10000 == 0:
            print(f"  Processed {idx + 1}/{len(df)}")

        email_data = {
            'body': str(row.get('email', '')),
            'subject': '',
            'sender': '',
            'urls': [],
            'headers': {}
        }

        try:
            features = extractor.extract_all_features(email_data)
            features_list.append(features)
            labels_list.append(row['label'])
        except:
            continue

    feature_names = list(features_list[0].keys())
    X = np.array([list(f.values()) for f in features_list])
    y = np.array(labels_list)

    print(f"✓ Extracted features: {X.shape}")

    # Verify features have variance
    feature_vars = X.var(axis=0)
    non_zero_vars = (feature_vars > 0).sum()
    print(f"  Features with variance: {non_zero_vars}/{len(feature_names)}")

    # ============================================
    # KEY: Use class_weight='balanced' PROPERLY
    # ============================================
    print("\n" + "="*70)
    print("TRAINING WITH BALANCED CLASS WEIGHTS")
    print("="*70)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"\nTrain set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    print(f"Train - Phishing: {(y_train == 1).sum()}, Legitimate: {(y_train == 0).sum()}")
    print(f"Test - Phishing: {(y_test == 1).sum()}, Legitimate: {(y_test == 0).sum()}")

    # Create model with BALANCED class weights
    print("\nCreating Random Forest with class_weight='balanced'...")
    model = RandomForestClassifier(
        n_estimators=200,  # More trees for stability
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'  # THIS IS KEY
    )

    print("Training...")
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_pred_proba)

    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Accuracy:  {accuracy:.2%}")
    print(f"Precision: {precision:.2%}")
    print(f"Recall:    {recall:.2%}")
    print(f"F1-Score:  {f1:.2%}")
    print(f"ROC-AUC:   {roc_auc:.2%}")

    # Save
    print("\nSaving model...")
    import pickle

    model_path = str(models_dir / 'phishing_model_phase2.pkl')
    scaler_path = str(models_dir / 'scaler_phase2.pkl')

    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)

    print(f"✓ Model saved to {model_path}")
    print(f"✓ Scaler saved to {scaler_path}")

    # Save summary
    summary_path = Path(__file__).parent.parent / '5_results' / 'final_training_summary.txt'
    with open(summary_path, 'w') as f:
        f.write(f"PHASE 2 - FINAL TRAINING WITH BALANCED WEIGHTS\n")
        f.write(f"{'='*70}\n\n")
        f.write(f"Data: {len(df)} emails\n")
        f.write(f"Train/Test Split: {len(X_train)}/{len(X_test)}\n")
        f.write(f"Features: {X.shape[1]}\n\n")
        f.write(f"Results:\n")
        f.write(f"  Accuracy:  {accuracy:.2%}\n")
        f.write(f"  Precision: {precision:.2%}\n")
        f.write(f"  Recall:    {recall:.2%}\n")
        f.write(f"  F1-Score:  {f1:.2%}\n")
        f.write(f"  ROC-AUC:   {roc_auc:.2%}\n")

    print(f"✓ Summary saved")

    return model, scaler, accuracy, precision, recall, f1, roc_auc

if __name__ == "__main__":
    try:
        model, scaler, acc, prec, rec, f1, auc = train_with_balanced_weights()
        print("\n✓ Training complete!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
