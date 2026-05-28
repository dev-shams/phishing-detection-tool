"""
Download and prepare combined datasets for model retraining
- Kaggle 2026 Phishing Dataset (10,000+ emails)
- MeAJOR Corpus (135,894 emails)
"""

import os
import pandas as pd
from pathlib import Path
import zipfile
import json

# Create output directory
output_dir = Path(__file__).parent / "1_data_combined"
output_dir.mkdir(exist_ok=True)

print("=" * 80)
print("DOWNLOADING DATASETS FOR MODEL RETRAINING")
print("=" * 80)

# ============================================================================
# STEP 1: Download Kaggle 2026 Dataset
# ============================================================================
print("\n[STEP 1] Downloading Kaggle 2026 Dataset...")
print("-" * 80)

try:
    from kaggle.api.kaggle_api_extended import KaggleApi

    # Initialize Kaggle API
    api = KaggleApi()
    api.authenticate()

    # Download dataset
    kaggle_dir = output_dir / "kaggle_2026"
    kaggle_dir.mkdir(exist_ok=True)

    print(f"Downloading to: {kaggle_dir}")
    api.dataset_download_files(
        'kuladeep19/phishing-and-legitimate-emails-dataset',
        path=str(kaggle_dir),
        unzip=True
    )

    print("✓ Kaggle dataset downloaded successfully")

    # Check what files were downloaded
    kaggle_files = list(kaggle_dir.glob("*"))
    print(f"  Files found: {len(kaggle_files)}")
    for f in kaggle_files[:5]:
        print(f"    - {f.name}")

except Exception as e:
    print(f"✗ Error downloading Kaggle dataset: {str(e)}")
    print("  Make sure your Kaggle API key is set up at ~/.kaggle/kaggle.json")

# ============================================================================
# STEP 2: Download MeAJOR Corpus from HuggingFace
# ============================================================================
print("\n[STEP 2] Downloading MeAJOR Corpus from HuggingFace...")
print("-" * 80)

try:
    from datasets import load_dataset

    print("Loading MeAJOR Corpus dataset...")

    # Load the dataset from HuggingFace
    dataset = load_dataset("zefang-liu/phishing-email-dataset")

    # Convert to pandas DataFrame
    df_major = dataset['train'].to_pandas()

    # Save as CSV
    major_csv = output_dir / "meajor_corpus.csv"
    df_major.to_csv(major_csv, index=False)

    print(f"✓ MeAJOR Corpus downloaded successfully")
    print(f"  Samples: {len(df_major)}")
    print(f"  Columns: {list(df_major.columns)}")
    print(f"  Saved to: {major_csv}")

except Exception as e:
    print(f"✗ Error downloading MeAJOR Corpus: {str(e)}")
    print("  Trying alternative method...")

    # Alternative: Create a placeholder for manual download
    print("\n  ALTERNATIVE: Manual download from HuggingFace")
    print("  Visit: https://huggingface.co/datasets/zefang-liu/phishing-email-dataset")
    print("  Download the dataset files and place them in:")
    print(f"  {output_dir / 'meajor_corpus'}/")

# ============================================================================
# STEP 3: Summary
# ============================================================================
print("\n" + "=" * 80)
print("DOWNLOAD SUMMARY")
print("=" * 80)

print(f"\nDatasets downloaded to: {output_dir}")
print("\nNext steps:")
print("1. Check that files are present in the output directory")
print("2. Run: python prepare_datasets.py")
print("3. This will combine and clean the datasets")

print("\n" + "=" * 80)
