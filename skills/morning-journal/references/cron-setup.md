# Cron Setup

The morning journal prompt runs as a daily cron job at 8:00 AM Pacific.

## Cron Job Definition

```json
{
  "name": "Morning Journal Prompt",
  "schedule": { "kind": "cron", "expr": "0 8 * * *", "tz": "America/Los_Angeles" },
  "payload": {
    "kind": "systemEvent",
    "text": "Run the morning-journal skill: deliver the daily reflection prompt to Michael in chat. Ask him what he's grateful for, his tasks for the day, and which strengths he'll need."
  },
  "sessionTarget": "main"
}
```

## To Create the Cron Job

Use the `cron` tool with `action: add` and the job definition above.

## Notes

- sessionTarget must be "main" for systemEvent payloads
- The review phase (Phase 2 + 3) is triggered by Michael's response in chat, not a separate cron job
