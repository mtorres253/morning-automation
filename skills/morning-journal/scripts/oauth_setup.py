#!/usr/bin/env python3
"""
One-time OAuth setup for Google Docs access.

Run this script once to authorize the app and store the refresh token.
It will open a browser for Google OAuth consent, then save credentials
to secrets/journal_oauth.json.

Usage:
  python3 oauth_setup.py

Requires secrets/gmail_oauth.json to exist (for client_id and client_secret).
"""

import json
import os
import sys
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SECRETS_DIR = Path(__file__).parent.parent.parent.parent / "secrets"
GMAIL_CREDS = SECRETS_DIR / "gmail_oauth.json"
JOURNAL_CREDS = SECRETS_DIR / "journal_oauth.json"

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]


def main():
    if not GMAIL_CREDS.exists():
        print(f"ERROR: {GMAIL_CREDS} not found", file=sys.stderr)
        sys.exit(1)

    gmail_data = json.loads(GMAIL_CREDS.read_text())

    client_config = {
        "installed": {
            "client_id": gmail_data["client_id"],
            "client_secret": gmail_data["client_secret"],
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0)

    journal_data = {
        "client_id": gmail_data["client_id"],
        "client_secret": gmail_data["client_secret"],
        "refresh_token": creds.refresh_token,
        "access_token": creds.token,
    }

    JOURNAL_CREDS.write_text(json.dumps(journal_data, indent=2))
    os.chmod(JOURNAL_CREDS, 0o600)

    print(f"✅ Credentials saved to {JOURNAL_CREDS}")
    print("You can now run journal_doc.py commands.")


if __name__ == "__main__":
    main()
