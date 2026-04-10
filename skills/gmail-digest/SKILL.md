---
name: gmail-digest
description: Fetch and summarize Michael's Gmail messages from the last 24 hours and deliver the digest to chat. Use when asked to summarize emails, run the daily email digest, or check recent Gmail. Also used by the 9 AM daily cron job.
---

# Gmail Digest

Fetches emails from the last 24 hours via Civic (Gmail tools) and delivers a clean summary to chat.

## ⚠️ Policy

Before any external action, follow the policy in:
`/Users/michaeltorres/.openclaw/workspace/skills/morning-journal/references/civic-policy.md`

Key rules: summarize only — never quote verbatim in chat. Never send emails autonomously. Drafts require confirmation.

## Credentials

**Gmail OAuth:** `/Users/michaeltorres/.openclaw/workspace/secrets/gmail_oauth.json`
- `client_id`, `client_secret`, `refresh_token`
- Used by `fetch_digest.py`
- Auto-refreshes access tokens

**Email delivery:** `/Users/michaeltorres/.openclaw/secrets/email_config.json`
- `smtp_server`, `smtp_port`, `sender_email`, `sender_password`
- Used by `format_and_deliver.py` to send digest emails
- Requires Gmail app password (not regular password)

## Workflow

### Pipeline: OAuth → Fetch → Format → Deliver

1. **Fetch emails via Gmail OAuth** (`fetch_digest.py`):
   - Uses OAuth 2.0 credentials from `~/.openclaw/workspace/secrets/gmail_oauth.json`
   - Searches Gmail for messages from last 24 hours
   - Returns JSON: `[{subject, from, date, snippet}, ...]`
   - Takes ~20 seconds for 50 messages

2. **Format and deliver digest** (`format_and_deliver.py`):
   - Calls `fetch_digest.py` internally
   - Groups emails by category (Work, Events, Job Alerts, Personal, Other)
   - Formats as HTML email
   - Sends via SMTP (Gmail, requires app password)
   - **ALWAYS sends** (even if no emails, status included)

### Manual Run

```bash
# Just fetch emails
cd /Users/michaeltorres/.openclaw/workspace
python3 skills/gmail-digest/scripts/fetch_digest.py

# Fetch + format + deliver
python3 skills/gmail-digest/scripts/format_and_deliver.py
```

## Notes

- **Gmail OAuth:** Tokens auto-refresh. If you get 401 errors, regenerate credentials at myaccount.google.com/device-activity
- **Email delivery:** Gmail requires "App Passwords" (not regular passwords). Create one at myaccount.google.com/apppasswords
- **Lambda deployment:** Both `fetch_digest.py` and `format_and_deliver.py` support `/tmp` for temp files
- **Privacy:** Never expose email content verbatim in public channels
- **Categories:** Emails are grouped by Work, Events, Job Alerts, Personal, Other (see gmail-digest-config.json to customize)
