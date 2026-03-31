# Resume Matcher Workflow Guide

## Complete Workflow

### Phase 1: Preparation (One-time)

1. Ensure your resume markdown file is well-structured:
   ```markdown
   # Your Name
   Location | Email | Phone | LinkedIn
   
   ## Work History
   
   ### Product Director — Company A
   *Dates*
   - Achievement 1
   - Achievement 2
   
   ### Other Role — Company B
   *Dates*
   - Achievement 1
   ```

2. Ensure your cover letter file contains paragraphs or sections:
   ```markdown
   # Cover Letter Content
   
   ## Opening
   [Your opening paragraphs]
   
   ## Technical Skills
   [Your technical background]
   
   ## Leadership
   [Your leadership experience]
   ```

### Phase 2: Job Matching (Per job application)

1. **Find the job posting** you want to apply for
2. **Copy the full job description** (copy-paste from the job board or email)
3. **Share with the skill** — Either:
   - Paste directly in the conversation, or
   - Point to a text file with the job description
4. **Wait for draft generation** — The skill creates:
   - `resume_draft.md` — Your resume reordered by relevance
   - `cover_letter_draft.md` — Your cover letter sections ranked by relevance
5. **Review the drafts**:
   - Check if the reordering makes sense
   - Note which experiences the skill prioritized
   - Identify gaps or mismatches
6. **Edit as needed**:
   - Reorder sections if you disagree
   - Add missing context
   - Adjust cover letter flow
   - Polish formatting

### Phase 3: Submission

1. Copy the finalized content into your application system
2. Keep a copy of your customized documents
3. Track which version you sent to which company (helpful for interview prep)

## Decision Points

### Should I Use Resume Matcher?

**YES, if:**
- You have multiple roles/experiences and want to highlight the most relevant ones
- You're applying to very different types of roles (PM one day, strategy the next)
- You want to preserve your original wording while reordering for impact
- You need a quick draft to build from

**NO, if:**
- You want to rewrite/improve your content (use a different skill for that)
- Your resume is already very targeted for a specific role
- You're applying to similar roles repeatedly with minimal changes

### Custom Content vs. Full Content

The skill works best when:
- **Resume has 3+ distinct roles** (reordering has more impact)
- **Cover letter has varied sections** (e.g., technical, leadership, industry-specific)
- **Job description is detailed** (better keyword extraction)

For highly specific roles, you may want to manually select content instead of using full reordering.

## Troubleshooting

### Issue: Relevance scoring seems off

**Diagnosis**: The skill weights keyword frequency. If a job description emphasizes "leadership" but you have many "project management" bullets, the scoring may not align perfectly.

**Solution**: Review the ranked output, then manually reorder sections to your preferred order.

### Issue: Cover letter draft is too short or too long

**Diagnosis**: The skill selects top 5 most relevant paragraphs from your cover letter content.

**Solution**: Edit the output to include/exclude specific paragraphs and adjust length.

### Issue: Some important experiences ranked low

**Diagnosis**: Their keywords may not overlap heavily with the job description.

**Solution**: Manually move those sections higher if you believe they're relevant. The skill provides a starting point, not gospel.

## Example: Complete Cycle

**Job**: Senior Product Manager at a Healthcare SaaS company

**Keywords extracted**: healthcare, saas, product strategy, regulatory, compliance, user research, agile, cross-functional, roadmap

**Your roles scored**:
1. "Director of Product Management — Acubed" (Score: 0.89) — Regulatory compliance, cross-functional, strategy
2. "Executive Product Advisor — Jarvus" (Score: 0.62) — Strategy, roadmap, team leadership
3. "Product Manager — OldCorp" (Score: 0.34) — Some agile/roadmap experience

**Draft generated**: Resume reordered with #1 at top, #2 second, #3 lower

**Your review**: You agree with the order, but you add a bullet from role #3 that mentions healthcare domain experience

**Final document**: Submitted with #1 prominent, healthcare context added, roles #2 and #3 supporting

---

## Tips for Iterating

1. **Keep versions** — Save each draft (v1, v2, etc.) so you can reference what you sent
2. **A/B test if possible** — If you apply to similar roles, try different orderings and track which gets interviews
3. **Customize cover letter manually** — The skill orders sections; you should add personalization (company name, specific role, etc.)
4. **Update your source files** — As you add new roles/accomplishments, update resumes.md and cover_letters.md so they're ready for the next job
