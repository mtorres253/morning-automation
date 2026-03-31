# Resume-Draft Skill 🚀

**Quickly create tailored resumes and cover letters by matching your snippet library against job descriptions.**

## What It Does

1. **Parses a job description** (URL or pasted text) → extracts keywords
2. **Matches your resume snippets** → scores by relevance (0-100%)
3. **Generates a tailored resume** → formatted markdown, ready for Google Docs
4. **Generates a cover letter** → structured template with your top matches

**Result:** Professional resume & cover letter drafts in <2 seconds, with relevance scores so you can review and customize.

---

## Quick Example

You have a library of resume snippets. Job posting says "Senior Python Engineer, AWS, Docker, Kubernetes."

This skill:
- Extracts those keywords
- Scores each of your snippets
- Selects the top matches
- Formats them into a resume with bolded keywords
- Provides a cover letter template

**Output:** Two markdown files ready to open, review, and customize.

---

## Get Started (5 Minutes)

### 1. Copy the template

```bash
cp references/resume-snippets-template.json my-snippets.json
```

Edit `my-snippets.json` with your own resume snippets (see format below).

### 2. Run the one-liner

```bash
JOB_URL="https://example.com/jobs/123"

python scripts/parse_job_description.py --url "$JOB_URL" > p.json && \
python scripts/match_snippets.py p.json my-snippets.json > m.json && \
python scripts/generate_draft.py m.json --output resume.md && \
python scripts/generate_draft.py m.json --type cover-letter --output letter.md
```

### 3. Open and customize

```bash
open resume.md letter.md
# or
cat resume.md
cat letter.md
```

Copy into Google Docs, add personalization, submit.

---

## The 3 Steps (Explained)

### Step 1: Parse Job Description

Extract keywords from a job posting:

```bash
python scripts/parse_job_description.py --url "https://..." > parsed.json
```

**Input:** Job posting URL or text  
**Output:** JSON with keywords, technologies, experience levels, requirements

### Step 2: Match Snippets

Score each snippet against the parsed job:

```bash
python scripts/match_snippets.py parsed.json my-snippets.json > matches.json
```

**Input:** Parsed job + your snippets library  
**Output:** Snippets ranked by relevance score (highest first)

### Step 3: Generate Drafts

Format into resume and/or cover letter:

```bash
# Resume
python scripts/generate_draft.py matches.json --type resume --output resume.md

# Cover letter
python scripts/generate_draft.py matches.json --type cover-letter --output letter.md
```

**Input:** Matched snippets  
**Output:** Formatted markdown (ready for Google Docs)

---

## Snippets Library Format

```json
{
  "resume_snippets": [
    {
      "id": "exp-001",
      "category": "experience",
      "title": "Backend Engineering Lead",
      "text": "Led architecture and delivery of microservices platform using Python and AWS, reducing API latency by 40%."
    },
    {
      "id": "skill-python",
      "category": "skills",
      "title": "Python & Backend Development",
      "text": "Expert in Python (8+ years), Django REST Framework, and async programming. Built scalable backend systems supporting 10M+ daily requests."
    }
  ]
}
```

**Categories:** `experience`, `skills`, `achievements`, `leadership`, or custom

**Tips:**
- Use specific keywords (Python, AWS, Docker, not just "programming")
- Include numbers/metrics ("40% faster", "10M requests")
- Vary length (1-3 sentence snippets work best)
- 15-30 snippets is ideal (not too few, not too many)

---

## Resume Output Example

```markdown
# Tailored Resume Draft

**Overall Match Score: 82.3%**

## Experience

**[92%]** Led architecture and delivery of **microservices platform** using **Python** and **AWS**, reducing API latency by 40% and supporting 10M+ daily requests.

## Technical Skills

**[88%]** Expert in **Python** (8+ years), **Django REST Framework**, **FastAPI**, **async programming**, and designing scalable backend systems.

**[85%]** Proficient in **Docker**, **Kubernetes**, **AWS**, **CI/CD** pipelines, and infrastructure-as-code.
```

Keywords from the job are **bolded** so you can see what matched. Relevance scores help you review.

---

## Documentation

Start with one of these:

- **🚀 30-second setup**: Read `QUICKSTART.md`
- **📖 Complete guide**: Read `SKILL.md`
- **🎓 Real example**: Read `references/example-workflow.md`
- **🔧 Technical details**: Read `references/USAGE.md`
- **📚 File reference**: Read `INDEX.md`

---

## Key Features

✅ **Keyword extraction** from job postings (URL or text)  
✅ **Relevance scoring** (0-100%) based on snippet-job match  
✅ **Resume generation** organized by category  
✅ **Cover letter generation** with templates  
✅ **Keyword highlighting** (bold in output)  
✅ **Google Docs ready** (copy-paste friendly markdown)  
✅ **Zero dependencies** (Python standard library only)  
✅ **Fast** (<2 seconds per job)  
✅ **Private** (no API calls, runs locally)  
✅ **Flexible** (adjust thresholds, top-n snippets, etc.)  

---

## Common Commands

### Resume from URL
```bash
python scripts/parse_job_description.py --url "https://..." > p.json
python scripts/match_snippets.py p.json my-snippets.json > m.json
python scripts/generate_draft.py m.json --output resume.md
```

### Resume from pasted text
```bash
python scripts/parse_job_description.py --text "Senior Engineer, Python, AWS..." > p.json
python scripts/match_snippets.py p.json my-snippets.json > m.json
python scripts/generate_draft.py m.json --output resume.md
```

### Cover letter
```bash
python scripts/generate_draft.py matches.json --type cover-letter --output letter.md
```

### Only top 5 snippets
```bash
python scripts/generate_draft.py matches.json --top-n 5 --output resume.md
```

### Lower threshold (get more matches)
```bash
python scripts/match_snippets.py parsed.json my-snippets.json --min-score 20 > m.json
```

### Without scores
```bash
python scripts/generate_draft.py matches.json --no-scores --output resume.md
```

---

## Workflow Tips

1. **Build your snippets library first** - More snippets = more flexibility
2. **Use specific keywords** - "Python, Django, AWS" beats "programming"
3. **Include metrics** - "Reduced latency 40%" is stronger than "improved performance"
4. **Keep snippets 1-3 sentences** - Longer is harder to customize
5. **Review the relevance scores** - They tell you how well your snippet matches the job
6. **Customize the draft** - Generated drafts are starting points, not final documents
7. **Copy-paste into Google Docs** - Markdown formatting preserves nicely
8. **Reuse and iterate** - Use the same library across multiple applications

---

## Troubleshooting

**No snippets matched?**
- Try lowering `--min-score` (default 30%, try 20)
- Ensure snippets contain job keywords (e.g., "Python", "AWS")
- Check that the job description has clear keywords

**Relevance scores too low?**
- Your snippets may not match the job well (consider this genuine feedback!)
- Add more keywords to your snippets
- Try using full job description (with "nice to haves")

**Script not found?**
- Ensure you're in the skill directory
- Check scripts are executable: `ls -la scripts/`

**JSON parsing error?**
- Validate JSON: `python -m json.tool my-snippets.json`
- Check for trailing commas or missing quotes

See `references/USAGE.md` for more troubleshooting.

---

## Technical Details

- **Language:** Python 3.7+
- **Dependencies:** None (standard library only)
- **Performance:** ~2 seconds per job (includes URL fetching)
- **Size:** ~100KB total, ~620 lines of code
- **Output:** Markdown (Google Docs ready) or JSON (for integration)

---

## Files in This Skill

```
resume-draft/
├── SKILL.md                                    (Main documentation)
├── QUICKSTART.md                               (30-second guide)
├── INDEX.md                                    (File reference)
├── COMPLETION_SUMMARY.md                       (What's included)
├── README.md                                   (This file)
├── scripts/
│   ├── parse_job_description.py               (Step 1)
│   ├── match_snippets.py                      (Step 2)
│   └── generate_draft.py                      (Step 3)
└── references/
    ├── USAGE.md                                (Technical guide)
    ├── example-workflow.md                     (Real example)
    └── resume-snippets-template.json           (Template library)
```

---

## What This Skill Does NOT Do

❌ Submit applications for you  
❌ Auto-fill applications  
❌ Post to LinkedIn  
❌ Provide interview tips  
❌ Guarantee you'll get the job  

✅ What it DOES do: Generate tailored, keyword-matched resume and cover letter drafts in seconds, so you can customize and submit them yourself.

---

## Future Enhancements

Ideas for future versions:
- Semantic matching (AI-based similarity beyond keyword matching)
- LinkedIn auto-import
- Google Docs API integration
- ATS optimization analysis
- Interview prep questions from job description
- Industry-specific cover letter templates
- Batch processing (multiple jobs at once)

---

## Questions?

- **Quick start?** → `QUICKSTART.md`
- **How does it work?** → `SKILL.md`
- **Real example?** → `references/example-workflow.md`
- **Technical help?** → `references/USAGE.md`
- **All files?** → `INDEX.md`

---

## Ready to Use! 🚀

1. Copy the template: `cp references/resume-snippets-template.json my-snippets.json`
2. Add your snippets
3. Run the workflow
4. Get tailored drafts in seconds

Enjoy saving time on resume customization!

---

**Created:** 2026-03-28  
**Status:** ✅ Complete and tested  
**Location:** `~/.openclaw/workspace/skills/resume-draft/`
