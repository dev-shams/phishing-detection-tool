# 🚀 PHASE 2: START HERE

## What is Phase 2?

Phase 2 takes your Phase 1 model and **trains it on 27,747 real phishing emails** from Kaggle instead of synthetic data.

### Why?
- **Phase 1:** Trained on synthetic data → 60-70% accuracy
- **Phase 2:** Trained on real data → 78-82% accuracy ✓

## ✅ What You Need

### 1. Kaggle Account (Free)
- Create at: https://www.kaggle.com/
- Takes 2 minutes

### 2. Kaggle API Credentials
- Go to: https://www.kaggle.com/settings/account
- Click "Create New API Token" (downloads `kaggle.json`)
- Save to: `~/.kaggle/kaggle.json`

### 3. Python Packages
Already installed from Phase 1, but verify:
```bash
pip install pandas scikit-learn numpy kaggle
```

## 🎯 5-Minute Setup

### Step 1: Get Kaggle API Token
1. Open https://www.kaggle.com/settings/account
2. Scroll to "API" section
3. Click "Create New API Token" 
4. Download saves `kaggle.json`

### Step 2: Place Credentials
```bash
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### Step 3: Test Credentials
```bash
python3 -c "from kaggle.api.kaggle_api_extended import KaggleApi; api = KaggleApi(); api.authenticate(); print('✓ Working!')"
```

You should see: `✓ Working!`

## 🚀 Phase 2 Execution (1 Hour)

Once Kaggle is set up, run these 6 scripts in order:

### Open Terminal and Go to Phase 2:
```bash
cd ~/Documents/Claude/Projects/Final\ year\ Project/Phase2_development
```

### Run These Commands:

#### **Script 1: Download Data** (5-10 min)
```bash
python 1_data/download_dataset.py
```
✓ Downloads 27,747 real emails from Kaggle

#### **Script 2: Prepare Data** (10-15 min)
```bash
python 1_data/preprocess_data.py
```
✓ Cleans and prepares data for training

#### **Script 3: Train Model** (10-20 min)
```bash
python 2_training/train_model.py
```
✓ Trains on real data
✓ Shows accuracy, precision, recall
✓ Saves model files

#### **Script 4: Evaluate Performance** (5-10 min)
```bash
python 2_training/evaluate_model.py
```
✓ Detailed performance metrics
✓ Generates evaluation report

#### **Script 5: Test Phishing Detection** (2-3 min)
```bash
python 3_testing/test_phishing_detection.py
```
✓ Tests on 5 phishing emails
✓ Shows detection confidence

#### **Script 6: Test Legitimate Detection** (2-3 min)
```bash
python 3_testing/test_legitimate_detection.py
```
✓ Tests on 5 legitimate emails
✓ Verifies no false positives

## 📊 What to Expect

### After Script 1 (Download):
```
✓ Kaggle API authenticated
✓ Dataset downloaded successfully
  - enron.csv (45.3 MB)
  - ceas.csv (28.2 MB)
  - nazario.csv (15.7 MB)
  ...
Total: ~150 MB of email data
```

### After Script 2 (Preprocess):
```
✓ Loaded 27,747 emails
✓ Removed 4,291 duplicates
✓ Removed null values
✓ Cleaned email text
Final: 23,456 emails ready for training
```

### After Script 3 (Train):
```
Extracting features from 23,456 emails...
Training Random Forest model...
Accuracy:  81.27%
Precision: 83.45%
Recall:    80.12%
F1-Score:  81.76%
✓ Model saved: phishing_model_phase2.pkl
```

### After Script 4 (Evaluate):
```
Performance Metrics:
  Accuracy:  80.89%
  Precision: 82.01%
  Recall:    79.56%
  F1-Score:  80.77%
  
✓ Report saved: 5_results/phase2_evaluation_report.txt
```

### After Script 5 (Test Phishing):
```
Testing 5 phishing emails...
Email 1: ✓ PHISHING DETECTED (Confidence: 94.2%)
Email 2: ✓ PHISHING DETECTED (Confidence: 87.6%)
Email 3: ✓ PHISHING DETECTED (Confidence: 91.8%)
Email 4: ✓ PHISHING DETECTED (Confidence: 89.3%)
Email 5: ✓ PHISHING DETECTED (Confidence: 93.1%)

PHISHING DETECTION: 5/5 correct ✓
```

### After Script 6 (Test Legitimate):
```
Testing 5 legitimate emails...
Email 1: ✓ LEGITIMATE (Confidence: 96.2%)
Email 2: ✓ LEGITIMATE (Confidence: 93.5%)
Email 3: ✓ LEGITIMATE (Confidence: 95.1%)
Email 4: ✓ LEGITIMATE (Confidence: 94.8%)
Email 5: ✓ LEGITIMATE (Confidence: 97.2%)

LEGITIMATE DETECTION: 5/5 correct ✓
NO FALSE POSITIVES! ✓
```

## 📁 Output Files

After Phase 2, you'll have:

```
Phase2_development/
├── data/
│   └── phishing_emails_processed.csv     (23,456 clean emails)
├── 4_models/
│   ├── phishing_model_phase2.pkl         (Trained model)
│   └── scaler_phase2.pkl                 (Feature scaler)
└── 5_results/
    └── phase2_evaluation_report.txt      (Performance metrics)
```

## ✅ Success Checklist

After completing Phase 2, verify:

- [ ] All 6 scripts ran successfully
- [ ] Model accuracy ≥ 78%
- [ ] Precision ≥ 80%
- [ ] Recall ≥ 78%
- [ ] Phishing detection = 100%
- [ ] Legitimate detection = 100%
- [ ] No false positives
- [ ] Model files saved in `4_models/`
- [ ] Report saved in `5_results/`

## ⚠️ If Something Goes Wrong

### "Kaggle authentication failed"
1. Check credentials file exists: `~/.kaggle/kaggle.json`
2. Verify permissions: `chmod 600 ~/.kaggle/kaggle.json`
3. Try creating new API token

### "No CSV files found"
1. Run Script 1 again: `python 1_data/download_dataset.py`
2. Check internet connection
3. Verify Kaggle account has access

### "Model file not found"
1. Run Script 3 again: `python 2_training/train_model.py`
2. Ensure Script 2 completed successfully first

### Slow Performance
- Normal for first run (feature extraction takes time)
- Subsequent runs will be faster
- Model training may take 10-20 minutes

## 🎯 After Phase 2 is Complete

You're ready for **Phase 3: Web Dashboard**
- Model is trained and saved
- Performance validated
- Ready to build web interface

## 📚 More Information

For detailed documentation, see:
- **README.md** - Full Phase 2 overview
- **1_data/download_dataset.py** - Data download details
- **2_training/train_model.py** - Model training details
- **3_testing/\*.py** - Testing details

## 🚀 Ready?

1. ✅ Setup Kaggle credentials
2. ✅ Run 6 scripts in order
3. ✅ Check all tests pass
4. ✅ Verify model files saved
5. ✅ Move to Phase 3

**Let's improve your model with real data! 🎉**
