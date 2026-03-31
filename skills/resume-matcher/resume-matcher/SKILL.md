---
name: resume-matcher
description: "Create tailored resume and cover letter drafts from original content. Use when: (1) you have a job description to match against, (2) you want to reorder/select your original resume and cover letter content to emphasize relevant experience, (3) you need draft documents using only your own writing (no AI rewording). Paste the job description, and the skill will create draft documents that highlight the most relevant original sections."
---

# Resume Matcher

Matches a job description against your resume and cover letter content, creating draft documents that emphasize relevant experience using only your original writing.

## Workflow

1. **Paste the job description** — Share the full job posting or description
2. **Specify your content files** — Point to your resume and cover letter markdown files (default: `/Users/michaeltorres/Downloads/resumes.md` and `/Users/michaeltorres/Downloads/cover_letters.md`)
3. **Generate drafts** — The skill extracts keywords from the job description and reorders your existing content to prioritize relevance
4. **Edit and refine** — You then polish the drafts for submission

## How It Works

- **Keyword extraction** — Analyzes the job description to identify key skills, technologies, and concepts
- **Content scoring** — Rates each work experience and cover letter section by relevance to those keywords
- **Intelligent reordering** — Ranks your original content from most to least relevant, without changing any wording
- **Draft output** — Creates two markdown files: `resume_draft.md` and `cover_letter_draft.md`

## Key Features

✓ **Zero AI rewording** — All content is yours; no generated or rephrased text
✓ **Preserves formatting** — Maintains your original markdown structure and styling
✓ **Multiple sections** — Works with all resume sections (work history, skills, education, etc.)
✓ **Quick iteration** — Regenerate drafts instantly as you refine the job match

## Getting Started

### Step 1: Prepare Your Content Files

Have your resume and cover letter in markdown format. The skill expects:

- **Resume**: Structured by sections (## Work History, ## Skills, etc.) with work experiences as `### Role — Company`
- **Cover letter**: Paragraphs or sections separated by blank lines

Default locations:
- Resume: `/Users/michaeltorres/Downloads/resumes.md`
- Cover letter: `/Users/michaeltorres/Downloads/cover_letters.md`

### Step 2: Paste the Job Description

Share the complete job posting. The skill will extract keywords to match against your content.

### Step 3: Run the Matcher

The skill will:
1. Extract keywords and themes from the job description
2. Score each experience/paragraph in your resume and cover letter
3. Create two draft markdown files (in your current directory or specified output location)
4. Show relevance scores so you can understand the matching

### Step 4: Review and Edit

Open the draft files and refine:
- Reorder sections if you disagree with the scoring
- Add context or remove less relevant bullets
- Customize the cover letter opening/closing
- Adjust formatting as needed

## Usage Examples

**Example 1: Product Manager role**

> _Paste job description for a PM role at a tech company_

The skill reorders your work history to highlight product-focused experiences (e.g., UTM platform, product operations) above non-product roles, while keeping all original wording intact.

**Example 2: Engineering role**

> _Paste job description for an engineering position_

The skill prioritizes technical experiences and skills sections that match technologies mentioned (Python, AWS, CI/CD, etc.).

## Technical Details

See `scripts/match_resume.py` for the matching algorithm. The script:
- Parses markdown sections and work experiences
- Extracts and normalizes keywords from job descriptions
- Scores content relevance using keyword overlap
- Outputs two markdown files with sorted sections

To run manually:

```bash
python3 scripts/match_resume.py <job_description.txt> <resume.md> <cover_letter.md> [output_dir]
```

## Tips for Best Results

1. **Use clear markdown structure** — Section headers and bullet points help the skill identify content boundaries
2. **Be specific in job descriptions** — Paste the full job posting for better keyword extraction
3. **Keep original content focused** — Shorter, specific bullet points score better than vague paragraphs
4. **Review the scoring** — Check which experiences ranked highest to understand the matching logic
5. **Customize the output** — The draft is a starting point; adjust ranking and emphasis as needed

## What This Skill Does NOT Do

- ✗ Rewrite or rephrase your content
- ✗ Generate new bullet points or accomplishments
- ✗ Create entirely new cover letters
- ✗ Change your resume structure (only reorders existing sections)

Use this skill to organize and highlight your original content, then polish manually.
