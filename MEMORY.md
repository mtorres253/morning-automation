# Long-Term Memory

## Job Search Skill (April 8, 2026)

### Problem
Daily job search emails were showing the same 5 jobs every day instead of fresh listings.

### Root Cause
- Indeed scraper was silently failing (403 Forbidden, outdated HTML selectors)
- When Indeed failed, script fell back to hardcoded sample data
- User had no visibility into what was failing
- No deduplication of jobs across days

### Solution Implemented
1. **Removed silent fallback** — No more sample data in results
2. **Always send email** — Even if searches fail or no jobs found
3. **Added search status reporting** — Each email shows which sources worked/failed
4. **Job deduplication** — Only new jobs sent (tracks sent-jobs.json)
5. **Job removal** — Old postings automatically disappear when no longer posted
6. **Updated documentation** — Created BEHAVIOR.md, QUICK_START.md, STATUS_REPORT.md

### Current Status
- ✅ Indeed scraper removed (was brittle, JSearch covers Indeed anyway)
- ✅ JSearch integrated (OpenWeb Ninja's JSearch API via RapidAPI) — primary source
- ✅ AngelList attempted but blocks automated access (403 Forbidden)
- ✅ Y Combinator RSS attempted but endpoint not available (404)
- ✅ Email behavior fixed (always sends, with clear status)
- ✅ Deduplication implemented (sent-jobs.json tracks what's been sent)
- ✅ Test runs successful (10 real jobs found from LinkedIn, ZipRecruiter, Adobe, Google, etc)
- 🚀 Ready for daily 9 AM delivery with JSearch as primary source

### Next Steps (COMPLETED ✅)
1. ✅ Set up JSearch API via RapidAPI (OpenWeb Ninja's JSearch)
2. ✅ Integrated into search_jobs.py
3. ✅ Email delivery working (tested with 10 real jobs)
4. Job emails will start arriving daily at 9 AM with fresh listings

### Technical Details
- Search script: `skills/job-search/scripts/search_jobs.py`
- Delivery script: `skills/job-search/scripts/filter_and_deliver.py`
- Tracking: `skills/job-search/sent-jobs.json` (auto-created)
- Config: `skills/job-search/job-search-config.json` (can customize keywords/salary/locations)

### Key Files Created/Updated
- `BEHAVIOR.md` — Email flow and scenarios
- `QUICK_START.md` — Quick reference
- `STATUS_REPORT.md` — Detailed status and options
- `CREDENTIALS_CHECKLIST.md` — Credential setup reference
- `LINKEDIN_SETUP.md` — LinkedIn options (official API vs scraping)
- `ANGELLIST_SETUP.md` — AngelList setup (API issues found)

### Lambda Deployment & Architecture Finalized (April 17, 2026)

**Status:** All three automation systems (job-search, gmail-digest, morning-journal) migrated to AWS Lambda.

**What's Running:**
- ✅ **Morning-journal Lambda** — EventBridge rule at 8:00 AM PDT
  - Sends daily reflection prompt email
  - Uses AWS SES for delivery
  
- ✅ **Job-search Lambda** — EventBridge rule at 9:00 AM PDT  
  - Uses JSearch API (OpenWeb Ninja) for job searches
  - Covers 100+ job boards (LinkedIn, Indeed, ZipRecruiter, etc.)
  - Deduplicates and ranks jobs
  - Sends digest via AWS SES
  
- ✅ **Gmail-digest Lambda** — EventBridge rule at 9:00 AM PDT
  - Fetches emails via Gmail OAuth 2.0
  - Groups by category (Work, Job Alerts, Calendar, GitHub, Personal, Newsletters, Notifications, Transactional)
  - Sends digest via AWS SES

**Local Cron Jobs:**
- ❌ Morning-journal cron disabled (April 17)
- ❌ All local cron jobs disabled — Lambda is sole execution engine

**Credentials:**
- ✅ `~/.openclaw/workspace/secrets/gmail_oauth.json` — Gmail OAuth (refresh token)
- ✅ Lambda env vars: `GMAIL_OAUTH_CONFIG`, `JSEARCH_API_KEY`, `GMAIL_EMAIL`, `SES_EMAIL`
- ✅ AWS IAM permissions: Lambda can invoke SES for email delivery

**Documentation Updated (April 17):**
- ✅ `ARCHITECTURE.md` — Explains manifest concept and Lambda vs Claude vs Cron
- ✅ `skills/gmail-digest/SKILL.md` — Updated to reflect Gmail OAuth + Lambda (no Civic)
- ✅ `skills/job-search/SKILL.md` — Updated to reflect JSearch API only, Lambda, 9 AM delivery
- ✅ `skills/morning-journal/SKILL.md` — Updated to reflect Lambda email delivery, no S3 storage

**System Architecture:**
- All execution on AWS Lambda (no local cron dependencies)
- EventBridge triggers scheduled jobs
- AWS SES handles email delivery
- CloudWatch logs available for debugging
- SKILL.md files serve as documentation only (not execution manifests)

---

### Civic Trial Expired (April 9, 2026)

**Status:** Civic's 14-day free trial expired — gmail-digest skill can no longer access Gmail without a paid plan.

**Impact:**
- ❌ Gmail digest no longer works (9 AM cron job fails)
- Morning-journal skill still works (uses different mechanism)
- Job-search Lambda works fine (uses JSearch API)

**Options:**
1. **Upgrade Civic** — Pay for Standard Plan to continue using Civic tools
2. **Switch to Gmail OAuth** — Set up direct Gmail OAuth (no cost, but requires setup)
3. **Alternative email tool** — Use a different service/library for Gmail access

**Recommendation:** Set up Gmail OAuth directly if you want a free solution. It's more robust anyway than relying on Civic.

---

### Professional Materials (April 8, 2026)

Created `assets/job-search/resumes.md` with:

**Capabilities (deduplicated & organized):**
- Product & Strategy (6 items)
- Delivery & Operations (6 items)
- Leadership & People (6 items)
- Domain Expertise (7 items)

**Sections:**
- Executive summary
- Core competencies with sub-skills
- Professional experience template
- Education section
- Notable projects template
- Role-specific tailoring guides (Director/VP, Civic/Gov, Enterprise SaaS, Startup)
- Cover letter template placeholders
- Keyword lists for tailoring
- Notes on keeping materials current

All capabilities from request included and deduplicated:
- Agile software product management
- Strategic leadership
- Program & portfolio management delivery
- Professional services consulting
- Resource management & staffing
- Stakeholder relationship management
- Strategic partnership development
- Scoping and feasibility assessment
- Change management and adoption
- Customer relationship management
- Contract compliance and government contracting
- Metrics and KPI development
- Continuous integration & service delivery
- ISO 27001 compliance
- User research & journey mapping
- People management and coaching
- Organizational roadmapping

---

## Preferences & Setup

- **Name:** Michael
- **Timezone:** America/Los_Angeles (PDT)
- **Job Search Preferences:** Director/Principal Product roles in Civic Tech, Gov Tech, Aviation, Drone Tech, Transportation, Mobility, Healthcare Innovation, Finance Innovation
- **Salary Range:** $200K-$250K
- **Locations:** San Francisco Bay Area, Remote, Hybrid
- **Company Stage:** Series C+, Late Stage, Public
- **Email:** mtorres253@gmail.com

---

## Important Dates
- **Job Search Skill Fixed:** April 8, 2026
- **LinkedIn Setup Started:** April 8, 2026 (pending)
