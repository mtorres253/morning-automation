#!/usr/bin/env python3
"""
Filter jobs and deliver via email digest.
Reads raw job search results, applies filtering/ranking, and sends email.
"""

import json
import os
import smtplib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

def calculate_relevance_score(job: Dict[str, Any]) -> float:
    """
    Calculate a relevance score (0-1) based on job attributes and interaction history.
    """
    score = 0.5  # Base score
    
    search_params = config["searches"][0]
    
    # Title match bonus
    title_lower = job.get("title", "").lower()
    for kw in search_params["keywords"]:
        if kw.lower() in title_lower:
            score += 0.15
    
    # Salary match bonus
    salary_text = job.get("salary", "").lower()
    if any(str(n) in salary_text for n in range(200, 251)):
        score += 0.2
    
    # Remote/Hybrid bonus
    if any(arr in job.get("location", "").lower() for arr in ["remote", "hybrid"]):
        score += 0.15
    
    # Industry/location bonus (rough check on description)
    snippet = job.get("snippet", "").lower()
    for industry in search_params["company"]["industries"]:
        if industry.lower() in snippet or industry.lower() in job.get("company", "").lower():
            score += 0.1
    
    # Learning signal: penalize if previously rejected
    job_id = job.get("jobId", "")
    if job_id in interactions.get("jobs", {}):
        interaction = interactions["jobs"][job_id]
        if interaction.get("action") == "rejected":
            score *= 0.3
        elif interaction.get("action") == "applied":
            score *= 1.2  # Slight boost for similar jobs after applying
    
    return min(score, 1.0)  # Cap at 1.0

def filter_and_rank_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter and rank jobs by relevance."""
    # Calculate scores
    for job in jobs:
        job["relevanceScore"] = calculate_relevance_score(job)
    
    # Filter: minimum score threshold
    filtered = [j for j in jobs if j["relevanceScore"] >= 0.4]
    
    # Sort by score (descending)
    ranked = sorted(filtered, key=lambda j: j["relevanceScore"], reverse=True)
    
    return ranked

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

def format_email_body(jobs: List[Dict[str, Any]], search_status: List[str] = None) -> str:
    """Format jobs into an HTML email body."""
    
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
    
    # Build job listings section (or "no jobs" message)
    jobs_html = ""
    if jobs:
        grouped = group_jobs_by_category(jobs)
        for category, category_jobs in grouped.items():
            jobs_html += f"""
            <div class="category">
                <div class="category-title">{category} ({len(category_jobs)})</div>
            """
            
            for job in category_jobs[:5]:  # Limit to top 5 per category
                score_pct = int(job["relevanceScore"] * 100)
                jobs_html += f"""
                <div class="job">
                    <div class="job-title">{job.get('title', 'Unknown Position')}</div>
                    <div class="job-company">{job.get('company', 'Unknown Company')}</div>
                    <div class="job-details">
                        📍 {job.get('location', 'Not specified')} | 
                        💰 {job.get('salary', 'Not specified')} | 
                        📊 <span class="score">Match: {score_pct}%</span>
                    </div>
                    <div class="job-details">
                        Source: {job.get('source', 'unknown').title()}
                    </div>
                    <div class="job-snippet">{job.get('snippet', 'No description available')[:150]}...</div>
                    <div class="apply-link">
                        <a href="{job.get('url', '#')}">View Job →</a>
                    </div>
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
            .no-jobs-message {{ background-color: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0; border-radius: 4px; }}
            .category {{ margin-bottom: 30px; }}
            .category-title {{ font-size: 18px; font-weight: bold; color: #2c5aa0; margin-bottom: 10px; border-bottom: 2px solid #2c5aa0; padding-bottom: 5px; }}
            .job {{ background-color: #f9f9f9; border-left: 4px solid #2c5aa0; padding: 15px; margin-bottom: 15px; }}
            .job-title {{ font-size: 16px; font-weight: bold; color: #000; }}
            .job-company {{ color: #555; font-weight: 500; }}
            .job-details {{ color: #666; font-size: 14px; margin: 8px 0; }}
            .job-snippet {{ color: #777; font-size: 13px; margin: 10px 0; font-style: italic; }}
            .score {{ background-color: #e8f4f8; padding: 2px 8px; border-radius: 3px; font-size: 12px; }}
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
        
        filtered_jobs = []
        
        # If we have real jobs, filter to only NEW jobs (not sent before)
        if real_jobs:
            new_jobs = filter_to_new_jobs(real_jobs)
            print(f"📋 {len(new_jobs)} new jobs (out of {len(real_jobs)} total)")
            
            if new_jobs:
                filtered_jobs = filter_and_rank_jobs(new_jobs)
                print(f"✓ {len(filtered_jobs)} jobs passed filter")
            else:
                print("✓ All jobs already sent in previous digests. No new jobs today.")
        else:
            print("ℹ️  No real job search results found.")
        
        # ALWAYS send email (with jobs if found, or status/message if not)
        html_body = format_email_body(filtered_jobs, search_status)
        subject = f"🔍 Daily Job Search Digest — {datetime.now().strftime('%A, %B %d')}"
        
        # Get email recipient from config or default
        to_email = config.get("emailTo", "mtorres253@gmail.com")
        
        if send_email(subject, html_body, to_email):
            print(f"✓ Digest delivered to {to_email}")
            if filtered_jobs:
                print(f"  → {len(filtered_jobs)} jobs included")
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
                "totalMatched": len(filtered_jobs),
                "jobs": filtered_jobs
            }, f, indent=2)
        
        print(f"📁 Saved filtered results to: {output_file}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
