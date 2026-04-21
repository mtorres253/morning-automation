# Skill Architecture & Claude Integration

## File Organization

Every skill lives in `/Users/michaeltorres/.openclaw/workspace/skills/<skill-name>/`

### Standard Structure (Job-Search Example)

```
skills/job-search/
├── SKILL.md                     # Skill definition (metadata + user docs)
├── job-search-config.json       # User configuration (keywords, locations, etc)
├── job-interactions.json        # Learning history (auto-generated)
├── sent-jobs.json              # Tracking what's been delivered
├── results/                    # Raw & filtered results (timestamped)
├── assets/                     # Resumes, cover letters (user content)
├── references/                 # Setup guides, policies, technical docs
├── scripts/                    # Executable Python scripts
│   ├── search_jobs.py         # Search logic
│   └── filter_and_deliver.py  # Filter + email delivery
└── venv/                       # Virtual environment (if used locally)
```

### Key Files Explained

1. **SKILL.md** — Controls everything about how the skill appears and works
   - Metadata: `name`, `description`
   - User-facing documentation
   - Workflow instructions
   - Limitations and TODOs
   - This is what OpenClaw reads to understand the skill

2. **Config files** (e.g., `job-search-config.json`)
   - User preferences (keywords, salary range, locations)
   - Source selection (which job boards to search)
   - Delivery settings (schedule, format, email)
   - Not controlled by SKILL.md, but referenced by scripts

3. **Scripts** (Python, shell, or any executable)
   - Core logic that actually runs
   - Can be called by cron, Lambda, or directly via CLI
   - **No direct Claude integration here** (see "When Is Claude Called?" below)
   - Self-contained: fetch data, process, deliver

---

## How Skills Are Controlled

### 1. SKILL.md as the Manifest

The **SKILL.md file is the authoritative definition** of a skill. It tells OpenClaw:
- What the skill does
- How to invoke it
- What files it uses
- Limitations and TODOs

**Example from job-search/SKILL.md:**

```markdown
# Job Search Skill

Automates job hunting by searching multiple platforms...

## Configuration

Edit `job-search-config.json` to set your search parameters...

## Workflow

### 1. Search
Run job searches across configured sources:
```bash
cd /Users/michaeltorres/.openclaw/workspace/skills/job-search
python3 scripts/search_jobs.py
```

### 2. Filter, Rank & Email
Apply learning-based filtering and send email digest:
```bash
python3 scripts/filter_and_deliver.py
```
```

**This SKILL.md doesn't hardcode the schedule.** The schedule is defined separately (see "When Is Claude Called?" below).

### 2. How the Skill Is Actually Invoked

There are **three ways** to run a skill:

#### A. Manual Invocation (You Run It Directly)

```bash
# Search for jobs
python3 ~/.openclaw/workspace/skills/job-search/scripts/search_jobs.py

# Filter and deliver
python3 ~/.openclaw/workspace/skills/job-search/scripts/filter_and_deliver.py
```

**Claude's involvement:** None. It's just a script.

#### B. Cron Job (Scheduled, Automated)

Defined in OpenClaw's cron scheduler:

```json
{
  "id": "job-search-daily",
  "name": "Job Search Daily",
  "schedule": { "kind": "cron", "expr": "0 9 * * *", "tz": "America/Los_Angeles" },
  "payload": { 
    "kind": "agentTurn",
    "message": "Run the job-search skill: execute search_jobs.py and filter_and_deliver.py, deliver results to Michael in chat"
  },
  "sessionTarget": "main"
}
```

**Claude's involvement:** OpenClaw sends Claude this message as a `systemEvent`, and Claude calls the skill via tool execution.

#### C. Lambda Function (Cloud Deployment)

AWS Lambda with EventBridge trigger:

```python
# lambda_functions/job_search_lambda.py
def lambda_handler(event, context):
    # Run the job search directly (no Claude involved)
    job_results = get_job_search_results()
    send_results_email(subject, body)
    return { 'statusCode': 200, ... }
```

**Claude's involvement:** None. Lambda runs independently on a schedule.

---

## When Is Claude Called?

### The Agent Loop

When you interact with OpenClaw in chat, here's what happens:

1. **You send a message** → Gateway receives it
2. **System prompt is built** including:
   - OpenClaw's base prompt
   - Skills snapshot (list of available skills)
   - Your workspace context (SOUL.md, USER.md, MEMORY.md, etc.)
   - Available tools (exec, read, write, web_search, cron, sessions, etc.)
3. **Claude is called** with this system prompt + your message
4. **Claude sees the skill list** and can decide to call a skill
5. **Claude reads SKILL.md** if it needs to understand how to use a skill
6. **Claude calls tools** (like `exec` to run Python scripts)
7. **Claude streams response back** to you

### Example: You Ask "Run job search"

```
YOU: "Run the job search skill and send me the results"

OPENCLAW:
  1. Builds system prompt with all available skills
  2. Calls Claude with: "User wants job search, here are available skills: [job-search, gmail-digest, morning-journal, ...]"
  3. Claude reads SKILL.md for job-search
  4. Claude sees the workflow and runs: python3 skills/job-search/scripts/search_jobs.py
  5. Claude captures output
  6. Claude runs: python3 skills/job-search/scripts/filter_and_deliver.py
  7. Claude streams results back to you
```

### What Claude Actually Sees (System Prompt Structure)

The system prompt that gets sent to Claude includes:

```
## Skills (Snapshot)

Available skills:
- job-search: Automated job search across multiple platforms...
- gmail-digest: Fetch and summarize Michael's Gmail messages...
- morning-journal: Daily journal prompt...

When a skill is needed, read its SKILL.md file from the skill directory (parent of the SKILL.md file) and follow it.
```

Then in the **Project Context** section, your workspace files are injected:

```
## /Users/michaeltorres/.openclaw/workspace/SOUL.md
# SOUL.md - Who You Are

_You're not a chatbot. You're becoming someone._

## Core Truths

**Be genuinely helpful, not performatively helpful.** Skip the "Great question!" ...
```

---

## Caching & Model Calls

### How Caching Works

OpenClaw uses **prompt caching** at the model level:

1. **System prompt is relatively stable** across calls
   - Base prompt + skills + workspace context
   - Doesn't change between messages unless you edit config/skills
   - Gets cached by the model provider (Claude's implementation)

2. **User message changes** every turn
   - This is NOT cached (it's the variable part)
   - Only the system context can be cached

3. **Cache is invalidated when:**
   - You edit SKILL.md
   - You edit SOUL.md, USER.md, MEMORY.md
   - You change agent configuration
   - You add/remove skills
   - The OpenClaw version updates

### When Claude Is Called

- **Every message you send** triggers a Claude call
- **Cron jobs** trigger Claude calls (if `kind="agentTurn"`)
- **Heartbeats** trigger Claude calls (if HEARTBEAT.md has tasks)
- **Lambda functions** do NOT call Claude (they run independently)

### Call Timing

| Event | Claude Called? | When? | Caching? |
|-------|---|---|---|
| You send a message | ✅ Yes | Immediately | Prompt cached |
| Cron job fires (agentTurn) | ✅ Yes | At scheduled time | Prompt cached |
| Cron job fires (systemEvent) | ✅ Yes | At scheduled time | Prompt cached |
| Lambda executes | ❌ No | At scheduled time | N/A |
| Manual script run | ❌ No | When you run it | N/A |

---

## Example: Job Search Flow

### Current Setup (as of April 2026)

**Trigger:** Cron job at 9 AM PDT

```json
{
  "name": "Job Search Daily",
  "schedule": { "kind": "cron", "expr": "0 9 * * *" },
  "payload": { 
    "kind": "agentTurn",
    "message": "Run the job-search skill: execute search_jobs.py and filter_and_deliver.py to fetch latest jobs and send digest"
  }
}
```

**What happens:**

1. **9:00 AM:** Cron fires, sends message to Claude
2. **Claude sees:** "Run the job-search skill"
3. **Claude reads:** `skills/job-search/SKILL.md`
4. **Claude understands:** It needs to run two Python scripts
5. **Claude executes:**
   ```bash
   python3 skills/job-search/scripts/search_jobs.py
   python3 skills/job-search/scripts/filter_and_deliver.py
   ```
6. **Scripts run:**
   - search_jobs.py: queries JSearch API, finds jobs
   - filter_and_deliver.py: deduplicates, ranks, sends email
7. **Email delivered:** Job digest arrives in your inbox
8. **Claude reports back:** "Job search completed, 10 new jobs found, email sent"
9. **No further action:** Email is in your inbox

**Where's Claude in this?** Only steps 2-4 and 8. The actual job searching (steps 5-7) is pure Python, no Claude involved.

---

## File Control Hierarchy

From highest to lowest priority:

1. **SKILL.md** — Tells OpenClaw what the skill is and how to use it
2. **Config JSON** (e.g., job-search-config.json) — User preferences for that skill
3. **Script logic** (Python) — Actual implementation
4. **Cron definition** — When and how often to run
5. **Lambda definition** — Alternative cloud deployment (no Claude)

Changing the script doesn't change the skill's interface (SKILL.md). Changing SKILL.md might require changing the script or config.

---

## Summary

| Aspect | Answer |
|--------|--------|
| **What controls a skill?** | SKILL.md (manifest) + config JSON (settings) + scripts (implementation) |
| **When is Claude called?** | On every message, cron agentTurn, or heartbeat task |
| **When is Claude NOT called?** | Manual script runs, Lambda functions, heartbeat checks (if no tasks) |
| **Is caching enabled?** | Yes, on system prompt; user messages are not cached |
| **How often is the model queried?** | Only when triggered (message, cron, heartbeat) |
| **Can scripts run without Claude?** | Yes, via manual CLI, Lambda, or standalone execution |

---

**Last updated:** April 17, 2026
**Written for:** Understanding the Lambda vs Claude vs Cron split
