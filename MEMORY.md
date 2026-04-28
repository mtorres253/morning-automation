# Long-Term Memory

## Active Systems

### Job Search Automation (Running on AWS Lambda)
- **Schedule:** 9:00 AM PDT daily via EventBridge
- **Primary Source:** JSearch API (OpenWeb Ninja) — covers 100+ job boards
- **Features:** Job deduplication (sent-jobs.json), LLM-based scoring (7+/10 featured), ranked delivery
- **Email:** Sent to mtorres253@gmail.com with featured jobs + full ranked list
- **Config:** `skills/job-search/job-search-config.json`
- **Tracking:** `skills/job-search/sent-jobs.json`

### Morning Journal (Running on AWS Lambda)
- **Schedule:** 8:00 AM PDT daily via EventBridge
- **Delivery:** Reflection prompt email sent via AWS SES

### Gmail Digest (Running on AWS Lambda)
- **Schedule:** 9:00 AM PDT daily via EventBridge
- **Auth:** Gmail OAuth 2.0 (refresh token in `secrets/gmail_oauth.json`)
- **Categories:** Work, Job Alerts, Calendar, GitHub, Personal, Newsletters, Notifications, Transactional
- **Delivery:** Digest email via AWS SES

## User Preferences & Setup

- **Name:** Michael
- **Timezone:** America/Los_Angeles (PDT)
- **Email:** mtorres253@gmail.com

### Job Search Criteria
- **Roles:** Director/Principal Product in Civic Tech, Gov Tech, Aviation, Drone Tech, Transportation, Mobility, Healthcare Innovation, Finance Innovation
- **Salary:** $200K-$250K
- **Locations:** San Francisco Bay Area, Remote, Hybrid (prefer remote/SF)
- **Company Stage:** Series C+, Late Stage, Public

## Key Technical Notes

**Context Optimization (April 25, 2026):**
- Archived all memory files older than 1 week to `memory/archive/` to reduce initial prompt size
- Allows use of cost-effective models (Groq: 32K token window works post-archival)
- Claude Haiku remains default (budget priority) — can override per-task as needed

**LLM Configuration:**
- Default: `anthropic/claude-haiku-4-5-20251001` (cost-optimized)
- Available: Groq (32K window, free tier), Claude Sonnet (200K window, capable)
- Job search uses Claude for scoring (embedded in Lambda function)

**Lambda Architecture:**
- All three skills (job-search, gmail-digest, morning-journal) run on AWS Lambda
- No local cron dependencies
- EventBridge triggers on schedule
- AWS SES handles email delivery
- CloudWatch logs for debugging

## Professional Materials

**File:** `assets/job-search/resumes.md`
- Consolidated capability list (25 core competencies)
- Role-specific tailoring guides
- Experience, education, and project templates
- Keywords for customization
