"""
Morning Journal Lambda Function
Sends a journal prompt email.
"""

import json
import boto3
import os
from datetime import datetime

# Initialize AWS clients
ses_client = boto3.client('ses', region_name='us-west-2')
s3_client = boto3.client('s3', region_name='us-west-2')

# Configuration
GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL', 'mtorres253@gmail.com')
SES_EMAIL = os.environ.get('SES_EMAIL', 'mtorres253@gmail.com')
S3_BUCKET = os.environ.get('S3_BUCKET', 'michael-journal-entries')

def send_journal_prompt_email():
    """Send journal prompt email via SES."""
    subject = f"Your Daily Journal Prompt - {datetime.now().strftime('%Y-%m-%d')}"
    body = """Hi Michael,

Three things to anchor your day:

1. What are you grateful for today? (Even small things count.)
2. What are your main tasks? (What does "done" look like?)
3. Which strengths will you need? (What are you bringing to the table?)

Reply to this email with your journal entry. Your response will be automatically saved.

---
Sent by Morning Journal Lambda
"""
    
    try:
        ses_client.send_email(
            Source=SES_EMAIL,
            Destination={'ToAddresses': [GMAIL_EMAIL]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )
        print(f"Journal prompt email sent to {GMAIL_EMAIL}")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def lambda_handler(event, context):
    """Main Lambda handler."""
    try:
        print("Starting Morning Journal Lambda")
        
        # Send journal prompt
        email_sent = send_journal_prompt_email()
        
        if not email_sent:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to send journal prompt email'})
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Morning journal prompt sent',
                'email_sent': True,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
