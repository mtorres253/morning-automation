# Quick Start Guide

This guide will get your Lambda functions running in minutes.

## Prerequisites

1. **AWS Account** with console access
2. **AWS CLI** installed (`aws --version`)
3. **AWS Credentials configured** (`aws configure`)

## Step 1: Verify AWS Credentials

```bash
aws sts get-caller-identity
```

Should output your AWS Account ID and ARN. If not, run `aws configure` first.

## Step 2: Create S3 Bucket

```bash
aws s3api create-bucket \
  --bucket michael-journal-entries \
  --region us-west-2 \
  --create-bucket-configuration LocationConstraint=us-west-2
```

**Output:** Should say bucket was created.

## Step 3: Create IAM Role

```bash
# 1. Create trust policy
cat > /tmp/lambda-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

# 2. Create the role
aws iam create-role \
  --role-name lambda-morning-automation-role \
  --assume-role-policy-document file:///tmp/lambda-trust-policy.json
```

## Step 4: Attach IAM Policy

```bash
# 1. Create the policy
cat > /tmp/lambda-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:*"],
      "Resource": ["arn:aws:s3:::michael-journal-entries", "arn:aws:s3:::michael-journal-entries/*"]
    },
    {
      "Effect": "Allow",
      "Action": ["ses:SendEmail", "ses:SendRawEmail"],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
      "Resource": "arn:aws:logs:us-west-2:*:*"
    }
  ]
}
EOF

# 2. Attach policy to role
aws iam put-role-policy \
  --role-name lambda-morning-automation-role \
  --policy-name lambda-morning-automation-policy \
  --policy-document file:///tmp/lambda-policy.json
```

## Step 5: Verify SES Email

```bash
aws ses verify-email-identity \
  --email-address mtorres253@gmail.com \
  --region us-west-2
```

You may need to confirm the email in your inbox. Check for an AWS verification email.

## Step 6: Deploy Lambda Functions

```bash
cd /Users/michaeltorres/.openclaw/workspace/aws-lambda-setup
python3 deploy.py
```

This script will:
- Package all three Lambda functions
- Upload them to AWS
- Create EventBridge rules for daily 9 AM PT execution

**Expected output:**
```
✓ Deployed 3 Lambda function(s):
  - morning-journal-lambda
  - job-search-lambda
  - gmail-digest-lambda
```

## Step 7: Test the Functions

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

## Monitoring

Check CloudWatch logs for any errors:

```bash
# View logs for morning-journal-lambda
aws logs tail /aws/lambda/morning-journal-lambda --follow

# View logs for job-search-lambda
aws logs tail /aws/lambda/job-search-lambda --follow

# View logs for gmail-digest-lambda
aws logs tail /aws/lambda/gmail-digest-lambda --follow
```

## Troubleshooting

### SES Sandbox Mode

If emails aren't being sent, your SES account may be in sandbox mode.

1. Go to AWS Console → SES → Account dashboard
2. Request production access
3. AWS will review (usually instant)

### Lambda Timeout

If a function times out, increase its timeout:

```bash
aws lambda update-function-configuration \
  --function-name morning-journal-lambda \
  --timeout 3600 \
  --region us-west-2
```

### Check CloudWatch Events

View the EventBridge rules:

```bash
aws events list-rules --region us-west-2
aws events list-targets-by-rule --rule morning-automation-rule --region us-west-2
```

### Enable CloudTrail

For deeper troubleshooting, enable CloudTrail logging in your AWS account to see all API calls.

## What's Next

1. **Wait for 9 AM PT** - Functions will run automatically
2. **Check your email** - You should receive:
   - Journal prompt email
   - Job search results email
   - Gmail digest email
3. **Review S3 bucket** - Journal entries are stored in `michael-journal-entries`
4. **Monitor logs** - Check CloudWatch for any issues

## Manual Trigger

To trigger a function outside the scheduled time:

```bash
aws lambda invoke \
  --function-name morning-journal-lambda \
  --invocation-type RequestResponse \
  --region us-west-2 \
  --payload '{}' \
  /tmp/response.json
```

---

Questions? Check the full README.md for detailed setup instructions.
