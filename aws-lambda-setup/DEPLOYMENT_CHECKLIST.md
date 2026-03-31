# Deployment Checklist

Complete these steps in order. Check off each one as you go.

---

## Pre-Deployment (5 min)

- [ ] Open terminal: `cd /Users/michaeltorres/.openclaw/workspace/aws-lambda-setup`
- [ ] Verify AWS CLI installed: `aws --version`
- [ ] Verify AWS credentials: `aws sts get-caller-identity`
  - Should show your Account ID and ARN
  - If error, run `aws configure` first

---

## Step 1: Create S3 Bucket (1 min)

```bash
aws s3api create-bucket \
  --bucket michael-journal-entries \
  --region us-west-2 \
  --create-bucket-configuration LocationConstraint=us-west-2
```

- [ ] Command ran successfully
- [ ] Verify: `aws s3 ls | grep michael-journal-entries`

---

## Step 2: Create IAM Role (2 min)

Copy and paste this entire block:

```bash
# Create trust policy
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

# Create role
aws iam create-role \
  --role-name lambda-morning-automation-role \
  --assume-role-policy-document file:///tmp/lambda-trust-policy.json
```

- [ ] Role creation command ran
- [ ] Got role ARN in output

---

## Step 3: Attach IAM Policy (2 min)

Copy and paste this entire block:

```bash
# Create policy
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

# Attach policy
aws iam put-role-policy \
  --role-name lambda-morning-automation-role \
  --policy-name lambda-morning-automation-policy \
  --policy-document file:///tmp/lambda-policy.json
```

- [ ] Policy attachment command ran
- [ ] Verify: `aws iam get-role --role-name lambda-morning-automation-role`

---

## Step 4: Verify SES Email (1 min)

```bash
aws ses verify-email-identity \
  --email-address mtorres253@gmail.com \
  --region us-west-2
```

- [ ] Command ran successfully
- [ ] Check inbox for AWS verification email (if needed)
- [ ] Verify: `aws ses list-verified-email-addresses --region us-west-2`

---

## Step 5: Deploy Lambda Functions (5-10 min)

```bash
cd /Users/michaeltorres/.openclaw/workspace/aws-lambda-setup
python3 deploy.py
```

This script will:
- Package all three Lambda functions
- Upload to AWS
- Create EventBridge rules

- [ ] Script ran successfully
- [ ] All 3 functions deployed (see output)
- [ ] No errors in output

**Expected output:**
```
✓ Deployed 3 Lambda function(s):
  - morning-journal-lambda
  - job-search-lambda
  - gmail-digest-lambda
```

---

## Step 6: Verify Functions Created (2 min)

```bash
aws lambda list-functions \
  --region us-west-2 \
  --query 'Functions[?starts_with(FunctionName, `morning`) || starts_with(FunctionName, `job`) || starts_with(FunctionName, `gmail`)].{Name:FunctionName, Runtime:Runtime, Status:State}'
```

- [ ] All 3 functions listed
- [ ] Status is "Active" for all

---

## Step 7: Verify EventBridge Rules (1 min)

```bash
aws events describe-rule \
  --name morning-automation-rule \
  --region us-west-2
```

- [ ] Rule exists
- [ ] State is "ENABLED"
- [ ] ScheduleExpression shows `cron(0 16 * * ? *)`

---

## Step 8: Test Each Function (5 min)

### Test 1: Morning Journal Lambda

```bash
aws lambda invoke \
  --function-name morning-journal-lambda \
  --region us-west-2 \
  /tmp/test1.json

cat /tmp/test1.json
```

- [ ] Returns StatusCode 200
- [ ] No errors in output

### Test 2: Job Search Lambda

```bash
aws lambda invoke \
  --function-name job-search-lambda \
  --region us-west-2 \
  /tmp/test2.json

cat /tmp/test2.json
```

- [ ] Returns StatusCode 200
- [ ] No errors in output

### Test 3: Gmail Digest Lambda

```bash
aws lambda invoke \
  --function-name gmail-digest-lambda \
  --region us-west-2 \
  /tmp/test3.json

cat /tmp/test3.json
```

- [ ] Returns StatusCode 200
- [ ] No errors in output

---

## Step 9: Check CloudWatch Logs (5 min)

```bash
# View morning journal logs
aws logs tail /aws/lambda/morning-journal-lambda --region us-west-2

# View job search logs
aws logs tail /aws/lambda/job-search-lambda --region us-west-2

# View gmail digest logs
aws logs tail /aws/lambda/gmail-digest-lambda --region us-west-2
```

- [ ] No error messages in any log
- [ ] Check for "success" or completion messages
- [ ] If errors, see TROUBLESHOOTING.md

---

## Step 10: Verify Email was Sent (5 min)

- [ ] Check inbox for test emails
  - Look for "Your Daily Journal Prompt"
  - Look for "Daily Job Search Results"
  - Look for "Email Digest"

**Note:** If emails don't arrive:
1. Check spam folder
2. Check CloudWatch logs for errors
3. See TROUBLESHOOTING.md section 2 (SES)

---

## Step 11: Verify S3 Storage (2 min)

```bash
# List bucket contents
aws s3 ls s3://michael-journal-entries --recursive

# View a journal entry (if one exists)
aws s3 cp s3://michael-journal-entries/journals/2026-03-28.json - | jq .
```

- [ ] Bucket is accessible
- [ ] Files are being stored (once you reply to journal email)

---

## Post-Deployment Setup (Optional, but Recommended)

### Set Log Retention (Keep logs for 7 days)

```bash
for log_group in \
  "/aws/lambda/morning-journal-lambda" \
  "/aws/lambda/job-search-lambda" \
  "/aws/lambda/gmail-digest-lambda"
do
  aws logs put-retention-policy \
    --log-group-name "$log_group" \
    --retention-in-days 7 \
    --region us-west-2
done
```

- [ ] Retention policy set

---

## Final Checklist

- [ ] S3 bucket created
- [ ] IAM role created
- [ ] IAM policy attached
- [ ] SES email verified
- [ ] Lambda functions deployed
- [ ] EventBridge rules created
- [ ] All tests passed
- [ ] CloudWatch logs look good
- [ ] No error messages

---

## What Happens Next

✅ **Functions are scheduled to run at 9 AM PT daily**

- Morning Journal: Sends prompt, polls for 1 hour
- Job Search: Runs search, sends results
- Gmail Digest: Summarizes last 24h of emails

You can:
- Wait for 9 AM PT for automatic execution
- Manually trigger anytime: `aws lambda invoke --function-name morning-journal-lambda --region us-west-2 /tmp/response.json`
- Monitor logs: `aws logs tail /aws/lambda/morning-journal-lambda --follow`

---

## Troubleshooting

**Problem:** Function failed  
**Solution:** Check `TROUBLESHOOTING.md`

**Problem:** Email didn't arrive  
**Solution:** See TROUBLESHOOTING.md Section 2 (SES)

**Problem:** Gmail error  
**Solution:** See TROUBLESHOOTING.md Section 3 (Gmail)

---

## Success Criteria

You're done when:

✅ All 3 Lambda functions exist in AWS  
✅ EventBridge rule is created and enabled  
✅ All tests return StatusCode 200  
✅ Test emails arrive in your inbox  
✅ CloudWatch logs show no errors  

---

**Estimated Total Time:** 30-45 minutes  
**Last Updated:** 2026-03-28

Once you complete this checklist, you're all set! The Lambda functions will run automatically every day at 9 AM PT.
