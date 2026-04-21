# LLM-Based Job Scoring System

## Overview

The job-search skill now uses Claude to intelligently score and rank jobs based on your profile, experience, and preferences.

## How It Works

### 1. Candidate Profile Loading
- Loads your `resumes.md` with all capabilities, experience, and background
- Claude uses this to understand your skills, expertise, and career level

### 2. Job Scoring (0-10 Scale)
For each job, Claude evaluates:
- **Title Match** — Director/VP/Principal preferred
- **Skills & Experience** — How well job requirements align with your background
- **Location Preference** — Weighted scoring:
  - SF proper / Remote = **highest** ⭐⭐⭐
  - Bay Area (non-SF) = **acceptable** ⭐⭐
  - Hybrid = **lower** ⭐
  - In-office non-Bay Area = **lowest**

Claude provides a brief reasoning for each score explaining the match.

### 3. Featured Section
Jobs scoring **7/10 or higher** appear in the **featured section** at the top of your email:
- Sorted by score (best first)
- Highlighted with gold badges
- Includes LLM's reasoning for why it's a good match
- "Why:" explanation helps you understand the match

### 4. Full Ranked List
All jobs (top 15 shown) appear below in ranked order:
- Sorted by score
- Quick glance at match percentage
- Featured jobs marked with ⭐ in the list

## What Changed

**File:** `scripts/filter_and_deliver.py`

**New Functions:**
- `load_candidate_profile()` — Reads resumes.md
- `score_job_with_llm()` — Uses Claude to score individual jobs
- `fallback_simple_score()` — Rule-based fallback if Claude unavailable

**Updated Functions:**
- `filter_and_rank_jobs()` — Now uses LLM, returns (featured, all_jobs) tuple
- `format_email_body()` — New layout with featured section first

**New Dependencies:**
- `anthropic` Python package (installed in venv)

## Email Layout

```
┌─────────────────────────────────┐
│ 🔍 Daily Job Search Digest      │
│ Found N matching jobs           │
└─────────────────────────────────┘

Search Status
✓ LinkedIn search successful
✓ Indeed search successful

═══════════════════════════════════
⭐ FEATURED MATCHES (3)
Top matches personalized to your profile
═══════════════════════════════════

[Featured Job 1] - 8.5/10
Why: Director-level product role at civic tech startup in SF...

[Featured Job 2] - 7.8/10
Why: Principal PM at enterprise SaaS in remote position...

═══════════════════════════════════
📋 ALL MATCHES (15)
Complete ranked list
═══════════════════════════════════

[All Jobs Ranked by Score]

... and N more jobs

Footer: How to manage preferences
```

## Configuration

### Environment Variables (Lambda)
- `ANTHROPIC_API_KEY` — Claude API key (required for scoring)

### Local Testing
Set the API key before running:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python3 scripts/filter_and_deliver.py
```

## How to Use

**For daily automated delivery:**
Lambda function at 9 AM PDT handles everything:
1. Searches for jobs (JSearch API)
2. Filters to new jobs
3. Loads your profile
4. Scores each job with Claude
5. Sends ranked digest email

**For manual testing:**
```bash
cd /Users/michaeltorres/.openclaw/workspace/skills/job-search
source venv/bin/activate
export ANTHROPIC_API_KEY="your-key-here"
python3 scripts/filter_and_deliver.py
```

## Fallback Behavior

If Claude is unavailable or API fails:
- Script automatically falls back to simple rule-based scoring
- "Fallback scoring" is noted in each job's reasoning
- Email still sends with scores and rankings

## Customization

**Want to adjust scoring weights?**
Edit the LLM prompt in `score_job_with_llm()` function to emphasize different criteria.

**Want to change featured threshold?**
Change the `7.0` score in `filter_and_rank_jobs()` function (line ~115).

**Want to adjust location preferences?**
Update the location scoring in the LLM prompt or fallback function.

## Notes

- First run will score all new jobs (may take a moment with many jobs)
- Subsequent runs only score new jobs that haven't been sent before
- Scores are stored in the `filtered_results_*.json` files for history
- You can review past scores in `skills/job-search/results/`

## Status

✅ Implemented and tested
✅ Anthropic SDK installed in venv
✅ Syntax validated
⏳ Ready for first Lambda execution
