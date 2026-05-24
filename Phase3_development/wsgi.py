"""
Production WSGI entry point for the Phishing Email Detection Tool
Used by Gunicorn and other production WSGI servers
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app import app

if __name__ == "__main__":
    app.run()
