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

# Model Configuration
MODEL_PATH = Path(__file__).parent.parent / 'Phase2_development' / '4_models' / 'phishing_model_phase2.pkl'
SCALER_PATH = Path(__file__).parent.parent / 'Phase2_development' / '4_models' / 'scaler_phase2.pkl'
FEATURE_EXTRACTOR_PATH = Path(__file__).parent.parent / 'Phase2_development'

# Decision Threshold (optimized from testing)
DECISION_THRESHOLD = 0.55

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
