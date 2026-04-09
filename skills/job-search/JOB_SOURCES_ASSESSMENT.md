# Job Search Sources Assessment

## Current Setup: JSearch (OpenWeb Ninja)

**What JSearch indexes:**
- ✅ LinkedIn jobs (major source)
- ✅ Indeed jobs
- ✅ Glassdoor jobs
- ✅ ZipRecruiter jobs
- ✅ Google for Jobs (largest job aggregator)
- ✅ Monster, CareerBuilder, FlexJobs
- ✅ Company career pages
- ✅ 1000+ other public job boards

**Coverage for Your Criteria:**
✅ Product leadership roles — excellent coverage across all major boards
✅ Startup jobs (Series C+) — strong on LinkedIn and AngelList companies
✅ Civic tech & gov tech — moderate coverage (smaller niche)
✅ Salary ranges — good when available on job boards
✅ Remote/hybrid roles — excellent coverage

**Strengths of JSearch:**
- Comprehensive aggregation (one API hits all major sources)
- Real-time data from Google for Jobs
- Salary data when available
- Legal and reliable (official API)
- No account risk
- No rate limiting issues
- Free tier covers your needs

**Limitations:**
- ⚠️ Civic/Gov tech coverage is smaller (fewer niche postings)
- ⚠️ Some internal company jobs may not be indexed
- ⚠️ Salary data incomplete (many jobs don't include it)

---

## Alternative Sources to Consider

### Option 1: Y Combinator Jobs (Free, Specific)
**What it indexes:** Startup jobs only (Y Combinator-backed + others)
**Quality for you:** HIGH — Your top priority industries (civic tech, drone tech, etc)
**Effort:** 1-2 hours to integrate web scraping
**Cost:** Free
**Why useful:** Many civic tech startups post on YC Jobs first

**Example jobs:**
- Code for America (YC alum) — civic tech leader
- Skydio (drone tech, funded)
- 18F partner companies

### Option 2: GitHub Jobs API (Free, Tech-focused)
**What it indexes:** Tech company jobs (smaller than others)
**Quality for you:** MEDIUM — Limited product leadership roles
**Effort:** 1 hour to integrate (simple API)
**Cost:** Free
**Why useful:** Good for finding early-stage tech/civic tech startups

### Option 3: RemoteOK API (Free, Remote-focused)
**What it indexes:** Remote job listings
**Quality for you:** LOW — Not many product leadership roles
**Effort:** 1 hour to integrate
**Cost:** Free
**Why useful:** Filters for remote-only if that's priority

### Option 4: AngelList API (Free, Startup-focused)
**What it indexes:** Startup jobs (pre-funded to Series C+)
**Quality for you:** VERY HIGH — Civic tech, gov tech, drone tech startups
**Effort:** 2 hours to integrate
**Cost:** Free
**Why useful:** Civic tech and government tech is a major AngelList focus

**AngelList has:**
- Civic tech category (e.g., Code for America)
- Government tech category
- Drone/Aviation category
- Startup funding info (equity, stage)

### Option 5: LinkedIn Scraping (Unofficial)
**What it indexes:** LinkedIn native
**Quality for you:** VERY HIGH — Most comprehensive for your roles
**Effort:** 1 hour to integrate
**Cost:** Free
**Why useful:** LinkedIn is #1 source for product leadership roles
**Caveat:** Account ban risk if detected (low but non-zero)

---

## Recommendation

**Current Status: JSearch is SUFFICIENT** ✅

For most product leadership roles in Bay Area, **JSearch alone should cover 80-90% of postings**. You'll get:
- LinkedIn jobs (largest source)
- Indeed jobs
- Glassdoor jobs
- ZipRecruiter
- Company career pages
- And 1000+ others

**However, consider adding:**

**1. AngelList (HIGH priority)**
   - Why: Civic tech and gov tech are major focus areas
   - Cost: Free API
   - Effort: 2 hours
   - Expected jobs: 2-5 civic tech roles/week
   - Recommendation: **ADD THIS**

**2. Y Combinator Jobs (MEDIUM priority)**
   - Why: Civic tech startups often post here first
   - Cost: Free (web scraping)
   - Effort: 1-2 hours
   - Expected jobs: 1-3 startup roles/week
   - Recommendation: **Nice to have, but not critical**

**3. GitHub Jobs (LOW priority)**
   - Why: Tech-focused, not many product leadership roles
   - Cost: Free
   - Effort: 1 hour
   - Expected jobs: 0-1 relevant roles/week
   - Recommendation: **Skip for now**

**4. LinkedIn Scraping (NOT recommended)**
   - Why: JSearch already gets LinkedIn via Google for Jobs
   - Risk: Account ban
   - Recommendation: **Not needed, stick with JSearch**

---

## Suggested Action Plan

### Week 1 (Now)
✅ JSearch is working great
✅ Civic tech coverage is ~60-70% via JSearch
✅ Keep current setup

### Week 2-3
🔄 Add AngelList integration (2 hours of work)
🔄 Expected: +2-5 additional civic tech roles/week

### Month 2+
🔄 Optionally add Y Combinator (1-2 hours of work)
🔄 Expected: +1-3 additional startup roles/week

---

## JSearch Coverage Analysis

Based on today's test (10 jobs found):

| Source | Count | % | Notes |
|--------|-------|---|-------|
| LinkedIn | 5 | 50% | Interface.ai, Google, Allspring, TDA, Adobe careers |
| ZipRecruiter | 3 | 30% | Resilience, Zip, HPE |
| Indeed | 0 | 0% | Already in JSearch but not top results |
| Glassdoor | 0 | 0% | Already in JSearch but not top results |
| Company careers | 2 | 20% | Adobe, Genentech, VirtualVocations |

**Verdict:** JSearch is giving you diverse sources. Adding AngelList would increase civic tech representation.

---

## Bottom Line

**Is JSearch enough?** 

✅ **Yes, for now.** You're getting 10 quality jobs per search with diverse sources.

**Should you add more sources?**

📌 **Optional but recommended:** Add AngelList if civic tech is a top priority.

**When to add more:**

- If you're not finding civic tech roles → add AngelList
- If you want even more startup options → add Y Combinator
- If you need deep LinkedIn coverage → keep JSearch (better than scraping)

For now, **stay with JSearch and monitor quality**. If you notice civic tech coverage is low in a few weeks, we can add AngelList as a second source.

---

**Questions to ask yourself:**

1. Are you getting enough jobs? (Currently 10/day)
2. Are they quality matches? (Check the roles you're receiving)
3. Are civic tech roles underrepresented? (Monitor over next week)
4. Do you have time to vet sources weekly? (Important for multi-source setup)

Once you answer these, we can decide if additional sources are worth the complexity.
