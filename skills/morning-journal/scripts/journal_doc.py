#!/usr/bin/env python3
"""
Google Docs journal helper for morning-journal skill.

Usage:
  journal_doc.py create                        → creates "Michael's Journal" doc, prints doc_id
  journal_doc.py append <date> <entry_json>   → appends a dated entry to the doc
  journal_doc.py read                          → prints the full doc text (for review)
  journal_doc.py get_id                        → prints stored doc_id (from state file)
"""

import sys
import json
import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SECRETS_PATH = Path(__file__).parent.parent.parent.parent / "secrets" / "journal_oauth.json"
STATE_PATH = Path(__file__).parent.parent / "state.json"

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]


def load_creds():
    data = json.loads(SECRETS_PATH.read_text())
    creds = Credentials(
        token=data.get("access_token"),
        refresh_token=data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=data["client_id"],
        client_secret=data["client_secret"],
        scopes=SCOPES,
    )
    if not creds.valid:
        creds.refresh(Request())
        data["access_token"] = creds.token
        SECRETS_PATH.write_text(json.dumps(data, indent=2))
    return creds


def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {}


def save_state(state):
    STATE_PATH.write_text(json.dumps(state, indent=2))


def create_doc(creds):
    drive = build("drive", "v3", credentials=creds)
    docs = build("docs", "v1", credentials=creds)

    # Create the doc
    doc = docs.documents().create(body={"title": "Michael's Journal"}).execute()
    doc_id = doc["documentId"]

    # Insert header
    docs.documents().batchUpdate(
        documentId=doc_id,
        body={
            "requests": [
                {
                    "insertText": {
                        "location": {"index": 1},
                        "text": "Michael's Journal\n\n",
                    }
                },
                {
                    "updateParagraphStyle": {
                        "range": {"startIndex": 1, "endIndex": 18},
                        "paragraphStyle": {"namedStyleType": "HEADING_1"},
                        "fields": "namedStyleType",
                    }
                },
            ]
        },
    ).execute()

    state = load_state()
    state["doc_id"] = doc_id
    save_state(state)

    print(doc_id)
    return doc_id


def append_entry(creds, date_str, entry):
    state = load_state()
    doc_id = state.get("doc_id")
    if not doc_id:
        print("ERROR: No doc_id found. Run 'create' first.", file=sys.stderr)
        sys.exit(1)

    docs = build("docs", "v1", credentials=creds)

    # Build entry text
    gratitude = entry.get("gratitude", "")
    tasks = entry.get("tasks", "")
    strengths = entry.get("strengths", "")

    text = (
        f"\n---\n"
        f"📅 {date_str}\n\n"
        f"🙏 Grateful for:\n{gratitude}\n\n"
        f"✅ Tasks for the day:\n{tasks}\n\n"
        f"💪 Strengths I'll draw on:\n{strengths}\n"
    )

    # Get current end index
    doc = docs.documents().get(documentId=doc_id).execute()
    end_index = doc["body"]["content"][-1]["endIndex"] - 1

    docs.documents().batchUpdate(
        documentId=doc_id,
        body={
            "requests": [
                {
                    "insertText": {
                        "location": {"index": end_index},
                        "text": text,
                    }
                }
            ]
        },
    ).execute()

    print(f"Entry appended for {date_str}")


def read_doc(creds):
    state = load_state()
    doc_id = state.get("doc_id")
    if not doc_id:
        print("ERROR: No doc_id found. Run 'create' first.", file=sys.stderr)
        sys.exit(1)

    docs = build("docs", "v1", credentials=creds)
    doc = docs.documents().get(documentId=doc_id).execute()

    text = ""
    for element in doc["body"]["content"]:
        if "paragraph" in element:
            for run in element["paragraph"].get("elements", []):
                text += run.get("textRun", {}).get("content", "")
    print(text)


def get_id():
    state = load_state()
    doc_id = state.get("doc_id")
    if doc_id:
        print(doc_id)
    else:
        print("ERROR: No doc_id stored.", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "get_id":
        get_id()
        return

    creds = load_creds()

    if cmd == "create":
        create_doc(creds)
    elif cmd == "append":
        if len(sys.argv) < 4:
            print("Usage: journal_doc.py append <date> <entry_json>", file=sys.stderr)
            sys.exit(1)
        date_str = sys.argv[2]
        entry = json.loads(sys.argv[3])
        append_entry(creds, date_str, entry)
    elif cmd == "read":
        read_doc(creds)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
