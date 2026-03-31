---
name: job-search
description: Automated job search across multiple platforms with filtering and learning. Searches LinkedIn, Indeed, Glassdoor, and other sources based on your criteria. Delivers curated results daily or on-demand.
---

# Job Search Skill

Automates job hunting by searching multiple platforms, filtering by your preferences, and delivering curated results without the algorithm bias of paid placements.

## Configuration

Edit `job-search-config.json` to set your search parameters:

```json
{
  "searches": [
    {
      "name": "Product Manager - SF Bay",
      "keywords": ["product manager", "director of product"],
      "locations": ["San Francisco, CA", "Remote"],
      "salaryMin": 180000,
      "salaryMax": 300000,
      "company": {
        "excludeNames": ["company-to-skip"],
        "includeStage": ["Series A", "Series B", "Series C", "Mature"],
        "preferredIndustries": ["AI/ML", "SaaS", "FinTech"]
      },
      "recency": "7days"
    }
  ],
  "sources": {
    "linkedin": true,
    "indeed": true,
    "glassdoor": true,
    "angellist": true,
    "ycombinator": true,
    "techcrunch": false,
    "customRSS": []
  },
  "deliveryMode": "digest",
  "deliverySchedule": "daily",
  "deliveryTime": "09:00"
}
```

## Workflow

### 1. Search

Run job searches across configured sources (Indeed, AngelList, Y Combinator):

```bash
cd /Users/michaeltorres/.openclaw/workspace/skills/job-search
python3 scripts/search_jobs.py
```

- Queries Indeed, AngelList, and Y Combinator Jobs
- Applies filters (salary, location, company stage, keywords)
- De-duplicates across platforms
- Saves raw results as JSON in `results/`

### 2. Filter, Rank & Email

Apply learning-based filtering and send email digest:

```bash
python3 scripts/filter_and_deliver.py
```

- Calculates relevance score (0-100%) based on your criteria
- Compares against past interactions (applied, rejected jobs)
- Groups by title category
- Formats as HTML email with direct apply links
- Sends via Gmail (or configured SMTP)
- Saves filtered results for history

### Email Setup

Before running, configure email delivery:

1. Read `references/EMAIL_SETUP.md` for Gmail/SMTP configuration
2. Create `~/.openclaw/secrets/email_config.json` with credentials
3. Update `emailTo` field in `job-search-config.json`

## Learning System

Jobs you interact with train the filter:

- **Saved job** → increase weight for similar roles
- **Applied to job** → track application status
- **Rejected job** → learn what you don't want
- **Ignored job** → minor signal, might revisit later

Stored in `job-interactions.json`:

```json
{
  "jobs": {
    "linkedin_12345": {
      "title": "Director, Product",
      "company": "Acme Inc",
      "action": "applied",
      "actionDate": "2026-03-27",
      "relevanceScore": 0.92
    }
  }
}
```

## Scheduling

### On-Demand

```bash
openclaw run job-search
```

### Daily Digest (Cron)

Set up a daily job in your cron config to run at 9 AM:

```json
{
  "schedule": { "kind": "cron", "expr": "0 9 * * *", "tz": "America/Los_Angeles" },
  "payload": { "kind": "agentTurn", "message": "Run job search and deliver digest" }
}
```

## Data & Privacy

- **Stored locally:** `job-search-config.json`, `job-interactions.json`, `results/`
- **Never shared:** Your criteria, preferences, and interaction history stay private
- **History:** Keeps last 30 days of searches for trend analysis

## Limitations & To-Do

- [x] Y Combinator Jobs RSS parsing
- [x] AngelList API integration
- [x] Indeed scraping (via BeautifulSoup, rate-limited)
- [x] Email delivery (Gmail/SMTP)
- [ ] LinkedIn scraping requires auth (LinkedIn API not currently available)
- [ ] Glassdoor: Limited scraping due to bot detection; may add later
- [ ] Expand to other job boards (Greenhouse, Workable, custom job sites)
- [ ] Learning system: Track user interactions (applied, saved, rejected) to improve scores
- [ ] Custom job board support (add your own RSS feeds)
- [ ] Slack/Discord delivery option (alternative to email)

## Files

- `SKILL.md` — This file
- `job-search-config.json` — Your search configuration
- `job-interactions.json` — Learning history (auto-generated)
- `scripts/search_jobs.py` — Multi-source search
- `scripts/filter_jobs.py` — Filtering & ranking
- `scripts/deliver_digest.py` — Digest generation
- `results/` — Raw and filtered results (timestamped)

---

_This skill is a work in progress. Feedback and feature requests welcome._
