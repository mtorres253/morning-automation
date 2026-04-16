"""
Job Search Lambda Function
Sends job search results via email.
"""

import json
import boto3
import os
from datetime import datetime

# Initialize AWS clients
ses_client = boto3.client('ses', region_name='us-east-2')

# Configuration
GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL', 'mtorres253@gmail.com')
SES_EMAIL = os.environ.get('SES_EMAIL', 'mtorres253@gmail.com')

def get_job_search_results():
    """Return sample job search results."""
    # TODO: Integrate with actual job search script/API
    results = [
        {
            "title": "Director of Product",
            "company": "Skydio",
            "location": "San Francisco, CA (Hybrid)",
            "salary": "$230K - $250K",
            "url": "https://www.skydio.com/careers"
        },
        {
            "title": "Principal Product Manager",
            "company": "Code for America",
            "location": "Remote",
            "salary": "$220K - $245K",
            "url": "https://www.codeforamerica.org/careers"
        },
        {
            "title": "Chief of Staff, Product",
            "company": "Lime (Mobility)",
            "location": "San Francisco, CA",
            "salary": "$210K - $240K",
            "url": "https://www.li.me/careers"
        }
    ]
    return results

def format_job_results_email(job_results):
    """Format job search results for email."""
    date_str = datetime.now().strftime('%Y-%m-%d')
    subject = f"Daily Job Search Results - {date_str}"
    
    body = "🎯 Job Search Results\n"
    body += "=" * 50 + "\n\n"
    
    for i, job in enumerate(job_results, 1):
        body += f"{i}. {job['title']}\n"
        body += f"   Company: {job['company']}\n"
        body += f"   Location: {job['location']}\n"
        body += f"   Salary: {job['salary']}\n"
        body += f"   Apply: {job['url']}\n\n"
    
    body += "---\n"
    body += f"Sent by Job Search Lambda at {datetime.now().isoformat()}\n"
    
    return subject, body

def send_results_email(subject, body):
    """Send job search results via SES."""
    try:
        ses_client.send_email(
            Source=SES_EMAIL,
            Destination={'ToAddresses': [GMAIL_EMAIL]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )
        print(f"Results email sent to {GMAIL_EMAIL}")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def lambda_handler(event, context):
    """Main Lambda handler."""
    try:
        print("Starting Job Search Lambda")
        
        # Get job search results
        job_results = get_job_search_results()
        
        # Format and send email
        subject, body = format_job_results_email(job_results)
        
        email_sent = send_results_email(subject, body)
        
        if not email_sent:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to send results email'})
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Job search lambda completed',
                'jobs_found': len(job_results),
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
