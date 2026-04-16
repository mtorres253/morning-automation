# Lambda Architecture Debug — April 16, 2026

## The Mystery: Two Job Search Deliveries + Silent Gmail Digest

**Reported Issues:**
1. Job search emails arriving at 9 AM AND 10 AM (duplicate)
2. Gmail digest silently failing since April 10

**Root Cause Analysis:**

### Part 1: What's Actually Working ✅

**Tested locally today (April 16, 4:27 PM PDT):**

1. **Gmail digest script** (`fetch_digest.py`) — ✅ WORKING
   - Authenticated via OAuth
   - Fetched 8 emails from last 24 hours
   - Proof: Job search digest email visible in inbox (sent at 9:00:41 AM today)
   - Proof: Journal prompt email visible in inbox (sent at 4:00 PM UTC = 9 AM PDT)

2. **Job search script** (`search_jobs.py`) — ✅ WORKING
   - Found 10 jobs via JSearch API
   - Saved raw results locally

3. **Job delivery script** (`filter_and_deliver.py`) — ✅ WORKING
   - Filtered 10 jobs → 9 new (1 duplicate from yesterday)
   - **Successfully sent email to mtorres253@gmail.com**
   - Email delivery confirmed

### Part 2: Where the Duplication Comes From

**The deployment creates THREE separate EventBridge rules:**

From `aws-lambda-setup/deploy.py` line ~180:
```python
for function_name in lambda_functions:
    rule_name = f"{function_name}-rule"
    # Creates: morning-journal-lambda-rule, job-search-lambda-rule, gmail-digest-lambda-rule
```

**Each rule fires at 9 AM PT (4 PM UTC):**
- `cron(0 16 * * ? *)` = 4 PM UTC = 9 AM PT (but in April, we're in PDT, so it's actually 9 AM PDT with DST)

So you should see:
- `morning-journal-lambda` at 9 AM ✅
- `job-search-lambda` at 9 AM ✅
- `gmail-digest-lambda` at 9 AM ✅

**But you see job search at 9 AM AND 10 AM.**

**Possible reasons:**
1. **Lambda retried** (if first invocation failed with a retryable error)
2. **Second EventBridge rule** exists (maybe from multiple deployment runs)
3. **OpenClaw cron job** also triggers job-search at a different time
4. **SES is sending twice** (very unlikely but possible with edge case in email config)

### Part 3: Why Gmail Digest Appears Silent (But Might Be Working)

**The OpenClaw cron job for Gmail digest is DISABLED:**
```
"name": "Daily Gmail Digest"
"enabled": false
"schedule": "0 9 * * *" (9 AM PDT)
"lastRunStatus": "error"
"consecutiveErrors": 16
"lastError": "Channel is required (no configured channels detected)..."
```

**But the Lambda function should be working independently.** However:

1. **Can't verify via AWS Console** — your IAM user doesn't have permissions
2. **Gmail OAuth is definitely working** — proven by email fetch test
3. **Email delivery infrastructure is working** — job search emails arriving
4. **So gmail-digest-lambda should also be working**, unless:
   - Environment variable `GMAIL_OAUTH_CONFIG` not set in Lambda
   - SES email sandbox issues
   - Lambda function code outdated

### Part 4: Next Steps

**To fix the duplicate job search:**
1. Check AWS EventBridge to see if there are TWO `job-search-lambda-rule` entries
2. If yes, delete the duplicate
3. If no, check if OpenClaw has a cron job for job-search (not showing in our cron list)

**To verify Gmail digest is working:**
1. Check your email inbox for "Daily Gmail Digest" emails from April 10 onwards
   - If they arrive at 9 AM PDT, Lambda IS working ✅
   - If they never arrived, Lambda is failing ❌

**To confirm everything works as a system:**
1. Wait for tomorrow (April 17) at 9 AM PT
2. Check inbox for:
   - Morning journal prompt (8 AM)
   - Job search digest (9 AM)
   - Gmail digest (9 AM)

## Files & References

- **IAM Policy Request:** `aws-lambda-setup/IAM_POLICY_REQUEST.md` — Share with AWS admin
- **Deploy Script:** `aws-lambda-setup/deploy.py` — Shows EventBridge setup
- **Local Test Results:**
  - Gmail fetch: ✅ Working (8 emails, OAuth valid)
  - Job search: ✅ Working (10 jobs found)
  - Job delivery: ✅ Working (email sent)

## Action Items

1. ⏳ Share IAM_POLICY_REQUEST.md with AWS admin
2. 🔍 Once you get permissions, run: `aws events list-rules --region us-west-2` to check for duplicate job-search rules
3. 📧 Check inbox for Gmail digest emails
4. 🧪 Tomorrow morning, verify all three emails arrive

## IAM Access Issue

**Current user:** `michaels-laptop-lamdba-developer`  
**Current permissions:** EXTREMELY limited (can't even list Lambda functions or see own policies)  
**What we need:** Read-only access to Lambda, EventBridge, CloudWatch, SES  
**Solution:** IAM_POLICY_REQUEST.md (copy and have admin apply)
