"""
Prepare and combine datasets for model retraining
- Standardize formats
- Remove duplicates
- Check class balance
- Save combined dataset
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================
data_dir = Path(__file__).parent / "1_data_combined"
output_file = Path(__file__).parent / "1_data_combined" / "combined_dataset.csv"

print("=" * 80)
print("PREPARING AND COMBINING DATASETS")
print("=" * 80)

# ============================================================================
# STEP 1: Load Kaggle 2026 Dataset
# ============================================================================
print("\n[STEP 1] Loading Kaggle 2026 Dataset...")
print("-" * 80)

df_kaggle = None
try:
    # Look for Kaggle CSV files - search in data_dir and kaggle_2026 subdirectory
    csv_files = list(data_dir.glob("phishing_legit*.csv"))

    if not csv_files:
        # Try kaggle_2026 subdirectory
        kaggle_dir = data_dir / "kaggle_2026"
        csv_files = list(kaggle_dir.glob("*.csv"))

    if csv_files:
        kaggle_csv = csv_files[0]
        df_kaggle = pd.read_csv(kaggle_csv)
        print(f"✓ Loaded: {kaggle_csv.name}")
        print(f"  Shape: {df_kaggle.shape}")
        print(f"  Columns: {list(df_kaggle.columns)}")
    else:
        print("✗ No Kaggle CSV files found")
        df_kaggle = None

except Exception as e:
    print(f"✗ Error loading Kaggle dataset: {str(e)}")
    df_kaggle = None

# ============================================================================
# STEP 2: Load MeAJOR Corpus
# ============================================================================
print("\n[STEP 2] Loading MeAJOR Corpus...")
print("-" * 80)

try:
    meajor_csv = data_dir / "meajor_corpus.csv"

    if meajor_csv.exists():
        df_meajor = pd.read_csv(meajor_csv)
        print(f"✓ Loaded: {meajor_csv.name}")
        print(f"  Shape: {df_meajor.shape}")
        print(f"  Columns: {list(df_meajor.columns)}")
    else:
        print(f"✗ File not found: {meajor_csv}")
        print("  Make sure you've run download_datasets.py first")
        df_meajor = None

except Exception as e:
    print(f"✗ Error loading MeAJOR: {str(e)}")
    df_meajor = None

# ============================================================================
# STEP 3: Standardize and Combine
# ============================================================================
print("\n[STEP 3] Standardizing and Combining Datasets...")
print("-" * 80)

dfs_to_combine = []

# Process Kaggle dataset
if df_kaggle is not None:
    print("Processing Kaggle 2026...")
    # Determine label column
    label_col = None
    for col in df_kaggle.columns:
        if 'label' in col.lower() or 'class' in col.lower():
            label_col = col
            break

    if label_col:
        df_kaggle_clean = df_kaggle.copy()
        # Standardize column names
        df_kaggle_clean.columns = df_kaggle_clean.columns.str.lower()
        dfs_to_combine.append(df_kaggle_clean)
        print(f"  ✓ Processed with {len(df_kaggle_clean)} emails")
    else:
        print("  ✗ Could not find label column")

# Process MeAJOR dataset
if df_meajor is not None:
    print("Processing MeAJOR Corpus...")
    df_meajor_clean = df_meajor.copy()
    # Standardize column names
    df_meajor_clean.columns = df_meajor_clean.columns.str.lower()
    dfs_to_combine.append(df_meajor_clean)
    print(f"  ✓ Processed with {len(df_meajor_clean)} emails")

# Combine datasets
if dfs_to_combine:
    print("\nCombining datasets...")
    df_combined = pd.concat(dfs_to_combine, ignore_index=True)
    print(f"✓ Combined shape: {df_combined.shape}")
else:
    print("✗ No datasets to combine")
    df_combined = None

# ============================================================================
# STEP 4: Remove Duplicates
# ============================================================================
if df_combined is not None:
    print("\n[STEP 4] Removing Duplicates...")
    print("-" * 80)

    initial_count = len(df_combined)

    # Remove exact duplicates across all columns
    df_combined = df_combined.drop_duplicates()

    duplicates_removed = initial_count - len(df_combined)
    print(f"Duplicates removed: {duplicates_removed}")
    print(f"Remaining samples: {len(df_combined)}")

    # ========================================================================
    # STEP 5: Analyze Class Balance
    # ========================================================================
    print("\n[STEP 5] Analyzing Class Balance...")
    print("-" * 80)

    # Find label column
    label_col = None
    for col in df_combined.columns:
        if 'label' in col.lower() or 'class' in col.lower():
            label_col = col
            break

    if label_col:
        class_dist = df_combined[label_col].value_counts()
        print(f"Class distribution:")
        for label, count in class_dist.items():
            pct = (count / len(df_combined)) * 100
            print(f"  {label}: {count} ({pct:.1f}%)")

    # ========================================================================
    # STEP 6: Save Combined Dataset
    # ========================================================================
    print("\n[STEP 6] Saving Combined Dataset...")
    print("-" * 80)

    df_combined.to_csv(output_file, index=False)
    print(f"✓ Saved to: {output_file}")
    print(f"  Total samples: {len(df_combined)}")
    print(f"  Total columns: {len(df_combined.columns)}")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("PREPARATION COMPLETE")
    print("=" * 80)
    print(f"\nCombined dataset ready for training:")
    print(f"  File: {output_file}")
    print(f"  Samples: {len(df_combined):,}")
    print(f"  Columns: {list(df_combined.columns)}")
    print(f"\nNext step: Retrain model with this combined dataset")
    print("=" * 80)

else:
    print("\n✗ Could not prepare dataset. Check errors above.")
