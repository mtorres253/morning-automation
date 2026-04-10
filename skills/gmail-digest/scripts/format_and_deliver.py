#!/usr/bin/env python3
"""
Format Gmail digest and deliver via email.
Reads raw email JSON from fetch_digest.py, formats, and sends digest email.
"""

import json
import os
import sys
import smtplib
import subprocess
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any

# Use /tmp for Lambda compatibility
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    TEMP_DIR = Path("/tmp")
else:
    TEMP_DIR = Path("/tmp")

def load_config() -> Dict[str, Any]:
    """Load gmail-digest config if it exists."""
    config_path = Path.home() / ".openclaw" / "workspace" / "skills" / "gmail-digest" / "gmail-digest-config.json"
    default_config = {
        "emailTo": "mtorres253@gmail.com",
        "categories": {
            "Work & Team": ["github", "gsatts", "identity-dev", "pull request", "merge", "issue"],
            "Events & Meetings": ["meeting", "invite", "invitation", "calendar", "event"],
            "Job Alerts": ["job search", "digest", "matching jobs"],
            "Personal": ["david", "russell"],
            "Other": []
        }
    }
    
    if config_path.exists():
        with open(config_path, "r") as f:
            return json.load(f)
    
    return default_config

def categorize_email(email: Dict[str, Any], categories: Dict[str, List[str]]) -> str:
    """Categorize an email based on subject/from keywords."""
    subject = email.get("subject", "").lower()
    from_addr = email.get("from", "").lower()
    snippet = email.get("snippet", "").lower()
    
    # Check each category
    for category, keywords in categories.items():
        if category == "Other":
            continue
        for keyword in keywords:
            if keyword.lower() in subject or keyword.lower() in from_addr:
                return category
    
    return "Other"

def group_emails_by_category(emails: List[Dict[str, Any]], categories: Dict[str, List[str]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group emails by category."""
    groups = {cat: [] for cat in categories.keys()}
    
    for email in emails:
        category = categorize_email(email, categories)
        groups[category].append(email)
    
    # Remove empty categories
    return {k: v for k, v in groups.items() if v}

def format_email_body(emails: List[Dict[str, Any]], config: Dict[str, Any]) -> str:
    """Format emails into an HTML email body."""
    
    if not emails:
        emails_html = """
        <div class="no-emails-message">
            <p style="font-size: 16px; color: #666; text-align: center; padding: 30px;">
                ✨ No emails in the last 24 hours.
            </p>
        </div>
        """
    else:
        grouped = group_emails_by_category(emails, config.get("categories", {}))
        emails_html = ""
        
        for category, category_emails in grouped.items():
            emails_html += f"""
            <div class="category">
                <div class="category-title">{category} ({len(category_emails)})</div>
            """
            
            for email in category_emails[:10]:  # Limit to 10 per category
                from_name = email.get("from", "Unknown").split("<")[0].strip()
                date_str = email.get("date", "").split(",")[-1].strip() if "," in email.get("date", "") else email.get("date", "")
                
                emails_html += f"""
                <div class="email">
                    <div class="email-from">{from_name}</div>
                    <div class="email-subject">{email.get('subject', '(no subject)')}</div>
                    <div class="email-date">{date_str}</div>
                    <div class="email-snippet">{email.get('snippet', 'No preview available')[:120]}...</div>
                </div>
                """
            
            emails_html += "</div>"
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background-color: #f0f0f0; padding: 20px; margin-bottom: 20px; }}
            .header h1 {{ margin: 0; color: #2c5aa0; }}
            .header p {{ margin: 5px 0; color: #666; }}
            .no-emails-message {{ background-color: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0; border-radius: 4px; }}
            .category {{ margin-bottom: 30px; }}
            .category-title {{ font-size: 18px; font-weight: bold; color: #2c5aa0; margin-bottom: 10px; border-bottom: 2px solid #2c5aa0; padding-bottom: 5px; }}
            .email {{ background-color: #f9f9f9; border-left: 4px solid #2c5aa0; padding: 15px; margin-bottom: 12px; }}
            .email-from {{ font-size: 13px; color: #999; margin-bottom: 3px; }}
            .email-subject {{ font-size: 14px; font-weight: bold; color: #000; margin-bottom: 5px; }}
            .email-date {{ font-size: 12px; color: #aaa; margin-bottom: 8px; }}
            .email-snippet {{ color: #666; font-size: 13px; font-style: italic; }}
            .footer {{ margin-top: 40px; font-size: 12px; color: #999; border-top: 1px solid #ddd; padding-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📬 Email Digest</h1>
            <p>Last 24 hours • {len(emails)} messages</p>
            <p>Generated: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p %Z')}</p>
        </div>
        {emails_html}
        <div class="footer">
            <p>This is an automated email digest. Emails are grouped by category for easier scanning.</p>
        </div>
    </body>
    </html>
    """
    
    return html

def fetch_emails() -> List[Dict[str, Any]]:
    """Call fetch_digest.py and return parsed JSON."""
    script_path = Path(__file__).parent / "fetch_digest.py"
    
    try:
        result = subprocess.run(
            ["python3", str(script_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"✗ fetch_digest.py failed: {result.stderr}", file=sys.stderr)
            return []
        
        emails = json.loads(result.stdout)
        print(f"✓ Fetched {len(emails)} emails")
        return emails
    
    except subprocess.TimeoutExpired:
        print("✗ fetch_digest.py timed out", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON from fetch_digest.py: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"✗ Error fetching emails: {e}", file=sys.stderr)
        return []

def send_email(subject: str, html_body: str, to_email: str) -> bool:
    """Send email via SMTP."""
    try:
        # Try environment variables (for Lambda)
        smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        sender_email = os.environ.get("SENDER_EMAIL")
        sender_password = os.environ.get("SENDER_PASSWORD")
        
        # Fall back to config file if env vars not set
        if not sender_email or not sender_password:
            # Try workspace secrets first, then fallback to home secrets
            secrets_path = Path.home() / ".openclaw" / "workspace" / "secrets" / "email_config.json"
            if not secrets_path.exists():
                secrets_path = Path.home() / ".openclaw" / "secrets" / "email_config.json"
            
            if secrets_path.exists():
                with open(secrets_path, "r") as f:
                    email_config = json.load(f)
                smtp_server = email_config.get("smtp_server", smtp_server)
                smtp_port = email_config.get("smtp_port", smtp_port)
                sender_email = email_config.get("sender_email", sender_email)
                sender_password = email_config.get("sender_password", sender_password)
        
        if not sender_email or not sender_password:
            print("⚠️  Email credentials not configured. Skipping email delivery.")
            return False
        
        # Create email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email
        
        part = MIMEText(html_body, "html")
        msg.attach(part)
        
        # Send
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        
        print(f"✓ Email sent to {to_email}")
        return True
    
    except Exception as e:
        print(f"✗ Email delivery failed: {e}")
        return False

def main():
    try:
        config = load_config()
        
        # Fetch emails
        emails = fetch_emails()
        
        if not emails:
            print("ℹ️  No emails found. Not sending digest.")
            return
        
        # Format digest
        html_body = format_email_body(emails, config)
        subject = f"📬 Email Digest — {datetime.now().strftime('%A, %B %d')}"
        
        # Send
        to_email = config.get("emailTo", "mtorres253@gmail.com")
        
        if send_email(subject, html_body, to_email):
            print(f"✓ Digest delivered ({len(emails)} emails)")
        else:
            print(f"✗ Failed to deliver digest")
    
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
