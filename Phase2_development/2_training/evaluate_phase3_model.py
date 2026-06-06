#!/usr/bin/env python3
"""
Phase 3 Evaluation Script
=========================
Loads the deployed Phase 3 model artefacts (joblib files in Phase3_development/models/)
and evaluates them against a held-out sample of the combined dataset.

Produces:
  - Terminal output with Accuracy / Precision / Recall / F1 / ROC-AUC and a confusion matrix
  - confusion_matrix.png  (Figure 11 in the report)
  - roc_pr_curves.png     (Figure 12 in the report)

Usage:
  cd Phase2_development/2_training
  python3 evaluate_phase3_model.py
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, ConfusionMatrixDisplay,
    RocCurveDisplay, PrecisionRecallDisplay,
)

ROOT = Path(__file__).resolve().parents[2]
MODELS = ROOT / "Phase3_development" / "models"
DATA_DIR = ROOT / "Phase2_development" / "1_data_combined"

# Use the exact same 20-feature extractor used during retraining
sys.path.insert(0, str(Path(__file__).parent))
from retrain_phase3_model import extract_handcrafted_20

print("=" * 70)
print("PHASE 3 MODEL EVALUATION")
print("=" * 70)

# -- Load artefacts ----------------------------------------------------------
print("\n[1/4] Loading model artefacts ...")
model = joblib.load(MODELS / "phishing_model_enhanced.joblib")
tfidf = joblib.load(MODELS / "tfidf_vectorizer_enhanced.joblib")
scaler = joblib.load(MODELS / "scaler_enhanced.joblib")
hc_scaler = joblib.load(MODELS / "handcrafted_scaler_enhanced.joblib")
print(f"  Model: {type(model).__name__}")
print(f"  TF-IDF vocab size: {len(tfidf.vocabulary_)}")
print(f"  Handcrafted features: {getattr(hc_scaler,'n_features_in_', 20)}")

# -- Load dataset (mirror retrain_phase3_model.py exactly to get held-out test set) -
print("\n[2/4] Loading evaluation dataset (held-out 20% test split) ...")
from sklearn.model_selection import train_test_split as _tts

frames = []
try:
    m = pd.read_csv(DATA_DIR / "naser_phishing_email_dataset.csv", on_bad_lines="skip")
    m = m.dropna(subset=["Email Text", "Email Type"])
    m["text"] = m["Email Text"].astype(str)
    m["label"] = m["Email Type"].map({"Phishing Email": 1, "Safe Email": 0})
    m = m.dropna(subset=["label"]); m["label"] = m["label"].astype(int)
    frames.append(m[["text", "label"]])
except FileNotFoundError:
    pass
try:
    k = pd.read_csv(DATA_DIR / "phishing_legit_dataset_KD_10000.csv", on_bad_lines="skip")
    k = k.dropna(subset=["text", "label"])
    k["label"] = pd.to_numeric(k["label"], errors="coerce")
    k = k.dropna(subset=["label"]); k["label"] = k["label"].astype(int)
    frames.append(k[["text", "label"]])
except FileNotFoundError:
    pass

df_all = pd.concat(frames, ignore_index=True).drop_duplicates(subset="text").reset_index(drop=True)
mc = df_all["label"].value_counts().min()
df_bal = pd.concat([
    df_all[df_all["label"] == 0].sample(mc, random_state=42),
    df_all[df_all["label"] == 1].sample(mc, random_state=42),
]).sample(frac=1, random_state=42).reset_index(drop=True)

# Same split as retrain_phase3_model.py
_, X_test_text, _, y_test = _tts(
    df_bal["text"].astype(str).tolist(),
    df_bal["label"].astype(int).values,
    test_size=0.20, stratify=df_bal["label"].astype(int).values, random_state=42
)
df = pd.DataFrame({"text": X_test_text, "label": y_test})
print(f"  Evaluating on {len(df):,} held-out samples")
print(f"  Phishing: {(df['label'] == 1).sum()}  Legitimate: {(df['label'] == 0).sum()}")

# -- Extract features --------------------------------------------------------
print("\n[3/4] Extracting features ...")
texts = df["text"].astype(str).tolist()
labels = df["label"].astype(int).values

# TF-IDF block
X_tfidf = tfidf.transform(texts)

# Handcrafted block — uses the SAME 20-feature extractor as retraining
hc = np.array([extract_handcrafted_20(t) for t in texts], dtype=float)

# Combine TF-IDF (5000) + Handcrafted (20) → 5020
from scipy.sparse import hstack, csr_matrix
X_combined = hstack([X_tfidf, csr_matrix(hc)]).tocsr()
# Apply the global StandardScaler trained on the 5020-dim combined matrix
X = scaler.transform(X_combined) if 'scaler' in dir() else X_combined
print(f"  Final feature matrix: {X.shape}")

# -- Predict and report ------------------------------------------------------
print("\n[4/4] Predicting ...")
y_proba = model.predict_proba(X)[:, 1]
THRESH = 0.50
y_pred = (y_proba >= THRESH).astype(int)

acc = accuracy_score(labels, y_pred)
prec = precision_score(labels, y_pred, zero_division=0)
rec = recall_score(labels, y_pred, zero_division=0)
f1 = f1_score(labels, y_pred, zero_division=0)
auc = roc_auc_score(labels, y_proba)

cm = confusion_matrix(labels, y_pred)

print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)
print(f"  Threshold      : {THRESH}")
print(f"  Accuracy       : {acc:.4f}")
print(f"  Precision      : {prec:.4f}")
print(f"  Recall         : {rec:.4f}")
print(f"  F1-score       : {f1:.4f}")
print(f"  ROC-AUC        : {auc:.4f}")
print()
print("  Confusion Matrix")
print("                   Predicted Legit  Predicted Phish")
print(f"  Actual Legit    {cm[0,0]:>15}  {cm[0,1]:>15}")
print(f"  Actual Phish    {cm[1,0]:>15}  {cm[1,1]:>15}")

# -- Save plots --------------------------------------------------------------
print("\nSaving plots ...")
out = Path(__file__).parent
fig, ax = plt.subplots(figsize=(6, 5))
ConfusionMatrixDisplay(cm, display_labels=["Legitimate", "Phishing"]).plot(
    ax=ax, cmap="Blues", values_format="d"
)
ax.set_title("Phase 3 Model — Confusion Matrix")
plt.tight_layout()
plt.savefig(out / "confusion_matrix.png", dpi=150, bbox_inches="tight")
print("  -> confusion_matrix.png  (saved in this folder)")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
RocCurveDisplay.from_predictions(labels, y_proba, ax=axes[0])
axes[0].set_title("ROC Curve")
PrecisionRecallDisplay.from_predictions(labels, y_proba, ax=axes[1])
axes[1].set_title("Precision-Recall Curve")
plt.tight_layout()
plt.savefig(out / "roc_pr_curves.png", dpi=150, bbox_inches="tight")
print("  -> roc_pr_curves.png  (saved in this folder)")
