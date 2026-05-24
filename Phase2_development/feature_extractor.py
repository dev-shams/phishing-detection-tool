"""
Feature Extraction Module
Extracts meaningful features from parsed emails for ML model
"""

import re
from typing import Dict, List
from collections import Counter

class FeatureExtractor:
    """Extract features from email data for machine learning"""

    # Phishing-related keywords (expanded list)
    PHISHING_KEYWORDS = [
        'verify', 'confirm', 'urgent', 'action required', 'update',
        'click here', 'activate', 'suspended', 'claim', 'reset',
        'unusual activity', 'security alert', 'locked', 'download',
        'confirm identity', 'update information', 'verify account',
        'confirm account', 'invalid', 'expired', 'authenticate',
        'reactivate', 'unusual access', 'suspicious activity',
        'immediate action', 'validate', 'secure your account',
        'protect your account', 'resolve issue', 'billing problem'
    ]

    # Urgency keywords
    URGENCY_KEYWORDS = [
        'urgent', 'immediately', 'asap', 'right now', 'quickly',
        'hurry', 'expire', 'expired', 'deadline', 'rush',
        'act now', 'limited time', 'immediate action'
    ]

    # Authority keywords
    AUTHORITY_KEYWORDS = [
        'ceo', 'cfo', 'manager', 'admin', 'administrator',
        'director', 'executive', 'support', 'security',
        'bank', 'paypal', 'amazon', 'apple', 'microsoft',
        'google', 'federal', 'government', 'official'
    ]

    def __init__(self):
        self.features = {}

    def extract_all_features(self, email_data: Dict) -> Dict[str, float]:
        """
        Extract all features from email data

        Args:
            email_data: Dictionary from EmailParser

        Returns:
            Dictionary of numerical features
        """
        features = {}

        # Header-based features
        features.update(self._extract_header_features(email_data))

        # URL-based features
        features.update(self._extract_url_features(email_data))

        # Text-based features
        features.update(self._extract_text_features(email_data))

        # Authentication features
        features.update(self._extract_authentication_features(email_data))

        # Domain features
        features.update(self._extract_domain_features(email_data))

        return features

    def _extract_header_features(self, email_data: Dict) -> Dict[str, float]:
        """Extract features from email headers"""
        headers = email_data.get('headers', {})

        return {
            'has_reply_to': 1.0 if email_data.get('reply_to') else 0.0,
            'has_return_path': 1.0 if 'return-path' in headers else 0.0,
            'has_received': float(len([k for k in headers if 'received' in k.lower()])),
        }

    def _extract_url_features(self, email_data: Dict) -> Dict[str, float]:
        """Extract features related to URLs"""
        urls = email_data.get('urls', [])

        if not urls:
            return {
                'url_count': 0.0,
                'suspicious_url_count': 0.0,
                'has_shortened_urls': 0.0,
                'url_domain_diversity': 0.0,
                'has_ip_urls': 0.0,
            }

        suspicious_count = 0
        domains_in_urls = []
        has_ip = 0
        has_shortened = 0

        for url in urls:
            if self._is_suspicious_url(url):
                suspicious_count += 1
            if self._is_ip_address(url):
                has_ip = 1
            if self._is_shortened_url(url):
                has_shortened = 1

            domain = self._extract_domain_from_url(url)
            if domain:
                domains_in_urls.append(domain)

        # Domain diversity (unique domains)
        unique_domains = len(set(domains_in_urls))
        diversity = unique_domains / len(urls) if urls else 0.0

        return {
            'url_count': float(len(urls)),
            'suspicious_url_count': float(suspicious_count),
            'has_shortened_urls': float(has_shortened),
            'url_domain_diversity': diversity,
            'has_ip_urls': float(has_ip),
        }

    def _extract_text_features(self, email_data: Dict) -> Dict[str, float]:
        """Extract features from email body and subject"""
        body = email_data.get('body', '').lower()
        subject = email_data.get('subject', '').lower()
        full_text = body + ' ' + subject

        # Count keywords
        phishing_count = self._count_keywords(full_text, self.PHISHING_KEYWORDS)
        urgency_count = self._count_keywords(full_text, self.URGENCY_KEYWORDS)
        authority_count = self._count_keywords(full_text, self.AUTHORITY_KEYWORDS)

        # Text statistics
        body_length = len(body)
        word_count = len(body.split())
        char_to_word_ratio = body_length / word_count if word_count > 0 else 0

        # Spelling/grammar (simple heuristic)
        spelling_score = self._estimate_spelling_quality(body)

        return {
            'phishing_keyword_count': float(phishing_count),
            'urgency_keyword_count': float(urgency_count),
            'authority_keyword_count': float(authority_count),
            'body_length': float(body_length),
            'word_count': float(word_count),
            'char_to_word_ratio': float(char_to_word_ratio),
            'spelling_quality_score': float(spelling_score),
            'has_all_caps_words': float(self._has_excessive_caps(body)),
            'has_exclamation_marks': float(body.count('!')),
        }

    def _extract_authentication_features(self, email_data: Dict) -> Dict[str, float]:
        """Extract email authentication related features"""
        headers = email_data.get('headers', {})

        return {
            'has_dkim': 1.0 if 'dkim-signature' in headers else 0.0,
            'has_spf': 1.0 if self._check_spf_header(headers) else 0.0,
            'has_dmarc': 1.0 if self._check_dmarc_header(headers) else 0.0,
            'has_x_mailer': 1.0 if 'x-mailer' in headers else 0.0,
            'has_x_priority': 1.0 if 'x-priority' in headers else 0.0,
        }

    def _extract_domain_features(self, email_data: Dict) -> Dict[str, float]:
        """Extract features related to sender domain"""
        sender = email_data.get('sender', '')
        sender_domain = email_data.get('sender_domain', '')
        to = email_data.get('to', '')
        subject = email_data.get('subject', '')

        domain_length = len(sender_domain)
        has_suspicious_tld = self._has_suspicious_tld(sender_domain)
        is_free_email = self._is_free_email_provider(sender_domain)
        domain_mismatch = self._check_domain_mismatch(subject, sender_domain)

        return {
            'sender_domain_length': float(domain_length),
            'has_suspicious_tld': float(has_suspicious_tld),
            'is_free_email_provider': float(is_free_email),
            'domain_name_mismatch': float(domain_mismatch),
            'sender_domain_age': 0.0,  # Would need WHOIS lookup
        }

    # Helper methods

    def _count_keywords(self, text: str, keywords: List[str]) -> int:
        """Count occurrences of keywords in text"""
        count = 0
        for keyword in keywords:
            count += len(re.findall(r'\b' + keyword + r'\b', text, re.IGNORECASE))
        return count

    def _is_suspicious_url(self, url: str) -> bool:
        """Check if URL has phishing characteristics"""
        url_lower = url.lower()

        # Check for @ symbol (can hide real domain)
        if '@' in url_lower:
            return True

        # Check for IP address
        if self._is_ip_address(url):
            return True

        # Check for too many dots
        if url.count('.') > 3:
            return True

        # Check for common misspellings
        if self._has_misspelled_domain(url):
            return True

        return False

    def _is_ip_address(self, text: str) -> bool:
        """Check if text contains an IP address"""
        ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        return bool(re.search(ip_pattern, text))

    def _is_shortened_url(self, url: str) -> bool:
        """Check if URL is shortened"""
        short_url_domains = ['bit.ly', 'tinyurl', 'goo.gl', 'ow.ly', 'short.link']
        url_lower = url.lower()
        return any(domain in url_lower for domain in short_url_domains)

    def _extract_domain_from_url(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            # Remove protocol
            if '://' in url:
                url = url.split('://')[1]
            # Remove path
            domain = url.split('/')[0]
            # Remove port
            domain = domain.split(':')[0]
            return domain
        except:
            return ""

    def _estimate_spelling_quality(self, text: str) -> float:
        """
        Estimate spelling quality (simple heuristic)
        Returns 0-1 score
        """
        if not text:
            return 1.0

        # Look for common misspellings or strange character combinations
        suspicious_patterns = [
            r'\b[a-z]{1,2}\b',  # Single/double letter words (too many)
            r'[aeiou]{3,}',      # Too many vowels
            r'\d{10,}',          # Very long number sequences
        ]

        text_lower = text.lower()
        issues = 0

        for pattern in suspicious_patterns:
            issues += len(re.findall(pattern, text_lower))

        # Score: fewer issues = higher score
        quality_score = max(0, 1 - (issues / 100))
        return quality_score

    def _has_excessive_caps(self, text: str) -> float:
        """Check for excessive capitalization"""
        if not text:
            return 0.0

        uppercase_count = sum(1 for c in text if c.isupper())
        total_count = len([c for c in text if c.isalpha()])

        if total_count == 0:
            return 0.0

        ratio = uppercase_count / total_count
        return 1.0 if ratio > 0.3 else 0.0  # More than 30% caps is suspicious

    def _check_spf_header(self, headers: Dict) -> bool:
        """Check if SPF header is present"""
        return 'authentication-results' in headers or 'received-spf' in headers

    def _check_dmarc_header(self, headers: Dict) -> bool:
        """Check if DMARC header is present"""
        return 'authentication-results' in headers

    def _has_suspicious_tld(self, domain: str) -> bool:
        """Check if domain has suspicious TLD"""
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.online', '.xyz']
        return any(domain.endswith(tld) for tld in suspicious_tlds)

    def _is_free_email_provider(self, domain: str) -> bool:
        """Check if domain is a free email provider"""
        free_providers = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'aol.com', 'mail.com', 'protonmail.com', 'tutanota.com'
        ]
        return domain in free_providers

    def _has_misspelled_domain(self, url: str) -> bool:
        """Check for misspelled popular domains"""
        misspelled = [
            'gmai1', 'gmial', 'g00gle', 'googl', 'ama2on', 'amaz0n',
            'paypa1', 'payypal', 'microsof', 'app1e', 'rn5', 'alibab'
        ]
        url_lower = url.lower()
        return any(miss in url_lower for miss in misspelled)

    def _check_domain_mismatch(self, subject: str, domain: str) -> bool:
        """Check if domain matches what's mentioned in subject"""
        # Simple check: if subject mentions a different company
        companies = ['amazon', 'google', 'apple', 'microsoft', 'paypal', 'bank']
        subject_lower = subject.lower()
        domain_lower = domain.lower()

        for company in companies:
            if company in subject_lower and company not in domain_lower:
                return True

        return False

    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        if not text:
            return []

        # URL regex pattern
        url_pattern = r'https?://[^\s\)"\'\]]+'
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        return urls

    def get_feature_names(self) -> List[str]:
        """Get list of all feature names"""
        # Create dummy data to get feature names
        dummy_data = {
            'sender': 'test@example.com',
            'sender_domain': 'example.com',
            'subject': 'Test',
            'to': 'user@example.com',
            'reply_to': '',
            'body': 'Test email body',
            'urls': [],
            'headers': {}
        }

        features = self.extract_all_features(dummy_data)
        return list(features.keys())

    def print_feature_summary(self, features: Dict) -> None:
        """Print feature summary (for debugging)"""
        print("\n" + "="*60)
        print("EXTRACTED FEATURES")
        print("="*60)

        categories = {
            'URL Features': ['url_count', 'suspicious_url_count', 'has_ip_urls'],
            'Text Features': ['phishing_keyword_count', 'urgency_keyword_count'],
            'Authentication': ['has_dkim', 'has_spf', 'has_dmarc'],
            'Domain Features': ['sender_domain_length', 'is_free_email_provider'],
        }

        for category, feature_keys in categories.items():
            print(f"\n{category}:")
            for key in feature_keys:
                if key in features:
                    print(f"  {key}: {features[key]}")

        print("\n" + "="*60 + "\n")


# Quick test
if __name__ == "__main__":
    # Test with sample email data
    sample_email = {
        'sender': 'support@amazon-verify.com',
        'sender_domain': 'amazon-verify.com',
        'subject': 'URGENT: Verify Your Amazon Account Now!',
        'to': 'user@gmail.com',
        'reply_to': '',
        'body': 'Click here to verify your account immediately. Unusual activity detected.',
        'urls': ['https://amazon-verify.com/login', 'http://192.168.1.1/phish'],
        'headers': {}
    }

    extractor = FeatureExtractor()
    features = extractor.extract_all_features(sample_email)
    extractor.print_feature_summary(features)

    print("\n✓ Feature extraction working!")
