#!/usr/bin/env python3
"""
fetch_digest.py - Fetch Gmail messages from the last 24 hours and print a summary-ready payload.
Uses OAuth 2.0 with token caching. Outputs JSON to stdout: list of {subject, from, date, snippet}
"""

import json
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

CREDS_PATH = Path.home() / '.openclaw' / 'workspace' / 'secrets' / 'gmail_oauth.json'

def load_or_refresh_token():
    """Load cached credentials and refresh access token if needed."""
    if not CREDS_PATH.exists():
        print(f"❌ ERROR: Gmail credentials not found at {CREDS_PATH}", file=sys.stderr)
        sys.exit(1)
    
    with open(CREDS_PATH) as f:
        creds = json.load(f)
    
    # Refresh the access token
    data = urllib.parse.urlencode({
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
        "refresh_token": creds["refresh_token"],
        "grant_type": "refresh_token"
    }).encode()
    
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    
    try:
        with urllib.request.urlopen(req) as resp:
            response = json.loads(resp.read())
            if "access_token" not in response:
                print(f"❌ ERROR: No access_token in response: {response}", file=sys.stderr)
                sys.exit(1)
            return response["access_token"]
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"❌ ERROR: Failed to refresh token: {e.code} {e.reason}", file=sys.stderr)
        print(f"Details: {body}", file=sys.stderr)
        sys.exit(1)

def gmail_get(path, token):
    """Make authenticated request to Gmail API."""
    url = f"https://gmail.googleapis.com/gmail/v1/{path}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def header_val(headers, name):
    """Extract header value by name (case-insensitive)."""
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""

def main():
    """Fetch emails from last 24 hours."""
    # Get access token (refresh if needed)
    token = load_or_refresh_token()
    
    # Search for messages from last 24 hours
    since = int((datetime.now(timezone.utc) - timedelta(hours=24)).timestamp())
    query = f"after:{since}"
    encoded_query = urllib.parse.urlencode({"q": query, "maxResults": 50})

    try:
        result = gmail_get(f"users/me/messages?{encoded_query}", token)
        messages = result.get("messages", [])

        emails = []
        for msg in messages:
            detail = gmail_get(
                f"users/me/messages/{msg['id']}?format=metadata&metadataHeaders=Subject&metadataHeaders=From&metadataHeaders=Date",
                token
            )
            headers = detail.get("payload", {}).get("headers", [])
            emails.append({
                "subject": header_val(headers, "Subject") or "(no subject)",
                "from": header_val(headers, "From"),
                "date": header_val(headers, "Date"),
                "snippet": detail.get("snippet", "")
            })

        print(json.dumps(emails, indent=2))
    
    except urllib.error.HTTPError as e:
        body = e.read().decode() if hasattr(e, 'read') else str(e)
        print(f"❌ ERROR: Gmail API error: {e.code} {e.reason}", file=sys.stderr)
        print(f"Details: {body}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
