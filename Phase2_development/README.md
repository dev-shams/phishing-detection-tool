# Phase 2: Real Data Training & Model Optimization

## 📋 Overview

Phase 2 improves upon Phase 1 by training the phishing detection model on **27,747+ real emails** from the Kaggle Phishing Email Dataset instead of synthetic data.

### Phase 1 → Phase 2 Improvement:
- **Phase 1:** Synthetic data training (~60-70% accuracy)
- **Phase 2:** Real data training (~78-82% accuracy) ✓

## 🎯 Objectives

Phase 2 focuses on:
1. **Importing Real Data** - Download Kaggle Phishing Email Dataset
2. **Data Preprocessing** - Clean and prepare 27,747+ emails
3. **Model Training** - Train on real-world email patterns
4. **Performance Evaluation** - Measure accuracy, precision, recall
5. **Testing & Verification** - Test phishing & legitimate detection

## 📂 Folder Structure

```
Phase2_development/
├── 1_data/                          # Data import & preprocessing
│   ├── download_dataset.py          # Download from Kaggle
│   └── preprocess_data.py           # Clean and prepare data
├── 2_training/                      # Model training
│   ├── train_model.py               # Train on real data
│   └── evaluate_model.py            # Performance metrics
├── 3_testing/                       # Testing & verification
│   ├── test_phishing_detection.py   # Test phishing detection
│   └── test_legitimate_detection.py # Test legitimate detection
├── 4_models/                        # Trained models (generated)
│   ├── phishing_model_phase2.pkl    # Trained model
│   └── scaler_phase2.pkl            # Feature scaler
├── 5_results/                       # Results & reports (generated)
│   └── phase2_evaluation_report.txt # Performance report
├── data/                            # Raw email data (generated)
│   └── phishing_emails_processed.csv
├── feature_extractor.py             # From Phase 1
├── ml_model.py                      # From Phase 1
├── requirements.txt                 # Dependencies
└── README.md                        # This file
```

## 🚀 Quick Start

### Prerequisites
- Kaggle account (free at https://www.kaggle.com/)
- Python 3.8+
- Dependencies installed

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Setup Kaggle Credentials
1. Go to: https://www.kaggle.com/settings/account
2. Click "Create New API Token" (downloads `kaggle.json`)
3. Place in `~/.kaggle/kaggle.json`:
   ```bash
   mkdir -p ~/.kaggle
   mv ~/Downloads/kaggle.json ~/.kaggle/
   chmod 600 ~/.kaggle/kaggle.json  # Mac/Linux only
   ```

### Step 3: Run Phase 2 Workflow

Execute these commands in order:

```bash
cd Phase2_development

# Step 1: Download real data from Kaggle (5-10 min)
python 1_data/download_dataset.py

# Step 2: Preprocess data (10-15 min)
python 1_data/preprocess_data.py

# Step 3: Train model on real data (10-20 min)
python 2_training/train_model.py

# Step 4: Evaluate model performance (5-10 min)
python 2_training/evaluate_model.py

# Step 5: Test phishing detection (2-3 min)
python 3_testing/test_phishing_detection.py

# Step 6: Test legitimate detection (2-3 min)
python 3_testing/test_legitimate_detection.py
```

**Total time: ~1 hour**

## 📊 Expected Results

After completing Phase 2:

### Model Performance
- **Accuracy:** 78-82%
- **Precision:** 80-85%
- **Recall:** 78-82%
- **F1-Score:** 79-83%
- **ROC-AUC:** 0.85+

### Generated Files
- `4_models/phishing_model_phase2.pkl` (~50 MB)
- `4_models/scaler_phase2.pkl` (~1 KB)
- `5_results/phase2_evaluation_report.txt`
- `data/phishing_emails_processed.csv` (~150 MB)

### Verification Tests
- ✓ Phishing emails detected correctly (100% target)
- ✓ Legitimate emails identified correctly (0 false positives)
- ✓ Confidence scores > 70%

## 🔍 Detailed Steps

### 1_data/download_dataset.py
**Downloads Kaggle Phishing Email Dataset**

What it does:
- Authenticates with Kaggle API
- Downloads 27,747+ real phishing emails
- Extracts zip files automatically
- Lists downloaded files

Input: None (uses Kaggle credentials)
Output: `data/` folder with CSV files

### 1_data/preprocess_data.py
**Prepares data for training**

What it does:
- Loads all CSV files
- Removes duplicates (4,291 duplicate emails)
- Removes null values
- Cleans email text
- Normalizes labels (0=legitimate, 1=phishing)
- Creates `phishing_emails_processed.csv`

Input: `data/*.csv`
Output: `data/phishing_emails_processed.csv`

### 2_training/train_model.py
**Trains model on real data**

What it does:
- Loads preprocessed emails
- Extracts 24 features per email
- Trains Random Forest classifier
- Performs 5-fold cross-validation
- Saves trained model and scaler

Input: `data/phishing_emails_processed.csv`
Output:
- `4_models/phishing_model_phase2.pkl`
- `4_models/scaler_phase2.pkl`

### 2_training/evaluate_model.py
**Evaluates model performance**

What it does:
- Loads trained model
- Extracts features from test data
- Makes predictions
- Calculates metrics (accuracy, precision, recall, F1)
- Generates evaluation report

Input:
- `4_models/phishing_model_phase2.pkl`
- `data/phishing_emails_processed.csv`

Output: `5_results/phase2_evaluation_report.txt`

### 3_testing/test_phishing_detection.py
**Tests phishing detection capability**

What it does:
- Tests model on 5 sample phishing emails
- Shows prediction confidence
- Verifies correct identification
- Reports detection rate

Expected: 100% detection rate

### 3_testing/test_legitimate_detection.py
**Tests legitimate email identification**

What it does:
- Tests model on 5 sample legitimate emails
- Shows prediction confidence
- Verifies no false positives
- Reports accuracy

Expected: 100% accuracy, 0 false positives

## 📈 Features Extracted (24 total)

The model uses 24 features per email:

**URL Features (5):**
- `url_count` - Number of URLs
- `suspicious_url_count` - Suspicious URLs detected
- `has_shortened_urls` - Bit.ly, TinyURL, etc.
- `url_domain_diversity` - Number of unique domains
- `has_ip_urls` - IP addresses instead of domains

**Text Features (9):**
- `phishing_keyword_count` - "verify", "confirm", "urgent", etc.
- `urgency_keyword_count` - "immediately", "asap", etc.
- `authority_keyword_count` - "CEO", "admin", "bank", etc.
- `body_length` - Email body size
- `word_count` - Number of words
- `char_to_word_ratio` - Average word length
- `spelling_quality_score` - Grammar/spelling quality
- `has_all_caps_words` - EXCESSIVE CAPS DETECTED
- `has_exclamation_marks` - Number of exclamation marks

**Authentication Features (5):**
- `has_dkim` - DKIM signature present
- `has_spf` - SPF authentication
- `has_dmarc` - DMARC present
- `has_x_mailer` - X-Mailer header
- `has_x_priority` - X-Priority header

**Domain Features (5):**
- `sender_domain_length` - Length of domain name
- `has_suspicious_tld` - .tk, .ml, .ga, etc.
- `is_free_email_provider` - Gmail, Yahoo, etc.
- `domain_name_mismatch` - Subject vs. sender mismatch
- `sender_domain_age` - Domain age (placeholder)

## 🔐 Dataset Information

**Kaggle Dataset:** Phishing Email Dataset for Machine Learning
- **Author:** Naser Abdullah Alam
- **Total Emails:** 27,747+
- **Sources:**
  - Enron Dataset (legitimate emails)
  - CEAS Dataset (phishing emails)
  - Nazario Dataset (phishing emails)
  - Nigerian Fraud Dataset (phishing emails)
  - SpamAssassin (phishing emails)
  - Ling Dataset (mixed)

## ⚠️ Troubleshooting

### Error: "Kaggle authentication failed"
**Solution:**
1. Check `~/.kaggle/kaggle.json` exists
2. Verify credentials are correct
3. Try creating a new API token at https://www.kaggle.com/settings/account

### Error: "No CSV files found"
**Solution:** Run `python 1_data/download_dataset.py` first

### Error: "Model file not found"
**Solution:** Run `python 2_training/train_model.py` first

### Error: "Module not found: pandas/sklearn"
**Solution:** Install dependencies: `pip install -r requirements.txt`

## 📝 Monitoring Progress

Each script prints detailed progress:

```bash
# While downloading (shows progress)
✓ Dataset downloaded and extracted successfully
  phishing.csv (45.3 MB)
  ceas.csv (28.2 MB)
  ...

# While preprocessing (shows progress every 1000 emails)
✓ Loaded 27,747 emails
✓ Removed duplicates: 4,291 emails
✓ Cleaned email text

# While training (shows progress every 100 iterations)
Extracting features... 100/23,456 emails processed
Training Random Forest...
Accuracy: 81.27%
```

## 🎯 Success Criteria

Phase 2 is successful when:

✅ **Data Pipeline**
- [ ] 27,747+ emails downloaded
- [ ] Data preprocessed and cleaned
- [ ] `phishing_emails_processed.csv` created

✅ **Model Training**
- [ ] Model trained on real data
- [ ] Accuracy ≥ 78%
- [ ] Precision ≥ 80%
- [ ] Recall ≥ 78%
- [ ] `phishing_model_phase2.pkl` saved

✅ **Testing**
- [ ] Phishing detection: 100% accuracy
- [ ] Legitimate detection: 100% accuracy
- [ ] No false positives

✅ **Documentation**
- [ ] Evaluation report generated
- [ ] All metrics documented

## 🚀 Next Phase

Once Phase 2 is complete, move to **Phase 3: Web Dashboard Development**
- Build Flask web interface
- Create HTML/CSS frontend
- Deploy and test web application

## 📚 References

- **Phase 1:** `/Phase1_development/` - Baseline model and feature extraction
- **Kaggle Dataset:** https://www.kaggle.com/datasets/shashwatwork/phishing-dataset-for-machine-learning
- **Scikit-learn:** https://scikit-learn.org/ - ML algorithms
- **Random Forest:** https://en.wikipedia.org/wiki/Random_forest

## ✅ Completion

Phase 2 Status: **Ready to Execute**

```
Phase 1: ✓ COMPLETE (Synthetic data training)
Phase 2: 🚀 START HERE (Real data training)
Phase 3: 📋 Next (Web dashboard)
```

**Let's improve your model with real data! 🎯**
