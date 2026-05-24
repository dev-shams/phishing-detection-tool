#!/usr/bin/env python3
"""
Phase 2: Download Real Phishing Email Dataset from Kaggle

Downloads the "Phishing Email Dataset" which contains:
- 27,747+ real phishing emails
- Multiple sources: Enron, CEAS, Nazario, Nigerian Fraud, SpamAssassin
- Labeled as phishing or legitimate

This replaces the synthetic data from Phase 1.
"""

import os
import sys
from pathlib import Path

print("\n" + "="*70)
print("PHASE 2: DOWNLOAD REAL PHISHING EMAIL DATASET")
print("="*70)

# Check if Kaggle API is installed
try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    print("\n✓ Kaggle API installed")
except ImportError:
    print("\n✗ Kaggle API not installed")
    print("\nInstall with: pip install kaggle --break-system-packages")
    sys.exit(1)

# Setup Kaggle credentials
print("\nAuthenticating with Kaggle...")
api = KaggleApi()

try:
    api.authenticate()
    print("✓ Kaggle credentials found and authenticated")
except Exception as e:
    print("✗ Kaggle authentication failed")
    print("\nTo set up Kaggle credentials:")
    print("1. Go to: https://www.kaggle.com/settings/account")
    print("2. Click 'Create New API Token' - downloads kaggle.json")
    print("3. Save to: ~/.kaggle/kaggle.json")
    print("4. Run: chmod 600 ~/.kaggle/kaggle.json")
    print(f"\nError: {str(e)}")
    sys.exit(1)

# Create data directory
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)

print(f"\nDownloading dataset to: {data_dir}")
print("Dataset: Phishing Email Dataset for Machine Learning")
print("Author: Naser Abdullah Alam")
print("URL: https://www.kaggle.com/datasets/shashwatwork/phishing-dataset-for-machine-learning")

# Download dataset
print("\nDownloading... (this may take 5-10 minutes)")
try:
    api.dataset_download_files(
        'shashwatwork/phishing-dataset-for-machine-learning',
        path=str(data_dir),
        unzip=True
    )
    print("✓ Dataset downloaded and extracted successfully")
except Exception as e:
    print(f"✗ Download failed: {str(e)}")
    print("\nTroubleshooting:")
    print("- Check your Kaggle credentials are correct")
    print("- Check your internet connection")
    print("- Try again in a few minutes")
    sys.exit(1)

# List downloaded files
print("\n" + "="*70)
print("DOWNLOADED FILES:")
print("="*70)

csv_files = list(data_dir.glob("*.csv"))
if not csv_files:
    print("⚠ No CSV files found in downloaded data")
    sys.exit(1)

total_size_mb = 0
for csv_file in csv_files:
    size_mb = csv_file.stat().st_size / (1024*1024)
    total_size_mb += size_mb
    print(f"  ✓ {csv_file.name:<40} {size_mb:>8.2f} MB")

print("="*70)
print(f"Total data size: {total_size_mb:.2f} MB")
print("="*70)

print("\n✓ DATASET DOWNLOAD COMPLETE")
print("\nNext step: Run python 1_data/preprocess_data.py")
print("="*70 + "\n")
