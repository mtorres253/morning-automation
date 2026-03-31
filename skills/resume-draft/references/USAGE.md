# Resume Draft - Technical Usage Guide

## Setup

### Python Requirements

```bash
python3 --version  # Requires Python 3.7+
pip install -r requirements.txt  # (Optional, scripts are dependency-free)
```

The scripts use only Python standard library (no external dependencies required).

### Directory Structure

```
resume-draft/
├── scripts/
│   ├── parse_job_description.py    # Step 1: Parse job
│   ├── match_snippets.py           # Step 2: Match & score
│   └── generate_draft.py           # Step 3: Generate draft
├── references/
│   ├── resume-snippets-template.json
│   └── USAGE.md (this file)
└── SKILL.md
```

## Detailed Script Reference

### Script 1: `parse_job_description.py`

Extract keywords, requirements, and technologies from a job posting.

#### Basic Usage

```bash
# From URL
python scripts/parse_job_description.py --url "https://careers.example.com/jobs/123"

# From text
python scripts/parse_job_description.py --text "Senior Python Engineer needed..."

# Save to file
python scripts/parse_job_description.py --url "https://..." --output parsed.json
```

#### Output Format

```json
{
  "source_type": "url",
  "all_keywords": [
    "5+ years",
    "python",
    "aws",
    "docker",
    "kubernetes",
    ...
  ],
  "keywords_detail": {
    "matched_keywords": ["5+ years", "python", "aws", ...],
    "technologies": ["Python", "AWS", "Docker", ...],
    "years_of_experience": ["5+ years"],
    "possible_job_titles": ["Senior Engineer", ...]
  },
  "requirements": [
    "Design and build scalable APIs...",
    "Lead architecture decisions...",
    ...
  ],
  "total_keywords": 42
}
```

#### How It Works

1. **Fetches URL** (if --url provided) using HTTP + strips HTML
2. **Extracts resume keywords** - matches common tech terms (Python, AWS, Docker, etc.)
3. **Identifies technologies** - capitalized multi-word phrases
4. **Parses experience levels** - "5+ years", "10+ years"
5. **Extracts requirements** - finds bullet points and numbered lists
6. **Identifies job titles** - capitalized phrases that look like titles

#### Options

- `--url URL` - Job posting URL (fetches and parses HTML)
- `--text TEXT` - Job description text
- `--output FILE` - Save JSON output (default: stdout)

### Script 2: `match_snippets.py`

Score each snippet based on keyword overlap with the job description.

#### Basic Usage

```bash
# Match snippets against parsed job
python scripts/match_snippets.py parsed.json snippets.json

# Save matches
python scripts/match_snippets.py parsed.json snippets.json --output matches.json

# Only include snippets with >50% match
python scripts/match_snippets.py parsed.json snippets.json --min-score 50

# Verbose output
python scripts/match_snippets.py parsed.json snippets.json --verbose
```

#### Output Format

```json
{
  "job_source": "url",
  "job_keywords_count": 42,
  "min_score_threshold": 30,
  "matched_snippets_count": 8,
  "matched_snippets": [
    {
      "id": "exp-001",
      "category": "experience",
      "title": "Backend Engineering Lead",
      "text": "Led architecture and delivery...",
      "relevance_score": 85.2,
      "matched_keywords": ["python", "aws", "microservices", ...],
      "match_count": 12
    },
    ...
  ]
}
```

#### Scoring Algorithm

For each snippet:
1. Split text into words
2. Count exact keyword matches (case-insensitive)
3. Calculate: `score = (matches / total_keywords) × 100`
4. Rank by score (highest first)

**Example:**
- Job has 40 keywords
- Snippet matches 12 of them
- Score = (12 / 40) × 100 = 30%

#### Options

- `job_file` - Parsed job JSON (required)
- `snippets_file` - Snippets library JSON (required)
- `--output FILE` - Save JSON output (default: stdout)
- `--min-score N` - Only include snippets with score >= N% (default: 30)
- `--verbose` - Print debug info to stderr

### Script 3: `generate_draft.py`

Format matched snippets into a markdown resume or cover letter.

#### Basic Usage

```bash
# Generate resume (default)
python scripts/generate_draft.py matches.json

# Generate cover letter
python scripts/generate_draft.py matches.json --type cover-letter

# Save to file
python scripts/generate_draft.py matches.json --output draft.md

# Use only top 5 snippets
python scripts/generate_draft.py matches.json --top-n 5

# Without relevance scores
python scripts/generate_draft.py matches.json --no-scores

# Output as JSON
python scripts/generate_draft.py matches.json --format json
```

#### Resume Output Format

```markdown
# Tailored Resume Draft

**Overall Match Score: 82.3%**

## Experience

**[85%]** Led architecture and delivery of **microservices platform** using **Python** and **AWS**, reducing API latency by 40%...

**[72%]** Built **REST APIs** with **Django** and **React** frontends...

## Technical Skills

**[91%]** Expert in **Python** (8+ years), **Django**, **async programming**...

...
```

#### Cover Letter Output Format

```markdown
# Cover Letter Draft

**Relevance Score: 82.3%**

---

## Opening Paragraph

[Personalize: Add company name, hiring manager name, and why you're excited...]

## Why I'm a Great Fit

### Backend Engineering Lead
[Match: 85%] Led architecture and delivery...

### DevOps & Cloud Infrastructure
[Match: 78%] Proficient in Docker, Kubernetes...

## Closing Paragraph

[Personalize: Thank them for considering...]
```

#### Options

- `matches_file` - Matched snippets JSON (required)
- `--type {resume|cover-letter}` - Draft type (default: resume)
- `--output FILE` - Save to file (default: stdout)
- `--top-n N` - Use only top N snippets
- `--format {markdown|json}` - Output format (default: markdown)
- `--no-scores` - Hide relevance scores

## Complete Workflow Example

```bash
# 1. Parse job description
python scripts/parse_job_description.py \
  --url "https://example.com/jobs/senior-python-engineer" \
  --output parsed.json

# 2. Match snippets against job
python scripts/match_snippets.py parsed.json my-snippets.json \
  --min-score 25 \
  --output matches.json

# 3. Generate resume draft
python scripts/generate_draft.py matches.json \
  --type resume \
  --output my-resume-draft.md

# 4. Generate cover letter draft
python scripts/generate_draft.py matches.json \
  --type cover-letter \
  --output my-cover-letter-draft.md

# 5. Review drafts in your editor
cat my-resume-draft.md
cat my-cover-letter-draft.md

# 6. Copy-paste into Google Docs for final editing
```

Or as a one-liner (resume):
```bash
python scripts/parse_job_description.py --url "https://..." > parsed.json && \
python scripts/match_snippets.py parsed.json my-snippets.json > matches.json && \
python scripts/generate_draft.py matches.json --type resume --output draft.md && \
cat draft.md
```

## Snippets Library Management

### Creating Your Library

Start with the template:
```bash
cp references/resume-snippets-template.json my-snippets.json
```

Edit in any text editor (JSON format). Keep it organized by category:
- `experience` - Job roles, projects, responsibilities
- `skills` - Technical proficiencies
- `achievements` - Quantified results, awards
- `leadership` - Team management, mentoring

### Adding New Snippets

Each snippet needs:
- `id` - Unique identifier (e.g., "exp-001", "skill-python")
- `category` - One of: experience, skills, achievements, leadership
- `title` - Brief description (1-3 words)
- `text` - Full snippet text (1-3 sentences, with keywords)

**Good snippet example:**
```json
{
  "id": "exp-004",
  "category": "experience",
  "title": "Platform Architect at Enterprise Co",
  "text": "Designed and implemented microservices architecture supporting 5M+ users, led team of 8 engineers, and established CI/CD best practices using GitHub Actions and Docker."
}
```

**Bad snippet example (too vague):**
```json
{
  "id": "exp-004",
  "category": "experience",
  "title": "Senior Engineer",
  "text": "Worked on various projects and accomplished things."
}
```

### Tips for Better Matching

- **Include specific technologies**: "Python", "Docker", "AWS" (not just "programming")
- **Use quantifiable results**: "reduced latency 40%", "supported 10M requests" 
- **Vary snippet length**: Mix 1-sentence and 3-sentence snippets
- **Group related snippets**: Similar skills under same category
- **Use industry keywords**: "microservices", "scalable", "REST API", "agile"

## JSON Schema Reference

### Parsed Job Format

```json
{
  "source_type": "url|text",
  "all_keywords": [string],
  "keywords_detail": {
    "matched_keywords": [string],
    "technologies": [string],
    "years_of_experience": [string],
    "possible_job_titles": [string]
  },
  "requirements": [string],
  "total_keywords": number
}
```

### Snippets Library Format

```json
{
  "resume_snippets": [
    {
      "id": string,
      "category": "experience|skills|achievements|leadership|other",
      "title": string,
      "text": string
    }
  ]
}
```

### Matched Snippets Format

```json
{
  "job_source": "url|text",
  "job_keywords_count": number,
  "min_score_threshold": number,
  "matched_snippets_count": number,
  "matched_snippets": [
    {
      "id": string,
      "category": string,
      "title": string,
      "text": string,
      "relevance_score": number,
      "matched_keywords": [string],
      "match_count": number
    }
  ]
}
```

## Troubleshooting

### No matches found

**Problem:** "matched_snippets_count": 0

**Solutions:**
1. Lower the `--min-score` threshold (try 20 or 15 instead of 30)
2. Check that snippets contain job keywords (e.g., "Python", "AWS")
3. Ensure job description was parsed correctly (check `parsed.json`)
4. Add more keywords to your snippets library

### Low relevance scores

**Problem:** All matched snippets have scores <50%

**Solutions:**
1. Your snippets may not match the job well (consider this)
2. Job description may not have clear keywords
3. Try pasting full job description (with "nice to haves") for more context
4. Add more specific snippets for this type of role

### HTML parsing issues

**Problem:** Error fetching URL or garbled text in parsed output

**Solutions:**
1. Ensure URL is publicly accessible (no login required)
2. Try copying job text and using `--text` instead of `--url`
3. Job site may block automated fetching; try manual copy-paste

## Performance Notes

- **Parsing:** ~1-2 seconds for typical job posting
- **Matching:** <100ms for 15 snippets against 40 keywords
- **Generation:** <100ms to format output

No external API calls needed - everything runs locally.

## File Size Limits

- Job descriptions: Tested up to 20KB (typical job is 2-5KB)
- Snippets library: Tested with 100+ snippets (typical use is 15-30)
- Output files: Markdown drafts typically 2-5KB

For very large snippet libraries (100+), consider splitting into multiple files by role (e.g., `snippets-backend.json`, `snippets-fullstack.json`).
