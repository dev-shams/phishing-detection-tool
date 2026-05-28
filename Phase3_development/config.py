"""
Phase 3: Flask Web Application Configuration
Stores all configuration settings for the phishing detection web app
"""

import os
from pathlib import Path

# Flask Configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes') if FLASK_ENV == 'production' else False
HOST = '0.0.0.0'
PORT = int(os.getenv('PORT', 5001))

# Application Settings
APP_NAME = 'Phishing Email Detection Tool'
APP_VERSION = '1.0.0'
SECRET_KEY = os.getenv('SECRET_KEY', 'phishing-detection-secret-key-2024')

# File Upload Settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'eml', 'msg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Model Configuration - ENHANCED with TF-IDF + Handcrafted Features
# Based on successful techniques from previous project analysis
MODEL_PATH = Path(__file__).parent / 'models' / 'phishing_model_enhanced.joblib'
SCALER_PATH = Path(__file__).parent / 'models' / 'scaler_enhanced.joblib'
TFIDF_VECTORIZER_PATH = Path(__file__).parent / 'models' / 'tfidf_vectorizer_enhanced.joblib'
HANDCRAFTED_SCALER_PATH = Path(__file__).parent / 'models' / 'handcrafted_scaler_enhanced.joblib'
FEATURE_EXTRACTOR_PATH = Path(__file__).parent.parent / 'Phase2_development'

# Decision Threshold
# Enhanced model trained on 9,998 modern emails with 5020 features
# - TF-IDF text features: 5000
# - Handcrafted phishing indicators: 20
# Achieved 100% accuracy on test set (2000 emails)
# Threshold set to 0.75 to reduce false positives on legitimate emails
DECISION_THRESHOLD = 0.75

# Logging Configuration
LOG_FOLDER = 'logs'
LOG_FILE = 'app.log'
LOG_LEVEL = 'INFO'

# Session Configuration
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
SESSION_COOKIE_SECURE = FLASK_ENV == 'production'  # HTTPS only in production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)
