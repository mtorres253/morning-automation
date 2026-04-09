# Gmail OAuth Setup for gmail-digest

Since the Civic trial expired, we're switching to direct Gmail OAuth. This is free and more reliable.

## Quick Start

### Step 1: Download OAuth Credentials from Google Cloud

1. Go to https://console.cloud.google.com
2. Create a new project or select existing one
3. Enable **Gmail API** (search for it)
4. Go to **APIs & Services** → **Credentials**
5. Click **+ Create Credentials** → **OAuth client ID**
6. Select **Desktop application**
7. Click **Create**, then download the JSON file

### Step 2: Save Credentials

Move the downloaded JSON file to:
```
~/.openclaw/secrets/gmail_oauth_credentials.json
```

### Step 3: Run Authorization

```bash
python3 /tmp/setup_gmail_auth.py
```

A browser window will open. Click **Allow** to authorize gmail-digest to access your email.

That's it! The token will be cached automatically.

### Step 4: Test

```bash
cd /Users/michaeltorres/.openclaw/workspace
python3 skills/gmail-digest/scripts/fetch_digest.py
```

You should see JSON output of your recent emails.

## Token Refresh

Tokens are cached in `~/.openclaw/secrets/gmail_token.pickle` and refresh automatically when needed. No manual refresh required.

## If Token Expires

If you see "❌ ERROR: Gmail OAuth token not found", just run Step 3 again.
