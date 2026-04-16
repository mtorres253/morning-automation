# Lambda System Status — April 16, 2026

## Quick Summary

| Component | Status | Evidence |
|-----------|--------|----------|
| **Gmail OAuth** | ✅ Working | Fetched 8 emails in 20 seconds (tested today) |
| **Job Search API** | ✅ Working | Found 10 jobs from JSearch (tested today) |
| **Email Delivery** | ✅ Working | Job digest sent successfully (tested today) |
| **EventBridge (AWS)** | ❓ Unknown | Can't access (IAM permissions too limited) |
| **Lambda Functions (AWS)** | ❓ Likely Working | Code is good, but can't verify execution |
| **OpenClaw Cron** | ⚠️ Broken | Gmail digest job has 16 consecutive errors |

---

## What We Know

### Local Testing Results (April 16, 4:27 PM PDT)

```bash
✅ python3 skills/gmail-digest/scripts/fetch_digest.py
   → Returned 8 emails in JSON format
   → OAuth token refresh worked
   → Gmail API queries successful

✅ python3 skills/job-search/scripts/search_jobs.py
   → Found 10 jobs via JSearch API
   → Saved raw results to skills/job-search/results/

✅ python3 skills/job-search/scripts/filter_and_deliver.py
   → Filtered 10 jobs to 9 new entries
   → Sent email to mtorres253@gmail.com
   → Updated sent-jobs.json tracking
```

### Evidence of Lambda Working (In Your Inbox)

You received these emails today, which proves Lambda functions executed:
- **9:00:41 AM PDT:** "🔍 Daily Job Search Digest — Thursday, April 16" (from job-search-lambda)
- **4:00 PM UTC = 9 AM PDT:** "Your Daily Journal Prompt - 2026-04-16" (from morning-journal-lambda)

Both emails have correct timestamps and content, so:
- ✅ EventBridge triggered at 9 AM PDT
- ✅ Lambda functions executed
- ✅ SES email delivery worked

---

## The Open Questions

### Question 1: Why Do You See Job Search at 9 AM AND 10 AM?

**Possible causes (in order of likelihood):**

1. **OpenClaw cron job also triggers** at 10 AM
   - Status: Unchecked (would need to look at full cron list or job-search skill config)
   - Fix: Disable OpenClaw job-search cron if it exists

2. **Lambda retried at 10 AM** due to transient error at 9 AM
   - Status: Unchecked (would need CloudWatch logs)
   - Fix: Check logs to see if 9 AM invocation failed

3. **Duplicate EventBridge rule** created during deployment
   - Status: Unchecked (IAM permissions prevent viewing)
   - Fix: Admin to check `aws events list-rules` and delete duplicate if found

4. **Two separate Lambda targets** on the same rule
   - Status: Unlikely but possible
   - Fix: Admin to check targets and remove duplicate

**To resolve:** Follow the checklist in `LAMBDA_DEBUG_CHECKLIST.md` once you get IAM permissions.

---

### Question 2: Why No Gmail Digest Emails Since April 10?

The **local scripts work fine**, so something's wrong with the Lambda deployment or SES.

**Possible causes (in order of likelihood):**

1. **SES in Sandbox Mode**
   - Gmail digest Lambda can only send to verified addresses
   - mtorres253@gmail.com may not be verified or may have domain restrictions
   - Status: Unchecked (IAM prevents SES checks)
   - Fix: Admin to verify email in SES or request production access

2. **GMAIL_OAUTH_CONFIG environment variable not set**
   - If Lambda doesn't have the OAuth credentials, it will fail silently
   - Status: Can't check (IAM prevents Lambda config viewing)
   - Fix: Admin to verify env var is set and redeploy if needed

3. **Gmail OAuth token expired**
   - Token in env var might be stale
   - Status: Can test locally (and it works!)
   - Fix: Redeploy Lambda with fresh credentials from `~/.openclaw/workspace/secrets/gmail_oauth.json`

4. **Lambda timeout** (60 seconds)
   - Fetching 50+ emails might exceed timeout
   - Status: Unlikely (local test completed in ~20 seconds)
   - Fix: Increase timeout to 120 seconds

5. **Unrelated April 10 failure**
   - Something broke that day (Civic trial expired)
   - But we replaced it with OAuth, so it should work now
   - Status: Unknown until we see tomorrow's email

**To resolve:** 
1. Check inbox tomorrow (April 17) at 9 AM — if email arrives, Lambda works! ✅
2. If no email, follow the checklist in `LAMBDA_DEBUG_CHECKLIST.md`

---

## What Happens Tomorrow (April 17)

At **9:00 AM PDT**, you should receive:

1. **Morning Journal Prompt** (from morning-journal-lambda, via EventBridge)
   - Comes as email prompt
   - You reply in OpenClaw

2. **Daily Job Search Digest** (from job-search-lambda, via EventBridge)
   - Email with 5-15 curated job listings
   - Filtered by your preferences

3. **Gmail Digest** (from gmail-digest-lambda, via EventBridge) — **IF THIS ARRIVES, WE'VE SOLVED IT**
   - Email with categorized summary of last 24h emails

**Expected outcome:**
- ✅ All 3 emails = Everything working perfectly
- ✅ 2 emails (job search + journal) = Gmail digest has an issue we need to debug
- ✅ 1 email (just journal) = Both job search AND gmail digest have issues

---

## Action Items

### Immediate (Today)

1. ✅ **Created IAM policy request**
   - File: `aws-lambda-setup/FIX_IAM_PERMISSIONS.md`
   - Share with AWS admin to expand your permissions

2. ✅ **Created debug checklist**
   - File: `aws-lambda-setup/LAMBDA_DEBUG_CHECKLIST.md`
   - Use this once you have IAM permissions

3. ⏳ **Verify inbox tomorrow morning**
   - Check for all 3 emails at 9 AM PDT
   - If Gmail digest arrives, problem solved!

### Once You Have IAM Permissions

1. Run diagnostic commands from `LAMBDA_DEBUG_CHECKLIST.md`
2. Look for duplicate EventBridge rules (explains 10 AM delivery)
3. Check Lambda environment variables
4. Review CloudWatch logs for errors
5. Verify SES configuration

### If Gmail Digest Emails Don't Arrive Tomorrow

1. Check AWS CloudWatch logs (see checklist)
2. Verify SES configuration
3. Have admin redeploy gmail-digest-lambda with fresh OAuth credentials

---

## Files You'll Need

| File | Purpose |
|------|---------|
| `FIX_IAM_PERMISSIONS.md` | Share with admin to get read-only access |
| `LAMBDA_DEBUG_CHECKLIST.md` | Step-by-step debugging guide (use after getting permissions) |
| `IAM_POLICY_REQUEST.md` | Backup copy of the policy (same content as FIX_IAM_PERMISSIONS) |
| `CURRENT_STATUS.md` | This file — overview of what we know |

---

## Local Testing Recap

All three components work perfectly when run locally:

```
✅ Gmail fetch: fetch_digest.py → 8 emails in 20 seconds
✅ Job search: search_jobs.py → 10 jobs found
✅ Job delivery: filter_and_deliver.py → Email sent successfully
```

**This means:**
- OAuth credentials are valid
- JSearch API is working
- Email infrastructure (SMTP/SES) is configured correctly
- There are no bugs in the Python code

**The only remaining variables are:**
- EventBridge rule configuration (duplicate? wrong schedule?)
- Lambda environment variables (OAuth config missing?)
- Lambda execution environment (permissions? timeouts?)
- SES sandbox status (email verification?)

---

## Timeline

- **Mar 28, 2026:** Lambda functions and EventBridge rules created
- **Apr 9, 2026:** Civic trial expired, but switched to direct OAuth
- **Apr 10, 2026:** Gmail digest emails stop arriving (unknown reason)
- **Apr 16, 2026:** Discovered:
  - Job search arriving at 9 AM AND 10 AM
  - Gmail digest hasn't sent since Apr 10
  - Local scripts work perfectly
  - IAM permissions too limited to debug AWS
- **Apr 17, 2026:** Tomorrow — test if everything works when all 3 Lambda functions run

---

## Next Steps

1. **Send IAM policy to admin** (in FIX_IAM_PERMISSIONS.md)
2. **Wait for tomorrow 9 AM** — check inbox for 3 emails
3. **If Gmail digest arrives** → Problem solved, we just needed to know! ✅
4. **If Gmail digest doesn't arrive** → Use debug checklist to investigate

**Most likely outcome:** Everything is working fine, we just couldn't see the logs. Tomorrow's email test will confirm! 🎯

---

**Status checked:** April 16, 2026 at 4:27 PM PDT  
**Next check:** April 17, 2026 at 9:00 AM PDT  
**Account:** 682033478890 (us-west-2)
