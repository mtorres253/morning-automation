# JSearch API Setup (Recommended Alternative)

**JSearch by OpenWeb Ninja** is a comprehensive job search API that indexes **LinkedIn, Indeed, Glassdoor, ZipRecruiter, Google for Jobs, and 1000+ other job boards**. It's legal, reliable, and requires no approval process.

## Why JSearch is Better Than Scraping

✅ **Legal** — Officially published API, no Terms of Service violations  
✅ **Instant** — No waiting for approval (5 minutes to set up)  
✅ **Reliable** — Includes LinkedIn jobs + many other sources  
✅ **Free** — Free tier with generous limits (plenty for daily digests)  
✅ **No Account Risk** — Won't get your LinkedIn account blocked  
✅ **Most Maintained** — Most comprehensive and actively updated option available

---

## Step 1: Sign Up for RapidAPI

1. Go to https://rapidapi.com/auth/sign-up
2. Sign up with email, GitHub, or Google (free)
3. Verify your email

## Step 2: Find JSearch API (OpenWeb Ninja)

1. Visit https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
2. Click "Subscribe" button
3. Select **Free Plan**
4. Click "Subscribe to Test"

## Step 3: Get Your API Key

1. Go to https://rapidapi.com/settings/applications
2. Find "default" application
3. Copy the **API Key** (labeled `X-RapidAPI-Key`)
4. Also copy the **Host**: `jsearch.p.rapidapi.com`

## Step 4: Save Credentials

Create `~/.openclaw/secrets/jsearch_credentials.json`:

```bash
mkdir -p ~/.openclaw/secrets
```

Then create the file with:

```json
{
  "api_key": "YOUR_API_KEY_HERE",
  "api_host": "jsearch.p.rapidapi.com",
  "api_url": "https://jsearch.p.rapidapi.com/search"
}
```

Replace `YOUR_API_KEY_HERE` with your actual key from step 3.

## Step 5: Tell Me You're Ready

Once you've saved the credentials, let me know and I'll integrate JSearch into the job search script.

---

## JSearch API Reference

### Endpoint
```
GET https://jsearch.p.rapidapi.com/search
```

### Query Parameters

| Parameter | Type | Example |
|-----------|------|---------|
| `query` | string | "product manager" |
| `page` | number | 1 |
| `num_pages` | number | 1 (max 5) |
| `date_posted` | string | "last_7_days", "last_month", "last_3_months" |
| `remote_jobs_only` | boolean | true |
| `employment_type` | string | "FULLTIME" |
| `job_title` | string | "Director" |
| `job_category` | string | "Business_and_Management" |
| `country` | string | "US" |
| `is_remote` | boolean | true |

### Headers

```
X-RapidAPI-Key: YOUR_API_KEY
X-RapidAPI-Host: jsearch.p.rapidapi.com
```

### Example Request

```python
import requests

url = "https://jsearch.p.rapidapi.com/search"

querystring = {
    "query": "product manager San Francisco",
    "page": "1",
    "num_pages": "1",
    "date_posted": "last_7_days",
    "employment_type": "FULLTIME",
    "country": "US"
}

headers = {
    "X-RapidAPI-Key": "YOUR_API_KEY",
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)
print(response.json())
```

### Example Response

```json
{
  "data": [
    {
      "job_id": "abc123",
      "job_title": "Director of Product",
      "employer_name": "Acme Corp",
      "job_location": "San Francisco, CA",
      "job_country": "US",
      "job_employment_type": "FULLTIME",
      "job_posting_date": "2026-04-01T10:00:00Z",
      "job_salary_currency": "USD",
      "job_salary_max": 250000,
      "job_salary_min": 200000,
      "job_salary_period": "YEARLY",
      "job_description": "We're looking for a Director of Product...",
      "job_apply_link": "https://company.com/jobs/123",
      "job_required_experience": "5+ years"
    }
  ]
}
```

---

## Free Tier Limits

- **Free tier** provides generous limits for job searches
- Plenty for daily digest at 9 AM
- If you need more: upgrade to paid tier ($25/month for higher limits)

---

## Advantages Over LinkedIn Scraping

| Aspect | LinkedIn Scraping | JSearch API |
|--------|-------------------|------------|
| **Legal** | ❌ Violates ToS | ✅ Official API |
| **Account Risk** | ⚠️ May be blocked | ✅ No risk |
| **Setup Time** | 5 mins | 5 mins |
| **LinkedIn Jobs** | ✅ Yes | ✅ Yes |
| **Other Sources** | ❌ No | ✅ Indeed, Glassdoor, 1000+ more |
| **Salary Data** | ⚠️ Limited | ✅ Good coverage |
| **Free Tier** | N/A | ✅ 100 req/month |
| **Approval Wait** | N/A | ✅ Instant |
| **Reliability** | ⚠️ Site changes break it | ✅ Stable API |

---

## Next Steps

1. Sign up for RapidAPI (5 minutes)
2. Subscribe to JSearch free plan (1 click)
3. Copy API key and host
4. Create `~/.openclaw/secrets/jsearch_credentials.json`
5. Tell me you're ready
6. I integrate it into the search script
7. Tomorrow's email includes real LinkedIn + other job board listings

---

## Questions?

- **"Is this legal?"** — Yes, JSearch is a published API by Rapid API
- **"Will I get blocked?"** — No, it's legitimate
- **"How many jobs will I get?"** — Typically 5-20 per day, depending on criteria
- **"Can I upgrade later?"** — Yes, seamlessly
- **"What if I hit the limit?"** — Upgrade to paid tier or I can add another source

Let me know when you've set up the API key!
