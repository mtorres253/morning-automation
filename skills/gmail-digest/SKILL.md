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

Civic credentials: `/Users/michaeltorres/.openclaw/secrets/civic_credentials.json`
Fields: `mcp_url`, `access_token`

Legacy OAuth script (`skills/gmail-digest/scripts/fetch_digest.py`) still works as fallback if Civic is unavailable.

## Workflow

### Primary: Civic

1. Search Gmail for messages from the last 24 hours:
   ```bash
   cd /Users/michaeltorres/.openclaw/workspace/skills/openclaw-civic-skill
   CIVIC_URL="<from secrets>" CIVIC_TOKEN="<from secrets>" \
   npx tsx civic-tool-runner.ts --call google-gmail-search_gmail_messages \
     --args '{"query": "newer_than:1d", "max_results": 50}'
   ```

2. Batch fetch message content:
   ```
   tool: google-gmail-get_gmail_messages_content_batch
   args: {"message_ids": [...]}
   ```

3. Group and summarize by category (Job Alerts, Events, Personal, Newsletters, etc.)

4. Deliver as a scannable digest — bullets, grouped, no walls of text.

### Fallback: Legacy Script

If Civic tools fail or return an auth error:
```bash
cd /Users/michaeltorres/.openclaw/workspace
python3 skills/gmail-digest/scripts/fetch_digest.py
```

## Notes

- Civic tokens expire after ~30 days — if you get 401 errors, Michael needs to regenerate at nexus.civic.com
- Never expose email content verbatim in public channels
- Flag urgent items (replies needed, calendar events) prominently at the top of the digest
