"""
Phase 3: Phishing Email Detection Web Dashboard
Flask application for email phishing detection with web interface
"""

import os
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
from config import *
from models import PhishingDetector

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_FOLDER, LOG_FILE)),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize detector (model wrapper)
detector = None

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_email_from_file(file_path):
    """Extract email content from uploaded file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return content
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        return None

@app.before_request
def initialize_detector():
    """Initialize detector on first request"""
    global detector
    if detector is None:
        try:
            detector = PhishingDetector(
                model_path=MODEL_PATH,
                scaler_path=SCALER_PATH,
                feature_extractor_path=FEATURE_EXTRACTOR_PATH,
                threshold=DECISION_THRESHOLD
            )
            logger.info("✓ Phishing detector initialized")
        except Exception as e:
            logger.error(f"✗ Failed to initialize detector: {str(e)}")

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html', app_name=APP_NAME, app_version=APP_VERSION)

@app.route('/analyzer')
def analyzer():
    """Email analyzer page"""
    return render_template('analyzer.html', app_name=APP_NAME)

@app.route('/results')
def results():
    """Results page (accessed after analysis)"""
    result = session.get('last_result', None)
    return render_template('results.html', result=result)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """
    API endpoint for email analysis
    Accepts either text input or file upload
    """
    if not detector or not detector.is_ready():
        return jsonify({
            'success': False,
            'error': 'Detector not ready. Please check server logs.'
        }), 500

    try:
        email_text = None
        email_source = None

        # Check for text input
        if 'email_text' in request.form and request.form['email_text'].strip():
            email_text = request.form['email_text'].strip()
            email_source = 'text_input'

        # Check for file upload
        elif 'email_file' in request.files:
            file = request.files['email_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                email_text = extract_email_from_file(file_path)
                email_source = f'file_upload ({filename})'

                # Clean up file
                try:
                    os.remove(file_path)
                except:
                    pass

        if not email_text:
            return jsonify({
                'success': False,
                'error': 'Please provide email text or upload a file'
            }), 400

        # Prepare email data
        email_data = {
            'body': email_text,
            'subject': request.form.get('subject', ''),
            'sender': request.form.get('sender', ''),
            'urls': [],
            'headers': {}
        }

        # Get prediction
        result = detector.predict(email_data)

        # Store in session
        session['last_result'] = result
        session['email_source'] = email_source

        return jsonify({
            'success': True,
            'result': result,
            'email_preview': email_text[:200] + '...' if len(email_text) > 200 else email_text
        })

    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/api/status')
def api_status():
    """API endpoint for health check"""
    return jsonify({
        'status': 'operational' if detector and detector.is_ready() else 'initializing',
        'app_name': APP_NAME,
        'app_version': APP_VERSION,
        'threshold': DECISION_THRESHOLD,
        'flask_env': FLASK_ENV
    })

@app.route('/api/batch-analyze', methods=['POST'])
def api_batch_analyze():
    """API endpoint for batch email analysis (for future use)"""
    if not detector or not detector.is_ready():
        return jsonify({
            'success': False,
            'error': 'Detector not ready'
        }), 500

    try:
        data = request.get_json()
        if not data or 'emails' not in data:
            return jsonify({
                'success': False,
                'error': 'Invalid request format'
            }), 400

        emails = data['emails']
        if not isinstance(emails, list):
            return jsonify({
                'success': False,
                'error': 'Emails must be a list'
            }), 400

        results = []
        for email_text in emails:
            email_data = {
                'body': email_text,
                'subject': '',
                'sender': '',
                'urls': [],
                'headers': {}
            }
            result = detector.predict(email_data)
            results.append(result)

        return jsonify({
            'success': True,
            'count': len(results),
            'results': results
        })

    except Exception as e:
        logger.error(f"Batch analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/info')
def api_info():
    """API endpoint for application information"""
    return jsonify({
        'app_name': APP_NAME,
        'version': APP_VERSION,
        'description': 'Phishing Email Detection Tool using Random Forest ML Model',
        'model_type': 'Random Forest Classifier',
        'features': 27,
        'decision_threshold': DECISION_THRESHOLD,
        'training_data': '82,479 real emails from Kaggle dataset',
        'endpoints': {
            '/': 'Home page',
            '/analyzer': 'Email analyzer interface',
            '/api/analyze': 'Analyze single email (POST)',
            '/api/batch-analyze': 'Analyze multiple emails (POST)',
            '/api/status': 'Health check',
            '/api/info': 'Application information'
        }
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(error)}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    logger.info(f"Environment: {FLASK_ENV}")
    logger.info(f"Debug mode: {DEBUG}")
    logger.info(f"Listening on {HOST}:{PORT}")

    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG,
        use_reloader=True
    )
