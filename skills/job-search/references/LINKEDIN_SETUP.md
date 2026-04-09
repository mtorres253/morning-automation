# LinkedIn Job Search Setup

LinkedIn's official API is restricted and requires business partnership approval. However, there are a few practical options:

## Option 1: LinkedIn Official API (Recommended, but Limited)

**Requirements:**
- LinkedIn Developer Account (free)
- Company verification (may take a few days)
- Business use case approval

**Steps:**

1. Go to https://www.linkedin.com/developers/apps
2. Click "Create app"
3. Fill in:
   - App name: "Job Search Tool" (or similar)
   - LinkedIn Page: Select your profile or company
   - App logo: Upload a simple image
   - Legal agreement: Check the box
4. Click "Create app"
5. Go to the "Auth" tab and find your credentials:
   - **Client ID**
   - **Client Secret**

6. Request access to the **Jobs API**:
   - Go to "Products" → "Request access"
   - Select "Jobs" and explain your use case
   - Wait for approval (usually 1-3 days)

7. Once approved, save credentials to `~/.openclaw/secrets/linkedin_credentials.json`:

```json
{
  "client_id": "YOUR_CLIENT_ID_HERE",
  "client_secret": "YOUR_CLIENT_SECRET_HERE",
  "redirect_uri": "http://localhost:3000/callback"
}
```

**Limitations:**
- API access is restricted and may require a LinkedIn business partner agreement
- Rate limits apply (typically 100 requests/day for free tier)
- May not include all job postings

## Option 2: Web Scraping (Unofficial, Higher Risk)

**Note:** LinkedIn's Terms of Service prohibit scraping. Use at your own risk.

If you go this route, tools like **Selenium** or **Playwright** can:
1. Log in with your credentials
2. Perform authenticated searches
3. Extract job listings

**Tools:**
- `linkedin-api` (Python package) — unofficial but functional
- `playwright` — browser automation with Python

**Setup (if you choose this):**

```bash
pip install linkedin-api
```

Then store your LinkedIn credentials in `~/.openclaw/secrets/linkedin_auth.json`:

```json
{
  "email": "your-email@example.com",
  "password": "your-password"
}
```

**⚠️ Risks:**
- LinkedIn may block your account for scraping
- Your password is stored locally (use a throwaway password or app-specific password if LinkedIn supports it)
- No guarantee of uptime or accuracy

## Option 3: Third-Party Job Aggregators (Safest)

Instead of scraping LinkedIn directly, use job aggregators that legally index LinkedIn jobs:

- **Indeed** (already integrated) — indexes LinkedIn jobs
- **Adzuna** — aggregator with free API (requires key)
- **JSearch** (Rapid API) — indexes multiple job boards
- **RapidAPI Job Search** — various job APIs in one marketplace

These are safer and legal.

---

## Recommendation

**For now:** Skip LinkedIn and focus on **AngelList + Y Combinator**, which are easier and don't have legal risks.

**If you really want LinkedIn:** Request the official API (Option 1). It takes a few days but is the safest approach.

**For scraping (not recommended):** Use `linkedin-api` package if you're comfortable with TOS risk, but expect account issues over time.
