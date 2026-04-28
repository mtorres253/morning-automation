# Lambda Deployment Guide

This package is ready to deploy to AWS Lambda for daily job search digest emails.

## Setup Instructions

### Step 1: Prepare Environment Variables

You'll need the following in your Lambda environment:

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

**How to get JSearch API Key:**
1. Go to https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
2. Click "Subscribe" → Free Plan
3. Go to https://rapidapi.com/settings/applications
4. Copy API Key from "default" application

**How to get Gmail app password:**
1. Go to https://myaccount.google.com/security
2. Enable 2-factor authentication
3. Go to "App passwords"
4. Select Mail + your OS
5. Copy the 16-character password

### Step 2: Create Deployment Package

```bash
# Install dependencies
pip install -r requirements.txt -t .

# Create zip file
zip -r job-search-lambda.zip . \
  -x "*.git*" "*.md" ".DS_Store" "__pycache__/*"
```

Or use the provided script:
```bash
bash create_package.sh
```

### Step 3: Create Lambda Function

**In AWS Console:**

1. Go to Lambda → Create Function
2. **Function name:** `job-search-digest`
3. **Runtime:** Python 3.11
4. **Architecture:** x86_64 (or arm64 if preferred)
5. Click "Create function"

### Step 4: Upload Code

1. Click "Upload from" → ".zip file"
2. Select `job-search-lambda.zip`
3. Click "Save"

### Step 5: Configure Settings

1. **Handler:** `lambda_handler.lambda_handler`
2. **Timeout:** 60 seconds (minimum)
3. **Memory:** 512 MB (minimum, 1024 MB recommended)
4. **Ephemeral storage:** 512 MB (default)

### Step 6: Set Environment Variables

1. Click "Configuration" → "Environment variables"
2. Click "Edit"
3. Add all the variables from Step 1
4. Click "Save"

### Step 7: Schedule Daily Execution

**Create CloudWatch Events Rule:**

1. Go to CloudWatch → Events → Rules → Create rule
2. **Name:** `job-search-daily`
3. **Event source:** Schedule expression
4. **Schedule:** `cron(0 17 * * ? *)` (9 AM PDT = 5 PM UTC)
5. **Target:** Lambda function → `job-search-digest`
6. Click "Create rule"

**Alternative time zones:**
- 9 AM PDT (Pacific): `cron(0 17 * * ? *)` (UTC)
- 9 AM PST (Pacific, winter): `cron(0 17 * * ? *)` (UTC)
- 9 AM EST (Eastern): `cron(0 14 * * ? *)` (UTC)
- 9 AM CST (Central): `cron(0 15 * * ? *)` (UTC)

### Step 8: Test

1. In Lambda console, click "Test"
2. Create a test event (empty JSON `{}`)
3. Click "Test"
4. Check CloudWatch Logs for output
5. Verify email received

## File Structure

```
job-search-lambda/
├── lambda_handler.py          # Lambda entry point
├── requirements.txt           # Python dependencies
├── LAMBDA_DEPLOYMENT.md       # This file
├── create_package.sh          # Package creation script
├── job_search/
│   ├── __init__.py
│   ├── scripts/
│   │   ├── search_jobs.py     # Job search logic
│   │   └── filter_and_deliver.py  # Filtering & email
│   ├── config/
│   │   └── job-search-config.json # Search criteria
│   ├── secrets/               # (empty, use env vars)
│   └── results/               # (generated at runtime)
```

## Monitoring

### CloudWatch Logs

All execution logs go to CloudWatch. View them:

1. Lambda console → Function → Monitor
2. Click "View logs in CloudWatch"
3. Click latest log stream

### Lambda Metrics

Watch these metrics in CloudWatch:

- **Invocations:** Should be 1 per day
- **Duration:** Should be 10-30 seconds
- **Errors:** Should be 0
- **Throttles:** Should be 0

### Email Delivery

Check your email inbox for digests at 9 AM daily.

If email doesn't arrive:
1. Check CloudWatch logs for errors
2. Verify SMTP credentials are correct
3. Verify EMAIL_TO is set correctly
4. Check Gmail "Less secure apps" is disabled (you're using app password)

## Troubleshooting

### "Unable to locate credentials"

**Fix:** Set all environment variables in Lambda console (Step 5)

### "429 Too Many Requests (JSearch)"

**Cause:** Hit API rate limit
**Fix:** JSearch free tier is 100 requests/month. Once per day = 30/month. Upgrade plan if needed.

### "SMTP authentication failed"

**Fix:** 
- Verify sender email is Gmail
- Regenerate app password
- Verify "Less secure apps" is NOT enabled (you use app password)
- Verify SENDER_EMAIL matches the Gmail account

### "Job listings not showing up"

**Cause:** Same jobs shown for only 3 days, then dropped
**Fix:** This is by design. Only shows jobs from last 3 days to avoid stale listings.

### Lambda timeout

**Fix:** Increase timeout in Lambda settings to 60+ seconds

## Updates

To update the function:

1. Make changes locally
2. Run `bash create_package.sh`
3. Upload new `job-search-lambda.zip` to Lambda
4. Click "Save"

Changes to `job-search-config.json` can be updated:
- Via environment variables in Lambda console
- Or redeploy with updated config file

## Cost

**Free tier covers:**
- Lambda: 1 million requests/month (only 30 invocations/month needed)
- CloudWatch Logs: 5 GB/month free
- CloudWatch Events: Free

**Monthly cost for this function: ~$0**

## Support

If you encounter issues:

1. Check CloudWatch Logs for error messages
2. Verify all environment variables are set
3. Test locally with `python lambda_handler.py`
4. Review the troubleshooting section above

---

**Last updated:** April 8, 2026
