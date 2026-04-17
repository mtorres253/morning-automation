---
name: job-search
description: Automated job search via JSearch API with filtering and learning. Searches across LinkedIn, Indeed, ZipRecruiter, and other job boards. Delivers curated results daily at 9 AM PDT via email.
---

# Job Search Skill

Automates job hunting by searching multiple job platforms via JSearch API, filtering by your preferences, and delivering curated results via email.

**Status:** Running on AWS Lambda (automated, no manual intervention needed)

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
        "includeStage": ["Series C", "Late Stage", "Public"],
        "preferredIndustries": ["Civic Tech", "Gov Tech", "Transportation"]
      },
      "recency": "7days"
    }
  ],
  "deliveryMode": "digest",
  "deliveryTime": "10:00"
}
```

## Workflow (Lambda Automated)

**EventBridge triggers at 9:00 AM PDT daily:**

1. **Search via JSearch API** (`search_jobs.py` equivalent in Lambda):
   - Queries JSearch API (OpenWeb Ninja's unified job board aggregator)
   - Covers: LinkedIn, Indeed, ZipRecruiter, and 100+ other job boards
   - Applies filters (salary, location, company stage, keywords)
   - De-duplicates across platforms
   - Saves raw results

2. **Filter, Rank & Email** (`filter_and_deliver.py` equivalent in Lambda):
   - Calculates relevance score (0-100%) based on your criteria
   - Tracks previously sent jobs (deduplication via `sent-jobs.json`)
   - Groups by title category
   - Formats as HTML email with direct apply links
   - Sends via AWS SES to `mtorres253@gmail.com`
   - Removes old postings (jobs not seen in 3 days)

**Expected:** Job digest email arrives in inbox at 9:00-9:05 AM PDT daily

### Professional Materials

Your resumes and cover letters are stored in `/assets/job-search/`:

- `assets/job-search/resumes.md` — Your resume(s), formatted and ready to tailor
- `assets/job-search/cover_letters.md` — Your cover letter templates

When applying to jobs, the skill can reference these files to:
- Tailor cover letters for specific roles
- Extract relevant experience for custom applications
- Maintain consistency across all applications

## Credentials (Lambda)

**JSearch API:** Set as Lambda environment variable `JSEARCH_API_KEY`
- Provided by OpenWeb Ninja via RapidAPI
- Covers 100+ job boards including LinkedIn, Indeed, ZipRecruiter

**Email delivery:** Uses AWS SES (Simple Email Service)
- Lambda has IAM permissions to send via SES
- Sends formatted HTML digests to `mtorres253@gmail.com`

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

## Manual Testing (Local)

If you need to test locally:

```bash
cd /Users/michaeltorres/.openclaw/workspace/skills/job-search
python3 scripts/search_jobs.py       # Search for jobs
python3 scripts/filter_and_deliver.py # Filter + deliver via SMTP
```

Requires `job-search-config.json` and `email_config.json` locally configured.

## Data & Privacy

- **Stored locally:** `job-search-config.json`, `job-interactions.json`, `results/`
- **Never shared:** Your criteria, preferences, and interaction history stay private
- **History:** Keeps last 30 days of searches for trend analysis

## Data & Privacy

- **Stored:** `job-search-config.json`, `job-interactions.json`, `sent-jobs.json`, `results/` (local only, not in Lambda)
- **Never shared:** Your criteria, preferences, and interaction history stay private
- **History:** Keeps tracking of sent jobs to prevent duplicates
- **Cleanup:** Jobs disappear from listings automatically after 3 days of no posts

## Notes

- **JSearch API:** Covers 100+ job boards; rate-limited by RapidAPI
- **CloudWatch logs:** Check Lambda CloudWatch logs if digest doesn't arrive
- **Deduplication:** Tracks sent jobs across days to prevent sending the same job multiple times
- **Job removal:** Postings older than 3 days are automatically removed from tracking

---

**Schedule:** Daily at 9:00 AM PDT (via EventBridge + Lambda)  
**Last updated:** April 17, 2026
