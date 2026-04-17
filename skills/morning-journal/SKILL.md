---
name: morning-journal
description: Daily morning reflection and planning journal. Sends a journal prompt email each morning at 8 AM PDT asking what you're grateful for, your tasks for the day, and which personal strengths you'll need. Delivered via AWS Lambda.
---

# Morning Journal

Daily morning reflection prompt. Sends a simple email at 8 AM PDT with three questions to anchor your day.

**Status:** Running on AWS Lambda (automated, no manual intervention needed)

## How It Works

**EventBridge triggers at 8:00 AM PDT daily:**

1. Lambda function `morning_journal_lambda` runs
2. Sends email to `mtorres253@gmail.com` with the three reflection questions
3. Completes and logs to CloudWatch

**Expected:** Journal prompt email arrives in inbox at 8:00-8:05 AM PDT daily

**Email content:**
```
Subject: Your Daily Journal Prompt - YYYY-MM-DD

Hi Michael,

Three things to anchor your day:

1. What are you grateful for today? (Even small things count.)
2. What are your main tasks? (What does "done" look like?)
3. Which strengths will you need? (What are you bringing to the table?)

Reply to this email with your journal entry. Your response will be automatically saved.
```

## Notes

- **Email-based:** Unlike the original Civic-based system, this version sends a simple email prompt. No automatic Google Docs recording yet.
- **CloudWatch logs:** Check Lambda CloudWatch logs if prompt doesn't arrive
- **Future:** Could expand to capture replies and store in a journaling system
- **No S3 storage:** Responses are not stored in S3 (S3 client initialized but not used)
