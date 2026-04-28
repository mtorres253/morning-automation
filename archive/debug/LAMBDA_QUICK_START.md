# Lambda Deployment Quick Start

## Files Ready

✅ **job-search-lambda.zip** (912 KB) — Ready to upload to AWS Lambda

This zip file contains everything needed to run daily job search digests in AWS Lambda.

## What Changed

1. **3-Day Job Window** — Jobs show for 3 days, then drop from list
2. **Fixed Email Count** — Header count now matches actual jobs shown
3. **All Jobs Listed** — All jobs in the 3-day window appear in email

## AWS Setup (5 minutes)

### Step 1: Create Lambda Function

1. Go to AWS Lambda console
2. Click "Create function"
3. **Name:** `job-search-digest`
4. **Runtime:** Python 3.11
5. Click "Create function"

### Step 2: Upload Code

1. Click "Upload from" → ".zip file"
2. Select `job-search-lambda.zip` from this workspace
3. Click "Save"

### Step 3: Configure

1. **Handler:** `lambda_handler.lambda_handler`
2. **Timeout:** 60 seconds
3. **Memory:** 512 MB (minimum)

### Step 4: Add Environment Variables

Click "Configuration" → "Environment variables" → "Edit" → Add these:

```
JSEARCH_API_KEY=<your-jsearch-api-key>
JSEARCH_API_HOST=jsearch.p.rapidapi.com
JSEARCH_API_URL=https://jsearch.p.rapidapi.com/search
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-specific-password
EMAIL_TO=your-email@gmail.com
LOG_LEVEL=INFO
```

**Get JSearch API key:**
1. Go to https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
2. Subscribe to Free Plan
3. Go to https://rapidapi.com/settings/applications
4. Copy API Key

**Get Gmail app password:**
1. https://myaccount.google.com/security
2. Enable 2FA (if not already)
3. Go to "App passwords"
4. Select Mail + your OS
5. Copy the 16-character password

### Step 5: Test

1. Click "Test"
2. Create empty test event `{}`
3. Click "Test"
4. Check CloudWatch logs for success

### Step 6: Schedule

1. Go to CloudWatch → Events → Create rule
2. **Name:** `job-search-daily`
3. **Schedule:** `cron(0 17 * * ? *)` (9 AM PDT / 5 PM UTC)
4. **Target:** Lambda → `job-search-digest`
5. Create rule

## Done!

Your job search digest will run automatically every day at 9 AM PDT and email you the results.

## Files Reference

- **job-search-lambda.zip** — Upload to Lambda
- **LAMBDA_DEPLOYMENT.md** — Full deployment guide with troubleshooting
- **lambda_handler.py** — (inside zip) Entry point for Lambda

## What Happens Each Day

1. **9 AM PDT:** Lambda runs automatically
2. **Search:** JSearch finds jobs from LinkedIn, Glassdoor, ZipRecruiter, Google for Jobs, etc.
3. **Filter:** Shows only jobs from last 3 days (prevents stale listings)
4. **Email:** You receive digest with all current jobs
5. **Logs:** Check CloudWatch if anything fails

## Cost

**$0/month** (free tier covers everything)

---

See LAMBDA_DEPLOYMENT.md for detailed instructions and troubleshooting.
