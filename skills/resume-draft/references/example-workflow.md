# Example Workflow: Complete Job Application

This document walks through a real-world example using the resume-draft skill.

## Scenario

Michael is applying for a **Senior Backend Engineer** role at TechCorp. The job posting is at:
`https://techcorp.example.com/careers/senior-backend-engineer-123`

He has a library of resume snippets in `my-snippets.json` and wants to:
1. Generate a tailored resume draft
2. Generate a cover letter draft
3. Review both and customize before submission

## Step 1: Set up the snippets library

Michael copies the template and adds his own snippets:

```bash
cp references/resume-snippets-template.json my-snippets.json
```

He edits `my-snippets.json` to include:
- Experience from his last 3 roles
- Skills in Python, AWS, Docker, Kubernetes
- Key achievements with metrics
- Leadership experience

(In this example, we're using the provided template snippets as his library.)

## Step 2: Parse the job description

He fetches and parses the job posting:

```bash
python scripts/parse_job_description.py \
  --url "https://techcorp.example.com/careers/senior-backend-engineer-123" \
  --output job-parsed.json
```

**Output (job-parsed.json):**
```json
{
  "source_type": "url",
  "all_keywords": [
    "5+ years",
    "python",
    "aws",
    "docker",
    "kubernetes",
    "microservices",
    "rest api",
    "sql",
    "team",
    "leadership",
    ...
  ],
  "keywords_detail": {
    "matched_keywords": [
      "5+ years",
      "python",
      "aws",
      "docker",
      "kubernetes",
      "microservices",
      "rest",
      "sql",
      "team",
      "leadership",
      ...
    ],
    "technologies": [
      "Python",
      "AWS",
      "Docker",
      "Kubernetes",
      "PostgreSQL",
      "Redis",
      ...
    ],
    "years_of_experience": [
      "5+ years"
    ],
    "possible_job_titles": [
      "Senior Backend Engineer",
      "Tech Lead",
      "Platform Engineer"
    ]
  },
  "requirements": [
    "Design and build REST APIs in Python",
    "Lead architecture decisions for microservices",
    "Mentor junior engineers",
    "Own deployment and infrastructure",
    ...
  ],
  "total_keywords": 42
}
```

## Step 3: Match snippets against the job

He scores his snippets against the parsed job:

```bash
python scripts/match_snippets.py job-parsed.json my-snippets.json \
  --output matches.json \
  --verbose
```

**Console output:**
```
Job keywords extracted: 42
Snippets loaded: 15
Snippets matching threshold (30%+): 10
Matched snippets saved to matches.json
```

**matches.json preview:**
```json
{
  "job_source": "url",
  "job_keywords_count": 42,
  "min_score_threshold": 30,
  "matched_snippets_count": 10,
  "matched_snippets": [
    {
      "id": "exp-001",
      "category": "experience",
      "title": "Backend Engineering Lead at TechCorp",
      "text": "Led architecture and delivery of microservices platform using Python and AWS...",
      "relevance_score": 92.3,
      "matched_keywords": [
        "python",
        "aws",
        "microservices",
        "leadership",
        "docker",
        ...
      ],
      "match_count": 12
    },
    {
      "id": "skill-python",
      "category": "skills",
      "title": "Python & Backend Development",
      "text": "Expert in Python (8+ years), Django REST Framework, FastAPI...",
      "relevance_score": 88.1,
      "matched_keywords": [
        "python",
        "rest api",
        "5+ years",
        ...
      ],
      "match_count": 10
    },
    ...
  ]
}
```

**Key insight:** The top 3 snippets have 85%+ relevance scores - excellent matches!

## Step 4: Generate resume draft

He generates a formatted markdown resume:

```bash
python scripts/generate_draft.py matches.json \
  --type resume \
  --output my-resume-draft.md
```

**my-resume-draft.md output:**
```markdown
# Tailored Resume Draft

**Overall Match Score: 82.3%**

## Experience

**[92.3%]** Led architecture and delivery of **microservices platform** using **Python** and **AWS**, reducing API latency by 40% and supporting 10M+ daily requests across 5 services.

**[81.5%]** Built **REST APIs** with **Django REST Framework**, implemented automated testing (**pytest**), and deployed infrastructure using **Docker** and **Kubernetes** on **AWS**.

## Technical Skills

**[88.1%]** Expert in **Python** (8+ years), **Django REST Framework**, **FastAPI**, **async programming** (asyncio), and designing scalable backend systems for high-traffic applications.

**[85.2%]** Proficient in **Docker**, **Kubernetes**, **AWS** services (EC2, RDS, S3, Lambda), **CI/CD** pipelines (**GitHub Actions**, Jenkins), and infrastructure-as-code (Terraform).

**[79.8%]** Deep expertise in **PostgreSQL**, **MySQL**, **MongoDB**, query optimization, and designing scalable database schemas. Experience with **Redis** for caching and pub/sub.

## Key Achievements

**[78.5%]** Redesigned database queries and added caching layer (**Redis**), reducing page load time from 3s to 400ms (87% improvement) and saving $50K/year in infrastructure costs.

**[76.2%]** Established automated testing and **CI/CD** pipeline, reducing deployment time from 2 hours to 15 minutes and cutting production bugs by 60% in 6 months.

## Leadership & Mentoring

**[82.1%]** Managed **team** of 5 engineers, conducted code reviews, mentored 3 junior developers (2 promoted within 18 months), and fostered agile/scrum practices.

**[79.3%]** Designed system architecture for new product line supporting 100K+ concurrent users. Led migration from monolith to **microservices** (6-month project, on-time and on-budget).
```

## Step 5: Generate cover letter draft

He generates a structured cover letter:

```bash
python scripts/generate_draft.py matches.json \
  --type cover-letter \
  --output my-cover-letter-draft.md
```

**my-cover-letter-draft.md output:**
```markdown
# Cover Letter Draft

**Relevance Score: 82.3%**

---

## Opening Paragraph

[Personalize: Add company name, hiring manager name, and why you're excited about this role]

## Why I'm a Great Fit

### Backend Engineering Lead at TechCorp
**[Match: 92.3%]** Led architecture and delivery of **microservices platform** using **Python** and **AWS**, reducing API latency by 40% and supporting 10M+ daily requests across 5 services.

### Python & Backend Development
**[Match: 88.1%]** Expert in **Python** (8+ years), **Django REST Framework**, **FastAPI**, **async programming** (asyncio), and designing scalable backend systems for high-traffic applications.

### DevOps & Cloud Infrastructure
**[Match: 85.2%]** Proficient in **Docker**, **Kubernetes**, **AWS** services (EC2, RDS, S3, Lambda), **CI/CD** pipelines (**GitHub Actions**, Jenkins), and infrastructure-as-code (Terraform).

## Closing Paragraph

[Personalize: Thank them for considering your application, express enthusiasm, and indicate next steps]

---

**Notes for refinement:**
- Add personalization in opening and closing (company name, hiring manager, specific role details)
- Feel free to reorder, combine, or split snippets as needed
- Edit for flow and tone to match your voice
- Remove or deemphasize low-scoring items
```

## Step 6: Review and customize

Michael opens both drafts in his text editor and reviews them:

**Resume draft changes:**
- ✅ Reorders snippets by importance (experience first, then achievements)
- ✅ Removes lowest-scoring item (relevance score ~76%)
- ✅ Adds quantified metrics where missing
- ✅ Edits for tone and flow
- ✅ Adds "Senior Backend Engineer" as title

**Cover letter customization:**
- ✅ Opens with: "I'm excited to apply for the Senior Backend Engineer role at TechCorp..."
- ✅ Mentions hiring manager by name (from job posting)
- ✅ Explains why TechCorp specifically (company vision alignment)
- ✅ Adds 2-3 personal touches (why this role, what you'll bring)
- ✅ Closes with action item ("I'd love to discuss how I can contribute...")

## Step 7: Convert to Google Docs

Michael copies the markdown from `my-resume-draft.md` and:
1. Pastes into Google Docs (formatting preserved)
2. Adjusts font, spacing, margins as needed
3. Adds contact info and links
4. Final polish for ATS compatibility (no fancy formatting)

## Step 8: Final submission

He submits the tailored resume and cover letter to TechCorp, confident that:
- ✅ Both documents are tailored to the specific job posting
- ✅ Relevant snippets are highlighted with relevance scores
- ✅ Each snippet includes keywords from the job description (bold for ATS scanning)
- ✅ Overall match score (82.3%) shows strong alignment
- ✅ Documents are polished and ready to submit

## Quick Stats

| Metric | Value |
|--------|-------|
| Time to parse job | ~1 second |
| Time to match snippets | <100ms |
| Time to generate drafts | <100ms |
| Relevant snippets found | 10/15 (67%) |
| Highest match score | 92.3% |
| Overall match score | 82.3% |
| Total time (Steps 2-4) | ~2 seconds |

## Variations

### Using with multiple job applications

For efficiency, Michael could create multiple variants:

```bash
# Save results for each application
for job_url in job1.txt job2.txt job3.txt; do
  jobname=$(basename "$job_url" .txt)
  
  python scripts/parse_job_description.py --url "$(cat $job_url)" > "jobs/$jobname-parsed.json"
  python scripts/match_snippets.py "jobs/$jobname-parsed.json" my-snippets.json > "jobs/$jobname-matches.json"
  python scripts/generate_draft.py "jobs/$jobname-matches.json" --output "drafts/$jobname-resume.md"
done
```

This generates tailored resumes for each job in minutes.

### Using with a lower threshold

If the default 30% threshold filters out too much:

```bash
python scripts/match_snippets.py job-parsed.json my-snippets.json \
  --min-score 20 \
  --output matches.json
```

This captures more marginal matches (useful for roles that aren't a perfect fit).

### Using JSON output

For programmatic integration:

```bash
python scripts/generate_draft.py matches.json --format json > resume-data.json
```

This outputs structured data for your own processing (e.g., custom formatting, database storage).

## Tips for Best Results

1. **Comprehensive snippets library** - More snippets = more flexibility
2. **Specific, quantified snippets** - "Reduced latency 40%" beats "improved performance"
3. **Full job descriptions** - Paste entire job posting (including "nice to haves")
4. **Proofread after generation** - Drafts are tools, not final documents
5. **Reuse and iterate** - Use same library across multiple applications
6. **Track what works** - Save your final resume docs for feedback

Enjoy the time saved on resume customization!
