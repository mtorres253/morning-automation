# Job Search Skill — Behavior & Flow

## Email Behavior (Updated)

**ALWAYS sends an email** — Even if:
- Searches fail (shows status + reasons)
- No jobs found (shows status + message)
- All jobs already sent (shows status + note)
- Jobs found (shows jobs + status)

## Daily Flow

### 9:00 AM: Search Phase
```
search_jobs.py runs:
├── Queries Indeed (currently fails: 403 Forbidden)
├── Queries Alternative source (currently empty: not configured)
└── Outputs: raw_results_TIMESTAMP.json with searchStatus
```

### 9:02 AM: Filter & Deliver Phase
```
filter_and_deliver.py runs:
├── Loads raw search results
├── Filters out sample/fallback jobs (keeps only real results)
├── Filters to only NEW jobs (removes previously sent)
├── Ranks remaining jobs by relevance
├── ALWAYS sends email with:
│   ├── Search Status (which sources worked/failed)
│   ├── Job listings (if found)
│   └── OR message (if no jobs found)
└── Updates sent-jobs.json tracking
```

## Email Content Based on Scenario

### Scenario A: Jobs Found
```
Subject: 🔍 Daily Job Search Digest — Tuesday, April 09

Content:
├── Header: "Found 3 matching jobs"
├── Search Status: 
│   ✓ AngelList: Found 5 jobs
├── Job Listings (by category):
│   ├── Director of Product (1)
│   │   └── [Job details + link]
│   └── Principal Product Manager (2)
│       ├── [Job details + link]
│       └── [Job details + link]
└── Footer: "This is an automated..."
```

### Scenario B: No New Jobs (All Already Sent)
```
Subject: 🔍 Daily Job Search Digest — Tuesday, April 09

Content:
├── Header: "Found 0 matching jobs"
├── Search Status:
│   ✓ AngelList: Found 5 jobs
├── No Jobs Message: "ℹ️ No matching jobs found today. Check back tomorrow..."
└── Footer
```

### Scenario C: Searches Failed, No Jobs Found
```
Subject: 🔍 Daily Job Search Digest — Tuesday, April 09

Content:
├── Header: "Found 0 matching jobs"
├── Search Status:
│   ✗ Indeed: No jobs found (selectors may be outdated)
│   ⚠️  No additional source configured yet
├── No Jobs Message: "ℹ️ No matching jobs found today. Check back tomorrow..."
└── Footer
```

### Scenario D: Mixed Success
```
Subject: 🔍 Daily Job Search Digest — Tuesday, April 09

Content:
├── Header: "Found 2 matching jobs"
├── Search Status:
│   ✓ LinkedIn: Found 8 jobs
│   ✗ Indeed: No jobs found (blocked)
├── Job Listings (2 new jobs from LinkedIn):
│   └── [Job details]
└── Footer
```

## Key Rules

1. **Always send email** — No exceptions
2. **Show search status** — Every email shows which sources worked/failed
3. **Only new jobs** — Never resend the same job twice
4. **Only current jobs** — Jobs that disappear are removed from future emails
5. **No sample data** — Only real search results are included

## How Job Deduplication Works

### First Run (Day 1)
```
Search finds: Job A, Job B, Job C
Email sent: [A, B, C]
sent-jobs.json: {A, B, C}
```

### Second Run (Day 2)
```
Search finds: Job A, Job B, Job D
New jobs: [D]  (A and B already sent)
Email sent: [D]
sent-jobs.json: {A, B, C, D}
```

### Third Run (Day 3) - Job A Disappears
```
Search finds: Job B, Job D, Job E
New jobs: [E]  (B and D already sent, A removed from tracking)
Email sent: [E]
sent-jobs.json: {B, D, E}
```

## Status Icons in Email

- **✓** (Green) — Search successful, jobs found
- **✗** (Red) — Search failed, reason provided
- **⚠️** (Yellow) — Warning or partial success

## When You Get Each Type of Email

| Condition | Email? | Content |
|-----------|--------|---------|
| Jobs found + not sent before | ✅ Yes | Jobs + status |
| Jobs found + all already sent | ✅ Yes | Status + "no new jobs" message |
| No jobs found | ✅ Yes | Status + "no matching jobs" message |
| Search fails completely | ✅ Yes | Status + failure reasons |
| Mixed success/failure | ✅ Yes | Status (both) + any jobs found |

## Customization

To adjust behavior, edit:
- `job-search-config.json` — Search criteria (keywords, salary, locations)
- `job-interactions.json` — Learning history (applied, rejected, saved jobs)
- Cron schedule — When email sends (currently 9 AM PDT daily)

## Troubleshooting

**Q: Why did I get an email with no jobs?**
A: Searches ran but found 0 matches OR all matches already sent. Check the Search Status section to see what happened.

**Q: Why do I see old jobs?**
A: You shouldn't. Check sent-jobs.json to see what's been sent. If a job reappears, it was probably reposted.

**Q: When will I get jobs?**
A: Once you set up LinkedIn or another source (currently nothing is configured).

**Q: Can I customize which jobs I see?**
A: Yes, edit job-search-config.json with different keywords, salary ranges, locations, or industries.
