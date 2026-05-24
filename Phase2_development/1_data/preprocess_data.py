#!/usr/bin/env python3
"""
Phase 2: Preprocess Real Email Data

Takes downloaded Kaggle CSV files and:
- Combines all datasets
- Removes duplicates and null values
- Cleans email text
- Creates training dataset ready for model training

Input: data/*.csv files from Kaggle
Output: data/phishing_emails_processed.csv
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
import re

print("\n" + "="*70)
print("PHASE 2: PREPROCESS EMAIL DATA")
print("="*70)

# Get data directory
data_dir = Path(__file__).parent.parent / "data"

if not data_dir.exists():
    print("\n✗ Data directory not found")
    print("Run this first: python 1_data/download_dataset.py")
    sys.exit(1)

# Find all CSV files
csv_files = list(data_dir.glob("*.csv"))

if not csv_files:
    print("\n✗ No CSV files found in data directory")
    print(f"Expected CSV files in: {data_dir}")
    sys.exit(1)

print(f"\nFound {len(csv_files)} CSV files:")
for f in csv_files:
    print(f"  ✓ {f.name}")

# Load and combine datasets
print("\nLoading datasets...")
dfs = []
total_rows = 0

for csv_file in csv_files:
    try:
        df = pd.read_csv(csv_file)
        print(f"  ✓ {csv_file.name}: {len(df)} rows, {len(df.columns)} columns")
        total_rows += len(df)
        dfs.append(df)
    except Exception as e:
        print(f"  ⚠ Error reading {csv_file.name}: {str(e)}")
        continue

if not dfs:
    print("\n✗ No valid CSV files could be loaded")
    sys.exit(1)

# Combine all dataframes
print(f"\nCombining {len(dfs)} datasets...")
df_combined = pd.concat(dfs, ignore_index=True)
print(f"  Total rows: {len(df_combined)}")
print(f"  Total columns: {len(df_combined.columns)}")

# Show column names
print(f"\nColumns in dataset:")
for i, col in enumerate(df_combined.columns):
    print(f"  {i}: {col}")

# Find email and label columns
print("\nAnalyzing data structure...")

# Common email column names
email_cols = ['Email', 'email', 'Email Text', 'email_text', 'body', 'Body', 'message', 'Message']
label_cols = ['Label', 'label', 'Class', 'class', 'Category', 'category', 'Type', 'type']

email_col = None
label_col = None

for col in df_combined.columns:
    if col in email_cols or 'email' in col.lower() or 'text' in col.lower() or 'body' in col.lower():
        if email_col is None:
            email_col = col
    if col in label_cols or 'label' in col.lower() or 'class' in col.lower():
        if label_col is None:
            label_col = col

if email_col is None or label_col is None:
    print("\n⚠ Could not auto-detect email/label columns")
    print(f"Email column (found): {email_col}")
    print(f"Label column (found): {label_col}")
    print("\nUsing first text column as email, last column as label")
    email_col = df_combined.columns[0]
    label_col = df_combined.columns[-1]

print(f"  Email column: {email_col}")
print(f"  Label column: {label_col}")

# Check data
print(f"\nLabel distribution:")
if label_col in df_combined.columns:
    print(df_combined[label_col].value_counts())

# Remove null values
print(f"\nCleaning data...")
initial_rows = len(df_combined)

# Remove rows with null email or label
df_combined = df_combined.dropna(subset=[email_col, label_col])
null_removed = initial_rows - len(df_combined)
print(f"  Removed null values: {null_removed} rows")

# Remove duplicates
initial_rows = len(df_combined)
df_combined = df_combined.drop_duplicates(subset=[email_col])
duplicates_removed = initial_rows - len(df_combined)
print(f"  Removed duplicates: {duplicates_removed} rows")

# Clean email text
print(f"\nCleaning email text...")

def clean_email_text(text):
    """Clean email text"""
    if not isinstance(text, str):
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Remove extra whitespace
    text = ' '.join(text.split())

    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,-?!:;\']', '', text)

    return text.strip()

df_combined[email_col] = df_combined[email_col].apply(clean_email_text)

# Remove empty emails
initial_rows = len(df_combined)
df_combined = df_combined[df_combined[email_col].str.len() > 0]
empty_removed = initial_rows - len(df_combined)
print(f"  Removed empty emails: {empty_removed} rows")

# Normalize labels
print(f"\nNormalizing labels...")
unique_labels = df_combined[label_col].unique()
print(f"  Unique labels: {unique_labels}")

# Try to detect phishing labels
label_mapping = {}
for label in unique_labels:
    label_str = str(label).lower().strip()
    if any(word in label_str for word in ['phishing', 'phish', 'spam', '1']):
        label_mapping[label] = 1  # Phishing
    else:
        label_mapping[label] = 0  # Legitimate

print(f"  Label mapping: {label_mapping}")
df_combined[label_col] = df_combined[label_col].map(label_mapping)

# Remove any unmapped labels
df_combined = df_combined[df_combined[label_col].notna()]

print(f"\nFinal label distribution:")
print(df_combined[label_col].value_counts())

# Select and rename columns
print(f"\nPreparing final dataset...")
df_final = df_combined[[email_col, label_col]].copy()
df_final.columns = ['email', 'label']

print(f"Final dataset:")
print(f"  Total emails: {len(df_final)}")
print(f"  Phishing: {(df_final['label'] == 1).sum()}")
print(f"  Legitimate: {(df_final['label'] == 0).sum()}")
print(f"  Avg email length: {df_final['email'].str.len().mean():.0f} characters")

# Save processed data
output_path = data_dir / "phishing_emails_processed.csv"
df_final.to_csv(output_path, index=False)
output_size_mb = output_path.stat().st_size / (1024*1024)

print("\n" + "="*70)
print("✓ DATA PREPROCESSING COMPLETE")
print("="*70)
print(f"Saved to: {output_path.name}")
print(f"File size: {output_size_mb:.2f} MB")
print(f"Ready for training!")
print("="*70)

print("\nNext step: Run python 2_training/train_model.py")
print("="*70 + "\n")
