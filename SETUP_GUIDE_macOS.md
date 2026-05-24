# macOS Setup Guide - Phishing Detector Project

## Step 1: Verify Python Installation

Open Terminal and check your Python version:

```bash
python3 --version
# Should show: Python 3.14.4 (or your version)

which python3
# Should show: /usr/local/bin/python3 or /opt/homebrew/bin/python3
```

Great! You're ready to go.

---

## Step 2: Create Project Directory

```bash
# Navigate to your project folder
cd /Users/user/Documents/Claude/Projects/Final\ year\ Project

# Create src directory for code
mkdir -p src
cd src
```

---

## Step 3: Create Virtual Environment

A virtual environment keeps your project dependencies isolated:

```bash
# Create virtual environment
python3 -m venv phishing_env

# Activate it
source phishing_env/bin/activate

# You should see (phishing_env) at the start of terminal line
# Now your terminal is isolated for this project
```

---

## Step 4: Upgrade pip

```bash
pip install --upgrade pip
```

---

## Step 5: Install Dependencies

```bash
# Copy requirements.txt to your src folder first
# Then run:
pip install -r requirements.txt

# This will install:
# - Flask (web framework)
# - scikit-learn (machine learning)
# - pandas, numpy (data processing)
# - pytest (testing)
# - And others
```

---

## Step 6: Verify Installation

```bash
# Test Python imports
python3 -c "import flask, sklearn, pandas; print('✓ All packages installed successfully')"

# If no error, you're good to go!
```

---

## Step 7: Open Project in VS Code

```bash
# From src folder
code .

# This opens the current folder in VS Code
```

In VS Code:
1. Press `Cmd + Shift + P`
2. Type: "Python: Select Interpreter"
3. Choose the one with `phishing_env` in the path

---

## Daily Workflow

Each time you work on the project:

```bash
# 1. Open Terminal
# 2. Navigate to project
cd /Users/user/Documents/Claude/Projects/Final\ year\ Project/src

# 3. Activate virtual environment
source phishing_env/bin/activate

# 4. You're ready to code!
python app.py
```

---

## Troubleshooting

### "Command not found: python3"
```bash
# Install Python using Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.11
```

### "Module not found" error
```bash
# Make sure virtual environment is activated
# You should see (phishing_env) in terminal
source phishing_env/bin/activate

# Then reinstall requirements
pip install -r requirements.txt
```

### Virtual environment won't activate
```bash
# Try this instead
. phishing_env/bin/activate

# Or check if file exists
ls phishing_env/bin/activate
```

---

## Deactivate Virtual Environment (when done)

```bash
deactivate

# Terminal will no longer show (phishing_env)
```

---

**Next Step:** Follow the code creation guide to build your first component!
