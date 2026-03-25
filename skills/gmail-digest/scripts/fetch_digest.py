#!/usr/bin/env python3
"""
fetch_digest.py - Fetch Gmail messages from the last 24 hours and print a summary-ready payload.
Outputs JSON to stdout: list of {subject, from, date, snippet}
"""

import json
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone

CREDS_PATH = "/Users/michaeltorres/.openclaw/workspace/secrets/gmail_oauth.json"

def get_access_token(creds):
    data = urllib.parse.urlencode({
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
        "refresh_token": creds["refresh_token"],
        "grant_type": "refresh_token"
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["access_token"]

def gmail_get(path, token):
    url = f"https://gmail.googleapis.com/gmail/v1/{path}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def header_val(headers, name):
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""

def main():
    with open(CREDS_PATH) as f:
        creds = json.load(f)

    token = get_access_token(creds)
    since = int((datetime.now(timezone.utc) - timedelta(hours=24)).timestamp())
    query = f"after:{since}"
    encoded_query = urllib.parse.urlencode({"q": query, "maxResults": 50})

    result = gmail_get(f"users/me/messages?{encoded_query}", token)
    messages = result.get("messages", [])

    emails = []
    for msg in messages:
        detail = gmail_get(f"users/me/messages/{msg['id']}?format=metadata&metadataHeaders=Subject&metadataHeaders=From&metadataHeaders=Date", token)
        headers = detail.get("payload", {}).get("headers", [])
        emails.append({
            "subject": header_val(headers, "Subject") or "(no subject)",
            "from": header_val(headers, "From"),
            "date": header_val(headers, "Date"),
            "snippet": detail.get("snippet", "")
        })

    print(json.dumps(emails, indent=2))

if __name__ == "__main__":
    main()
