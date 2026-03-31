# Resume-Draft Skill - Complete Index

## 📚 Files Overview

### Core Documentation

| File | Purpose |
|------|---------|
| **SKILL.md** | Main skill documentation (frontmatter + full workflow guide) |
| **QUICKSTART.md** | 30-second setup and common commands |
| **INDEX.md** | This file - complete file reference |

### Scripts (Python, no external dependencies)

| Script | Purpose |
|--------|---------|
| **parse_job_description.py** | Parse job posting (URL or text) → extract keywords |
| **match_snippets.py** | Score snippets against job → ranked matches |
| **generate_draft.py** | Format matches → markdown resume/cover letter |

### References & Examples

| File | Purpose |
|------|---------|
| **USAGE.md** | Technical reference (APIs, schemas, troubleshooting) |
| **example-workflow.md** | Real-world complete example (Senior Backend Engineer) |
| **resume-snippets-template.json** | Example snippets library (copy & customize) |

---

## 🚀 Getting Started (Pick Your Path)

### Path 1: Super Quick (5 minutes)
1. Read `QUICKSTART.md`
2. Copy `references/resume-snippets-template.json` → `my-snippets.json`
3. Edit your snippets
4. Run the one-liner command

### Path 2: Complete Understanding (20 minutes)
1. Read `SKILL.md` intro + workflow sections
2. Read `references/example-workflow.md` (real example)
3. Copy template and customize
4. Run scripts step-by-step

### Path 3: Deep Dive (30-45 minutes)
1. Read `SKILL.md` entirely
2. Read `references/USAGE.md` for technical details
3. Read `references/example-workflow.md` for context
4. Examine script source code (they're readable)
5. Experiment with your snippets library

---

## 📋 Workflow Overview

```
Job Description (URL or text)
         ↓
[parse_job_description.py]  → Extract keywords, requirements
         ↓
    parsed.json (keywords)
         ↓
[match_snippets.py]  → Score snippets against job
         ↓
    matches.json (ranked snippets with scores)
         ↓
[generate_draft.py]  → Format into resume or cover letter
         ↓
    resume.md / cover-letter.md (markdown, ready to edit)
```

---

## 🎯 Common Tasks

### Task: Generate tailored resume for a job URL

```bash
JOB_URL="https://example.com/jobs/123"
python scripts/parse_job_description.py --url "$JOB_URL" > p.json && \
python scripts/match_snippets.py p.json my-snippets.json > m.json && \
python scripts/generate_draft.py m.json --type resume --output resume.md
cat resume.md
```

### Task: Generate resume from pasted job text

```bash
python scripts/parse_job_description.py --text "Senior Engineer, Python, AWS..." > p.json
python scripts/match_snippets.py p.json my-snippets.json > m.json
python scripts/generate_draft.py m.json --type resume --output resume.md
```

### Task: Generate cover letter draft

```bash
python scripts/generate_draft.py matches.json --type cover-letter --output cover-letter.md
```

### Task: View relevance scores for each snippet

```bash
cat matches.json | grep -A 2 "relevance_score"
```

### Task: Only use top 5 highest-scoring snippets

```bash
python scripts/generate_draft.py matches.json --top-n 5 --output resume.md
```

### Task: Lower the matching threshold (get more snippets)

```bash
python scripts/match_snippets.py parsed.json my-snippets.json --min-score 20 > matches.json
```

### Task: See which keywords matched for each snippet

```bash
cat matches.json | jq '.matched_snippets[] | {title, relevance_score, matched_keywords}'
```

---

## 🔧 Script Details

### parse_job_description.py

**Input:** URL or job description text  
**Output:** JSON with extracted keywords, technologies, requirements

```bash
python scripts/parse_job_description.py --url "https://..."
python scripts/parse_job_description.py --text "Senior Engineer with..."
python scripts/parse_job_description.py --url "..." --output parsed.json
```

**Output includes:**
- `all_keywords` - Flat list of all extracted keywords
- `keywords_detail` - Broken down by type (matched_keywords, technologies, experience, job_titles)
- `requirements` - Bullet points / requirements from job posting
- `total_keywords` - Count of keywords

### match_snippets.py

**Input:** Parsed job (from parse_job_description.py) + snippets library  
**Output:** Ranked snippets with relevance scores

```bash
python scripts/match_snippets.py parsed.json snippets.json
python scripts/match_snippets.py parsed.json snippets.json --min-score 25
python scripts/match_snippets.py parsed.json snippets.json --output matches.json --verbose
```

**Scoring:**
- `relevance_score` - 0-100%, higher is better match
- `matched_keywords` - Which job keywords appeared in this snippet
- `match_count` - How many keywords matched

**Default:** Only includes snippets scoring ≥30%. Use `--min-score` to adjust.

### generate_draft.py

**Input:** Matched snippets (from match_snippets.py)  
**Output:** Formatted markdown (resume or cover letter)

```bash
# Resume (default)
python scripts/generate_draft.py matches.json --type resume

# Cover letter
python scripts/generate_draft.py matches.json --type cover-letter

# Save to file
python scripts/generate_draft.py matches.json --output draft.md

# With options
python scripts/generate_draft.py matches.json --type resume --top-n 5 --no-scores
```

**Output formats:**
- `--format markdown` (default) - Ready to paste into Google Docs
- `--format json` - Structured data for programmatic use

---

## 📊 Data Formats

### Parsed Job (JSON)

```json
{
  "source_type": "url|text",
  "all_keywords": ["python", "aws", "docker", ...],
  "keywords_detail": {
    "matched_keywords": [...],
    "technologies": [...],
    "years_of_experience": [...],
    "possible_job_titles": [...]
  },
  "requirements": ["Design REST APIs...", ...],
  "total_keywords": 42
}
```

### Snippets Library (JSON)

```json
{
  "resume_snippets": [
    {
      "id": "exp-001",
      "category": "experience|skills|achievements|leadership",
      "title": "Brief title",
      "text": "1-3 sentence snippet with keywords"
    }
  ]
}
```

### Matched Snippets (JSON)

```json
{
  "job_source": "url|text",
  "job_keywords_count": 42,
  "matched_snippets_count": 8,
  "matched_snippets": [
    {
      "id": "exp-001",
      "category": "experience",
      "title": "Backend Lead",
      "text": "...",
      "relevance_score": 85.5,
      "matched_keywords": ["python", "aws", ...],
      "match_count": 12
    }
  ]
}
```

---

## 🎓 Learning Path

### For Users (Resume Writers)
1. `QUICKSTART.md` - Get started in 5 minutes
2. `references/example-workflow.md` - See a real example
3. `SKILL.md` "Tips & Best Practices" - Improve your snippets
4. Experiment with your own snippets library

### For Developers / Integrators
1. `SKILL.md` entire document
2. `references/USAGE.md` - Technical details and schemas
3. Examine `scripts/*.py` - Code is readable and well-structured
4. Check JSON schemas for input/output formats
5. Integrate into your own tools

---

## 🚨 Troubleshooting

### "No snippets matched"
→ See `references/USAGE.md` "Troubleshooting" section

### "Relevance scores too low"
→ Try lowering `--min-score` threshold or adding more keywords to your snippets

### "Script not found"
→ Ensure you're in the `resume-draft` directory and scripts are executable

### "JSON parse error"
→ Check that JSON files are valid (use `jq .` to validate)

---

## 📈 Advanced Usage

### Batch process multiple jobs

```bash
for url in job1.txt job2.txt job3.txt; do
  jobname=$(basename "$url" .txt)
  python scripts/parse_job_description.py --url "$(cat $url)" > "parsed-$jobname.json"
  python scripts/match_snippets.py "parsed-$jobname.json" snippets.json > "matched-$jobname.json"
  python scripts/generate_draft.py "matched-$jobname.json" --output "resume-$jobname.md"
done
```

### Extract structured data for ATS scanning

```bash
python scripts/generate_draft.py matches.json --format json | jq '.snippets[] | {title, text, score: .relevance_score}' > ats-data.json
```

### Compare job fit across roles

```bash
jq '.matched_snippets | length' matched-role1.json matched-role2.json
jq '.matched_snippets[0].relevance_score' matched-role1.json matched-role2.json
```

---

## 🔮 Future Enhancements

Tracked in SKILL.md under "Future Enhancements":
- Semantic matching (AI-based similarity)
- LinkedIn profile import
- Google Docs integration
- ATS optimization analysis
- Multiple snippet source support
- Batch job processing

---

## 📝 Notes

- **No external dependencies** - Scripts use Python standard library only
- **No API calls** - Everything runs locally
- **Fast** - Typical workflow takes <2 seconds
- **Extensible** - Scripts output JSON for easy integration
- **Privacy-friendly** - Your snippets and job data stay on your machine

---

## 📞 Support

For detailed help:
- **Quick questions**: See `QUICKSTART.md`
- **Workflow questions**: See `references/example-workflow.md`
- **Technical questions**: See `references/USAGE.md`
- **How it works**: Read `SKILL.md` workflow sections

Last updated: 2026-03-28
