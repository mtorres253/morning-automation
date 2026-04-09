# AngelList Job Search Setup

AngelList (now part of Wellfound) provides a simple public API for job listings. This is one of the easiest integrations for sourcing startup jobs.

## Getting an AngelList API Token

AngelList's API is **free and public** — no authentication required for basic job search queries.

However, if you want higher rate limits or advanced features, you can request an API key:

### Step 1: Create a Wellfound Account (if you don't have one)

1. Go to https://wellfound.com/
2. Sign up with email or LinkedIn
3. Complete your profile (optional, but recommended)

### Step 2: Get API Access

AngelList's **Jobs API** is public and doesn't require authentication for basic searches.

**Public API endpoint:**
```
https://api.wellfound.com/jobs
```

**No token needed** — just make requests directly.

### Step 3: (Optional) Request Higher Rate Limits

If you want higher rate limits or dedicated support:

1. Go to https://wellfound.com/api-docs
2. Click "Request API Access"
3. Fill out the form:
   - App name: "Job Search Tool"
   - Use case: "Aggregating job listings for personal job search"
   - Expected volume: "50-100 requests/day"
4. Submit and wait for approval (usually instant or 1-2 days)

Once approved, you'll receive:
- **API Key** (optional, for higher limits)
- Rate limit: typically 1000 requests/day for free tier

### Step 4: Store Credentials (if you got an API key)

Save to `~/.openclaw/secrets/angellist_credentials.json`:

```json
{
  "api_key": "YOUR_API_KEY_HERE",
  "base_url": "https://api.wellfound.com"
}
```

If you don't have an API key, the script can still work with the public endpoint (no credentials needed).

## AngelList Job Search API Reference

**Endpoint:**
```
GET https://api.wellfound.com/jobs
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Keywords (e.g., "product manager") |
| `location` | string | City or remote (e.g., "San Francisco" or "Remote") |
| `job_type` | string | full_time, part_time, contract |
| `equity_min` | number | Minimum equity % |
| `funding_stage` | string | seed, series-a, series-b, etc. |
| `limit` | number | Results per page (max 100) |
| `page` | number | Page number for pagination |

**Example Request:**
```bash
curl "https://api.wellfound.com/jobs?query=product%20manager&location=San%20Francisco&job_type=full_time&limit=50"
```

**Example Response:**
```json
{
  "jobs": [
    {
      "id": "abc123",
      "title": "Product Manager",
      "company": "Acme Inc",
      "location": "San Francisco, CA",
      "salary_min": 150000,
      "salary_max": 200000,
      "equity": "0.5-1.0%",
      "job_url": "https://wellfound.com/jobs/abc123",
      "description": "We're hiring a product manager...",
      "posted_at": "2026-04-01T10:00:00Z"
    }
  ],
  "pagination": {
    "total": 127,
    "page": 1,
    "per_page": 50
  }
}
```

## Integration Notes

- **No auth required** for basic searches
- **Free tier:** 1000 requests/day (usually plenty)
- **Equity data available** — useful for startup filtering
- **Funding stage filters** — find pre-seed, Series A, B, C, etc.
- **Up-to-date listings** — AngelList/Wellfound is actively used by startups

## Implementation

To use this in the job search script:

```python
import requests

def search_angellist(keywords, location, salary_min, salary_max):
    """Search AngelList jobs API."""
    url = "https://api.wellfound.com/jobs"
    params = {
        "query": " ".join(keywords),
        "location": location,
        "job_type": "full_time",
        "limit": 50
    }
    
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    
    jobs = []
    for job in response.json().get("jobs", []):
        # Filter by salary if available
        if job.get("salary_min") and job.get("salary_min") < salary_min:
            continue
        
        jobs.append({
            "source": "angellist",
            "jobId": f"angellist_{job['id']}",
            "title": job["title"],
            "company": job["company"],
            "location": job["location"],
            "salary": f"${job.get('salary_min', 'N/A')} - ${job.get('salary_max', 'N/A')}",
            "equity": job.get("equity", "Not specified"),
            "snippet": job.get("description", "")[:200],
            "url": job["job_url"],
            "scrapedAt": datetime.utcnow().isoformat()
        })
    
    return jobs
```

---

## Summary

✅ **AngelList is the easiest to integrate:**
- No authentication required
- Simple REST API
- Free and legal
- Great for startup jobs (especially your interests in civic tech, drone tech, etc.)

**Recommended next step:** Use AngelList without an API key (it works fine). If you hit rate limits, then request an API key.
