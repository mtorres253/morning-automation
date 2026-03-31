# Resume Draft - Quick Start (30 seconds)

## 1. Copy your snippets library

```bash
cp references/resume-snippets-template.json my-snippets.json
```

Edit `my-snippets.json` with your real resume snippets.

## 2. One-liner: From job URL to resume draft

```bash
# Customize the URL below
JOB_URL="https://example.com/jobs/123"

python scripts/parse_job_description.py --url "$JOB_URL" > parsed.json && \
python scripts/match_snippets.py parsed.json my-snippets.json > matches.json && \
python scripts/generate_draft.py matches.json --type resume --output resume-draft.md && \
cat resume-draft.md
```

## 3. From pasted job text

```bash
python scripts/parse_job_description.py \
  --text "Senior Engineer with 5+ years Python, AWS, Docker..." \
  > parsed.json

python scripts/match_snippets.py parsed.json my-snippets.json > matches.json
python scripts/generate_draft.py matches.json --type resume --output resume.md
```

## 4. Generate cover letter too

```bash
python scripts/generate_draft.py matches.json --type cover-letter --output cover-letter.md
```

## 5. Review & customize

- Open `resume.md` and `cover-letter.md` in your editor
- Reorder snippets as needed
- Edit for tone and personalization
- Copy-paste into Google Docs

---

## Full Manual Workflow

```bash
# Step 1: Parse job description
python scripts/parse_job_description.py --url "https://..." --output parsed.json

# Step 2: Match snippets
python scripts/match_snippets.py parsed.json my-snippets.json --output matches.json

# Step 3: Generate resume
python scripts/generate_draft.py matches.json --type resume --output resume.md

# Step 4: Generate cover letter
python scripts/generate_draft.py matches.json --type cover-letter --output cover-letter.md

# Step 5: Review
cat resume.md
cat cover-letter.md
```

## Options

```bash
# Only use top 5 snippets
python scripts/generate_draft.py matches.json --top-n 5

# Don't show relevance scores
python scripts/generate_draft.py matches.json --no-scores

# Output as JSON instead of markdown
python scripts/generate_draft.py matches.json --format json

# Stricter matching (only snippets >50% relevant)
python scripts/match_snippets.py parsed.json my-snippets.json --min-score 50 > matches.json
```

## Need help?

- See `SKILL.md` for full documentation
- See `references/USAGE.md` for technical details
- See `references/example-workflow.md` for real-world walkthrough

That's it! You now have tailored resume and cover letter drafts in 2 seconds.
