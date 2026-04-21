#!/usr/bin/env python3
"""
Filter jobs and deliver via email digest.
Reads raw job search results, applies filtering/ranking, and sends email.
Uses LLM-based scoring to match jobs against candidate profile.
"""

import json
import os
import smtplib
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

CONFIG_PATH = Path(__file__).parent.parent / "job-search-config.json"
INTERACTIONS_PATH = Path(__file__).parent.parent / "job-interactions.json"

# Use /tmp for Lambda compatibility (read-only filesystem in Lambda)
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    RESULTS_DIR = Path("/tmp") / "job-search-results"
    SENT_JOBS_PATH = Path("/tmp") / "sent-jobs.json"
else:
    RESULTS_DIR = Path(__file__).parent.parent / "results"
    SENT_JOBS_PATH = Path(__file__).parent.parent / "sent-jobs.json"

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

# Load interaction history (for learning)
interactions = {}
if INTERACTIONS_PATH.exists():
    with open(INTERACTIONS_PATH, "r") as f:
        interactions = json.load(f)

# Load previously sent jobs (to track what's no longer posted)
sent_jobs = {}
if SENT_JOBS_PATH.exists():
    with open(SENT_JOBS_PATH, "r") as f:
        sent_jobs = json.load(f)

def load_latest_results() -> Dict[str, Any]:
    """Load the latest raw results file."""
    result_files = sorted(RESULTS_DIR.glob("raw_results_*.json"), reverse=True)
    if not result_files:
        raise FileNotFoundError("No job search results found")
    
    with open(result_files[0], "r") as f:
        return json.load(f)

def filter_to_new_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Return jobs that are either:
    1. New (never sent before)
    2. Previously sent but still want to show for up to 3 days
    
    Jobs disappear from listings after 3 days or when they're no longer in search results.
    """
    shown_jobs = []
    current_job_ids = {j.get("jobId") for j in jobs}
    
    for job in jobs:
        job_id = job.get("jobId")
        
        if job_id in sent_jobs:
            # Job was sent before - check if still within 3-day window
            sent_record = sent_jobs[job_id]
            sent_date = datetime.fromisoformat(sent_record["sentDate"])
            days_since_sent = (datetime.now() - sent_date).days
            
            if days_since_sent < 3:
                # Still within 3-day window, show it again
                shown_jobs.append(job)
                # Update the sent date to track the most recent showing
                sent_jobs[job_id]["sentDate"] = datetime.now().isoformat()
            else:
                # Past 3 days, remove from tracking
                del sent_jobs[job_id]
        else:
            # New job, always show it
            shown_jobs.append(job)
            sent_jobs[job_id] = {
                "title": job.get("title"),
                "company": job.get("company"),
                "sentDate": datetime.now().isoformat()
            }
    
    return shown_jobs

def load_candidate_profile() -> str:
    """
    Load the candidate's resume/profile from resumes.md.
    Falls back to a default profile if not found.
    """
    # Try workspace first, then home
    resume_path = Path.home() / ".openclaw" / "workspace" / "assets" / "job-search" / "resumes.md"
    if not resume_path.exists():
        resume_path = Path.home() / ".openclaw" / "assets" / "job-search" / "resumes.md"
    
    if resume_path.exists():
        with open(resume_path, "r") as f:
            return f.read()
    else:
        # Default profile for fallback
        return """
        Product leader with 12+ years building mission-critical digital platforms 
        supporting complex service delivery across aviation, government, and enterprise environments.
        Expertise in strategic leadership, product operations, compliance-driven development,
        and cross-functional team leadership.
        """

def score_job_with_llm(job: Dict[str, Any], candidate_profile: str) -> Tuple[float, str]:
    """
    Use Claude to intelligently score a job against the candidate profile.
    Returns (score: 0-10, reasoning: brief explanation).
    
    Scoring factors:
    - Title match (Director/VP/Principal preferred)
    - Skills/experience alignment
    - Location (SF/remote highest, Bay Area middle, hybrid lower, in-office non-SF lowest)
    """
    if not HAS_ANTHROPIC:
        # Fallback to simple scoring if Anthropic not available
        return fallback_simple_score(job, candidate_profile), "Simple scoring (Claude unavailable)"
    
    try:
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        
        prompt = f"""
You are an expert recruiter matching job opportunities to a candidate's profile.

CANDIDATE PROFILE:
{candidate_profile}

JOB OPPORTUNITY:
Title: {job.get('title', 'Unknown')}
Company: {job.get('company', 'Unknown')}
Location: {job.get('location', 'Unknown')}
Salary: {job.get('salary', 'Not specified')}
Job Description: {job.get('snippet', 'No description available')[:500]}

SCORING INSTRUCTIONS:
Rate this job fit on a scale of 0-10 based on:
1. Title Match (Director/VP/Principal preferred): Does the title align with the candidate's level?
2. Skills & Experience: How well do the job requirements match the candidate's experience?
3. Location Preference: 
   - SF proper or Remote = highest preference
   - Bay Area (non-SF) = acceptable but lower
   - Hybrid = lower than remote
   - In-office non-Bay Area = lowest preference

Be realistic and honest. A score of 7+ means this is a strong match worth featuring.

Respond with ONLY:
SCORE: <number 0-10>
REASONING: <one sentence explaining the score>

Example:
SCORE: 8
REASONING: Director-level product role at AI-focused startup in SF with strong product/strategy background match.
"""
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        text = response.content[0].text.strip()
        
        # Parse response
        score_match = re.search(r'SCORE:\s*(\d+(?:\.\d+)?)', text)
        reasoning_match = re.search(r'REASONING:\s*(.+?)(?:\n|$)', text)
        
        score = float(score_match.group(1)) if score_match else 5.0
        reasoning = reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"
        
        return min(max(score, 0), 10), reasoning
    
    except Exception as e:
        print(f"⚠️  LLM scoring failed ({e}), using fallback")
        return fallback_simple_score(job, candidate_profile), "Fallback scoring"

def fallback_simple_score(job: Dict[str, Any], candidate_profile: str) -> float:
    """
    Simple rule-based scoring when LLM is unavailable.
    """
    score = 5.0  # Base score
    
    # Title match
    title_lower = job.get("title", "").lower()
    if any(x in title_lower for x in ["director", "vp", "vice president", "principal"]):
        score += 2.0
    
    # Location preference
    location_lower = job.get("location", "").lower()
    if "san francisco" in location_lower or "sf" in location_lower:
        score += 1.5
    elif "remote" in location_lower:
        score += 1.5
    elif "bay area" in location_lower or "oakland" in location_lower or "palo alto" in location_lower:
        score += 1.0
    elif "hybrid" in location_lower:
        score += 0.5
    
    # Salary check (200-250K range preferred)
    salary_text = job.get("salary", "").lower()
    if any(str(n) in salary_text for n in range(200, 251)):
        score += 1.0
    
    return min(max(score, 0), 10)

def filter_and_rank_jobs(jobs: List[Dict[str, Any]], candidate_profile: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Filter and rank jobs using LLM-based scoring.
    Returns (featured_jobs: 7+/10, full_ranked_jobs: all jobs ranked by score).
    """
    print(f"📊 Scoring {len(jobs)} jobs with LLM...")
    
    # Calculate scores for all jobs
    for i, job in enumerate(jobs, 1):
        score, reasoning = score_job_with_llm(job, candidate_profile)
        job["score"] = score
        job["scoreReasoning"] = reasoning
        print(f"  [{i}/{len(jobs)}] {job.get('title', 'Unknown')[:40]:40s} → {score}/10")
    
    # Sort all jobs by score (descending)
    ranked_all = sorted(jobs, key=lambda j: j["score"], reverse=True)
    
    # Separate featured jobs (7+)
    featured = [j for j in ranked_all if j["score"] >= 7.0]
    
    print(f"\n✅ Featured ({len(featured)}): {[j.get('title', '')[:30] for j in featured]}")
    print(f"📋 Full list ({len(ranked_all)} total)\n")
    
    return featured, ranked_all

def group_jobs_by_category(jobs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group jobs by title category."""
    groups = {
        "Director of Product": [],
        "Principal Product Manager": [],
        "Chief of Staff": [],
        "Product Operations": [],
        "Other": []
    }
    
    for job in jobs:
        title_lower = job["title"].lower()
        if "director" in title_lower and "product" in title_lower:
            groups["Director of Product"].append(job)
        elif "principal" in title_lower and "product" in title_lower:
            groups["Principal Product Manager"].append(job)
        elif "chief of staff" in title_lower:
            groups["Chief of Staff"].append(job)
        elif "product operations" in title_lower or "product ops" in title_lower:
            groups["Product Operations"].append(job)
        else:
            groups["Other"].append(job)
    
    # Remove empty groups
    return {k: v for k, v in groups.items() if v}

def format_email_body(featured_jobs: List[Dict[str, Any]], all_jobs: List[Dict[str, Any]], search_status: List[str] = None) -> str:
    """Format jobs into an HTML email body with featured section first."""
    
    # Build search status section (always shown)
    status_html = ""
    if search_status:
        status_html = """
        <div class="search-status">
            <h3 style="color: #2c5aa0; margin-top: 0;">Search Status</h3>
        """
        for status in search_status:
            if status.startswith("✓"):
                status_color = "#28a745"  # Green
            elif status.startswith("✗"):
                status_color = "#dc3545"  # Red
            else:
                status_color = "#ffc107"  # Yellow
            
            status_html += f"""
            <div style="color: {status_color}; font-size: 14px; margin: 5px 0; font-weight: 500;">
                {status}
            </div>
            """
        status_html += "</div>"
    
    # Build featured section (7+/10)
    featured_html = ""
    if featured_jobs:
        featured_html = """
        <div class="featured-section">
            <h2 style="color: #d4af37; margin-bottom: 15px; border-bottom: 3px solid #d4af37; padding-bottom: 10px;">
                ⭐ Featured Matches ({})
            </h2>
            <p style="color: #666; font-size: 13px; margin-bottom: 15px;">
                Top matches (7+/10) personalized to your profile
            </p>
        """.format(len(featured_jobs))
        
        for job in featured_jobs:
            score = job.get("score", 0)
            reasoning = job.get("scoreReasoning", "")
            featured_html += f"""
            <div class="featured-job">
                <div class="job-title">{job.get('title', 'Unknown Position')}</div>
                <div class="job-company">{job.get('company', 'Unknown Company')}</div>
                <div class="job-details">
                    📍 {job.get('location', 'Not specified')} | 
                    💰 {job.get('salary', 'Not specified')} | 
                    ⭐ <span class="featured-score">{score:.1f}/10</span>
                </div>
                <div class="job-details" style="color: #0066cc; font-size: 13px; font-style: italic;">
                    Why: {reasoning}
                </div>
                <div class="job-details">
                    Source: {job.get('source', 'unknown').title()}
                </div>
                <div class="job-snippet">{job.get('snippet', 'No description available')[:150]}...</div>
                <div class="apply-link">
                    <a href="{job.get('url', '#')}" class="featured-link">View Job →</a>
                </div>
            </div>
            """
        
        featured_html += "</div>"
    
    # Build full jobs list section
    jobs_html = ""
    if all_jobs:
        jobs_html = """
        <div class="all-jobs-section">
            <h2 style="color: #2c5aa0; margin-top: 40px; margin-bottom: 15px; border-bottom: 2px solid #2c5aa0; padding-bottom: 10px;">
                📋 All Matches ({})
            </h2>
            <p style="color: #666; font-size: 13px; margin-bottom: 15px;">
                Complete ranked list (sorted by score)
            </p>
        """.format(len(all_jobs))
        
        for i, job in enumerate(all_jobs[:15], 1):  # Show top 15 in full list
            score = job.get("score", 0)
            is_featured = score >= 7.0
            featured_badge = " ⭐" if is_featured else ""
            
            jobs_html += f"""
            <div class="all-job" style="opacity: {'1.0' if not is_featured else '1.0'};">
                <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <div class="job-title">{job.get('title', 'Unknown Position')}</div>
                    <span class="score-badge">{score:.1f}/10{featured_badge}</span>
                </div>
                <div class="job-company">{job.get('company', 'Unknown Company')}</div>
                <div class="job-details">
                    📍 {job.get('location', 'Not specified')} | 
                    💰 {job.get('salary', 'Not specified')}
                </div>
                <div class="job-snippet">{job.get('snippet', 'No description available')[:120]}...</div>
                <div class="apply-link">
                    <a href="{job.get('url', '#')}">View Job →</a>
                </div>
            </div>
            """
        
        if len(all_jobs) > 15:
            jobs_html += f"""
            <div style="text-align: center; color: #999; font-size: 13px; margin-top: 20px;">
                ... and {len(all_jobs) - 15} more jobs
            </div>
            """
        
        jobs_html += "</div>"
    else:
        jobs_html = """
        <div class="no-jobs-message">
            <p style="font-size: 16px; color: #666; text-align: center; padding: 30px;">
                ℹ️ No matching jobs found today.
            </p>
            <p style="font-size: 14px; color: #999; text-align: center;">
                Check back tomorrow for new listings, or update your search criteria in job-search-config.json.
            </p>
        </div>
        """
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background-color: #f0f0f0; padding: 20px; margin-bottom: 20px; }}
            .search-status {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin-bottom: 20px; border-radius: 4px; }}
            .featured-section {{ background-color: #fffbf0; border-left: 5px solid #d4af37; padding: 20px; margin-bottom: 30px; border-radius: 4px; }}
            .featured-job {{ background-color: #fff; border: 2px solid #d4af37; border-left: 5px solid #d4af37; padding: 15px; margin-bottom: 15px; border-radius: 4px; box-shadow: 0 2px 4px rgba(212, 175, 55, 0.1); }}
            .featured-score {{ background-color: #ffd700; padding: 2px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; color: #333; }}
            .featured-link {{ color: #d4af37; text-decoration: none; font-weight: bold; }}
            .featured-link:hover {{ text-decoration: underline; }}
            .all-jobs-section {{ margin-top: 30px; }}
            .all-job {{ background-color: #f9f9f9; border-left: 3px solid #ccc; padding: 12px; margin-bottom: 12px; border-radius: 3px; }}
            .score-badge {{ background-color: #e8f4f8; padding: 3px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; color: #0066cc; }}
            .no-jobs-message {{ background-color: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0; border-radius: 4px; }}
            .job-title {{ font-size: 16px; font-weight: bold; color: #000; }}
            .job-company {{ color: #555; font-weight: 500; }}
            .job-details {{ color: #666; font-size: 14px; margin: 8px 0; }}
            .job-snippet {{ color: #777; font-size: 13px; margin: 10px 0; font-style: italic; }}
            .apply-link {{ margin-top: 10px; }}
            .apply-link a {{ color: #2c5aa0; text-decoration: none; font-weight: bold; }}
            .apply-link a:hover {{ text-decoration: underline; }}
            .footer {{ margin-top: 40px; font-size: 12px; color: #999; border-top: 1px solid #ddd; padding-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔍 Daily Job Search Digest</h1>
            <p>Found <strong>{len(jobs)}</strong> matching jobs</p>
            <p>Generated: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}</p>
        </div>
        {status_html}
        {jobs_html}
        <div class="footer">
            <p>This is an automated job search digest. To manage your preferences, edit job-search-config.json.</p>
            <p>Interact with jobs (save, apply, reject) to improve future recommendations.</p>
        </div>
    </body>
    </html>
    """
    
    return html

def send_email(subject: str, html_body: str, to_email: str):
    """Send email via SMTP."""
    # Load email config from environment variables first, then fall back to file
    try:
        # Try environment variables (for Lambda)
        smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", 587))
        sender_email = os.environ.get("SENDER_EMAIL")
        sender_password = os.environ.get("SENDER_PASSWORD")
        
        # Fall back to config file if env vars not set
        if not sender_email or not sender_password:
            # Try workspace secrets first, then fallback to home secrets
            secrets_path = Path.home() / ".openclaw" / "workspace" / "secrets" / "email_config.json"
            if not secrets_path.exists():
                secrets_path = Path.home() / ".openclaw" / "secrets" / "email_config.json"
            
            if secrets_path.exists():
                with open(secrets_path, "r") as f:
                    email_config = json.load(f)
                smtp_server = email_config.get("smtp_server", smtp_server)
                smtp_port = email_config.get("smtp_port", smtp_port)
                sender_email = email_config.get("sender_email", sender_email)
                sender_password = email_config.get("sender_password", sender_password)
        
        if not sender_email or not sender_password:
            print("⚠️  Email credentials not configured. Skipping email delivery.")
            return False
        
        # Create email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email
        
        part = MIMEText(html_body, "html")
        msg.attach(part)
        
        # Send
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        
        print(f"✓ Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"✗ Email delivery failed: {e}")
        return False

def main():
    try:
        # Load candidate profile
        candidate_profile = load_candidate_profile()
        print("📄 Loaded candidate profile from resumes.md\n")
        
        # Load and filter results
        raw_results = load_latest_results()
        jobs = raw_results.get("jobs", [])
        search_status = raw_results.get("searchStatus", [])  # Get search status from raw results
        
        # Filter out sample/fallback jobs - only keep real results
        real_jobs = [j for j in jobs if j.get("source") not in ["sample", "fallback"]]
        
        print(f"📊 Found {len(real_jobs)} real jobs (filtered out {len(jobs) - len(real_jobs)} sample/fallback jobs)")
        print("Search Status:")
        for status in search_status:
            print(f"  {status}")
        print()
        
        featured_jobs = []
        all_jobs = []
        
        # If we have real jobs, filter to only NEW jobs (not sent before)
        if real_jobs:
            new_jobs = filter_to_new_jobs(real_jobs)
            print(f"📋 {len(new_jobs)} new jobs (out of {len(real_jobs)} total)\n")
            
            if new_jobs:
                featured_jobs, all_jobs = filter_and_rank_jobs(new_jobs, candidate_profile)
                print(f"✓ Scoring complete")
            else:
                print("✓ All jobs already sent in previous digests. No new jobs today.")
        else:
            print("ℹ️  No real job search results found.")
        
        # ALWAYS send email (with jobs if found, or status/message if not)
        html_body = format_email_body(featured_jobs, all_jobs, search_status)
        subject = f"🔍 Daily Job Search Digest — {datetime.now().strftime('%A, %B %d')}"
        
        # Get email recipient from config or default
        to_email = config.get("emailTo", "mtorres253@gmail.com")
        
        if send_email(subject, html_body, to_email):
            print(f"✓ Digest delivered to {to_email}")
            if featured_jobs or all_jobs:
                print(f"  → {len(featured_jobs)} featured jobs + {len(all_jobs) - len(featured_jobs)} additional jobs")
            else:
                print(f"  → Status report sent (no jobs found)")
        
        # Save sent jobs tracking
        with open(SENT_JOBS_PATH, "w") as f:
            json.dump(sent_jobs, f, indent=2)
        print(f"📁 Updated sent jobs tracking: {SENT_JOBS_PATH}")
        
        # Save filtered results for history
        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = RESULTS_DIR / f"filtered_results_{timestamp}.json"
        
        with open(output_file, "w") as f:
            json.dump({
                "filteredAt": datetime.utcnow().isoformat(),
                "featured": len(featured_jobs),
                "total": len(all_jobs),
                "jobs": all_jobs
            }, f, indent=2)
        
        print(f"📁 Saved filtered results to: {output_file}")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
