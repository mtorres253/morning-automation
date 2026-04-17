---
name: gmail-digest
description: Fetch and summarize Michael's Gmail messages from the last 24 hours and deliver the digest via email. Runs daily at 9 AM PDT via AWS Lambda.
---

# Gmail Digest

Fetches emails from the last 24 hours via Gmail OAuth and delivers a formatted digest via email.

**Status:** Running on AWS Lambda (automated, no manual intervention needed)

## Credentials (Lambda)

**Gmail OAuth:** Set as Lambda environment variable `GMAIL_OAUTH_CONFIG`
- Contains: `client_id`, `client_secret`, `refresh_token`
- Auto-refreshes access tokens via OAuth 2.0

**Email delivery:** Uses AWS SES (Simple Email Service)
- Lambda has IAM permissions to send via SES
- Sends formatted HTML digests to `mtorres253@gmail.com`

## Workflow

**Automated (Lambda):**
1. EventBridge triggers at 9:00 AM PDT daily
2. Lambda function `gmail_digest_lambda` runs
3. Fetches emails from last 24 hours via Gmail OAuth
4. Groups emails by category (Work, Job Alerts, Calendar, GitHub, Personal, Newsletters, Notifications, Transactional)
5. Formats digest as HTML email
6. Sends via AWS SES to `mtorres253@gmail.com`
7. Completes and logs to CloudWatch

**Expected:** Digest email arrives in inbox at 9:00-9:05 AM PDT daily

## Manual Testing (Local)

If you need to test locally:

```bash
cd /Users/michaeltorres/.openclaw/workspace/skills/gmail-digest
python3 scripts/fetch_digest.py       # Just fetch emails
python3 scripts/format_and_deliver.py # Fetch + format + deliver via SMTP
```

These require `gmail_oauth.json` and `email_config.json` locally configured.

## Notes

- **Gmail OAuth:** Tokens auto-refresh via refresh_token. If Lambda gets 401 errors, regenerate credentials and update `GMAIL_OAUTH_CONFIG` env var
- **Email delivery:** Uses AWS SES (no app passwords needed)
- **CloudWatch logs:** Check Lambda CloudWatch logs if digest doesn't arrive
- **Categories:** Emails are grouped by Work, Job Alerts, Calendar, GitHub, Personal, Newsletters, Notifications, Transactional
- **Privacy:** Email content is only sent to your inbox, not exposed publicly
