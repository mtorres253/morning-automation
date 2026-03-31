# AWS Lambda Setup for Morning Automation

This directory contains the code and infrastructure setup for three Lambda functions that run daily at 9 AM PT:

1. **morning-journal-lambda** - Sends journal prompt, polls for responses, stores to S3
2. **job-search-lambda** - Runs job search and sends results via email
3. **gmail-digest-lambda** - Fetches and summarizes emails from last 24h

## Prerequisites

Before deploying, ensure:

1. **AWS Credentials Configured**
   ```bash
   aws configure
   # Enter your AWS Access Key ID, Secret Access Key, region (us-west-2), output format (json)
   ```

2. **Gmail OAuth Credentials** - Already present at:
   `/Users/michaeltorres/.openclaw/workspace/secrets/gmail_oauth.json`

3. **Job Search Config** - Already present at:
   `/Users/michaeltorres/.openclaw/workspace/skills/job-search/job-search-config.json`

## Deployment Steps

### 1. Create S3 Bucket for Journal Entries

```bash
aws s3api create-bucket \
  --bucket michael-journal-entries \
  --region us-west-2 \
  --create-bucket-configuration LocationConstraint=us-west-2
```

### 2. Create IAM Role for Lambda

```bash
# Create the trust policy
cat > /tmp/lambda-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create the role
aws iam create-role \
  --role-name lambda-morning-automation-role \
  --assume-role-policy-document file:///tmp/lambda-trust-policy.json
```

### 3. Create and Attach IAM Policy

```bash
# Create the policy
cat > /tmp/lambda-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::michael-journal-entries",
        "arn:aws:s3:::michael-journal-entries/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:us-west-2:*:*"
    }
  ]
}
EOF

# Attach the policy
aws iam put-role-policy \
  --role-name lambda-morning-automation-role \
  --policy-name lambda-morning-automation-policy \
  --policy-document file:///tmp/lambda-policy.json
```

### 4. Verify SES Email Address

```bash
# Verify the sender email (may need approval from AWS)
aws ses verify-email-identity \
  --email-address mtorres253@gmail.com \
  --region us-west-2
```

### 5. Deploy Lambda Functions

For each Lambda function, you'll need to:

1. Package the code with dependencies
2. Create the Lambda function
3. Set environment variables

**Run the deployment script:**

```bash
cd /Users/michaeltorres/.openclaw/workspace/aws-lambda-setup
python3 deploy.py
```

This script will:
- Package each Lambda function with dependencies
- Create the functions in AWS
- Set up environment variables
- Create EventBridge rules for 9 AM PT daily execution

## Testing

### Test Morning Journal Lambda

```bash
aws lambda invoke \
  --function-name morning-journal-lambda \
  --region us-west-2 \
  /tmp/response.json

cat /tmp/response.json
```

### Test Job Search Lambda

```bash
aws lambda invoke \
  --function-name job-search-lambda \
  --region us-west-2 \
  /tmp/response.json

cat /tmp/response.json
```

### Test Gmail Digest Lambda

```bash
aws lambda invoke \
  --function-name gmail-digest-lambda \
  --region us-west-2 \
  /tmp/response.json

cat /tmp/response.json
```

## Next Steps

1. Configure AWS credentials: `aws configure`
2. Run the deployment script: `python3 deploy.py`
3. Check CloudWatch logs for any errors
4. Verify emails are being sent to mtorres253@gmail.com
5. Once verified, the functions will run automatically at 9 AM PT daily

## Troubleshooting

- **SES Sandbox Mode**: If emails aren't sending, the account may be in SES sandbox mode. Request production access in AWS console.
- **Gmail API Errors**: Check that the refresh token is valid and not expired.
- **S3 Permission Errors**: Verify the IAM role has correct bucket permissions.
- **CloudWatch Logs**: Check `/aws/lambda/{function-name}` for detailed error messages.

---

Created for Michael's morning automation workflow (2026-03-28)
