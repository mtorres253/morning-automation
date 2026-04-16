"""
Gmail Digest Lambda Function
Fetches emails from last 24 hours, categorizes them, and sends a formatted digest.
"""

import json
import boto3
import os
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone

# Initialize AWS clients
ses_client = boto3.client('ses', region_name='us-east-2')

# Configuration
GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL', 'mtorres253@gmail.com')
SES_EMAIL = os.environ.get('SES_EMAIL', 'mtorres253@gmail.com')

# Gmail OAuth from environment
GMAIL_OAUTH_CONFIG = os.environ.get('GMAIL_OAUTH_CONFIG', '{}')

def get_access_token(creds):
    """Get fresh Gmail access token from refresh token."""
    data = urllib.parse.urlencode({
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
        "refresh_token": creds["refresh_token"],
        "grant_type": "refresh_token"
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["access_token"]

def gmail_get(path, token):
    """Make authenticated request to Gmail API."""
    url = f"https://gmail.googleapis.com/gmail/v1/{path}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def header_val(headers, name):
    """Extract header value by name."""
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""

def categorize_email(subject, sender):
    """Categorize email based on subject and sender."""
    subject_lower = subject.lower()
    sender_lower = sender.lower()
    
    if any(x in subject_lower for x in ['job', 'hiring', 'position', 'career', 'apply']):
        return 'Job Alerts'
    elif any(x in sender_lower for x in ['linkedin', 'indeed', 'glassdoor', 'ladders']):
        return 'Job Alerts'
    elif any(x in subject_lower for x in ['meeting', 'calendar', 'event', 'scheduled']):
        return 'Calendar'
    elif any(x in sender_lower for x in ['github', 'gitlab']):
        return 'GitHub'
    elif any(x in subject_lower for x in ['notification', 'alert', 'update']):
        return 'Notifications'
    elif any(x in sender_lower for x in ['newsletter', 'digest', 'substack', 'brew']):
        return 'Newsletters'
    elif any(x in subject_lower for x in ['receipt', 'order', 'confirmation', 'payment']):
        return 'Transactional'
    elif sender_lower.endswith('@gmail.com') or sender_lower.endswith('@hotmail.com'):
        return 'Personal'
    else:
        return 'Work'

def fetch_emails_last_24h(token):
    """Fetch emails from last 24 hours."""
    since = int((datetime.now(timezone.utc) - timedelta(hours=24)).timestamp())
    query = f"after:{since}"
    encoded_query = urllib.parse.urlencode({"q": query, "maxResults": 50})
    
    result = gmail_get(f"users/me/messages?{encoded_query}", token)
    messages = result.get("messages", [])
    
    emails = []
    for msg in messages:
        detail = gmail_get(
            f"users/me/messages/{msg['id']}?format=metadata&metadataHeaders=Subject&metadataHeaders=From&metadataHeaders=Date",
            token
        )
        headers = detail.get("payload", {}).get("headers", [])
        subject = header_val(headers, "Subject") or "(no subject)"
        sender = header_val(headers, "From")
        
        emails.append({
            "subject": subject,
            "from": sender,
            "date": header_val(headers, "Date"),
            "snippet": detail.get("snippet", ""),
            "category": categorize_email(subject, sender)
        })
    
    return emails

def format_digest(emails):
    """Format emails into a readable digest by category."""
    if not emails:
        return "No emails in the last 24 hours."
    
    # Group by category
    by_category = {}
    for email in emails:
        cat = email['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(email)
    
    # Build digest
    digest = "📧 Email Digest — Last 24 Hours\n"
    digest += "=" * 50 + "\n\n"
    
    # Summary
    digest += "📌 Highlights:\n"
    for category, items in sorted(by_category.items()):
        digest += f"- {category}: {len(items)} email{'s' if len(items) != 1 else ''}\n"
    digest += "\n"
    
    # Details by category
    category_order = ['Job Alerts', 'Calendar', 'Work', 'GitHub', 'Personal', 'Newsletters', 'Notifications', 'Transactional']
    for category in category_order:
        if category not in by_category:
            continue
        
        digest += f"**{category}** ({len(by_category[category])})\n"
        for email in by_category[category][:5]:  # Show top 5 per category
            digest += f"- {email['subject'][:60]}\n"
            if email['snippet']:
                digest += f"  {email['snippet'][:80]}...\n"
        
        if len(by_category[category]) > 5:
            digest += f"  ... and {len(by_category[category]) - 5} more\n"
        digest += "\n"
    
    return digest

def markdown_to_html(text):
    """Convert simple markdown to HTML."""
    html = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    html = html.replace('**', '<strong>').replace('**', '</strong>')
    # Fix the pattern properly
    import re
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    html = html.replace('\n', '<br>')
    return html

def send_digest_email(digest_content):
    """Send digest via SES as HTML."""
    subject = f"Email Digest — {datetime.now().strftime('%A, %B %d')}"
    
    # Convert to HTML
    html_body = markdown_to_html(digest_content)
    html_body += f"<br>---<br>Sent by Gmail Digest Lambda at {datetime.now().isoformat()}"
    
    # Wrap in basic HTML structure
    html_full = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto;">
    {html_body}
    </div>
    </body>
    </html>
    """
    
    try:
        ses_client.send_email(
            Source=SES_EMAIL,
            Destination={'ToAddresses': [GMAIL_EMAIL]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Html': {'Data': html_full}}
            }
        )
        print(f"Digest email sent to {GMAIL_EMAIL}")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def lambda_handler(event, context):
    """Main Lambda handler."""
    try:
        print("Starting Gmail Digest Lambda")
        
        # Parse OAuth config from environment
        oauth_config = json.loads(GMAIL_OAUTH_CONFIG)
        if not oauth_config:
            raise ValueError("Gmail OAuth config not found in environment")
        
        # Get access token
        access_token = get_access_token(oauth_config)
        print("✓ Gmail authenticated")
        
        # Fetch emails
        emails = fetch_emails_last_24h(access_token)
        print(f"✓ Fetched {len(emails)} emails")
        
        # Format digest
        digest = format_digest(emails)
        
        # Send email
        email_sent = send_digest_email(digest)
        
        if not email_sent:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to send digest email'})
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Email digest sent',
                'emails_processed': len(emails),
                'email_sent': True,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
