# Fix Gmail Digest & Update Lambda Functions — us-east-2 Region Mismatch

## The Problem (SOLVED)

All three Lambda functions were hardcoded to use `us-west-2` (Oregon), but they're actually deployed in `us-east-2` (Ohio).

**Result:** SES client fails silently because it's trying to connect to the wrong region.

## The Fix

I've updated all three Lambda function files to use `us-east-2`:
- ✅ gmail_digest_lambda.py
- ✅ job_search_lambda.py
- ✅ morning_journal_lambda.py

New zip files created:
- `aws-lambda-setup/gmail_digest-lambda-updated.zip`
- `aws-lambda-setup/job_search-lambda-updated.zip`
- `aws-lambda-setup/morning_journal-lambda-updated.zip`

## Now Upload the Updated Code

You need to upload each zip file to its corresponding Lambda function in AWS Console.

### Step 1: Go to Lambda Console

1. Log into AWS Console
2. Region: **us-east-2** (top right)
3. Service: **Lambda**
4. You should see three functions:
   - gmail-digest-lambda
   - job-search-lambda
   - morning-journal-lambda

### Step 2: Upload gmail-digest-lambda

1. Click **gmail-digest-lambda**
2. Scroll down to **Code** section
3. Click **Upload from** → **ZIP file**
4. Choose: `aws-lambda-setup/gmail_digest-lambda-updated.zip`
5. Click **Save**
6. Wait for confirmation message

### Step 3: Upload job-search-lambda

1. Go back to Lambda functions list
2. Click **job-search-lambda**
3. Click **Upload from** → **ZIP file**
4. Choose: `aws-lambda-setup/job_search-lambda-updated.zip`
5. Click **Save**
6. Wait for confirmation

### Step 4: Upload morning-journal-lambda

1. Go back to Lambda functions list
2. Click **morning-journal-lambda**
3. Click **Upload from** → **ZIP file**
4. Choose: `aws-lambda-setup/morning_journal-lambda-updated.zip`
5. Click **Save**
6. Wait for confirmation

## That's It!

Once all three are uploaded, the Lambda functions will use the correct region (`us-east-2`) and SES should work properly.

## Test Tomorrow Morning (April 17)

At 9 AM PDT, you should receive:
- ✅ Morning journal prompt email
- ✅ Job search digest email
- ✅ **Gmail digest email** (this should finally work!)

If any are missing, check CloudWatch logs for errors.

---

**Time to complete:** 5-10 minutes  
**Difficulty:** Easy (just upload files)  
**Expected result:** All three Lambda functions working correctly
