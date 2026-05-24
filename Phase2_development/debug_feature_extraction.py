"""
Debug Feature Extraction
Examines what features are being extracted from test emails
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from feature_extractor import FeatureExtractor

# Sample test email
test_email = {
    'subject': 'Project Status Update - Q2 Report',
    'body': '''Hi Team,

I wanted to provide an update on our Q2 project progress.

Key Achievements:
- Completed phase 1 deliverables on schedule
- Team productivity increased by 15%
- All stakeholder reviews completed successfully

Next Steps:
- Phase 2 kicks off next Monday
- Please review the attached timeline
- Schedule 1:1 meetings with your team lead

Let me know if you have any questions.

Best regards,
John Smith
Project Manager
john.smith@company.com''',
    'sender': 'john.smith@company.com'
}

print("="*70)
print("FEATURE EXTRACTION DEBUG")
print("="*70)

extractor = FeatureExtractor()

email_data = {
    'body': test_email['body'],
    'subject': test_email['subject'],
    'sender': test_email['sender'],
    'urls': [],
    'headers': {}
}

print(f"\nInput Email:")
print(f"  Subject: {email_data['subject']}")
print(f"  Body length: {len(email_data['body'])} chars")
print(f"  Sender: {email_data['sender']}")

print(f"\nExtracting features...")
features = extractor.extract_all_features(email_data)

print(f"\nExtracted Features ({len(features)} total):")
print("-"*70)
for name, value in features.items():
    print(f"  {name:<40} = {value}")

print("\n" + "="*70)
print("ANALYSIS")
print("="*70)

# Check for common issues
zero_count = sum(1 for v in features.values() if v == 0.0)
print(f"\nFeatures with value 0: {zero_count}/{len(features)}")

non_zero_features = {k: v for k, v in features.items() if v != 0.0}
print(f"\nNon-zero features ({len(non_zero_features)}):")
for name, value in non_zero_features.items():
    print(f"  {name}: {value}")

# Check specific feature categories
print(f"\nFeature Breakdown by Category:")
print("-"*70)

# URL features
url_features = {k: v for k, v in features.items() if 'url' in k.lower()}
print(f"URL Features ({len(url_features)}):")
for k, v in url_features.items():
    print(f"  {k}: {v}")

# Keyword features
keyword_features = {k: v for k, v in features.items() if 'keyword' in k.lower() or 'keyword' in k.lower()}
print(f"\nKeyword Features ({len(keyword_features)}):")
for k, v in keyword_features.items():
    print(f"  {k}: {v}")

# Text features
text_features = {k: v for k, v in features.items() if any(x in k.lower() for x in ['body', 'word', 'char', 'spelling', 'caps', 'exclamation'])}
print(f"\nText Features ({len(text_features)}):")
for k, v in text_features.items():
    print(f"  {k}: {v}")

# Auth features
auth_features = {k: v for k, v in features.items() if any(x in k.lower() for x in ['dkim', 'spf', 'dmarc', 'mailer', 'priority', 'reply', 'return', 'received'])}
print(f"\nAuthentication Features ({len(auth_features)}):")
for k, v in auth_features.items():
    print(f"  {k}: {v}")

# Domain features
domain_features = {k: v for k, v in features.items() if 'domain' in k.lower() or 'sender' in k.lower() or 'tld' in k.lower() or 'email' in k.lower() or 'mismatch' in k.lower() or 'age' in k.lower()}
print(f"\nDomain Features ({len(domain_features)}):")
for k, v in domain_features.items():
    print(f"  {k}: {v}")

print("\n" + "="*70)
