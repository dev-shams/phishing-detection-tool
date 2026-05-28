"""
Enhanced Feature Extractor - Incorporates Phishing-Specific Indicators
Based on analysis of previous successful phishing detection project

Combines:
1. TF-IDF text features (for language patterns)
2. Handcrafted phishing indicators (20 features)
"""

import re
import numpy as np
from collections import defaultdict

class EnhancedFeatureExtractor:
    """Extract phishing-specific features from emails"""

    def __init__(self):
        # Phishing indicators - learned from successful previous project
        self.URGENCY_KEYWORDS = [
            'urgent', 'immediately', 'action required', 'verify', 'confirm',
            'account suspended', 'click here', 'limited time', 'expire',
            'won', 'winner', 'prize', 'claim', 'free', 'congratulations',
            'password', 'bank', 'wire transfer', 'invoice', 'update your',
            'dear customer', 'dear user', 'suspended', 'security alert',
            'act now', 'take action', 'confirm identity', 'validate account'
        ]

        self.PHISHING_DOMAINS = [
            'bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly', 'tiny.cc',
            'is.gd', 'cli.gs', 'short.link', 'ln.is'
        ]

        self.SUSPICIOUS_TLDS = [
            '.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', '.ru', '.cn',
            '.top', '.pw', '.online', '.site'
        ]

        self.LOOKALIKE_PATTERNS = {
            'paypa1': 'paypal',
            'paypa|': 'paypal',
            'paya1': 'paypal',
            'micros0ft': 'microsoft',
            'app|e': 'apple',
            'go0gle': 'google',
            'amaz0n': 'amazon',
            'drppbox': 'dropbox',
            'twitt3r': 'twitter'
        }

    def extract_url_features(self, text):
        """Extract 6 URL-based features"""
        urls = re.findall(r'http[s]?://\S+', text)

        if not urls:
            return [0, 0, 0, 0, 0, 0]

        ip_urls = sum(1 for u in urls if re.search(r'http[s]?://(?:\d{1,3}\.){3}\d{1,3}', u))
        shortener_urls = sum(1 for u in urls if any(d in u for d in self.PHISHING_DOMAINS))
        avg_url_length = np.mean([len(u) for u in urls]) if urls else 0
        deep_subdomains = sum(1 for u in urls if u.count('.') > 3)
        suspicious_tld_urls = sum(1 for u in urls if any(tld in u for tld in self.SUSPICIOUS_TLDS))
        at_in_url = sum(1 for u in urls if '@' in u)

        return [
            ip_urls,
            shortener_urls,
            avg_url_length,
            deep_subdomains,
            suspicious_tld_urls,
            at_in_url
        ]

    def extract_header_features(self, text, sender='', subject=''):
        """Extract 4 header-based features"""
        full_text = f"{sender} {subject} {text}".lower()

        # Feature 1: Domain mismatch (from != reply-to)
        from_match = re.search(r'from:\s*[\w\.\-]+@([\w\.\-]+)', full_text)
        reply_match = re.search(r'reply-to:\s*[\w\.\-]+@([\w\.\-]+)', full_text)
        from_domain = from_match.group(1) if from_match else ''
        reply_domain = reply_match.group(1) if reply_match else ''
        domain_mismatch = 1 if (from_domain and reply_domain and from_domain != reply_domain) else 0

        # Feature 2: Lookalike domain (paypa1.com, micros0ft.com)
        lookalike = 0
        for pattern, original in self.LOOKALIKE_PATTERNS.items():
            if re.search(pattern, full_text):
                lookalike = 1
                break

        # Feature 3: Numeric in domain
        numeric_domain = 1 if (from_domain and re.search(r'\d', from_domain)) else 0

        # Feature 4: Suspicious TLD in header
        all_domains = f"{from_domain} {reply_domain}"
        suspicious_tld = 1 if any(tld in all_domains for tld in self.SUSPICIOUS_TLDS) else 0

        return [domain_mismatch, lookalike, numeric_domain, suspicious_tld]

    def extract_urgency_features(self, text):
        """Extract 5 urgency and formatting features"""
        t = text
        tl = text.lower()

        # Feature 1: Urgency keywords
        urgency_count = sum(1 for kw in self.URGENCY_KEYWORDS if kw in tl)

        # Feature 2: Exclamation marks
        exclamation_count = t.count('!')

        # Feature 3: Dollar signs
        dollar_count = t.count('$')

        # Feature 4: Capitalized words (all caps)
        caps_words = len(re.findall(r'\b[A-Z]{3,}\b', t))

        # Feature 5: Has HTML tags
        has_html = 1 if re.search(r'<[a-z]+[\s/>]', tl) else 0

        return [urgency_count, exclamation_count, dollar_count, caps_words, has_html]

    def extract_basic_features(self, text):
        """Extract 5 basic email features"""
        # Feature 1: URL count
        url_count = len(re.findall(r'http[s]?://\S+', text))

        # Feature 2: Suspicious shortened URL
        has_suspicious_url = 1 if any(d in text for d in self.PHISHING_DOMAINS) else 0

        # Feature 3: Text length
        text_length = len(text)

        # Feature 4: Word count
        word_count = len(text.split())

        # Feature 5: Has reply-to header
        has_reply_to = 1 if 'reply-to' in text.lower() else 0

        return [url_count, has_suspicious_url, text_length, word_count, has_reply_to]

    def extract_all_features(self, email_data):
        """
        Extract all 20 phishing-specific features

        Args:
            email_data: Dict with 'body', 'subject', 'sender'

        Returns:
            Dict with all features
        """
        body = str(email_data.get('body', ''))
        subject = str(email_data.get('subject', ''))
        sender = str(email_data.get('sender', ''))

        # Extract all feature groups
        basic = self.extract_basic_features(body)
        urgency = self.extract_urgency_features(body)
        header = self.extract_header_features(body, sender, subject)
        url = self.extract_url_features(body)

        # Combine all features
        all_features = basic + urgency + header + url

        feature_names = [
            'url_count', 'suspicious_url', 'text_length', 'word_count', 'has_reply_to',
            'urgency_keywords', 'exclamation_marks', 'dollar_signs', 'caps_words', 'has_html',
            'domain_mismatch', 'lookalike_domain', 'numeric_domain', 'suspicious_tld_header',
            'ip_url_count', 'shortener_url_count', 'avg_url_length', 'deep_subdomain_count',
            'suspicious_tld_url', 'at_in_url'
        ]

        return dict(zip(feature_names, all_features))

    def get_threat_indicators(self, email_data):
        """
        Get human-readable threat indicators

        Returns:
            List of detected threat indicators
        """
        features = self.extract_all_features(email_data)
        body = str(email_data.get('body', ''))
        indicators = []

        if features['url_count'] > 0:
            indicators.append(f"Contains {int(features['url_count'])} URL(s)")

        if features['suspicious_url']:
            indicators.append("Suspicious or shortened URL detected")

        if features['urgency_keywords'] > 0:
            indicators.append(f"Urgency keywords found ({int(features['urgency_keywords'])})")

        if features['exclamation_marks'] > 2:
            indicators.append(f"Excessive exclamation marks ({int(features['exclamation_marks'])})")

        if features['domain_mismatch']:
            indicators.append("From and Reply-To domain mismatch detected")

        if features['lookalike_domain']:
            indicators.append("Lookalike domain detected (e.g. paypa1.com)")

        if features['numeric_domain']:
            indicators.append("Numeric characters in sender domain")

        if features['suspicious_tld_header']:
            indicators.append("Suspicious TLD in sender address")

        if features['ip_url_count'] > 0:
            indicators.append(f"IP-based URL detected ({int(features['ip_url_count'])})")

        if features['shortener_url_count'] > 0:
            indicators.append(f"URL shortener detected ({int(features['shortener_url_count'])})")

        return indicators


# For backward compatibility
class FeatureExtractor:
    """Wrapper to maintain compatibility with existing code"""

    def __init__(self):
        self.enhanced = EnhancedFeatureExtractor()

    def extract_all_features(self, email_data):
        """Extract features - now using enhanced features"""
        return self.enhanced.extract_all_features(email_data)
