# Technical Implementation Guide
## Email Phishing Detection Tool

---

## TECHNOLOGY STACK RECOMMENDATION

### Why These Technologies?
- **Python:** Large ML and data science ecosystem (scikit-learn, pandas)
- **Flask/FastAPI:** Lightweight, easy to learn, perfect for FYP
- **scikit-learn:** Great for ML beginners, excellent documentation
- **SQLite:** No setup required, perfect for FYP scope

---

## PROJECT STRUCTURE

```
phishing-detector/
│
├── backend/
│   ├── app.py                      # Main Flask/FastAPI application
│   ├── config.py                   # Configuration settings
│   ├── requirements.txt            # Python dependencies
│   │
│   ├── email_processing/
│   │   ├── __init__.py
│   │   ├── parser.py              # Email parsing logic
│   │   ├── feature_extractor.py   # Feature extraction
│   │   └── utils.py               # Helper functions
│   │
│   ├── ml_model/
│   │   ├── __init__.py
│   │   ├── model_trainer.py       # Training pipeline
│   │   ├── model.pkl              # Saved trained model
│   │   ├── scaler.pkl             # Feature scaler
│   │   └── predictions.py         # Prediction logic
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── upload.py              # File upload routes
│   │   ├── analyze.py             # Analysis routes
│   │   └── results.py             # Results routes
│   │
│   └── tests/
│       ├── test_parser.py
│       ├── test_features.py
│       ├── test_model.py
│       └── test_api.py
│
├── frontend/
│   ├── index.html                 # Main page
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js                 # Frontend logic
│   └── assets/
│       └── images/
│
├── data/
│   ├── training/                  # Training email datasets
│   ├── testing/                   # Test emails
│   └── models/                    # Saved models
│
├── README.md                       # Setup instructions
├── setup.py                        # Python package setup
└── run.sh                          # Startup script
```

---

## DETAILED IMPLEMENTATION GUIDE

### 1. EMAIL PARSER

#### File: `backend/email_processing/parser.py`

**Purpose:** Parse .eml and .msg files, extract email components

```python
# Key functions to implement:

def parse_eml_file(file_path):
    """Parse .eml format email files"""
    # Use Python's built-in email library
    # Extract: sender, subject, body, headers, attachments
    
def parse_msg_file(file_path):
    """Parse .msg format email files"""
    # Use python-pptx or extract-msg library
    # Extract: sender, subject, body, headers, attachments

def extract_sender(email_message):
    """Extract sender email address"""
    # Parse From header
    # Return normalized email address
    
def extract_subject(email_message):
    """Extract email subject"""
    # Handle encoding issues
    
def extract_body(email_message):
    """Extract email body text"""
    # Handle multipart messages
    # Extract text/plain and text/html parts
    
def extract_headers(email_message):
    """Extract all email headers"""
    # Return dict of headers
    # Include: From, To, Subject, Date, Reply-To, etc.
    
def extract_urls(email_body):
    """Extract all URLs from email body"""
    # Use regex to find URLs
    # Return list of URLs
    
def validate_email_file(file_path):
    """Check if file is valid .eml or .msg"""
    # Return True/False
```

**Dependencies:**
```
email==5.0
python-pptx==0.6.21
extract-msg==0.41.0
# OR install: pip install python-docx
```

---

### 2. FEATURE EXTRACTION

#### File: `backend/email_processing/feature_extractor.py`

**Purpose:** Extract meaningful features from parsed emails for ML model

```python
# Key features to extract:

def extract_features(email_data):
    """Main feature extraction function"""
    # Returns: dict of numerical features
    
    features = {
        # Header-based features
        'has_reply_to': 1 if email_data['reply_to'] else 0,
        'sender_domain_length': len(email_data['sender_domain']),
        'sender_domain_age': calculate_domain_age(email_data['sender_domain']),
        'has_admin_address': 1 if 'admin' in email_data['sender'].lower() else 0,
        
        # URL-based features
        'url_count': len(email_data['urls']),
        'suspicious_url_count': count_suspicious_urls(email_data['urls']),
        'url_domain_diversity': calculate_domain_diversity(email_data['urls']),
        'has_shortened_urls': has_url_shorteners(email_data['urls']),
        
        # Text-based features
        'suspicious_keyword_count': count_suspicious_keywords(email_data['body']),
        'urgency_score': calculate_urgency_keywords(email_data['body']),
        'authority_mentions': count_authority_words(email_data['body']),
        'body_length': len(email_data['body']),
        'char_to_word_ratio': calculate_char_word_ratio(email_data['body']),
        
        # Grammar and style
        'spelling_errors': count_spelling_errors(email_data['body']),
        'grammar_errors': count_grammar_errors(email_data['body']),
        
        # Header authentication
        'spf_pass': 1 if spf_check_passes(email_data['headers']) else 0,
        'dkim_pass': 1 if dkim_check_passes(email_data['headers']) else 0,
        'dmarc_pass': 1 if dmarc_check_passes(email_data['headers']) else 0,
    }
    
    return features

# Suspicious keywords list
PHISHING_KEYWORDS = [
    'verify', 'confirm', 'urgent', 'action required', 'update',
    'click here', 'activate', 'suspended', 'claim', 'reset',
    'unusual activity', 'security alert', 'locked', 'download',
    # Add 50+ more based on your research
]

def count_suspicious_keywords(text):
    """Count occurrences of phishing keywords"""
    text_lower = text.lower()
    count = 0
    for keyword in PHISHING_KEYWORDS:
        count += text_lower.count(keyword)
    return count

def count_suspicious_urls(urls):
    """Identify URLs with phishing characteristics"""
    suspicious = 0
    for url in urls:
        if is_suspicious_url(url):
            suspicious += 1
    return suspicious

def is_suspicious_url(url):
    """Check if URL has phishing indicators"""
    # Check for: @ symbol, IP address, mismatched domain, etc.
    if '@' in url:  # URL with @ often hides real domain
        return True
    if is_ip_address(url):  # IP instead of domain name
        return True
    if has_misspelled_popular_domain(url):  # e.g., "gmai1.com" instead of "gmail.com"
        return True
    return False
```

**Key Suspicious Indicators:**
1. **Sender spoofing:** Domain doesn't match company name
2. **Authentication failures:** No SPF, DKIM, DMARC
3. **Suspicious URLs:** Shortened, mismatched domains, IP addresses
4. **Urgency language:** "Verify immediately", "Update required"
5. **Authority impersonation:** "From: IT Department", "CEO"
6. **Generic greetings:** "Dear User" instead of personal name
7. **Grammar errors:** Poor spelling in body
8. **Request for sensitive info:** Passwords, account numbers

---

### 3. MACHINE LEARNING MODEL

#### File: `backend/ml_model/model_trainer.py`

**Purpose:** Train and evaluate ML model

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pickle

def train_model(training_data_path):
    """Train the phishing detection model"""
    
    # 1. Load training data
    X, y = load_training_data(training_data_path)
    # X: features (numpy array)
    # y: labels (0=legitimate, 1=phishing)
    
    # 2. Normalize features (important!)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 3. Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    
    # 4. Train model
    model = RandomForestClassifier(
        n_estimators=100,      # Number of trees
        max_depth=15,          # Max tree depth
        min_samples_split=5,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # 5. Evaluate
    y_pred = model.predict(X_test)
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
    }
    
    print(f"Accuracy: {metrics['accuracy']:.2%}")
    print(f"Precision: {metrics['precision']:.2%}")
    print(f"Recall: {metrics['recall']:.2%}")
    print(f"F1-Score: {metrics['f1']:.2%}")
    
    # 6. Cross-validation
    cv_scores = cross_val_score(model, X_scaled, y, cv=5)
    print(f"Cross-validation scores: {cv_scores}")
    
    # 7. Save model
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    with open('scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    
    return model, scaler, metrics

# Alternative: Use Logistic Regression for simpler model
# from sklearn.linear_model import LogisticRegression
# model = LogisticRegression(max_iter=1000)
```

**Model Selection Rationale:**
- **Random Forest:**
  - Pros: Good accuracy, handles non-linear relationships, feature importance
  - Cons: Slower to train/predict
- **Logistic Regression:**
  - Pros: Fast, interpretable, easy to explain
  - Cons: Assumes linear relationships
- **Neural Network:**
  - Pros: Potentially higher accuracy
  - Cons: Requires more data, harder to interpret

**Recommendation:** Start with **Logistic Regression** (simple, fast), then try **Random Forest** if needed.

---

### 4. PREDICTION ENGINE

#### File: `backend/ml_model/predictions.py`

```python
import pickle
import numpy as np

class PhishingDetector:
    def __init__(self, model_path='model.pkl', scaler_path='scaler.pkl'):
        """Load trained model and scaler"""
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)
    
    def predict(self, email_file_path):
        """Predict if email is phishing"""
        
        # 1. Parse email
        email_data = parse_email(email_file_path)
        
        # 2. Extract features
        features_dict = extract_features(email_data)
        features_array = convert_to_array(features_dict)
        
        # 3. Scale features
        features_scaled = self.scaler.transform([features_array])
        
        # 4. Predict
        prediction = self.model.predict(features_scaled)[0]
        confidence = self.model.predict_proba(features_scaled)[0]
        
        # 5. Format result
        result = {
            'classification': 'PHISHING' if prediction == 1 else 'SAFE',
            'confidence_phishing': float(confidence[1]) * 100,
            'confidence_safe': float(confidence[0]) * 100,
            'threat_indicators': extract_threat_indicators(email_data),
            'recommendation': get_recommendation(prediction, confidence[1])
        }
        
        return result
    
    def extract_threat_indicators(self, email_data):
        """List specific threats found"""
        indicators = []
        
        if is_spoofed_domain(email_data['sender']):
            indicators.append("Spoofed sender domain")
        
        if has_suspicious_urls(email_data['urls']):
            indicators.append(f"Suspicious URLs detected ({count} found)")
        
        if has_urgency_language(email_data['body']):
            indicators.append("Uses urgency/pressure language")
        
        if lacks_authentication(email_data['headers']):
            indicators.append("Fails email authentication (SPF/DKIM/DMARC)")
        
        return indicators
```

---

### 5. FLASK/FASTAPI BACKEND

#### File: `backend/app.py` (Flask example)

```python
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from email_processing.parser import parse_email
from ml_model.predictions import PhishingDetector

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['UPLOAD_FOLDER'] = 'uploads'

detector = PhishingDetector()

@app.route('/', methods=['GET'])
def index():
    """Serve main dashboard"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Validate file
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only .eml and .msg files allowed'}), 400
    
    # Save temporarily
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Analyze
    try:
        result = detector.predict(filepath)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up
        os.remove(filepath)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze uploaded email"""
    data = request.json
    filepath = data.get('filepath')
    
    try:
        result = detector.predict(filepath)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def allowed_file(filename):
    """Check if file is valid"""
    return filename.lower().endswith(('.eml', '.msg'))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, port=5000)
```

---

### 6. FRONTEND (HTML/CSS/JS)

#### File: `frontend/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Phishing Email Detector</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center mb-4">Email Phishing Detector</h1>
        
        <div class="row">
            <div class="col-md-8 mx-auto">
                <!-- Upload Section -->
                <div class="card mb-4">
                    <div class="card-body">
                        <h5 class="card-title">Upload Email for Analysis</h5>
                        <div class="mb-3">
                            <label for="fileInput" class="form-label">Select email file (.eml or .msg)</label>
                            <input class="form-control" type="file" id="fileInput" accept=".eml,.msg">
                        </div>
                        <button class="btn btn-primary" onclick="analyzeEmail()">Analyze Email</button>
                    </div>
                </div>
                
                <!-- Loading Indicator -->
                <div id="loading" style="display:none;" class="text-center mb-4">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Analyzing...</span>
                    </div>
                    <p>Analyzing email...</p>
                </div>
                
                <!-- Results Section -->
                <div id="results" style="display:none;" class="card">
                    <div class="card-body">
                        <h5 class="card-title">Analysis Results</h5>
                        
                        <!-- Classification Badge -->
                        <div class="mb-4">
                            <h3 id="classification" class="badge" style="font-size: 1.5rem;"></h3>
                            <p id="confidence"></p>
                        </div>
                        
                        <!-- Threat Indicators -->
                        <div class="mb-4">
                            <h6>Threat Indicators:</h6>
                            <ul id="indicators"></ul>
                        </div>
                        
                        <!-- Recommendation -->
                        <div class="alert" id="recommendation"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="js/app.js"></script>
</body>
</html>
```

#### File: `frontend/js/app.js`

```javascript
async function analyzeEmail() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file');
        return;
    }
    
    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';
    
    // Create FormData
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        // Send to backend
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error);
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

function displayResults(data) {
    // Set classification
    const classEl = document.getElementById('classification');
    if (data.classification === 'PHISHING') {
        classEl.textContent = '⚠️ PHISHING DETECTED';
        classEl.className = 'badge bg-danger';
    } else {
        classEl.textContent = '✅ SAFE';
        classEl.className = 'badge bg-success';
    }
    
    // Set confidence
    document.getElementById('confidence').textContent = 
        `Confidence: ${data.confidence_phishing.toFixed(1)}% phishing, ${data.confidence_safe.toFixed(1)}% safe`;
    
    // Display threat indicators
    const indicatorsList = document.getElementById('indicators');
    indicatorsList.innerHTML = '';
    if (data.threat_indicators && data.threat_indicators.length > 0) {
        data.threat_indicators.forEach(indicator => {
            const li = document.createElement('li');
            li.textContent = indicator;
            indicatorsList.appendChild(li);
        });
    } else {
        indicatorsList.innerHTML = '<li>No specific threats detected</li>';
    }
    
    // Recommendation
    const recEl = document.getElementById('recommendation');
    recEl.textContent = data.recommendation;
    recEl.className = data.classification === 'PHISHING' ? 'alert alert-danger' : 'alert alert-success';
    
    // Show results
    document.getElementById('results').style.display = 'block';
}
```

#### File: `frontend/css/style.css`

```css
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px 0;
}

.container {
    background: white;
    border-radius: 10px;
    padding: 40px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}

h1 {
    color: #333;
    font-weight: 700;
}

.card {
    border: none;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.badge {
    padding: 10px 20px;
    font-weight: 600;
}

.badge.bg-danger {
    background-color: #dc3545 !important;
}

.badge.bg-success {
    background-color: #28a745 !important;
}

.alert {
    border-radius: 8px;
    padding: 15px;
    font-weight: 500;
}

#indicators {
    margin-left: 20px;
}

#indicators li {
    margin: 8px 0;
    color: #555;
}

.spinner-border {
    color: #667eea;
}
```

---

## DEPENDENCIES

### File: `requirements.txt`

```
Flask==2.3.0
scikit-learn==1.2.0
pandas==1.5.0
numpy==1.24.0
python-dotenv==0.21.0
extract-msg==0.41.0
email-validator==1.3.0
requests==2.31.0
pytest==7.2.0
pytest-flask==1.2.0
```

### Installation:
```bash
pip install -r requirements.txt
```

---

## TESTING EXAMPLES

### File: `backend/tests/test_parser.py`

```python
import unittest
from email_processing.parser import parse_eml_file, extract_urls

class TestEmailParser(unittest.TestCase):
    
    def test_parse_valid_eml(self):
        """Test parsing valid .eml file"""
        result = parse_eml_file('test_emails/legitimate.eml')
        self.assertIsNotNone(result)
        self.assertIn('sender', result)
        self.assertIn('subject', result)
    
    def test_extract_urls(self):
        """Test URL extraction"""
        body = "Check this link: https://example.com and http://test.org"
        urls = extract_urls(body)
        self.assertEqual(len(urls), 2)
        self.assertIn('https://example.com', urls)

if __name__ == '__main__':
    unittest.main()
```

---

## RUNNING THE APPLICATION

### Startup script: `run.sh`

```bash
#!/bin/bash
cd "$(dirname "$0")"
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python backend/app.py
```

Run with:
```bash
bash run.sh
```

Then navigate to: `http://localhost:5000`

---

## KEY DEVELOPMENT TIPS

1. **Start simple:** Get basic email parsing working first
2. **Test frequently:** Test each component as you build
3. **Use sample emails:** Create test dataset with known phishing/legitimate emails
4. **Handle errors:** Gracefully handle corrupted files, unexpected formats
5. **Document code:** Add comments explaining logic
6. **Version control:** Use Git to track changes

---

## EXPECTED ACCURACY

- **Baseline (simple rules):** 70-75%
- **Logistic Regression:** 80-85%
- **Random Forest:** 85-90%
- **Production system:** 95%+ (with enterprise tools)

---

Good luck with implementation! 🚀
