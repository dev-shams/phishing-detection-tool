"""
Phase 3: Phishing Detection Model Wrapper
Enhanced version using TF-IDF (5000 features) + Handcrafted phishing indicators (20 features)
Based on successful techniques from previous project analysis

Total feature space: 5020 features
Model: Random Forest trained on modern datasets (MeAJOR Corpus + Kaggle 2026)
"""

import sys
import joblib
import pickle
import cloudpickle
import numpy as np
import re
from pathlib import Path
import logging
import os

try:
    import onnxruntime as rt
except ImportError:
    rt = None

try:
    import gdown
except ImportError:
    gdown = None

# Setup logger
logger = logging.getLogger(__name__)

# Feature extraction constants (MUST match training script)
URGENCY_KEYWORDS = [
    'urgent', 'immediately', 'action required', 'verify', 'confirm',
    'account suspended', 'click here', 'limited time', 'expire',
    'won', 'winner', 'prize', 'claim', 'free', 'congratulations',
    'password', 'bank', 'wire transfer', 'invoice', 'update your',
    'dear customer', 'dear user', 'suspended', 'security alert'
]

PHISHING_DOMAINS = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly', 'tiny.cc', 'is.gd', 'cli.gs']
SUSPICIOUS_TLDS = ['.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', '.ru', '.cn']

# Google Drive direct download links (Updated May 29 - Enhanced model with 5020 features)
GDRIVE_MODEL_LINK = "https://drive.google.com/uc?export=download&id=1IvuF3zMlxF6rG09D7w81qF-W8QUaP6Oy"
GDRIVE_SCALER_LINK = "https://drive.google.com/uc?export=download&id=1Ezd3k5stwlfrhxUZj-irT14i8vUva4Xa"
GDRIVE_TFIDF_VECTORIZER_LINK = "https://drive.google.com/uc?export=download&id=1prgPNRK_SJTy2EFx_iH2WNe6XZzMFJkT"
GDRIVE_HANDCRAFTED_SCALER_LINK = "https://drive.google.com/uc?export=download&id=1W1gtZfGXAo-e7JpP5cMNS6I5Rc6tydAG"

class PhishingDetector:
    """
    Enhanced phishing detector using:
    - TF-IDF vectorization (5000 features) on email text
    - Handcrafted phishing-specific features (20 features)
    - Random Forest classifier trained on 9998 modern emails

    Total feature space: 5020 features
    """

    def __init__(self, model_path, scaler_path, feature_extractor_path,
                 tfidf_vectorizer_path=None, handcrafted_scaler_path=None, threshold=0.50):
        """
        Initialize the detector with model and component paths

        Args:
            model_path: Path to trained Logistic Regression model
            scaler_path: Path to StandardScaler for combined features
            feature_extractor_path: Path to Phase 2 directory with enhanced FeatureExtractor
            tfidf_vectorizer_path: Path to TF-IDF vectorizer (optional, calculated from model_path)
            handcrafted_scaler_path: Path to MinMaxScaler for handcrafted features (REQUIRED for fix #1)
            threshold: Decision threshold for phishing classification (default 0.50 for Logistic Regression)
        """
        self.model = None
        self.onnx_session = None  # For ONNX model inference
        self.scaler = None
        self.feature_extractor = None
        self.tfidf_vectorizer = None
        self.handcrafted_scaler = None  # NEW: MinMaxScaler for handcrafted features (FIX #1)
        self.threshold = threshold
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path)
        self.feature_extractor_path = Path(feature_extractor_path)

        # Derive paths if not provided
        model_dir = self.model_path.parent
        self.onnx_model_path = model_dir / "phishing_model_enhanced.onnx"
        self.tfidf_vectorizer_path = Path(tfidf_vectorizer_path) if tfidf_vectorizer_path else (model_dir / "tfidf_vectorizer_enhanced.joblib")
        self.handcrafted_scaler_path = Path(handcrafted_scaler_path) if handcrafted_scaler_path else (model_dir / "handcrafted_scaler_enhanced.joblib")

        # Ensure all model files exist (download from Google Drive if needed)
        self._ensure_model_files()

        # Load model components
        self._load_onnx_model()  # Try ONNX first (version-agnostic)
        if self.onnx_session is None:
            self._load_model()  # Fall back to sklearn model
        self._load_scaler()
        self._load_tfidf_vectorizer()
        self._load_handcrafted_scaler()
        self._load_feature_extractor()

    def _download_from_gdrive(self, url, dest_path):
        """
        Download a file from Google Drive using gdown (handles large files reliably)

        Args:
            url: Google Drive direct download link or file ID
            dest_path: Local path to save the file
        """
        try:
            logger.info(f"Downloading from Google Drive to {dest_path}...")

            # Create directory if it doesn't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Use gdown for reliable Google Drive downloads
            if gdown:
                # Extract file ID from URL if needed
                file_id = url.split('/d/')[1].split('/')[0] if '/d/' in url else url.split('id=')[-1]

                logger.info(f"Using gdown to download file ID: {file_id}")
                output = gdown.download(
                    f'https://drive.google.com/uc?id={file_id}',
                    str(dest_path),
                    quiet=False,
                    use_cookies=False
                )

                if output and Path(output).exists():
                    logger.info(f"✓ Successfully downloaded to {dest_path}")
                    return True
                else:
                    logger.error("gdown download failed or file not created")
                    return False
            else:
                logger.error("gdown not installed, cannot download from Google Drive")
                return False

        except Exception as e:
            logger.error(f"✗ Failed to download from Google Drive: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _ensure_model_files(self):
        """
        Ensure model files exist locally
        Download from Google Drive if they don't exist
        """
        # Check if model file exists
        if not self.model_path.exists():
            logger.warning(f"Model file not found: {self.model_path}")
            logger.info("Attempting to download from Google Drive...")
            if not self._download_from_gdrive(GDRIVE_MODEL_LINK, self.model_path):
                logger.error("Failed to download model file")
                raise RuntimeError("Could not obtain model file from local storage or Google Drive")
        else:
            logger.info(f"✓ Model file found: {self.model_path}")

        # Check if scaler file exists
        if not self.scaler_path.exists():
            logger.warning(f"Scaler file not found: {self.scaler_path}")
            logger.info("Attempting to download from Google Drive...")
            if not self._download_from_gdrive(GDRIVE_SCALER_LINK, self.scaler_path):
                logger.error("Failed to download scaler file")
                raise RuntimeError("Could not obtain scaler file from local storage or Google Drive")
        else:
            logger.info(f"✓ Scaler file found: {self.scaler_path}")

        # Check if tfidf vectorizer file exists
        if not self.tfidf_vectorizer_path.exists():
            logger.warning(f"TF-IDF vectorizer file not found: {self.tfidf_vectorizer_path}")
            logger.info("Attempting to download from Google Drive...")
            if not self._download_from_gdrive(GDRIVE_TFIDF_VECTORIZER_LINK, self.tfidf_vectorizer_path):
                logger.error("Failed to download TF-IDF vectorizer file")
                # Don't raise - system can work with zeros
                logger.warning("Will continue without TF-IDF vectorizer")
        else:
            logger.info(f"✓ TF-IDF vectorizer file found: {self.tfidf_vectorizer_path}")

        # Check if handcrafted scaler file exists
        if not self.handcrafted_scaler_path.exists():
            logger.warning(f"Handcrafted scaler file not found: {self.handcrafted_scaler_path}")
            logger.info("Attempting to download from Google Drive...")
            if not self._download_from_gdrive(GDRIVE_HANDCRAFTED_SCALER_LINK, self.handcrafted_scaler_path):
                logger.error("Failed to download handcrafted scaler file")
                # Don't raise - system can work with fallback scaler
                logger.warning("Will continue with fallback MinMaxScaler")
        else:
            logger.info(f"✓ Handcrafted scaler file found: {self.handcrafted_scaler_path}")

    def _load_onnx_model(self):
        """Load the ONNX model (version-agnostic, works with any sklearn version)"""
        try:
            if not rt:
                logger.warning("onnxruntime not installed, falling back to sklearn model")
                return

            if self.onnx_model_path.exists():
                self.onnx_session = rt.InferenceSession(str(self.onnx_model_path))
                logger.info(f"✓ ONNX model loaded (version-agnostic): {self.onnx_model_path.name}")
                return True
            else:
                logger.debug(f"ONNX model not found at {self.onnx_model_path}")
                return False
        except Exception as e:
            logger.warning(f"Failed to load ONNX model: {str(e)}, will use sklearn model")
            return False

    def _load_model(self):
        """Load the trained model from cloudpickle (version-agnostic)"""
        try:
            # Try cloudpickle first (sklearn version-agnostic)
            cloudpkl_path = self.model_path.with_suffix('.cloudpkl')
            if cloudpkl_path.exists():
                with open(cloudpkl_path, 'rb') as f:
                    self.model = cloudpickle.load(f)
                logger.info(f"✓ Model loaded (cloudpickle): {cloudpkl_path}")
            # Fall back to regular pickle
            elif self.model_path.with_suffix('.pkl').exists():
                pkl_path = self.model_path.with_suffix('.pkl')
                with open(pkl_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"✓ Model loaded (pickle): {pkl_path}")
            # Fall back to joblib
            elif self.model_path.exists():
                self.model = joblib.load(self.model_path)
                logger.info(f"✓ Model loaded (joblib): {self.model_path}")
            else:
                raise FileNotFoundError(f"Model file not found")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise RuntimeError(f"Could not load model file: {str(e)}")

    def _load_scaler(self):
        """Load the feature scaler from cloudpickle (version-agnostic)"""
        try:
            # Try cloudpickle first
            cloudpkl_path = self.scaler_path.with_suffix('.cloudpkl')
            if cloudpkl_path.exists():
                with open(cloudpkl_path, 'rb') as f:
                    self.scaler = cloudpickle.load(f)
                logger.info(f"✓ Scaler loaded (cloudpickle): {cloudpkl_path}")
            # Fall back to pickle
            elif self.scaler_path.with_suffix('.pkl').exists():
                pkl_path = self.scaler_path.with_suffix('.pkl')
                with open(pkl_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info(f"✓ Scaler loaded (pickle): {pkl_path}")
            # Fall back to joblib
            elif self.scaler_path.exists():
                self.scaler = joblib.load(self.scaler_path)
                logger.info(f"✓ Scaler loaded (joblib): {self.scaler_path}")
            else:
                raise FileNotFoundError(f"Scaler file not found")
        except Exception as e:
            logger.error(f"Failed to load scaler: {str(e)}")
            raise RuntimeError(f"Could not load scaler file: {str(e)}")

    def _load_tfidf_vectorizer(self):
        """Load the TF-IDF vectorizer from cloudpickle (version-agnostic)"""
        try:
            # Try cloudpickle first
            cloudpkl_path = self.tfidf_vectorizer_path.with_suffix('.cloudpkl')
            if cloudpkl_path.exists():
                with open(cloudpkl_path, 'rb') as f:
                    self.tfidf_vectorizer = cloudpickle.load(f)
                logger.info(f"✓ TF-IDF vectorizer loaded (cloudpickle): {self.tfidf_vectorizer.max_features} features")
            # Fall back to pickle
            elif self.tfidf_vectorizer_path.with_suffix('.pkl').exists():
                pkl_path = self.tfidf_vectorizer_path.with_suffix('.pkl')
                with open(pkl_path, 'rb') as f:
                    self.tfidf_vectorizer = pickle.load(f)
                logger.info(f"✓ TF-IDF vectorizer loaded (pickle): {self.tfidf_vectorizer.max_features} features")
            # Fall back to joblib
            elif self.tfidf_vectorizer_path.exists():
                self.tfidf_vectorizer = joblib.load(self.tfidf_vectorizer_path)
                logger.info(f"✓ TF-IDF vectorizer loaded (joblib): {self.tfidf_vectorizer.max_features} features")
            else:
                logger.warning(f"TF-IDF vectorizer not found")
                return
        except Exception as e:
            logger.error(f"✗ Failed to load TF-IDF vectorizer: {str(e)}")
            # Don't raise - might still work with handcrafted features only

    def _load_handcrafted_scaler(self):
        """Load the handcrafted features scaler (MinMaxScaler) from cloudpickle (version-agnostic)"""
        try:
            # Try cloudpickle first
            cloudpkl_path = self.handcrafted_scaler_path.with_suffix('.cloudpkl')
            if cloudpkl_path.exists():
                with open(cloudpkl_path, 'rb') as f:
                    self.handcrafted_scaler = cloudpickle.load(f)
                logger.info(f"✓ Handcrafted scaler loaded (cloudpickle): {cloudpkl_path}")
            # Fall back to pickle
            elif self.handcrafted_scaler_path.with_suffix('.pkl').exists():
                pkl_path = self.handcrafted_scaler_path.with_suffix('.pkl')
                with open(pkl_path, 'rb') as f:
                    self.handcrafted_scaler = pickle.load(f)
                logger.info(f"✓ Handcrafted scaler loaded (pickle): {pkl_path}")
            # Fall back to joblib
            elif self.handcrafted_scaler_path.exists():
                self.handcrafted_scaler = joblib.load(self.handcrafted_scaler_path)
                logger.info(f"✓ Handcrafted scaler loaded (joblib): {self.handcrafted_scaler_path}")
            else:
                logger.warning(f"Handcrafted scaler not found")
                return
        except Exception as e:
            logger.error(f"✗ Failed to load handcrafted scaler: {str(e)}")
            # Don't raise - will use default MinMaxScaler if needed

    def _extract_handcrafted_features(self, email_data):
        """
        Extract 20 handcrafted phishing-specific features (MUST MATCH TRAINING)

        This method ensures consistency between training and prediction.
        Features are the same as those used in train_enhanced_model.py

        Returns:
            numpy array of shape (1, 20) with handcrafted features
        """
        # Combine all text fields
        text = str(email_data.get('body', '')) + ' ' + str(email_data.get('subject', '')) + ' ' + str(email_data.get('sender', ''))
        t = str(text)
        tl = t.lower()

        # Phase 1 Features (10): Basic phishing indicators
        p1_features = [
            len(re.findall(r'http[s]?://\S+', t)),  # 1. url_count
            len(re.findall(r'http[s]?://(?:\d{1,3}\.){3}\d{1,3}|bit\.ly|tinyurl|goo\.gl', t)),  # 2. suspicious_url
            sum(1 for kw in URGENCY_KEYWORDS if kw in tl),  # 3. urgency_keywords
            t.count('!'),  # 4. exclamation_marks
            t.count('$'),  # 5. dollar_signs
            len(re.findall(r'\b[A-Z]{3,}\b', t)),  # 6. caps_words
            len(t),  # 7. text_length
            len(t.split()),  # 8. word_count
            1 if re.search(r'<[a-z]+[\s/>]', tl) else 0,  # 9. has_html
            1 if 'reply-to' in tl else 0,  # 10. has_reply_to
        ]

        # Phase 2 Features (10): Advanced signals
        # Header analysis (4)
        fm = re.search(r'from:\s*[\w\.\-]+@([\w\.\-]+)', tl)
        rm = re.search(r'reply-to:\s*[\w\.\-]+@([\w\.\-]+)', tl)
        fd = fm.group(1) if fm else ''
        rd = rm.group(1) if rm else ''

        header_features = [
            1 if (fd and rd and fd != rd) else 0,  # 11. domain_mismatch
            1 if re.search(r'(paypa[^l]|micros[^o]ft|app[^l]e|go{3,}gle|amaz[^o]n)', tl) else 0,  # 12. lookalike_domain
            1 if (fd and re.search(r'\d', fd)) else 0,  # 13. numeric_in_domain
            1 if any(tld in (fd + ' ' + rd) for tld in SUSPICIOUS_TLDS) else 0,  # 14. suspicious_tld_header
        ]

        # URL analysis (6)
        urls = re.findall(r'http[s]?://\S+', t)
        if not urls:
            url_features = [0, 0, 0, 0, 0, 0]
        else:
            url_features = [
                sum(1 for u in urls if re.search(r'http[s]?://(?:\d{1,3}\.){3}\d{1,3}', u)),  # 15. ip_url_count
                sum(1 for u in urls if any(d in u for d in PHISHING_DOMAINS)),  # 16. shortener_url_count
                float(np.mean([len(u) for u in urls])),  # 17. avg_url_length
                sum(1 for u in urls if u.count('.') > 3),  # 18. deep_subdomain_count
                sum(1 for u in urls if any(tld in u for tld in SUSPICIOUS_TLDS)),  # 19. suspicious_tld_url
                sum(1 for u in urls if '@' in u),  # 20. at_in_url
            ]

        features = np.array(p1_features + header_features + url_features).reshape(1, -1)
        logger.debug(f"Extracted handcrafted features: {features.shape}")
        return features

    def _load_feature_extractor(self):
        """Load the enhanced feature extractor from Phase 2 (for threat indicators only)"""
        try:
            # Add Phase 2 directory to path
            sys.path.insert(0, str(self.feature_extractor_path))

            # Try to load EnhancedFeatureExtractor first
            try:
                from feature_extractor_enhanced import EnhancedFeatureExtractor
                self.feature_extractor = EnhancedFeatureExtractor()
                logger.info("✓ EnhancedFeatureExtractor loaded (for threat indicators)")
            except ImportError:
                # Fall back to original FeatureExtractor
                from feature_extractor import FeatureExtractor
                self.feature_extractor = FeatureExtractor()
                logger.info("✓ FeatureExtractor loaded (for threat indicators)")
        except Exception as e:
            logger.warning(f"⚠ Failed to load feature extractor: {str(e)}")
            # Don't raise - we can still work without threat indicators

    def predict(self, email_data):
        """
        Make an enhanced prediction on email data
        Combines TF-IDF features (5000) + Handcrafted phishing features (20)

        Args:
            email_data: Dictionary with email components:
                - body: Email body text (required)
                - subject: Email subject (optional)
                - sender: Sender email address (optional)
                - urls: List of URLs in email (optional)
                - headers: Email headers dict (optional)

        Returns:
            Dictionary with prediction results including threat indicators
        """
        try:
            logger.info("Starting prediction...")

            # Ensure required fields exist
            if 'body' not in email_data:
                email_data['body'] = ''
            if 'subject' not in email_data:
                email_data['subject'] = ''
            if 'sender' not in email_data:
                email_data['sender'] = ''
            if 'urls' not in email_data:
                email_data['urls'] = []
            if 'headers' not in email_data:
                email_data['headers'] = {}

            email_body = str(email_data.get('body', ''))
            logger.debug(f"Email body length: {len(email_body)} characters")

            # ============================================================
            # STEP 1: Extract Handcrafted Phishing Features (20 features)
            # ============================================================
            try:
                # Use internal feature extraction (matches training exactly)
                handcrafted_values = self._extract_handcrafted_features(email_data)
                logger.debug(f"Handcrafted features extracted: {handcrafted_values.shape}")
            except Exception as e:
                logger.error(f"STEP 1 FAILED - Handcrafted feature extraction: {str(e)}")
                raise

            # Handcrafted features will be combined with TF-IDF
            # Both will be scaled together with StandardScaler in STEP 4
            handcrafted_scaled = handcrafted_values
            logger.debug(f"Handcrafted features ready for combination: {handcrafted_scaled.shape}")

            # ============================================================
            # STEP 2: Extract TF-IDF Features
            # ============================================================
            try:
                if self.tfidf_vectorizer:
                    tfidf_features = self.tfidf_vectorizer.transform([email_body]).toarray()
                else:
                    # Fallback: use zeros matching actual vectorizer size
                    # NOTE: Training data only had ~5 unique terms due to homogeneity
                    n_tfidf = 5 if not hasattr(self, '_n_tfidf') else self._n_tfidf
                    logger.warning(f"TF-IDF vectorizer not available, using {n_tfidf} zero features")
                    tfidf_features = np.zeros((1, n_tfidf))
                logger.debug(f"TF-IDF features extracted: {tfidf_features.shape}")
            except Exception as e:
                logger.error(f"STEP 2 FAILED - TF-IDF extraction: {str(e)}")
                raise

            # ============================================================
            # STEP 3: Combine Features
            # ============================================================
            try:
                combined_features = np.hstack([tfidf_features, handcrafted_scaled])
                logger.debug(f"Features combined: {combined_features.shape}")
            except Exception as e:
                logger.error(f"STEP 3 FAILED - Feature combination: {str(e)}")
                raise

            # ============================================================
            # STEP 4: Scale Combined Features
            # ============================================================
            try:
                X_scaled = self.scaler.transform(combined_features)
                logger.debug(f"Combined features scaled: {X_scaled.shape}")
            except Exception as e:
                logger.error(f"STEP 4 FAILED - Combined scaling: {str(e)}")
                raise

            # ============================================================
            # STEP 5: Detect Out-of-Domain Emails
            # ============================================================
            # Check if email matches training vocabulary
            tfidf_nonzero = np.count_nonzero(np.array(self.tfidf_vectorizer.transform([email_body]).toarray()) if self.tfidf_vectorizer else [])
            is_out_of_domain = tfidf_nonzero == 0  # No vocabulary matches
            logger.debug(f"TF-IDF vocabulary matches: {tfidf_nonzero} (out-of-domain: {is_out_of_domain})")

            # ============================================================
            # STEP 6: Make Prediction
            # ============================================================
            try:
                if self.onnx_session:
                    # Use ONNX for prediction (version-agnostic)
                    input_name = self.onnx_session.get_inputs()[0].name
                    label_name = self.onnx_session.get_outputs()[0].name
                    pred_name = self.onnx_session.get_outputs()[1].name

                    pred_onx = self.onnx_session.run(
                        [label_name, pred_name],
                        {input_name: X_scaled.astype(np.float32)}
                    )
                    probabilities = pred_onx[1][0]  # Get probabilities
                    phishing_probability = float(probabilities[1])
                    logger.debug(f"Prediction made (ONNX): {phishing_probability:.4f}")
                else:
                    # Fall back to sklearn
                    probabilities = self.model.predict_proba(X_scaled)[0]
                    phishing_probability = float(probabilities[1])
                    logger.debug(f"Prediction made (sklearn): {phishing_probability:.4f}")

                # For out-of-domain emails with extreme confidence, apply sanity check
                if is_out_of_domain and phishing_probability >= 0.99:
                    logger.warning(f"Out-of-domain email with extreme confidence - applying conservative adjustment")
                    # Adjust to moderate confidence instead of extreme
                    phishing_probability = 0.50
                    logger.debug(f"Adjusted probability: {phishing_probability:.4f}")
            except Exception as e:
                logger.error(f"STEP 6 FAILED - Model prediction: {str(e)}")
                raise

            # Apply decision threshold
            # With Logistic Regression + proper scaling, 0.50 is optimal
            is_phishing = phishing_probability >= self.threshold
            logger.debug(f"Decision: {'PHISHING' if is_phishing else 'LEGITIMATE'} (threshold={self.threshold}, prob={phishing_probability:.4f})")

            # ============================================================
            # STEP 7: Determine Risk Level (aligned with classification)
            # ============================================================
            try:
                if is_phishing:
                    # Email classified as PHISHING
                    if phishing_probability >= 0.9:
                        risk_level = "CRITICAL"
                    else:
                        risk_level = "HIGH"
                else:
                    # Email classified as LEGITIMATE
                    if phishing_probability >= 0.5:
                        risk_level = "MEDIUM"  # Borderline but still safe
                    else:
                        risk_level = "LOW"  # Definitely safe
                logger.debug(f"Risk level: {risk_level}")
            except Exception as e:
                logger.error(f"STEP 6 FAILED - Risk level determination: {str(e)}")
                raise

            # ============================================================
            # STEP 8: Extract Threat Indicators
            # ============================================================
            threat_indicators = []
            try:
                # Use the get_threat_indicators method if available
                if hasattr(self.feature_extractor, 'get_threat_indicators'):
                    threat_indicators = self.feature_extractor.get_threat_indicators(email_data)
                    logger.debug(f"Threat indicators extracted: {len(threat_indicators)} found")
            except Exception as e:
                logger.warning(f"Could not extract threat indicators: {str(e)}")

            # ============================================================
            # STEP 9: Prepare Result
            # ============================================================
            result = {
                'classification': 'PHISHING' if is_phishing else 'LEGITIMATE',
                'confidence_phishing': round(phishing_probability * 100, 2),
                'confidence_legitimate': round((1 - phishing_probability) * 100, 2),
                'decision_score': round(phishing_probability, 4),
                'threshold': self.threshold,
                'risk_level': risk_level,
                'is_phishing': is_phishing,
                'threat_indicators': threat_indicators,
                'feature_count': combined_features.shape[1]  # Should be 5020
            }

            logger.info(f"Prediction: {result['classification']} ({result['confidence_phishing']}%) - Risk: {risk_level}")
            if threat_indicators:
                logger.info(f"  Threat indicators: {len(threat_indicators)} detected")
            return result

        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'classification': 'ERROR',
                'error': str(e),
                'confidence_phishing': 0,
                'confidence_legitimate': 0,
                'decision_score': 0,
                'threshold': self.threshold,
                'risk_level': 'UNKNOWN',
                'threat_indicators': [],
                'feature_count': 0
            }

    def batch_predict(self, email_list):
        """
        Make predictions on multiple emails

        Args:
            email_list: List of email_data dictionaries

        Returns:
            List of prediction results
        """
        results = []
        for email_data in email_list:
            result = self.predict(email_data)
            results.append(result)
        return results

    def is_ready(self):
        """Check if detector is ready for predictions"""
        # Core components required
        # Either ONNX session OR sklearn model must be available
        has_model = (self.onnx_session is not None) or (self.model is not None)
        core_ready = (has_model and
                      self.scaler is not None and
                      self.feature_extractor is not None)

        # Log status
        model_type = "ONNX" if self.onnx_session else "sklearn" if self.model else "None"
        components_status = f"Model:{model_type}, Scaler:{self.scaler is not None}, FE:{self.feature_extractor is not None}, TFIDF:{self.tfidf_vectorizer is not None}"
        if not core_ready:
            logger.warning(f"Detector not ready - Missing components: {components_status}")
        else:
            logger.debug(f"Detector ready - Components: {components_status}")

        return core_ready
