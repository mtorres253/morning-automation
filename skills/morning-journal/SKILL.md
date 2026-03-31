---
name: morning-journal
description: Daily morning reflection and planning journal. Prompts Michael each morning at 8 AM to share what he's grateful for, his tasks for the day, and which personal strengths he'll need. Records responses in a Google Doc ("Michael's Journal") with date/day via Civic. After Michael responds, reads the doc and suggests action items, also reminding him what he was grateful for. Use when: delivering the morning journal prompt, recording a journal response, reviewing the journal, or suggesting daily action items.
---

# Morning Journal

Daily reflection + planning loop. Runs at 8 AM via cron. Uses Civic for Google Docs access.

## ⚠️ Policy

Before any external action, read and follow `references/civic-policy.md`.
Key rule: never delete or overwrite journal entries. Always append. Always confirm before sending anything externally.

## Civic Setup

Credentials are in `~/.openclaw/secrets/civic_credentials.json`.
All Google Docs operations use Civic via:
```bash
cd /Users/michaeltorres/.openclaw/workspace/skills/openclaw-civic-skill
CIVIC_URL="..." CIVIC_TOKEN="..." npx tsx civic-tool-runner.ts --call <tool> --args '<json>'
```

Load credentials from the secrets file — do not hardcode them.

## Redis Caching

Journal entries, action items, and past responses are cached in Redis (24h TTL for entries, 7d for response history). This speeds up future prompts and reduces Google Docs API calls.

**Setup:**
```bash
# Install Redis
brew install redis

# Start Redis
redis-server

# Test the cache
python3 skills/morning-journal/scripts/redis_cache.py
```

**How it works:**
- After appending an entry to Google Docs, cache it immediately
- Next session can fetch recent entries from Redis without hitting Docs API
- Action items cached separately for fast retrieval
- Cache expires after 24h (entries) or 7d (history) — always fresh data

## State File

`skills/morning-journal/state.json` stores the Google Doc ID:
```json
{ "doc_id": "1BxiM..." }
```

## Workflow

### Phase 1: Morning Prompt (8:00 AM cron)

Deliver this prompt to Michael in chat:

> Good morning, Michael! 🌿 Time for your daily reflection.
>
> Please share:
> 1. **What are you grateful for today?**
> 2. **What are your tasks for the day?**
> 3. **Which of your strengths will you need to get them done?**

Keep it warm and brief. No lists, no forms — just the three questions.

### Phase 2: Recording the Response

When Michael replies with his journal response:

1. Parse his message into three parts: gratitude, tasks, strengths
   - Be flexible — he may not label them; infer from context

2. Read `skills/morning-journal/state.json` to get the `doc_id`

3. Read the current doc content via Civic:
   ```
   tool: google-drive-get_drive_file_content
   args: {"file_id": "<doc_id>", "mime_type": "text/plain"}
   ```

4. Append the new entry by updating the doc via Civic:
   ```
   tool: google-drive-update_drive_file_content  (if available)
   ```
   If no update tool is available, use `google-gmail-draft_gmail_message` as fallback to capture the entry, then notify Michael.

   Entry format to append:
   ```
   ---
   📅 <Day, Month DD YYYY>

   🙏 Grateful for:
   <gratitude>

   ✅ Tasks for the day:
   <tasks>

   💪 Strengths I'll draw on:
   <strengths>
   ```

5. Read the full doc to surface recent entries for review

### Phase 3: Review & Action Items

After appending, deliver a response that:

1. **Acknowledges** what he's grateful for (1 warm sentence)
2. **Suggests action items** — specific, concrete next steps based on his tasks and strengths
3. **Invites him to confirm or swap** any suggestions

See `references/action-item-guide.md` for how to generate good action items.

## Cron Schedule

The 8 AM prompt runs as a daily cron job (America/Los_Angeles).
See `references/cron-setup.md` for setup instructions.
