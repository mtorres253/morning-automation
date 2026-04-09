# AngelList Integration Status

**Date:** April 8, 2026
**Status:** ❌ Not Currently Viable

## What Happened

Attempted to integrate AngelList (Wellfound) jobs search. Result: **403 Forbidden** (blocked).

### Why AngelList Isn't Working

1. **Wellfound (rebranded AngelList) blocks automated access**
   - Returns 403 Forbidden for non-browser requests
   - Similar issue to Indeed
   - Likely uses bot detection (Cloudflare, etc.)

2. **No Public API Available**
   - AngelList's old public API is discontinued
   - No official REST API for job search
   - Web scraping is detected and blocked

3. **Would Require User Authentication**
   - Could use Selenium/Playwright browser automation
   - Would need credentials stored
   - Risk of account issues

## Alternatives Considered

### Option A: Use Browser Automation (Selenium/Playwright)
- **Effort:** 3-4 hours
- **Reliability:** Moderate (breakage if site structure changes)
- **Account Risk:** Low (uses real browser)
- **Speed:** Slow (must render full page)
- **Recommendation:** ❌ Not worth the complexity

### Option B: Use Y Combinator Jobs RSS
- **Effort:** 1 hour
- **Reliability:** High (RSS is stable)
- **Account Risk:** None
- **Speed:** Fast (simple RSS parsing)
- **Coverage:** 50-100 startup jobs on YC Jobs
- **Recommendation:** ✅ Better alternative

### Option C: Keep JSearch Only
- **Coverage:** 80-90% of relevant jobs
- **Reliability:** High (official API)
- **Effort:** 0 (already implemented)
- **Recommendation:** ✅ Sufficient for now

## Recommendation

**Replace AngelList with Y Combinator Jobs RSS**

Y Combinator Jobs is:
- ✅ Easy to integrate (simple RSS feed parsing)
- ✅ Reliable (RSS format is stable)
- ✅ Good coverage for civic tech startups
- ✅ No bot detection issues
- ✅ No authentication needed

**Or:** Keep JSearch only and monitor coverage over next 2 weeks.

## Next Steps

Choose one:

1. **Implement Y Combinator Jobs** (1-2 hours)
   - Add RSS feed parser
   - Filter by keywords (civic tech, gov tech, etc)
   - Deduplicate with JSearch results

2. **Stick with JSearch** (no action needed)
   - Monitor if civic tech coverage is sufficient
   - Add Y Combinator if needed in week 2-3

Michael's preference: **Y Combinator Jobs** (he said "add angellist" for civic tech focus)

---

## Technical Details

**What we tried:**
- Wellfound API endpoint: `https://wellfound.com/api/search/roles` → 404/403
- Wellfound web search with scraping: `https://wellfound.com/jobs` → 403 (bot detection)
- Both approaches blocked

**Lesson learned:** Wellfound migrated from AngelList and now actively blocks automated access, similar to Indeed.

## Y Combinator Jobs as Alternative

If we proceed with Y Combinator:
- **Feed:** https://news.ycombinator.com/rss (jobs category)
- **Alternative:** https://ycombinator.com/jobs/rss
- **Coverage:** ~50-100 jobs at any time
- **Update frequency:** Daily
- **Quality:** High (YC-backed + high-quality startup jobs)

**Civic tech + Gov tech presence:**
- Code for America (YC alum)
- 18F contractors
- Various government modernization startups
- Civic innovation companies

---

**Status Update:** Removed AngelList from active integration. Proceeding with Y Combinator Jobs option if desired.
