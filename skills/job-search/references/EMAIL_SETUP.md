# Email Configuration

The job search skill can deliver results via email digest. Here's how to set it up.

## Gmail Setup (Recommended)

1. **Enable 2-Factor Authentication** on your Google account (required for app passwords)
2. **Generate an App Password:**
   - Go to https://myaccount.google.com/
   - Select "Security" in the left menu
   - Find "App passwords" (appears only if 2FA is enabled)
   - Select "Mail" and "Windows Computer" (or your device)
   - Generate a 16-character password
   - Copy it

3. **Create the email config file:**

```bash
mkdir -p ~/.openclaw/secrets
cat > ~/.openclaw/secrets/email_config.json << 'EOF'
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "sender_email": "your-email@gmail.com",
  "sender_password": "your-16-char-app-password"
}
EOF
chmod 600 ~/.openclaw/secrets/email_config.json
```

**Replace:**
- `your-email@gmail.com` with your actual email
- `your-16-char-app-password` with the app password you generated

## Update Job Search Config

Edit `job-search-config.json` to specify where emails should go:

```json
{
  ...
  "emailTo": "your-email@gmail.com",
  ...
}
```

## Test Email Delivery

Run the filter and deliver script manually to test:

```bash
cd /Users/michaeltorres/.openclaw/workspace/skills/job-search
python3 scripts/search_jobs.py
python3 scripts/filter_and_deliver.py
```

You should receive an email within a few seconds.

## Troubleshooting

**"Email credentials not configured"**
- Check that `~/.openclaw/secrets/email_config.json` exists
- Verify the path is exactly right
- Check file permissions: `chmod 600`

**"Login failed"**
- Gmail app passwords are 16 characters without spaces
- If using Gmail, ensure 2FA is enabled
- Try generating a new app password

**"Connection refused"**
- Check SMTP server and port (Gmail: smtp.gmail.com:587)
- Ensure TLS is enabled (it is in the script)

## Privacy & Security

- **Never commit** `email_config.json` to git
- The file is stored in `~/.openclaw/secrets/` (outside the workspace)
- Email credentials are read directly from the file, never logged

---

For other email providers (Outlook, custom domains, etc.), adjust `smtp_server` and `smtp_port` accordingly.
