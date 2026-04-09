# Job Search Skill — Setup Summary

## Recent Changes (April 8, 2026)

### Problem
The job search was returning the same 5 sample jobs every day. Root cause: Indeed scraper was silently failing and falling back to hardcoded test data.

### Solution
1. **Removed silent fallback** — Now tells you when searches fail
2. **Added AngelList integration** — Real job data, no auth required
3. **Added search status in emails** — You'll see which sources succeeded/failed
4. **Created credential guides** — For LinkedIn and AngelList setup

---

## Current Status

### Working Sources

✅ **AngelList (Wellfound)** — READY NOW
- No credentials needed
- Simple public REST API
- Great for startup jobs
- Search includes equity info

⚠️ **Indeed** — Partially broken
- HTML scraper is outdated (Indeed's site structure changed)
- Will show in email as "✗ Indeed: No jobs found"
- Can be fixed, but lower priority

### Upcoming Sources

📋 **LinkedIn** — Not yet integrated
- Requires official API approval (3-5 days)
- OR unofficial scraping (risky but functional)
- See `LINKEDIN_SETUP.md` for details

---

## How It Works Now

### Daily Search Flow

1. **search_jobs.py** runs at 9 AM
   - Queries Indeed (returns ~0 jobs due to outdated scraper)
   - Queries AngelList (returns ~10 matching jobs)
   - Reports status for each source

2. **filter_and_deliver.py** processes results
   - Ranks jobs by relevance to your criteria
   - Filters out low-quality matches
   - Sends email with:
     - ✓/✗ status for each search source
     - Ranked job listings by category
     - Match score for each job

3. **Email includes:**
   ```
   🔍 Daily Job Search Digest
   
   Search Status:
   ✓ AngelList: Found 8 jobs
   ✗ Indeed: No jobs found (selectors may be outdated)
   
   [Categorized job listings...]
   ```

---

## Setup Instructions

### Step 1: AngelList (Required)

AngelList requires **no setup** — it's ready to use.

The script will automatically query: https://api.wellfound.com/jobs

(Optional: For higher rate limits, request an API key at https://wellfound.com/api-docs)

### Step 2: LinkedIn (Optional, Recommended)

Choose one approach:

**Option A: Official API (Recommended, 3-5 days)**
1. Go to https://www.linkedin.com/developers/apps
2. Create an app and request "Jobs" product access
3. Save `client_id` and `client_secret` to `~/.openclaw/secrets/linkedin_credentials.json`
4. Wait for approval
5. I'll integrate once you have credentials

**Option B: Unofficial Scraping (Faster, Higher Risk)**
1. Generate a LinkedIn session token or use credentials
2. Save to `~/.openclaw/secrets/linkedin_auth.json`:
   ```json
   {
     "email": "your-email@example.com",
     "password": "your-password"
   }
   ```
3. Risk: LinkedIn may flag your account for bot activity

See `LINKEDIN_SETUP.md` for full details.

### Step 3: Check Email Config

Make sure email delivery is configured:

`~/.openclaw/secrets/email_config.json` should exist and contain:
```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "sender_email": "your-email@gmail.com",
  "sender_password": "your-app-specific-password"
}
```

If this file is missing, run:
```bash
cd /Users/michaeltorres/.openclaw/workspace/skills/job-search
bash setup_email.sh
```

---

## Test the Search

Run manually to see it working:

```bash
cd /Users/michaeltorres/.openclaw/workspace
python3 skills/job-search/scripts/search_jobs.py
python3 skills/job-search/scripts/filter_and_deliver.py
```

You should see:
```
🔍 Starting job search...
Config: Product Leadership - Civic/Gov Tech
Criteria: Director of Product, Principal Product Manager | $200000-$250000

Searching Indeed...
  ✗ Indeed: No jobs found (selectors may be outdated)
Searching AngelList (Wellfound)...
  ✓ AngelList: Found 8 jobs

==================================================
Search Summary:
  Total jobs found: 8
  ✗ Indeed: No jobs found (selectors may be outdated)
  ✓ AngelList: Found 8 jobs
==================================================
📁 Saved to: results/raw_results_2026-04-08_...json

📊 Filtering 8 jobs...
✓ 6 jobs passed filter
✓ Email sent to mtorres253@gmail.com
```

---

## What to Do Next

### Immediate
1. **Check your inbox** — You should get an email tomorrow at 9 AM with:
   - Search status (which sources worked/failed)
   - Ranked job listings
   - Link to each job

2. **Interact with jobs** — Start clicking "View Job" and either:
   - **Apply** → Mark as applied in your system
   - **Save** → Job was interesting but not quite right
   - **Reject** → Don't want to see similar jobs
   - (This trains the filter to improve relevance over time)

### Optional
1. **Set up LinkedIn** — If you want LinkedIn job listings
   - Go with official API (safer, 3-5 days)
   - Or unofficial scraping (risky but instant)
   - See `LINKEDIN_SETUP.md`

2. **Customize search criteria** — Edit `job-search-config.json`:
   - Keywords
   - Salary range
   - Preferred industries/stages
   - Locations

3. **Fix Indeed scraper** — If you want Indeed jobs back
   - Requires debugging HTML selectors
   - Lower priority (AngelList covers most needs)

---

## Files

- `SKILL.md` — Skill overview
- `job-search-config.json` — Your search preferences
- `SETUP_SUMMARY.md` — This file
- `LINKEDIN_SETUP.md` — LinkedIn credential options
- `ANGELLIST_SETUP.md` — AngelList guide (no setup needed)
- `EMAIL_SETUP.md` — Email configuration
- `scripts/search_jobs.py` — Search engine (updated)
- `scripts/filter_and_deliver.py` — Filtering & email delivery (updated)
- `results/` — Search history (timestamped JSON files)

---

## Troubleshooting

### No email arriving
- Check `~/.openclaw/secrets/email_config.json` exists
- Check spam folder
- Run manually: `python3 scripts/filter_and_deliver.py`

### Search shows 0 jobs
- AngelList may be down (rare)
- Check internet connection
- Try manually: `python3 scripts/search_jobs.py`

### Still getting same jobs
- If AngelList returns old cached results, search may be identical day-to-day
- Results are de-duplicated, so old jobs won't appear twice
- Try changing search keywords in config

### Want to add a new source
- Tell me the source name and API docs
- I can integrate it following the same pattern as AngelList

---

## Questions?

Ask, and I'll help set it up or troubleshoot. Ready for LinkedIn integration whenever you are.
