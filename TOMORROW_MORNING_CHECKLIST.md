# Tomorrow Morning Checklist — April 17, 2026

**Time:** 9:00 AM PDT  
**Task:** Check inbox for emails to test if Lambda system is working

---

## What to Look For

At exactly 9:00 AM PDT, you should receive (in this order, maybe within seconds of each other):

### Email #1: Morning Journal Prompt
- **From:** You (mtorres253@gmail.com)
- **Subject:** Your Daily Journal Prompt - 2026-04-17
- **Contains:** Three questions about gratitude, tasks, and strengths
- **Function:** morning-journal-lambda
- **Sent by:** EventBridge → morning-journal-lambda-rule at cron(0 16 * * ? *)

✅ **Expected:** YES (working since at least today)  
⚠️ **If missing:** Check if OpenClaw is running

---

### Email #2: Daily Job Search Digest
- **From:** You (mtorres253@gmail.com)
- **Subject:** 🔍 Daily Job Search Digest — Thursday, April 17
- **Contains:** 5-15 job listings with details
- **Function:** job-search-lambda
- **Sent by:** EventBridge → job-search-lambda-rule at cron(0 16 * * ? *)

✅ **Expected:** YES (you got this today at 9:00:41 AM)  
⚠️ **If missing:** Job search Lambda failed  
❌ **If ALSO at 10 AM:** Duplicate rule or cron job exists

---

### Email #3: Gmail Digest (THE KEY TEST)
- **From:** You (mtorres253@gmail.com)
- **Subject:** 📧 Email Digest — Thursday, April 17
- **Contains:** Summary of last 24h emails by category (Work, Jobs, Personal, etc.)
- **Function:** gmail-digest-lambda
- **Sent by:** EventBridge → gmail-digest-lambda-rule at cron(0 16 * * ? *)

✅ **Expected:** YES (NEVER arrived since April 10 — THIS IS THE TEST!)  
❌ **If missing:** Gmail digest Lambda failed (need to debug)  
📌 **IF IT ARRIVES:** Problem is already solved!

---

## The Test Results

Fill in what you see:

```
[ ] Email #1: Morning Journal Prompt
    Received at: _____ AM PDT
    Status: ☐ Yes ☐ No ☐ Multiple (if multiple, note times)

[ ] Email #2: Job Search Digest
    Received at: _____ AM PDT
    Status: ☐ Yes (9 AM only) ☐ Yes (9 AM + 10 AM) ☐ No ☐ Multiple

[ ] Email #3: Gmail Digest ← THE KEY ONE
    Received at: _____ AM PDT
    Status: ☐ Yes ✅ (PROBLEM SOLVED!) ☐ No (need to debug)
```

---

## How to Interpret Results

### Scenario A: All 3 Emails Arrived at 9 AM ✅

**Congratulations!**

- ✅ Gmail digest is working (it was fine all along)
- ✅ Morning journal is working
- ✅ Job search is working
- The 10 AM job search you saw before was probably:
  - A one-time Lambda retry (automatically fixed)
  - Or an OpenClaw cron job that's no longer running

**Action:** Nothing! Everything is working perfectly.

---

### Scenario B: Emails #1 + #2, But No #3 (Gmail Digest)

**Gmail digest has an issue.**

- ✅ Job search works (proved by email at 9 AM)
- ✅ Journal works (proved by email at 9 AM)
- ❌ Gmail digest fails (no email)

**Action:** 
1. Get IAM permissions (share FIX_IAM_PERMISSIONS.md with admin)
2. Run debug checklist: `aws-lambda-setup/LAMBDA_DEBUG_CHECKLIST.md`
3. Look specifically at:
   - Is `GMAIL_OAUTH_CONFIG` set in Lambda environment?
   - What errors are in CloudWatch logs?
   - Is SES verified or in sandbox?

---

### Scenario C: Only Email #1 (Missing #2 and #3)

**Both job search and Gmail digest failed.**

- ✅ Journal works
- ❌ Job search failed
- ❌ Gmail digest failed

**This is unlikely** but would mean:
- EventBridge rules aren't triggering job-search or gmail-digest
- Or those Lambda functions are broken

**Action:**
1. Get IAM permissions immediately
2. Check EventBridge rules exist and are enabled
3. Check CloudWatch logs for both functions
4. Manually invoke: `aws lambda invoke --function-name job-search-lambda ...`

---

### Scenario D: Email #2 Arrives at BOTH 9 AM AND 10 AM

**Duplicate job search confirmed.**

- ✅ Job search is running (twice!)
- ❓ Why the duplicate?

**Likely causes:**
1. OpenClaw cron job also triggers job-search at 10 AM
2. EventBridge rule has two targets
3. Lambda is retrying after first invocation

**Action:**
1. Check local cron jobs: `cron list`
2. Look for anything named `*job-search*` at 10 AM
3. Get IAM permissions
4. Run: `aws events list-targets-by-rule --rule job-search-lambda-rule`
5. Delete duplicates if found

---

## Immediate Actions

### If All 3 Arrive (Scenario A) ✅

```bash
# Just note that everything is working
echo "✅ Gmail Lambda system is fully functional"

# Optional: commit a note
git add -A
git commit -m "chore: Lambda system verified working (Apr 17, 2026)"
```

### If Gmail Digest Missing (Scenario B) ⚠️

```bash
# Step 1: Share with admin
echo "Share this with AWS admin: aws-lambda-setup/FIX_IAM_PERMISSIONS.md"

# Step 2: Wait for permissions to be granted

# Step 3: Run debug commands
# See: aws-lambda-setup/LAMBDA_DEBUG_CHECKLIST.md
aws lambda get-function-configuration --function-name gmail-digest-lambda --region us-west-2
aws logs tail /aws/lambda/gmail-digest-lambda --region us-west-2 --since 1d
```

### If Multiple Jobs (Scenario D) ⚠️

```bash
# Check OpenClaw cron
cron list | grep -i job-search

# If you see one at 10 AM, disable it:
cron remove {jobId}

# Or disable OpenClaw job-search completely
cron update {jobId} --enabled false
```

---

## Quick Reference

**Which file shows what:**
- `LAMBDA_STATUS_REPORT.md` ← Start here for overview
- `CURRENT_STATUS.md` ← Detailed technical summary
- `LAMBDA_DEBUG_CHECKLIST.md` ← Step-by-step AWS commands (after getting permissions)
- `FIX_IAM_PERMISSIONS.md` ← What to share with admin

**Key time:** 9:00 AM PDT tomorrow = 4:00 PM UTC

---

## Notes

- Times might vary by 30 seconds (normal for scheduled tasks)
- If you see emails at 8:59 or 9:01, that's still "on time"
- Check all emails including spam/promotions folders
- Keep email headers if there are issues (for debugging)

---

## After Tomorrow

Once you know which scenario you're in:

| Scenario | Next File |
|----------|-----------|
| All 3 ✅ | Done! Celebrate! |
| Missing #3 ⚠️ | `FIX_IAM_PERMISSIONS.md` → `LAMBDA_DEBUG_CHECKLIST.md` |
| Missing #2+#3 ⚠️ | `FIX_IAM_PERMISSIONS.md` → `LAMBDA_DEBUG_CHECKLIST.md` |
| Duplicate #2 ⚠️ | Check `cron list`, then debug as needed |

---

**Check-in time:** April 17, 2026 at 9:15 AM PDT  
**Expected outcome:** ✅ Answers about what's working
