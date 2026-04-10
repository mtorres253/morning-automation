# Gmail Digest Delivery Setup

## Status

✅ **Built:** Complete end-to-end pipeline (fetch → format → deliver)  
⚠️ **Credential Issue:** Email config has expired Gmail password  
🚀 **Ready to Deploy:** Once email credentials are updated

## Pipeline

```
Gmail API (OAuth)
    ↓
fetch_digest.py (get last 24h emails as JSON)
    ↓
format_and_deliver.py (group, format HTML, send email)
    ↓
Your inbox (mtorres253@gmail.com)
```

## Components

### 1. `fetch_digest.py` ✅
- **Purpose:** Fetch raw emails from Gmail API
- **Input:** Gmail OAuth credentials (`gmail_oauth.json`)
- **Output:** JSON array of `{subject, from, date, snippet}`
- **Time:** ~20 seconds for 50 messages
- **Status:** ✅ Tested & working

### 2. `format_and_deliver.py` ✅
- **Purpose:** Format emails into HTML digest and send
- **Input:** Calls `fetch_digest.py` internally
- **Output:** Sends email to `mtorres253@gmail.com`
- **Categorizes:** Work, Events, Jobs, Personal, Other
- **Status:** ✅ Tested (fails on email send due to bad password)

### 3. `lambda_handler.py` 
- **Purpose:** Entry point for AWS Lambda
- **Usage:** Deployed as `gmail-digest-lambda.zip`
- **Status:** ✅ Ready to package

## Credentials

### Gmail OAuth (Working ✅)
**File:** `~/.openclaw/workspace/secrets/gmail_oauth.json`  
**Status:** ✅ Valid, tested  
**Details:** Auto-refreshes access tokens

### Email SMTP (Needs Update ⚠️)
**File:** `~/.openclaw/workspace/secrets/email_config.json`  
**Current:** `mtorres253@gmail.com` with app password `vlex szac fabx ohsc`  
**Status:** ❌ Invalid (Gmail rejected as bad credentials)  
**Fix:** Generate new app password

## How to Fix Email Delivery

1. **Go to Google Account:**
   ```
   https://myaccount.google.com/apppasswords
   ```

2. **Generate new app password:**
   - Select "Mail" and "Windows Computer" (or "Other")
   - Google gives you a 16-character password

3. **Update the config:**
   ```bash
   cat > ~/.openclaw/workspace/secrets/email_config.json << 'EOF'
   {
     "smtp_server": "smtp.gmail.com",
     "smtp_port": 587,
     "sender_email": "mtorres253@gmail.com",
     "sender_password": "<YOUR_NEW_16_CHAR_PASSWORD>"
   }
   EOF
   ```

4. **Test:**
   ```bash
   python3 skills/gmail-digest/scripts/format_and_deliver.py
   ```

## Configuration

### Email Categories
**File:** `skills/gmail-digest/gmail-digest-config.json`

Customize how emails are grouped:
```json
{
  "emailTo": "mtorres253@gmail.com",
  "categories": {
    "Work & GitHub": ["github", "pull request", "merge"],
    "Meetings & Events": ["meeting", "invite", "calendar"],
    "Job Alerts": ["job search", "digest"],
    "Personal": ["david", "russell"],
    "Other": []
  }
}
```

## Local Testing

```bash
# Just fetch emails
python3 skills/gmail-digest/scripts/fetch_digest.py

# Fetch + format + send
python3 skills/gmail-digest/scripts/format_and_deliver.py

# Output should be:
# ✓ Fetched 50 emails
# ✓ Email sent to mtorres253@gmail.com
```

## Lambda Deployment

Package both Python scripts + credentials:

```bash
cd skills/gmail-digest
zip -r gmail-digest-lambda.zip \
  scripts/fetch_digest.py \
  scripts/format_and_deliver.py \
  scripts/lambda_handler.py \
  gmail-digest-config.json \
  ~/.openclaw/workspace/secrets/gmail_oauth.json \
  ~/.openclaw/secrets/email_config.json
```

Then upload `gmail-digest-lambda.zip` to AWS Lambda with:
- **Handler:** `scripts/lambda_handler.lambda_handler`
- **Environment vars** (if not bundled):
  - `GMAIL_OAUTH_JSON`: (base64-encoded gmail_oauth.json)
  - `EMAIL_CONFIG_JSON`: (base64-encoded email_config.json)

## Next Steps

1. ✅ Get new Gmail app password
2. ✅ Update `email_config.json`
3. ✅ Test locally: `python3 skills/gmail-digest/scripts/format_and_deliver.py`
4. ✅ Repackage Lambda: `gmail-digest-lambda.zip`
5. ✅ Re-upload to Lambda

## Monitoring

Check CloudWatch logs for:
- **Success:** "✓ Fetched X emails" and "✓ Email sent to mtorres253@gmail.com"
- **Errors:** "✗ Email delivery failed" or timeout messages
