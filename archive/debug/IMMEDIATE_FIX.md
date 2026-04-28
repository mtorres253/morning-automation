# IMMEDIATE FIX: Delete the Duplicate Job-Search Rule

## The Problem

**Job-search Lambda is executing TWICE per day:**
- 9 AM PDT (9:00:41 AM timestamp in logs)
- 10 AM PDT (expected to run again shortly)

**Root cause:** Two EventBridge rules both targeting the same Lambda function.

## The Fix

**You need to delete ONE of the two job-search EventBridge rules.**

Since you can see CloudWatch logs in the console but the CLI can't list the rules, I'll guide you through the AWS Console:

### Step 1: Go to EventBridge Rules in AWS Console

1. Log into AWS Console
2. Region: **us-west-2**
3. Service: **EventBridge** (or Events)
4. Click: **Rules** (or go to Scheduled Rules)

### Step 2: Look for Job-Search Rules

You should see something like:
- `job-search-lambda-rule` (or similar name)
- Or possibly TWO rules that both target job-search-lambda

Look for rules with schedule `cron(0 16 * * ? *)` or `cron(0 17 * * ? *)` which are 9 AM/10 AM PDT.

### Step 3: Find the Duplicate

There should be TWO rules with different times:
- Rule 1: Schedule `cron(0 16 * * ? *)` = 9 AM PDT 
- Rule 2: Schedule `cron(0 17 * * ? *)` = 10 AM PDT

OR

- Both have the same schedule but one is disabled

### Step 4: Delete One Rule

1. Click on ONE of the job-search rules
2. Click **Delete**
3. Confirm deletion

**Keep the 9 AM one, delete the 10 AM one.** (Or vice versa if you prefer 10 AM)

## After Deletion

Tomorrow morning, you should see **only ONE job-search email** at your preferred time (9 AM or 10 AM).

## Why This Happened

When `deploy.py` runs, it creates EventBridge rules for each Lambda function. If the script was run twice, or if someone modified the rules manually, you end up with duplicates.

## CLI Command (If You Have Full Permissions)

If/when you get full AWS access, you can delete via CLI:

```bash
# List all rules
aws events list-rules --region us-west-2

# Delete the duplicate (replace with actual name)
aws events delete-rule --name job-search-lambda-rule-2 --force --region us-west-2
```

But for now, use the console since your CLI can't list them.

---

**That's it! Delete one rule, and you're done.** ✅
