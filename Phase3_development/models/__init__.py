"""
Models package - Phishing Detection Models and Components
"""

try:
    from .detector import PhishingDetector
except ImportError:
    # Fallback if detector module can't be imported
    from detector import PhishingDetector

__all__ = ['PhishingDetector']
