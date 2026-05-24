# 🚀 Quick Start Guide

## Before You Begin

Make sure you're in the project folder:
```bash
cd /Users/user/Documents/Claude/Projects/Final\ year\ Project
```

---

## Step 1: Set Up Virtual Environment (First Time Only)

```bash
# Create virtual environment
python3 -m venv phishing_env

# Activate it
source phishing_env/bin/activate

# You should see (phishing_env) at the start of terminal line
```

---

## Step 2: Install Dependencies (First Time Only)

```bash
# Make sure virtual environment is activated
# (phishing_env) should be visible in terminal

# Install required packages
pip install -r requirements.txt

# This takes 1-2 minutes
```

---

## Step 3: Run the Application

```bash
# Make sure virtual environment is activated
source phishing_env/bin/activate

# Start the Flask server
python app.py
```

You should see output like:
```
======================================================
PHISHING EMAIL DETECTION TOOL
======================================================

Initializing model...
✓ Model loaded successfully

======================================================
Starting Flask server...
======================================================

Open your browser and go to: http://127.0.0.1:5000
Press Ctrl+C to stop the server
```

---

## Step 4: Open in Browser

1. **Open your web browser**
2. **Go to:** `http://127.0.0.1:5000` or `http://localhost:5000`
3. **You should see the Phishing Detector dashboard**

---

## Testing the Application

### Option 1: Upload a Test Email
1. Click "Upload Email for Analysis"
2. Select a .eml or .msg file
3. Click "Analyze Email"

### Option 2: Analyze Text Directly
1. Click "Or analyze email text directly"
2. Enter email details:
   - From: email@example.com
   - Subject: Something suspicious
   - Body: "Click here to verify your account"
3. Click "Analyze Text"

### Option 3: Create Test Emails

**Suspicious Email (phishing.eml):**
```
From: verify@amazon-support.com
To: user@gmail.com
Subject: URGENT: Verify Your Amazon Account Now!
Date: Mon, 22 May 2024 10:00:00 +0000

Dear Customer,

Your Amazon account requires immediate verification. Please click here to verify your account:
https://verify.amazon-account.xyz/login

Unusual activity detected. Click immediately to secure your account.

Best regards,
Amazon Security Team
```

**Legitimate Email (legitimate.eml):**
```
From: john.smith@company.com
To: user@gmail.com
Subject: Meeting scheduled for tomorrow
Date: Mon, 22 May 2024 10:00:00 +0000

Hi,

I wanted to confirm our meeting scheduled for tomorrow at 2 PM in Conference Room B.

Please let me know if you have any questions.

Best regards,
John Smith
Sales Manager
```

---

## Troubleshooting

### Problem: "Command not found: python3"
```bash
# Check Python installation
which python3

# If not found, install with Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.11
```

### Problem: "Module not found" error
```bash
# Make sure virtual environment is activated
source phishing_env/bin/activate

# Verify you're in the right directory
pwd
# Should show: /Users/user/Documents/Claude/Projects/Final year Project

# Reinstall dependencies
pip install -r requirements.txt
```

### Problem: Port 5000 already in use
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process (replace PID with actual process ID)
kill -9 <PID>

# Or change port in app.py line 223:
# app.run(debug=True, host='127.0.0.1', port=5001)  # Changed to 5001
```

### Problem: Template not found error
```bash
# Make sure you're in the project root directory
pwd
# Should show: /Users/user/Documents/Claude/Projects/Final year Project

# Verify folder structure
ls -la
# Should show: app.py, templates/, static/, etc.
```

---

## Next Steps (After Testing)

1. **Test with real emails:** Find sample phishing and legitimate emails
2. **Train the model:** Collect more training data and retrain
3. **Improve features:** Add more detection rules
4. **Write documentation:** Document your system
5. **Prepare for viva:** Practice your demonstration

---

## File Structure

```
Final year Project/
├── app.py                    # Main Flask application
├── email_parser.py           # Email parsing module
├── feature_extractor.py      # Feature extraction module
├── ml_model.py              # ML model training
├── requirements.txt          # Python dependencies
├── templates/
│   └── index.html           # Web interface
├── static/
│   ├── style.css            # Styling
│   └── app.js               # Frontend JavaScript
├── uploads/                 # Temporary email uploads
└── phishing_env/            # Virtual environment (don't edit)
```

---

## Development Tips

### View console output
```bash
# Run with verbose output
python app.py

# You'll see debugging info in terminal
```

### Stop the server
```bash
# Press Ctrl+C in terminal
# Or close the terminal window
```

### Exit virtual environment
```bash
deactivate

# (phishing_env) should disappear from terminal
```

### Re-enter virtual environment
```bash
source phishing_env/bin/activate
```

---

## Common Commands

```bash
# Activate environment (always do this first)
source phishing_env/bin/activate

# Run the application
python app.py

# Install a new package
pip install package-name

# List installed packages
pip list

# Deactivate environment
deactivate
```

---

## Performance Notes

- **First run:** May take 10-15 seconds to load model
- **Analysis:** Each email takes 1-2 seconds to analyze
- **Model training:** ~30 seconds for synthetic data
- **File upload:** Instant for files < 16MB

---

## Got Stuck?

1. Check this guide again
2. Read the error message carefully (it usually tells you what's wrong)
3. Check console output in terminal (Ctrl+C to stop, scroll up to see errors)
4. Delete `phishing_env` folder and start over with Step 1

---

**Good luck! You've got this! 🎉**

Need help? Check `TECHNICAL_IMPLEMENTATION_GUIDE.md` for more details.
