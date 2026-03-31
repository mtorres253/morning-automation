---
name: resume-draft
description: Match user's resume snippets against job descriptions to compile tailored draft resumes and cover letters. Use when: (1) user provides a job description (URL or text) and wants a draft resume/cover letter, (2) user wants to match their resume library against specific job postings, (3) user needs help identifying which resume snippets are most relevant to a target role. Supports keyword extraction, relevance scoring (0-100%), and markdown output optimized for Google Docs.
---

# Resume Draft Skill

Quickly compile tailored resume drafts and cover letters by matching your resume snippets library against job descriptions. This skill extracts job requirements, scores your snippets for relevance, and outputs a ready-to-customize markdown draft.

## Quick Start

### 1. Set up your snippets library

Create a JSON file with your resume snippets (see `references/resume-snippets-template.json`):

```bash
cp references/resume-snippets-template.json my-snippets.json
```

Edit to add your own snippets across categories: experience, skills, achievements, leadership.

### 2. Generate a resume draft

From a job URL:
```bash
python scripts/parse_job_description.py --url "https://example.com/jobs/123" > job_parsed.json
python scripts/match_snippets.py job_parsed.json my-snippets.json > matches.json
python scripts/generate_draft.py matches.json --type resume --output draft.md
```

From pasted job text:
```bash
echo "Senior Software Engineer - Python, AWS, Docker..." > job.txt
python scripts/parse_job_description.py --text "$(cat job.txt)" > job_parsed.json
python scripts/match_snippets.py job_parsed.json my-snippets.json > matches.json
python scripts/generate_draft.py matches.json --type resume --output draft.md
```

### 3. Review and customize

Open `draft.md` in your editor. Relevance scores are included for each snippet. Reorder, edit, or add context as needed. Convert to Google Docs via copy-paste (markdown formatting is preserved).

## Workflow

### Step 1: Parse Job Description

`parse_job_description.py` extracts key requirements and keywords from a job posting (URL or text).

**Input:** URL or job description text
**Output:** JSON with extracted keywords, requirements, and technologies

```bash
python scripts/parse_job_description.py --url "https://..." 
python scripts/parse_job_description.py --text "job description text..."
```

**How it works:**
- Extracts capitalized phrases (likely role names, company-specific terms)
- Identifies required skills and technologies
- Parses requirements lists
- Scores common resume keywords (5+ years, leadership, team, etc.)

### Step 2: Match Snippets

`match_snippets.py` scores each snippet based on keyword overlap with the job description.

**Input:** Parsed job (from Step 1) + snippets library
**Output:** Ranked snippets with relevance scores

```bash
python scripts/match_snippets.py job_parsed.json snippets.json > matches.json
```

**Scoring:**
- Each snippet gets a relevance score (0-100%)
- Score = (matched keywords / total job keywords) × 100
- Snippets ranked highest-to-lowest by relevance
- Includes breakdown of which keywords matched

### Step 3: Generate Draft

`generate_draft.py` compiles top-matching snippets into a formatted markdown draft.

**Input:** Matched snippets (from Step 2)
**Output:** Markdown draft (resume or cover letter)

```bash
# Resume draft
python scripts/generate_draft.py matches.json --type resume --output my-resume.md

# Cover letter draft
python scripts/generate_draft.py matches.json --type cover-letter --output my-cover-letter.md
```

**Options:**
- `--type`: `resume` (default) or `cover-letter`
- `--output`: output filename (default: stdout)
- `--top-n`: use only top N snippets (default: 5)
- `--min-score`: only include snippets above threshold (default: 30%)

## Input Format

### Job Description

Accept either:
- **URL:** `--url "https://example.com/jobs/123"` (fetches and parses HTML)
- **Text:** `--text "Senior Engineer needed..."` (parses provided text)

### Snippets Library

JSON format (see `references/resume-snippets-template.json`):

```json
{
  "resume_snippets": [
    {
      "id": "exp-001",
      "category": "experience",
      "title": "Backend Engineering Lead",
      "text": "Led architecture and delivery of microservices platform, reducing API latency by 40% and supporting 10M+ daily requests."
    },
    {
      "id": "skill-python",
      "category": "skills",
      "title": "Python & Django",
      "text": "Expert in Python (8+ years), Django REST framework, async programming (asyncio), and building scalable backend systems."
    }
  ]
}
```

**Categories:**
- `experience` - Job roles, projects, major accomplishments
- `skills` - Technical proficiencies, languages, tools
- `achievements` - Quantified results, awards, recognitions
- `leadership` - Team building, mentoring, management experience

## Output Format

Markdown with:
- **Section headers** by category
- **Bold keywords** (from job description) to highlight relevance
- **Relevance scores** for each snippet (for your review)
- **Google Docs ready** - paste directly into Google Docs, formatting preserved

Example output:
```markdown
# Senior Software Engineer

**Match: 92%**

## Experience

**[92%]** Led architecture and delivery of **microservices platform** on **AWS**, reducing API latency by 40% and supporting 10M+ daily requests.

## Technical Skills

**[85%]** Expert in **Python** (8+ years), **Django REST framework**, **async programming**, and building scalable **backend systems**.

**[78%]** Proficient in **Docker**, **Kubernetes**, and CI/CD pipelines using GitHub Actions and Jenkins.
```

## Snippets Library Management

### Editing snippets

Edit `my-snippets.json` directly in your editor. Each snippet is self-contained.

### Adding new snippets

Add entries to the `resume_snippets` array. Use clear, action-oriented language:
- ✅ "Led team of 5 engineers..." (good)
- ❌ "Responsible for team" (weak)

### Organizing snippets

Group by category. Within a category, order by:
1. Most recent/relevant first
2. Most impressive achievements first

### Removing snippets

Delete entries you no longer want to use. Keep a simple version history if needed (e.g., `my-snippets-2026-03.json`).

## Matching Algorithm

### Keyword Extraction

From the job description, we extract:
- **Skills** - Languages, frameworks, tools (Python, AWS, Docker, etc.)
- **Requirements** - Experience levels, soft skills ("5+ years", "team player", etc.)
- **Roles/Titles** - Capitalized phrases indicating seniority or focus areas

### Scoring

For each snippet:
1. Split text into words
2. Count matches against extracted job keywords (case-insensitive)
3. Calculate: `score = (matches / total_keywords) × 100`
4. Rank all snippets by score

**Threshold:** By default, only snippets with >30% match are included. Adjust with `--min-score`.

## Tips & Best Practices

### Snippet tips

- **Be specific:** "Reduced API latency from 500ms to 300ms" beats "improved performance"
- **Include metrics:** Numbers and percentages stand out
- **Vary length:** 1-3 sentence snippets work best
- **Use keywords:** Include technologies you actually used (Python, AWS, Docker, etc.)

### Job description tips

- Paste the full job description for best results (more keywords to match)
- Include job title, company context if available
- Include "nice to have" section (bonus keywords)

### Draft customization

After generation:
- **Reorder snippets** by importance for the specific role
- **Remove low-scoring snippets** that feel forced
- **Add context** - insert company name, role title at the top
- **Edit for flow** - combine or split snippets as needed
- **Polish language** - match your voice and tone

## Examples

### Example 1: Backend Engineer to AI/ML Role

Job description: "Looking for AI engineer with ML ops experience, Python, Kubernetes, data pipelines."

Your library includes snippets on:
- Python backend work (high match)
- Kubernetes/DevOps (high match)
- Data engineering (medium match)
- Frontend React (low match - excluded)

Generated draft highlights Python, data systems, and ops work. You review and reorder to emphasize ML-adjacent projects.

### Example 2: Cover Letter from Resume

Parse job → match snippets → generate cover letter draft with:
- Opening: Most relevant achievement
- Middle: 2-3 key skills matching job requirements
- Closing: Why you're interested in the role

Edit to add personalization (company name, hiring manager name, etc.).

## Technical Details

See `references/USAGE.md` for:
- Python dependencies and setup
- Script command-line API
- JSON schema details
- Troubleshooting common issues

## Future Enhancements

- Semantic matching (AI-based similarity)
- Multiple snippet sources (pull from LinkedIn, ATS, etc.)
- Google Docs integration (auto-create draft in your Drive)
- LinkedIn profile import
- ATS optimization analysis
- Batch job processing
