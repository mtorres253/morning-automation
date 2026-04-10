# Gmail Digest Lambda Deployment

## Quick Deploy

The `gmail-digest-lambda.zip` is ready to deploy. It contains:
- ✅ `fetch_digest.py` — fetches emails via Gmail OAuth
- ✅ `format_and_deliver.py` — formats and sends digest
- ✅ `lambda_handler.py` — Lambda entry point
- ✅ Gmail OAuth credentials (gmail_oauth.json)
- ✅ Email SMTP credentials (email_config.json)
- ✅ Configuration (gmail-digest-config.json)

## AWS Console Upload

1. Go to **AWS Lambda Console**
2. Find or create function: `gmail-digest`
3. **Upload from .zip file:**
   - Click "Upload from" → ".zip file"
   - Select: `skills/gmail-digest/gmail-digest-lambda.zip`
   - Click "Save"

4. **Set Handler:**
   - Handler: `scripts.lambda_handler.lambda_handler`

5. **Set Timeout:**
   - Timeout: 60 seconds (gives script time to fetch 50 emails)

6. **Test (optional):**
   - Create test event with empty JSON: `{}`
   - Run test
   - Should see: "✓ Fetched X emails" and "✓ Email sent to..."

## CloudWatch Events

Function should be triggered by EventBridge rule: `gmail-digest-daily`

- **Schedule:** `0 9 * * *` (9 AM UTC = midnight PDT... adjust as needed)
- **Target:** Lambda function `gmail-digest`

To verify:
```bash
aws events list-rules --query "Rules[?Name=='gmail-digest-daily']"
```

## Rebuild & Redeploy

Whenever you update credentials or code:

```bash
cd ~/.openclaw/workspace/skills/gmail-digest

# Rebuild zip
rm -f gmail-digest-lambda.zip
zip -r gmail-digest-lambda.zip \
  scripts/fetch_digest.py \
  scripts/format_and_deliver.py \
  scripts/lambda_handler.py \
  gmail-digest-config.json \
  ../../secrets/gmail_oauth.json \
  ../../secrets/email_config.json

# Upload to Lambda via AWS CLI
aws lambda update-function-code \
  --function-name gmail-digest \
  --zip-file fileb://gmail-digest-lambda.zip
```

## Environment Variables (Alternative)

If you prefer NOT to bundle credentials (more secure):

1. **Don't include credential files in zip**
2. **Set Lambda environment variables:**
   - `GMAIL_OAUTH_JSON`: (contents of gmail_oauth.json as JSON string)
   - `EMAIL_CONFIG_JSON`: (contents of email_config.json as JSON string)

3. **Update scripts to read from env:**
   ```python
   oauth_json = os.environ.get('GMAIL_OAUTH_JSON')
   creds = json.loads(oauth_json)
   ```

This approach is more secure for production.

## Troubleshooting

### Function times out (>60s)
- Increase timeout to 120 seconds
- Or: Reduce maxResults from 50 to 25 in fetch_digest.py

### "Module not found" error
- Check handler: should be `scripts.lambda_handler.lambda_handler`
- Ensure zip structure has `scripts/` folder at root

### "Credentials not found"
- If bundled: ensure json files are in zip root
- If env vars: check they're set correctly in Lambda console
- If neither: function will skip email delivery with warning

### "Email delivery failed"
- Check email_config.json has valid app password
- Test locally first: `python3 scripts/format_and_deliver.py`

## Logs

View execution logs in CloudWatch:
```bash
aws logs tail /aws/lambda/gmail-digest --follow
```

Or in AWS Console: Lambda → gmail-digest → Monitor → CloudWatch Logs
