"""
Phishing Email Detection Tool
Main Flask Web Application
"""

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import traceback

# Import our modules
from email_parser import EmailParser
from feature_extractor import FeatureExtractor
from ml_model import PhishingDetectionModel

# Flask app configuration
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'eml', 'msg'}

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components
email_parser = EmailParser()
feature_extractor = FeatureExtractor()
detection_model = None
model_trained = False


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def load_model():
    """Load trained model"""
    global detection_model, model_trained

    try:
        print("\n" + "="*60)
        print("INITIALIZING ML MODEL")
        print("="*60)

        # Create model instance
        detection_model = PhishingDetectionModel(model_type='random_forest')

        # Try to load saved model
        if os.path.exists('phishing_model.pkl') and os.path.exists('scaler.pkl'):
            try:
                print("Loading saved model...")
                detection_model.load_model('phishing_model.pkl', 'scaler.pkl')
                print("✓ Model loaded from saved files")
                model_trained = True
                return True
            except Exception as e:
                print(f"Could not load saved model: {e}")
                print("Will train new model...")

        # Train model with synthetic demo data
        print("\nTraining model with synthetic data...")
        import numpy as np

        # Create synthetic training data
        np.random.seed(42)

        # Legitimate emails (label 0)
        n_legit = 50
        X_legit = np.random.randn(n_legit, 27) * 0.5 + np.array(
            [1, 1, 1] +  # Header features (3)
            [1, 0, 0, 1.0, 0] +  # URL features (5)
            [0.5, 0, 0, 100, 50, 2, 0.8, 0, 1] +  # Text features (9)
            [1, 0.8, 0.8, 0, 0.8] +  # Auth features (5)
            [20, 0, 0, 0, 0]  # Domain features (5)
        )

        # Phishing emails (label 1)
        n_phish = 50
        X_phish = np.random.randn(n_phish, 27) * 0.5 + np.array(
            [0.5, 0.5, 0] +  # Header features (3)
            [3, 2, 1, 0.5, 1] +  # URL features (5)
            [3, 2, 2, 500, 150, 1.5, 0.2, 1, 2] +  # Text features (9)
            [0, 0, 0, 1, 0] +  # Auth features (5)
            [15, 1, 1, 1, 0]  # Domain features (5)
        )

        # Combine data
        X = np.vstack([X_legit, X_phish])
        y = np.hstack([np.zeros(n_legit), np.ones(n_phish)])

        print(f"  Legitimate samples: {n_legit}")
        print(f"  Phishing samples: {n_phish}")

        # Train the model
        print("Training Random Forest classifier...")
        metrics = detection_model.train(X, y)

        # Verify model is trained
        if not detection_model.is_trained:
            raise ValueError("Model training failed - is_trained flag not set")

        print("✓ Model trained successfully")
        print(f"  Accuracy: {metrics.get('accuracy', 'N/A'):.2%}")

        # Save the model
        print("Saving model...")
        detection_model.save_model('phishing_model.pkl', 'scaler.pkl')

        model_trained = True
        print("="*60)
        print("✓ MODEL INITIALIZATION COMPLETE")
        print("="*60 + "\n")
        return True

    except Exception as e:
        print(f"\n✗ ERROR LOADING MODEL: {e}")
        import traceback
        traceback.print_exc()
        model_trained = False
        return False


@app.before_request
def before_request():
    """Initialize model on first request if not already done"""
    global detection_model, model_trained

    if detection_model is None or not model_trained:
        print("Initializing model on first request...")
        load_model()


@app.route('/')
def index():
    """Serve the main dashboard"""
    return render_template('index.html', model_status='ready' if model_trained else 'initializing')


@app.route('/api/status', methods=['GET'])
def api_status():
    """Check system status"""
    return jsonify({
        'status': 'ok',
        'model_trained': model_trained,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Handle email file upload and analysis"""

    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file format. Allowed: .eml, .msg'
            }), 400

        # Save file temporarily
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        safe_filename = timestamp + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)

        file.save(filepath)

        # Parse email
        print(f"\nParsing email: {filename}")
        email_data = email_parser.parse_file(filepath)

        # Extract features
        print(f"Extracting features...")
        features = feature_extractor.extract_all_features(email_data)

        # Make prediction
        print(f"Making prediction...")
        if not model_trained:
            return jsonify({
                'error': 'Model not trained. Please train the model first.'
            }), 500

        prediction = detection_model.predict_single(features)

        # Prepare response
        response = {
            'success': True,
            'email_info': {
                'sender': email_data.get('sender', 'Unknown'),
                'sender_domain': email_data.get('sender_domain', 'Unknown'),
                'subject': email_data.get('subject', 'No Subject'),
                'to': email_data.get('to', 'Unknown'),
            },
            'prediction': prediction,
            'threat_indicators': extract_threat_indicators(email_data, features),
            'recommendation': get_recommendation(prediction),
        }

        # Clean up
        try:
            os.remove(filepath)
        except:
            pass

        return jsonify(response), 200

    except ValueError as e:
        return jsonify({'error': f'Invalid email file: {str(e)}'}), 400
    except Exception as e:
        print(f"Error processing file: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'Error processing email: {str(e)}'}), 500


@app.route('/api/analyze-text', methods=['POST'])
def api_analyze_text():
    """Analyze email content from text (for testing)"""

    try:
        data = request.json

        if not data or 'email_text' not in data:
            return jsonify({'error': 'No email text provided'}), 400

        email_text = data['email_text']

        # Create temporary email data structure
        email_data = {
            'sender': data.get('sender', 'unknown@example.com'),
            'sender_domain': data.get('sender', 'unknown@example.com').split('@')[1],
            'subject': data.get('subject', 'No Subject'),
            'to': data.get('to', 'user@example.com'),
            'reply_to': data.get('reply_to', ''),
            'body': email_text,
            'urls': feature_extractor._extract_urls(email_text),
            'headers': {}
        }

        # Extract features
        features = feature_extractor.extract_all_features(email_data)

        # Make prediction
        if not model_trained:
            return jsonify({'error': 'Model not trained.'}), 500

        prediction = detection_model.predict_single(features)

        response = {
            'success': True,
            'email_info': {
                'sender': email_data['sender'],
                'sender_domain': email_data['sender_domain'],
                'subject': email_data['subject'],
            },
            'prediction': prediction,
            'threat_indicators': extract_threat_indicators(email_data, features),
            'recommendation': get_recommendation(prediction),
        }

        return jsonify(response), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': f'Error: {str(e)}'}), 500


def extract_threat_indicators(email_data: dict, features: dict) -> list:
    """Extract and explain threat indicators"""

    indicators = []

    # Check domain spoofing
    sender_domain = email_data.get('sender_domain', '').lower()
    subject = email_data.get('subject', '').lower()

    if features.get('domain_name_mismatch', 0):
        indicators.append({
            'type': 'Domain Mismatch',
            'severity': 'high',
            'description': f'Subject mentions different company than sender domain ({sender_domain})'
        })

    # Check for phishing keywords
    phishing_keyword_count = features.get('phishing_keyword_count', 0)
    if phishing_keyword_count > 3:
        indicators.append({
            'type': 'Phishing Keywords',
            'severity': 'high',
            'description': f'Email contains {int(phishing_keyword_count)} phishing-related keywords'
        })

    # Check for urgency
    urgency_count = features.get('urgency_keyword_count', 0)
    if urgency_count > 2:
        indicators.append({
            'type': 'Urgency Language',
            'severity': 'medium',
            'description': f'Email uses urgent/pressure language ({int(urgency_count)} instances)'
        })

    # Check URLs
    url_count = features.get('url_count', 0)
    suspicious_urls = features.get('suspicious_url_count', 0)

    if suspicious_urls > 0:
        indicators.append({
            'type': 'Suspicious URLs',
            'severity': 'high',
            'description': f'{int(suspicious_urls)} out of {int(url_count)} URLs appear suspicious'
        })

    if features.get('has_ip_urls', 0):
        indicators.append({
            'type': 'IP Address URLs',
            'severity': 'high',
            'description': 'Email contains URLs with IP addresses instead of domain names'
        })

    # Check authentication
    if not features.get('has_spf', 0) and not features.get('has_dkim', 0):
        indicators.append({
            'type': 'Failed Authentication',
            'severity': 'medium',
            'description': 'Email fails SPF and DKIM authentication'
        })

    # Check for free email providers sending as company
    if features.get('is_free_email_provider', 0):
        if not sender_domain.startswith('gmail') and '@' not in sender_domain:
            indicators.append({
                'type': 'Free Email Provider',
                'severity': 'medium',
                'description': f'Sender uses free email provider ({sender_domain})'
            })

    # Check excessive caps
    if features.get('has_all_caps_words', 0):
        indicators.append({
            'type': 'Excessive Capitalization',
            'severity': 'low',
            'description': 'Email uses excessive capitalization'
        })

    return indicators[:5]  # Return top 5 indicators


def get_recommendation(prediction: dict) -> str:
    """Get recommendation based on prediction"""

    confidence = prediction['confidence_phishing']

    if prediction['classification'] == 'PHISHING':
        if confidence > 90:
            return '🚨 DANGER: This email is almost certainly a phishing attempt. DO NOT click any links or download attachments. Report it to your IT department immediately.'
        elif confidence > 70:
            return '⚠️ WARNING: This email appears to be a phishing attempt. Treat with caution. Verify the sender through another channel before responding.'
        else:
            return '⚠️ CAUTION: This email may be phishing. Be careful before clicking links or providing information.'
    else:
        if confidence < 20:
            return '✓ SAFE: This email appears to be legitimate. Standard email security practices recommended.'
        else:
            return '✓ LIKELY SAFE: This email appears legitimate, but always verify sender and links when in doubt.'


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    """Handle server errors"""
    return jsonify({'error': 'Server error'}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("PHISHING EMAIL DETECTION TOOL")
    print("="*60)

    # Load model
    print("\nInitializing model...")
    if load_model():
        print("✓ Model loaded successfully")
    else:
        print("✗ Could not load model")

    print("\n" + "="*60)
    print("Starting Flask server...")
    print("="*60)
    print("\nOpen your browser and go to: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server\n")

    # Run Flask app
    app.run(
        debug=True,
        host='127.0.0.1',
        port=5000,
        use_reloader=False
    )
