# Lambda Debug Checklist

**Prerequisite:** You must have IAM permissions first. See `FIX_IAM_PERMISSIONS.md`.

Once you have read access to Lambda/EventBridge/CloudWatch, follow this checklist to debug the three issues:

---

## Issue 1: Duplicate Job Search Emails

**Symptom:** Job search digest arrives at 9 AM AND 10 AM

### Check EventBridge Rules

```bash
# List all EventBridge rules in us-west-2
aws events list-rules --region us-west-2 --output table
```

**Look for:**
- How many rules contain `job-search`?
- Are there duplicates? (e.g., `job-search-lambda-rule` appears twice)
- What time is each scheduled for?

**Expected output:**
```
Name                          Description              State     ScheduleExpression
-----------------------------  -----------------------  --------  ----------------------
morning-journal-lambda-rule    (blank)                  ENABLED   cron(0 16 * * ? *)
job-search-lambda-rule         (blank)                  ENABLED   cron(0 16 * * ? *)
gmail-digest-lambda-rule       (blank)                  ENABLED   cron(0 16 * * ? *)
```

**If you see duplicates (e.g., two `job-search-lambda-rule`):**

The admin needs to delete the duplicate:
```bash
aws events delete-rule --name job-search-lambda-rule-2 --force --region us-west-2
```

### Check EventBridge Targets

```bash
# List targets for job-search rule
aws events list-targets-by-rule --rule job-search-lambda-rule --region us-west-2 --output table
```

**Expected:** One target pointing to the job-search-lambda function.

**If you see 2+ targets:** The admin needs to remove the duplicate.

### Check for OpenClaw Cron Jobs

```bash
# List all OpenClaw cron jobs
cron list
```

**Look for:** Any job named `*job-search*` or running at 10 AM

**If found:** That's the 10 AM source! Either:
1. Delete it: `cron remove {jobId}`
2. Or disable it: `cron update {jobId} --payload '{"enabled": false}'`

### Check Lambda Logs for Retries

```bash
# View last 7 days of job-search Lambda logs
aws logs tail /aws/lambda/job-search-lambda --region us-west-2 --since 7d

# Look for errors or multiple invocations at 9 AM
```

**If you see multiple invocations within seconds of each other** (around 9 AM), the Lambda might be retrying.

---

## Issue 2: Gmail Digest Silent Failure

**Symptom:** No "Daily Gmail Digest" emails arriving (expected at 9 AM)

### Check if Lambda is Configured Correctly

```bash
# Get gmail-digest-lambda configuration
aws lambda get-function-configuration --function-name gmail-digest-lambda --region us-west-2 --output json | jq '.Environment.Variables'
```

**Look for:**
- `GMAIL_OAUTH_CONFIG` — should be a JSON string with OAuth credentials
- `GMAIL_EMAIL` — should be `mtorres253@gmail.com`
- `SES_EMAIL` — should be `mtorres253@gmail.com`

**If `GMAIL_OAUTH_CONFIG` is empty or missing:**
The Lambda was deployed without credentials! The admin needs to:
1. Update the environment variable with the OAuth config
2. Redeploy

### Check Gmail Digest Lambda Logs

```bash
# View last 7 days of gmail-digest-lambda logs
aws logs tail /aws/lambda/gmail-digest-lambda --region us-west-2 --since 7d

# Or view last 24 hours specifically
aws logs tail /aws/lambda/gmail-digest-lambda --region us-west-2 --since 1d
```

**Look for errors like:**
- `AuthenticationError` — OAuth token expired (need to refresh)
- `AccessDeniedException` — SES not verified or in sandbox
- `Connection timeout` — Network issue
- `No module named...` — Missing Python dependency

**Common error patterns:**

```
ERROR: AuthenticationError: Invalid refresh token
→ Solution: Regenerate OAuth credentials and redeploy

ERROR: MessageRejected: Email address not verified in SES
→ Solution: Verify mtorres253@gmail.com in SES console, or request production access

ERROR: timeout while waiting for response
→ Solution: Increase Lambda timeout (currently 60s, try 120s)

ERROR: No such file or directory: gmail_oauth.json
→ Solution: Re-deploy with correct environment variables
```

### Check SES Status

```bash
# Check if SES is in sandbox or production
aws ses get-account-sending-enabled --region us-west-2

# List verified email addresses
aws ses list-identities --region us-west-2 --identity-type EmailAddress

# Check verification status for your email
aws ses get-identity-verification-attributes --identities mtorres253@gmail.com --region us-west-2
```

**Expected:**
```json
{
  "VerificationAttributes": {
    "mtorres253@gmail.com": {
      "VerificationStatus": "Success"
    }
  }
}
```

**If status is `Pending` or email not listed:**
The admin needs to verify the email in SES console.

---

## Issue 3: General Lambda Health Check

### Check All Lambda Functions

```bash
# List all Lambda functions
aws lambda list-functions --region us-west-2 --output table

# Get details on each
aws lambda get-function-configuration --function-name morning-journal-lambda --region us-west-2
aws lambda get-function-configuration --function-name job-search-lambda --region us-west-2
aws lambda get-function-configuration --function-name gmail-digest-lambda --region us-west-2
```

**Check for:**
- LastModified date (should be recent if you just deployed)
- Timeout (should be 3600s for journal, 300s for others)
- Memory (should be 512MB for journal, 256MB for others)
- State (should be `Active`)

### Manually Invoke a Lambda Function

Test if the function even runs:

```bash
# Invoke job-search manually
aws lambda invoke \
  --function-name job-search-lambda \
  --region us-west-2 \
  --log-type Tail \
  /tmp/response.json

# View response
cat /tmp/response.json | jq .

# View execution logs
aws lambda invoke \
  --function-name job-search-lambda \
  --region us-west-2 \
  --log-type Tail \
  /tmp/response.json | jq -r .LogResult | base64 --decode
```

**Expected:** HTTP 200 status and successful execution message.

**If error:** The logs will show why.

### Check EventBridge Rule Targets

```bash
# Verify each rule has the correct Lambda as target
aws events list-targets-by-rule --rule morning-journal-lambda-rule --region us-west-2
aws events list-targets-by-rule --rule job-search-lambda-rule --region us-west-2
aws events list-targets-by-rule --rule gmail-digest-lambda-rule --region us-west-2
```

**Expected output:**
```json
{
  "Targets": [
    {
      "Id": "1",
      "Arn": "arn:aws:lambda:us-west-2:682033478890:function:job-search-lambda",
      "RoleArn": "arn:aws:iam::682033478890:role/lambda-morning-automation-role"
    }
  ]
}
```

---

## Quick Diagnosis Script

Save this as `debug-lambda.sh`:

```bash
#!/bin/bash
set -e

echo "=== Lambda Debug Report ==="
echo "Region: us-west-2"
echo "Account: 682033478890"
echo ""

echo "--- EventBridge Rules ---"
aws events list-rules --region us-west-2 --output table

echo ""
echo "--- Lambda Functions ---"
aws lambda list-functions --region us-west-2 --query 'Functions[*].[FunctionName,State,LastModified]' --output table

echo ""
echo "--- Job Search Lambda Config ---"
aws lambda get-function-configuration --function-name job-search-lambda --region us-west-2 --output json | jq '{State, LastModified, Timeout, MemorySize}'

echo ""
echo "--- Gmail Digest Lambda Logs (Last 1h) ---"
aws logs tail /aws/lambda/gmail-digest-lambda --region us-west-2 --since 1h || echo "(No logs or permission issue)"

echo ""
echo "--- SES Status ---"
aws ses get-account-sending-enabled --region us-west-2

echo ""
echo "=== Done ==="
```

Run it:
```bash
bash debug-lambda.sh
```

---

## Resolution Checklist

Once you've diagnosed the issues, fill this out:

```
[ ] Issue 1: Duplicate job search
    [ ] Found duplicate EventBridge rule? YES/NO
    [ ] Found duplicate Lambda target? YES/NO
    [ ] Found OpenClaw cron job? YES/NO
    [ ] Action taken: ___________________

[ ] Issue 2: Gmail digest not sending
    [ ] GMAIL_OAUTH_CONFIG is set? YES/NO
    [ ] No errors in Lambda logs? YES/NO
    [ ] SES is in production mode? YES/NO
    [ ] mtorres253@gmail.com is verified in SES? YES/NO
    [ ] Action taken: ___________________

[ ] Issue 3: All systems working
    [ ] All 3 Lambda functions listed and active
    [ ] All 3 EventBridge rules pointing to correct targets
    [ ] Manual Lambda invocation successful
    [ ] Received all 3 emails at 9 AM PDT tomorrow
```

---

## Resources

- **AWS Lambda Docs:** https://docs.aws.amazon.com/lambda/
- **EventBridge Docs:** https://docs.aws.amazon.com/eventbridge/
- **CloudWatch Logs Docs:** https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/
- **SES Sandbox Limits:** https://docs.aws.amazon.com/ses/latest/DeveloperGuide/request-production-access.html

---

**Last updated:** April 16, 2026
