"""
Email Parser Module
Parses .eml and .msg format emails and extracts components
"""

import email
from email import policy
import os
import json
from typing import Dict, List, Optional
import re

class EmailParser:
    """Parse email files and extract components"""

    def __init__(self):
        self.email_data = None

    def parse_file(self, file_path: str) -> Dict:
        """
        Parse email file (.eml or .msg format)

        Args:
            file_path: Path to email file

        Returns:
            Dictionary with email components
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Email file not found: {file_path}")

        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.eml':
            return self._parse_eml(file_path)
        elif file_ext == '.msg':
            return self._parse_msg(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}. Use .eml or .msg")

    def _parse_eml(self, file_path: str) -> Dict:
        """Parse .eml format email file"""
        try:
            with open(file_path, 'rb') as f:
                msg = email.message_from_binary_file(f, policy=policy.default)

            return self._extract_components(msg)

        except Exception as e:
            raise ValueError(f"Error parsing .eml file: {str(e)}")

    def _parse_msg(self, file_path: str) -> Dict:
        """
        Parse .msg format email file
        Falls back to basic parsing if extract_msg not available
        """
        try:
            # Try using extract_msg library if available
            import extract_msg
            msg_file = extract_msg.Message(file_path)

            email_data = {
                'sender': msg_file.sender or 'Unknown',
                'subject': msg_file.subject or 'No Subject',
                'to': msg_file.to or 'Unknown',
                'cc': msg_file.cc or '',
                'bcc': msg_file.bcc or '',
                'date': msg_file.date or 'Unknown',
                'body': msg_file.body or '',
                'headers': dict(msg_file.headerDict) if hasattr(msg_file, 'headerDict') else {},
                'file_path': file_path,
                'file_format': 'msg'
            }

            return email_data

        except ImportError:
            raise ImportError("extract_msg library not available. Install: pip install extract-msg")
        except Exception as e:
            raise ValueError(f"Error parsing .msg file: {str(e)}")

    def _extract_components(self, msg) -> Dict:
        """Extract components from email message object"""

        # Extract headers
        headers = {}
        for key, value in msg.items():
            headers[key.lower()] = str(value)

        # Extract basic info
        sender = self._clean_email(msg.get('from', 'Unknown'))
        subject = msg.get('subject', 'No Subject') or 'No Subject'
        body = self._get_body(msg)

        email_data = {
            'sender': sender,
            'sender_domain': self._extract_domain(sender),
            'subject': subject,
            'to': self._clean_email(msg.get('to', 'Unknown')),
            'cc': self._clean_email(msg.get('cc', '')),
            'bcc': self._clean_email(msg.get('bcc', '')),
            'reply_to': self._clean_email(msg.get('reply-to', '')),
            'date': msg.get('date', 'Unknown'),
            'body': body,
            'headers': headers,
            'urls': self._extract_urls(body),
            'file_path': 'unknown',
            'file_format': 'eml'
        }

        return email_data

    def _get_body(self, msg) -> str:
        """Extract email body text"""
        body = ""

        if msg.is_multipart():
            for part in msg.iter_parts():
                if part.get_content_type() == 'text/plain':
                    try:
                        body += part.get_content()
                    except:
                        pass
        else:
            try:
                body = msg.get_content()
            except:
                body = str(msg.get_payload())

        return body if body else ""

    def _clean_email(self, email_str: str) -> str:
        """Clean email string and extract address"""
        if not email_str:
            return ""

        # Remove angle brackets and extra spaces
        email_str = email_str.strip()
        if '<' in email_str and '>' in email_str:
            email_str = email_str[email_str.find('<')+1:email_str.find('>')]

        return email_str.lower()

    def _extract_domain(self, email_address: str) -> str:
        """Extract domain from email address"""
        if not email_address or '@' not in email_address:
            return ""

        return email_address.split('@')[1].lower()

    def _extract_urls(self, text: str) -> List[str]:
        """Extract all URLs from text"""
        if not text:
            return []

        # Regex pattern for URLs
        url_pattern = r'https?://[^\s<>"\)\]]*|www\.[^\s<>"\)\]]*'
        urls = re.findall(url_pattern, text, re.IGNORECASE)

        return list(set(urls))  # Remove duplicates

    def print_summary(self, email_data: Dict) -> None:
        """Print email summary (for debugging)"""
        print("\n" + "="*60)
        print("EMAIL SUMMARY")
        print("="*60)
        print(f"From: {email_data['sender']}")
        print(f"To: {email_data['to']}")
        print(f"Subject: {email_data['subject']}")
        print(f"Domain: {email_data['sender_domain']}")
        print(f"Body Length: {len(email_data['body'])} characters")
        print(f"URLs Found: {len(email_data['urls'])}")
        if email_data['urls']:
            for url in email_data['urls'][:3]:
                print(f"  - {url}")
        print("="*60 + "\n")


# Quick test
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        parser = EmailParser()
        try:
            data = parser.parse_file(sys.argv[1])
            parser.print_summary(data)
            print("\n✓ Email parsed successfully!")
        except Exception as e:
            print(f"✗ Error: {e}")
    else:
        print("Usage: python email_parser.py <email_file.eml>")
