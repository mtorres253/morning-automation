# Lambda Mystery — MAJOR DISCOVERY — April 16, 2026

## The Bombshell Finding 💣

**After getting IAM permissions and checking AWS directly:**

### What Does NOT Exist

```
❌ NO AWS Lambda functions
   aws lambda list-functions → returns EMPTY

❌ NO EventBridge rules  
   aws events list-rules → returns EMPTY
   (even though console shows "morning-automation-rule" as legacy)

❌ NO EventBridge targets
   aws events list-targets-by-rule → fails (rule doesn't exist)

❌ NO system crontab
   crontab -l → no user crontab

❌ NO running Python processes
   ps aux | grep job-search → nothing

❌ NO recent changes to job-search code
   Last modified: April 10, 2026
```

### What DOES Exist

```
✅ OpenClaw Cron Jobs:
   - Morning Journal (8 AM) — ENABLED, working
   - Daily Gmail Digest (9 AM) — DISABLED, 16 errors

✅ Local skill scripts:
   - skills/gmail-digest/scripts/fetch_digest.py
   - skills/job-search/scripts/search_jobs.py
   - skills/job-search/scripts/filter_and_deliver.py

✅ Job search email in inbox:
   - Received: 9:00:41 AM PDT today
   - From: mtorres253@gmail.com
   - Subject: "🔍 Daily Job Search Digest — Thursday, April 16"
```

## The Mystery

**The job search email you received at 9:00:41 AM HAD TO come from somewhere, but:**

1. ❌ Not from AWS Lambda (doesn't exist)
2. ❌ Not from OpenClaw cron (no job-search job defined)
3. ❌ Not from system cron (crontab is empty)
4. ❌ Not from a running process (nothing in ps)

**Three possibilities:**

### Possibility 1: Different AWS Account
The Lambda functions might be in a DIFFERENT AWS account than 682033478890.
- Your credentials might have access to multiple accounts
- The console might show the wrong account
- Or you're authenticated to a different account

**Action:** Check which account you're logged into and if you have cross-account access

### Possibility 2: Someone Else Running It
Another person or system is triggering the job search manually:
- Another user on the same AWS account
- A different machine or automation
- A GitHub Actions workflow or similar

**Action:** Check who else has access to your AWS account and email system

### Possibility 3: Already Delivered Before 9 AM
The email might have been queued yesterday and delivered this morning:
- The email headers would show original send time
- SES might have retried/delivered it this morning

**Action:** Check the email headers to see actual send time vs delivery time

### Possibility 4: Manual Trigger You Forgot About
You or someone ran the job-search script manually this morning:
- `python3 skills/job-search/scripts/filter_and_deliver.py`
- Could explain the 9:00:41 AM timestamp

**Action:** Check bash history

## What We Need to Solve This

Run these commands to get more info:

```bash
# Check which AWS account you're currently authenticated to
aws sts get-caller-identity

# Check if you have access to other AWS accounts
aws sts list-accounts 2>/dev/null || echo "No permission to list accounts"

# Check your bash history for job-search runs
history | grep job-search

# Check mail logs (if available)
log stream --predicate 'process == "Mail"' --info 2>/dev/null || echo "No mail logs"

# List all scheduled tasks on Mac
launchctl list | grep job-search
```

## Theory: Possible Cross-Account Access

Your IAM user might be in account `682033478890`, but able to assume a role in ANOTHER account where the Lambda functions actually exist.

**Check:**
```bash
# Try to assume a role (if you have permission)
aws sts list-roles --region us-west-2

# Or look for AssumeRole capabilities
aws iam get-user
```

## Current Status

- 🔍 **Investigation ongoing:** Where did that 9 AM job search email really come from?
- ⏳ **Next step:** Check email headers and AWS account details
- 📧 **The email exists and is real** — we just need to find the source

---

**Key Insight:** The infrastructure as deployed (Lambda + EventBridge) doesn't appear to exist in the AWS account we have access to. Either:
1. It's in a different account (cross-account access)
2. It was never actually deployed
3. It was deleted
4. Something else is triggering the emails

**Smoking gun:** That 9:00:41 AM email is REAL and we received it. So SOMETHING triggered it. We just need to find what.
