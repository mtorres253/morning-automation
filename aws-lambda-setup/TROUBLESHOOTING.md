# Troubleshooting Guide

## Common Issues and Solutions

### 1. AWS Credentials Error

**Error:** `Unable to locate credentials`

**Solution:**
```bash
aws configure
# Enter:
# AWS Access Key ID: [your access key]
# AWS Secret Access Key: [your secret key]
# Default region: us-west-2
# Default output format: json
```

Then verify:
```bash
aws sts get-caller-identity
```

---

### 2. SES Email Not Sending

**Error:** Function runs but no email arrives

**Root cause:** SES Sandbox Mode or unverified email

**Solution:**

1. **Check SES status:**
   ```bash
   aws ses get-account-sending-enabled --region us-west-2
   ```

2. **Verify email address:**
   ```bash
   aws ses verify-email-identity \
     --email-address mtorres253@gmail.com \
     --region us-west-2
   ```

3. **Request production access:**
   - Go to AWS Console → SES → Account dashboard
   - Click "Request production access"
   - Answer the form (usually approved instantly)
   - Once approved, emails will send without verification limits

4. **Check verified addresses:**
   ```bash
   aws ses list-verified-email-addresses --region us-west-2
   ```

---

### 3. Gmail API Errors

**Error:** `AuthenticationError` or `Invalid refresh token`

**Root cause:** Gmail OAuth token expired or invalid

**Solution:**

1. **Check the token:**
   ```bash
   cat /Users/michaeltorres/.openclaw/workspace/secrets/gmail_oauth.json | jq .refresh_token
   ```

2. **Regenerate the token:**
   - Go to Google Cloud Console
   - OAuth 2.0 → Credentials
   - Delete the old OAuth consent screen approval
   - Or create a new OAuth app and update the token

3. **Verify the config is passed to Lambda:**
   ```bash
   aws lambda get-function-configuration \
     --function-name morning-journal-lambda \
     --query 'Environment.Variables.GMAIL_OAUTH_CONFIG' \
     --region us-west-2 | head -c 200
   ```

---

### 4. Lambda Timeout

**Error:** Function exceeds timeout (usually 60s default)

**Solution:**

1. **Increase timeout:**
   ```bash
   aws lambda update-function-configuration \
     --function-name morning-journal-lambda \
     --timeout 3600 \
     --region us-west-2
   ```

2. **Check what's slow:**
   ```bash
   aws logs tail /aws/lambda/morning-journal-lambda --follow
   ```

3. **Common causes:**
   - Gmail polling taking too long
   - Large email list
   - S3 network latency

---

### 5. S3 Permission Denied

**Error:** `AccessDenied` when writing to S3

**Solution:**

1. **Verify IAM policy:**
   ```bash
   aws iam get-role-policy \
     --role-name lambda-morning-automation-role \
     --policy-name lambda-morning-automation-policy
   ```

2. **Check bucket exists:**
   ```bash
   aws s3api list-buckets | grep michael-journal-entries
   ```

3. **Re-attach policy:**
   ```bash
   aws iam put-role-policy \
     --role-name lambda-morning-automation-role \
     --policy-name lambda-morning-automation-policy \
     --policy-document file:///tmp/lambda-policy.json
   ```

---

### 6. EventBridge Rule Not Triggering

**Error:** Function doesn't run at 9 AM PT

**Solution:**

1. **Check rule exists:**
   ```bash
   aws events describe-rule \
     --name morning-automation-rule \
     --region us-west-2
   ```

2. **Check targets:**
   ```bash
   aws events list-targets-by-rule \
     --rule morning-automation-rule \
     --region us-west-2
   ```

3. **Enable the rule:**
   ```bash
   aws events put-rule \
     --name morning-automation-rule \
     --state ENABLED \
     --schedule-expression 'cron(0 16 * * ? *)' \
     --region us-west-2
   ```

4. **Check Lambda permissions:**
   ```bash
   aws lambda list-policy-by-function \
     --function-name morning-journal-lambda \
     --region us-west-2
   ```

---

### 7. Job Search Lambda Can't Find Script

**Error:** `FileNotFoundError: /opt/job-search/run.py`

**Root cause:** Job search script not available in Lambda environment

**Solution:**

For now, the job search script needs to be bundled with the Lambda function. Options:

1. **Bundle the script:**
   - Copy `/Users/michaeltorres/.openclaw/workspace/skills/job-search/run.py` to `lambda_functions/job-search/`
   - Update deploy.py to include it
   - Redeploy

2. **Use environment variable:**
   ```bash
   aws lambda update-function-configuration \
     --function-name job-search-lambda \
     --environment 'Variables={SCRIPT_INLINE=true}' \
     --region us-west-2
   ```

3. **Or inline the logic** directly in the Lambda handler

---

### 8. CloudWatch Logs Full

**Error:** Lambda function creating too many logs

**Solution:**

1. **Check log retention:**
   ```bash
   aws logs describe-log-groups \
     --log-group-name-prefix /aws/lambda/ \
     --region us-west-2
   ```

2. **Set retention policy (7 days):**
   ```bash
   aws logs put-retention-policy \
     --log-group-name /aws/lambda/morning-journal-lambda \
     --retention-in-days 7 \
     --region us-west-2
   ```

---

### 9. Checking Function Logs

**View live logs:**
```bash
aws logs tail /aws/lambda/morning-journal-lambda --follow --region us-west-2
```

**Get last 100 lines:**
```bash
aws logs tail /aws/lambda/morning-journal-lambda --max-items 100 --region us-west-2
```

**Search for errors:**
```bash
aws logs filter-log-events \
  --log-group-name /aws/lambda/morning-journal-lambda \
  --filter-pattern "ERROR" \
  --region us-west-2
```

---

### 10. Redeeploy a Single Function

```bash
cd /Users/michaeltorres/.openclaw/workspace/aws-lambda-setup

# Edit the Lambda function code
nano lambda_functions/morning_journal_lambda.py

# Redeploy
python3 -c "
import deploy
func_config = [f for f in deploy.LAMBDA_FUNCTIONS if f['name'] == 'morning-journal-lambda'][0]
zip_path = deploy.package_lambda(func_config, 'lambda_functions')
role_arn = deploy.get_role_arn()
deploy.create_lambda_function(func_config, zip_path, role_arn)
"
```

---

## Debug Checklist

Before contacting support:

- [ ] AWS credentials configured (`aws sts get-caller-identity`)
- [ ] S3 bucket created (`aws s3 ls | grep michael-journal-entries`)
- [ ] IAM role exists (`aws iam get-role --role-name lambda-morning-automation-role`)
- [ ] SES email verified (`aws ses list-verified-email-addresses`)
- [ ] Lambda functions created (`aws lambda list-functions --region us-west-2`)
- [ ] EventBridge rule created (`aws events describe-rule --name morning-automation-rule`)
- [ ] CloudWatch logs checked (`aws logs tail /aws/lambda/morning-journal-lambda`)

---

## Getting Help

1. Check CloudWatch logs: `aws logs tail /aws/lambda/{function-name} --follow`
2. List all resources: `aws ec2 describe-instances`, `aws s3 ls`
3. Check IAM permissions: `aws iam get-user`
4. Review AWS documentation: https://docs.aws.amazon.com/lambda/

---

Last updated: 2026-03-28
