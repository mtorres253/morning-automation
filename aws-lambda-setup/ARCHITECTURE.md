# Architecture Overview

This document explains how the three Lambda functions work together as a daily automation system.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    9 AM PT Every Day                             │
│                 (EventBridge Scheduled Rule)                     │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ├─────────────────┬───────────────────┬────────────────┐
               │                 │                   │                │
               ▼                 ▼                   ▼                ▼
         ┌──────────┐       ┌──────────┐       ┌──────────┐
         │ Morning  │       │   Job    │       │  Gmail   │
         │ Journal  │       │  Search  │       │  Digest  │
         │ Lambda   │       │  Lambda  │       │  Lambda  │
         └──┬───────┘       └──┬───────┘       └──┬───────┘
            │                  │                  │
            ▼                  ▼                  ▼
        ┌────────────────────────────────────────────────┐
        │   AWS SES - Send Emails                        │
        │   mtorres253@gmail.com                         │
        └────────────────────────────────────────────────┘
            │                  │                  │
            ▼                  ▼                  ▼
        ┌─────────┐        ┌──────────┐      ┌────────┐
        │ Journal │        │  Results │      │ Digest │
        │ Prompt  │        │  Email   │      │ Email  │
        └────┬────┘        └──────────┘      └────────┘
             │
             │ (Michael replies)
             ▼
         ┌─────────────┐
         │   Gmail     │  (Polling)
         │   API       │  (Every 5 min)
         └─────────────┘  (For 1 hour)
             │
             ▼
        ┌──────────────────────┐
        │  Journal Entry Found │
        └──────────┬───────────┘
                   │
                   ▼
            ┌────────────────┐
            │   AWS S3       │
            │   Bucket       │
            │   michael-     │
            │   journal-     │
            │   entries      │
            └────────────────┘
```

---

## Component Details

### 1. EventBridge (Scheduler)

**Role:** Trigger all three Lambda functions daily at 9 AM PT

```
┌─ EventBridge Rule ─┐
│ Name: morning-automation-rule
│ Schedule: 9 AM PT daily (cron: 0 16 * * ? *)
│ Targets: All 3 Lambda functions
└────────────────────┘
```

**When:** Every day at 16:00 UTC (9 AM PT when DST applies)  
**Action:** Invokes three Lambda functions simultaneously  
**Retry:** Built-in AWS retry (max 2 times)

---

### 2. Morning Journal Lambda

**Purpose:** Collect daily journal entries

```
Input: Gmail OAuth credentials
  ↓
1. Send Email (via SES)
   - Subject: "Your Daily Journal Prompt - 2026-03-28"
   - To: mtorres253@gmail.com
   ↓
2. Poll Gmail API (1 hour, every 5 min)
   - Search: unread messages with "Your Daily Journal Prompt"
   - Extract: email body text
   ↓
3. Store to S3 (if found)
   - Bucket: michael-journal-entries
   - Key: journals/2026-03-28.json
   ↓
Output: Success/failure status
```

**Config:**
- Timeout: 3600 seconds (1 hour)
- Memory: 512 MB
- Handler: `morning_journal_lambda.lambda_handler`

**IAM Permissions Needed:**
- `ses:SendEmail` - Send journal prompt
- `gmail.readonly` - Read Gmail API
- `s3:PutObject` - Store journal

**Environment Variables:**
- `GMAIL_EMAIL` - mtorres253@gmail.com
- `SES_EMAIL` - mtorres253@gmail.com
- `S3_BUCKET` - michael-journal-entries
- `GMAIL_OAUTH_CONFIG` - OAuth token (JSON)

---

### 3. Job Search Lambda

**Purpose:** Run job search and email results

```
Input: Job search config
  ↓
1. Execute job search script
   - Read: /opt/job-search/run.py
   - Config: /opt/job-search/config.json
   - Searches: Indeed, AngelList, Y Combinator
   ↓
2. Format results
   - Extract: Job title, company, salary, location
   - Filter: Based on criteria in config
   ↓
3. Send email (via SES)
   - Subject: "Daily Job Search Results - 2026-03-28"
   - To: mtorres253@gmail.com
   - Body: Formatted search results
   ↓
Output: Success/failure status
```

**Config:**
- Timeout: 300 seconds (5 minutes)
- Memory: 256 MB
- Handler: `job_search_lambda.lambda_handler`

**IAM Permissions Needed:**
- `ses:SendEmail` - Send results

**Environment Variables:**
- `GMAIL_EMAIL` - mtorres253@gmail.com
- `SES_EMAIL` - mtorres253@gmail.com
- `JOB_SEARCH_SCRIPT` - /opt/job-search/run.py
- `JOB_SEARCH_CONFIG` - /opt/job-search/config.json

---

### 4. Gmail Digest Lambda

**Purpose:** Summarize recent emails

```
Input: Gmail OAuth credentials
  ↓
1. Query Gmail API
   - Filter: Last 24 hours
   - Max: 50 messages
   ↓
2. Extract metadata
   - From: Sender
   - Subject: Email subject
   - Date: Received date
   ↓
3. Format digest
   - Create: Bullet-point list
   - Sort: By most recent
   ↓
4. Send email (via SES)
   - Subject: "Email Digest - 2026-03-28"
   - To: mtorres253@gmail.com
   - Body: List of emails from last 24h
   ↓
Output: Success/failure status
```

**Config:**
- Timeout: 60 seconds
- Memory: 256 MB
- Handler: `gmail_digest_lambda.lambda_handler`

**IAM Permissions Needed:**
- `gmail.readonly` - Read Gmail
- `ses:SendEmail` - Send digest

**Environment Variables:**
- `GMAIL_EMAIL` - mtorres253@gmail.com
- `SES_EMAIL` - mtorres253@gmail.com
- `GMAIL_OAUTH_CONFIG` - OAuth token (JSON)

---

## Data Flow

### Morning Journal Entry

```
9 AM PT
  │
  ├─ Lambda sends: "Your Daily Journal Prompt - 2026-03-28"
  │  Email from: mtorres253@gmail.com
  │  Email to: mtorres253@gmail.com (your inbox)
  │
  ├─ Michael receives email
  │  │
  │  └─ Michael replies with journal entry
  │     (e.g., "Today was productive, worked on...")
  │
  ├─ Lambda polls Gmail every 5 minutes for 1 hour
  │  │
  │  ├─ 9:05 AM - Check: No new reply
  │  ├─ 9:10 AM - Check: No new reply
  │  ├─ 9:15 AM - Check: No new reply
  │  ├─ ...
  │  └─ 9:35 AM - Check: FOUND REPLY! ✓
  │
  └─ Lambda stores to S3
     File: s3://michael-journal-entries/journals/2026-03-28.json
     Content: {
       "found": true,
       "subject": "Your Daily Journal Prompt - 2026-03-28",
       "body": "Today was productive, worked on...",
       "timestamp": "2026-03-28T09:35:00Z"
     }
```

---

## AWS Service Interactions

```
┌─────────────────────┐
│  EventBridge        │  Scheduler
│  (trigger)          │
└──────────┬──────────┘
           │ Invokes (5 times/week)
           ▼
┌─────────────────────┐
│  AWS Lambda         │
│  (compute)          │
│  - 3 functions      │
│  - Run in parallel  │
└──────────┬──────────┘
     ┌─────┼─────┐
     │     │     │
     ▼     ▼     ▼
  ┌──────────┐ ┌──────────┐ ┌──────────┐
  │ SES      │ │ Gmail    │ │ S3       │
  │ (email)  │ │ (read)   │ │ (storage)│
  └─────┬────┘ └────┬─────┘ └────┬─────┘
        │           │            │
        └─────┬─────┴────────────┘
              │
              ▼
        ┌────────────────┐
        │ CloudWatch     │
        │ Logs           │
        │ (monitoring)   │
        └────────────────┘
```

---

## Security Model

### Credentials & Access

```
┌─────────────────────────────────┐
│ Credentials Storage             │
├─────────────────────────────────┤
│ Gmail OAuth Token               │
│ ├─ Stored in: Lambda env var   │
│ ├─ Encrypted: AWS KMS (default) │
│ └─ Scope: Read emails only      │
│                                 │
│ AWS IAM Role                    │
│ ├─ Lambda execution role        │
│ ├─ SES send emails              │
│ ├─ S3 write to bucket           │
│ └─ CloudWatch logs              │
└─────────────────────────────────┘
```

### Least Privilege Permissions

- Lambda has **only** permissions it needs
- No delete permissions
- No cross-account access
- No internet access (VPC default)
- Logs retained for 7 days then deleted

---

## Failure Scenarios

### If Morning Journal Lambda Fails

```
9 AM - Function starts
  ↓
❌ Error sending email?
  → CloudWatch logs it
  → Function continues to polling step
  → Polls for 1 hour anyway
  ↓
❌ Gmail API down?
  → Function retries 2 times (AWS default)
  → Logs error to CloudWatch
  → Exits gracefully
  ↓
❌ S3 write fails?
  → Logs error
  → But journal content still in memory
  → Can be retried manually
```

**Recovery:** Check CloudWatch logs, fix issue, redeploy

### If EventBridge Rule Fails

```
❌ Rule disabled accidentally?
  → Functions won't trigger at 9 AM
  → Manual trigger still works:
     aws lambda invoke --function-name morning-journal-lambda ...
  ✓ Reenable: aws events put-rule --name morning-automation-rule --state ENABLED
```

---

## Performance Characteristics

| Component | Typical Duration | Max Duration | Cost |
|-----------|------------------|--------------|------|
| Morning Journal | 30-60 min (polling) | 3600 sec | ~$0.20 |
| Job Search | 30-60 sec | 300 sec | ~$0.02 |
| Gmail Digest | 5-10 sec | 60 sec | ~$0.01 |
| Email Send (SES) | <1 sec | N/A | $0 (free tier) |
| S3 Write | <100 ms | N/A | ~$0.00 |

**Total monthly:** ~$0.35 (mostly from Lambda compute time)

---

## Scalability

This architecture scales to:
- **10,000+ emails/month** (well within SES free tier)
- **365 Lambda invocations/year** (minimal Lambda costs)
- **365 journal entries** (negligible S3 storage)

No changes needed unless you:
- Increase polling frequency to < 5 min
- Process hundreds of emails per digest
- Store large files to S3

---

## Monitoring & Alerts

```
┌─ CloudWatch Logs ─────────┐
│ /aws/lambda/morning-...    │
│ /aws/lambda/job-search-... │
│ /aws/lambda/gmail-digest-..│
└────────────┬──────────────┘
             │
    ┌────────▼────────┐
    │ CloudWatch      │
    │ Metrics         │
    │ - Invocations   │
    │ - Errors        │
    │ - Duration      │
    │ - Throttles     │
    └─────────────────┘
```

**Recommended Monitoring:**
- Check logs daily (or use CloudWatch Logs Insights)
- Create CloudWatch alarm if errors exceed 1/day
- Review costs monthly in AWS Billing console

---

## Deployment Options

### Option 1: Automated (Recommended)
```bash
python3 deploy.py
```
✓ Packages dependencies  
✓ Creates functions  
✓ Sets up EventBridge  
✓ 5-10 minutes  

### Option 2: CloudFormation
```bash
aws cloudformation create-stack ...
```
✓ Infrastructure as code  
✓ Repeatable  
✓ 2 minutes  

### Option 3: Manual
Use AWS Console  
✓ Full control  
✓ 30+ minutes  

---

## Daily Execution Timeline

```
08:55 AM PT - EventBridge prepares to trigger

09:00 AM PT - EXECUTION START
  │
  ├─ 09:00-09:00 - Morning Journal Lambda invoked
  │  ├─ 09:00 - Send journal prompt email (5 sec)
  │  ├─ 09:05-10:00 - Poll Gmail for response (1 hour max)
  │  ├─ 10:00 - Store to S3 if found
  │  └─ 10:00 - Function completes
  │
  ├─ 09:00-09:01 - Job Search Lambda invoked
  │  ├─ 09:00 - Run job search script (30 sec)
  │  ├─ 09:01 - Send results email (2 sec)
  │  └─ 09:01 - Function completes
  │
  └─ 09:00-09:00 - Gmail Digest Lambda invoked
     ├─ 09:00 - Query Gmail API (3 sec)
     ├─ 09:00 - Format digest (2 sec)
     ├─ 09:00 - Send digest email (2 sec)
     └─ 09:00 - Function completes

10:00+ AM PT - All functions complete
  └─ Michael receives 1-3 emails in inbox
```

---

## Customization Points

Want to change something? Edit these files:

1. **Journal prompt text:**
   → `lambda_functions/morning_journal_lambda.py` → `JOURNAL_PROMPT`

2. **Polling frequency:**
   → `lambda_functions/morning_journal_lambda.py` → `check_interval`

3. **Execution time:**
   → `deploy.py` → `cron_expression`  
   → Or: `QUICK_START.md` → Step 4 (cron syntax)

4. **Email recipients:**
   → Environment variables in each Lambda

5. **S3 bucket name:**
   → `deploy.py` → `S3_BUCKET`

---

## Disaster Recovery

### If S3 bucket deleted
→ Recreate bucket  
→ No data loss (first entry made same day)  

### If Lambda function deleted
→ Redeploy with `python3 deploy.py`  
→ EventBridge rule remains intact  

### If EventBridge rule deleted
→ Functions won't run at 9 AM  
→ Manually recreate with `deploy.py`  

### If IAM role deleted
→ Nothing will work  
→ Recreate role following QUICK_START.md steps  

---

## Advanced Topics

See full documentation:
- Performance tuning: README.md
- Cost optimization: DEPLOYMENT_SUMMARY.md
- Custom integrations: README.md
- Monitoring: TROUBLESHOOTING.md

---

Created: 2026-03-28  
Architecture Version: 1.0  
Last Updated: 2026-03-28
