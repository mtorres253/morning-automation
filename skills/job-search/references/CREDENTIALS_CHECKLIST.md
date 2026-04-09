# Credentials Checklist

## ✅ Ready (No Setup Needed)

- **AngelList** — Public API, no credentials required

## 📧 Email Delivery

**Status:** Should already be set up

**File:** `~/.openclaw/secrets/email_config.json`

**Required fields:**
```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "sender_email": "your-email@gmail.com",
  "sender_password": "your-app-password"
}
```

**How to get Gmail app password:**
1. Go to https://myaccount.google.com/security
2. Enable 2-factor authentication if not already done
3. Go to "App passwords"
4. Select Mail + Mac (or your platform)
5. Copy the 16-character password
6. Use that as `sender_password` above

---

## 📌 LinkedIn (Optional)

**Current Status:** Not integrated

**Choose one option:**

### Option A: Official API (Recommended)

**Time required:** 3-5 days (waiting for approval)

**Credentials file:** `~/.openclaw/secrets/linkedin_credentials.json`

```json
{
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "redirect_uri": "http://localhost:3000/callback"
}
```

**How to get them:**
1. Visit https://www.linkedin.com/developers/apps
2. Click "Create app"
3. Fill in app details
4. Request access to "Jobs" product
5. Wait for approval
6. Find credentials in app's "Auth" tab

**Pros:**
- Legal, official partnership
- Stable and reliable
- No account risk

**Cons:**
- Takes 3-5 days for approval
- Rate limits (typically 100 req/day free tier)

---

### Option B: Unofficial Scraping (Faster, Riskier)

**Time required:** Instant

**Credentials file:** `~/.openclaw/secrets/linkedin_auth.json`

```json
{
  "email": "your-email@linkedin.com",
  "password": "your-password"
}
```

**How to set up:**
1. Use your regular LinkedIn email and password
2. OR create a throwaway LinkedIn account
3. Save credentials to file above

**Pros:**
- Works immediately
- Access to full LinkedIn job listings
- No approval wait

**Cons:**
- Violates LinkedIn's Terms of Service
- Account may be flagged or banned
- Less reliable (LinkedIn changes their site frequently)
- Password stored locally (security risk)

**⚠️ Risk assessment:** LinkedIn actively blocks bot-like activity. Using this method:
- 50% chance of account block in 3-6 months
- May require repeated verification or password resets
- Not recommended for your primary LinkedIn account

---

## 🔍 Indeed (Currently Broken)

**Status:** Scraper outdated, returns 0 results

**Why:** Indeed updated their HTML structure; CSS selectors no longer match

**Fix required:** Debug and update selectors (low priority since AngelList works)

**No credentials needed** — it's just a broken scraper.

---

## 🧪 Quick Setup Checklist

Before tomorrow's 9 AM run:

- [ ] Email config exists: `~/.openclaw/secrets/email_config.json`
- [ ] Gmail app password configured in email config
- [ ] (Optional) LinkedIn credentials set up: `~/.openclaw/secrets/linkedin_credentials.json` (if going with official API)
- [ ] Job search config updated: `job-search-config.json` (if you want to change keywords/salary/location)

Run this to verify email works:
```bash
python3 /Users/michaeltorres/.openclaw/workspace/skills/job-search/scripts/filter_and_deliver.py
```

You should see an email arrive in your inbox within 30 seconds.

---

## 📞 Next Steps

Tell me:

1. **Email working?** ("Yes" or "needs setup")
2. **Want LinkedIn?**
   - "Yes, official API" (wait 3-5 days, then send me client_id/secret)
   - "Yes, scraping" (I'll set it up, understand the risks)
   - "No, AngelList is enough" (skip it)

Once you let me know, I can integrate LinkedIn and test the full flow.
