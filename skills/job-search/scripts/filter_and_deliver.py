#!/usr/bin/env python3
"""
Filter jobs and deliver via email digest.
Reads raw job search results, applies filtering/ranking, and sends email.
"""

import json
import smtplib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

CONFIG_PATH = Path(__file__).parent.parent / "job-search-config.json"
INTERACTIONS_PATH = Path(__file__).parent.parent / "job-interactions.json"
RESULTS_DIR = Path(__file__).parent.parent / "results"

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

# Load interaction history (for learning)
interactions = {}
if INTERACTIONS_PATH.exists():
    with open(INTERACTIONS_PATH, "r") as f:
        interactions = json.load(f)

def load_latest_results() -> Dict[str, Any]:
    """Load the latest raw results file."""
    result_files = sorted(RESULTS_DIR.glob("raw_results_*.json"), reverse=True)
    if not result_files:
        raise FileNotFoundError("No job search results found")
    
    with open(result_files[0], "r") as f:
        return json.load(f)

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

def format_email_body(jobs: List[Dict[str, Any]]) -> str:
    """Format jobs into an HTML email body."""
    grouped = group_jobs_by_category(jobs)
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background-color: #f0f0f0; padding: 20px; margin-bottom: 20px; }}
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
    """
    
    for category, category_jobs in grouped.items():
        html += f"""
        <div class="category">
            <div class="category-title">{category} ({len(category_jobs)})</div>
        """
        
        for job in category_jobs[:5]:  # Limit to top 5 per category
            score_pct = int(job["relevanceScore"] * 100)
            html += f"""
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
        
        html += "</div>"
    
    html += f"""
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
    # Load email config from secrets or use env
    try:
        secrets_path = Path.home() / ".openclaw" / "secrets" / "email_config.json"
        if secrets_path.exists():
            with open(secrets_path, "r") as f:
                email_config = json.load(f)
        else:
            raise FileNotFoundError("Email config not found. Please create ~/.openclaw/secrets/email_config.json")
        
        smtp_server = email_config.get("smtp_server", "smtp.gmail.com")
        smtp_port = email_config.get("smtp_port", 587)
        sender_email = email_config.get("sender_email")
        sender_password = email_config.get("sender_password")
        
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
        
        print(f"📊 Filtering {len(jobs)} jobs...")
        filtered_jobs = filter_and_rank_jobs(jobs)
        
        print(f"✓ {len(filtered_jobs)} jobs passed filter")
        
        if not filtered_jobs:
            print("No jobs matched your criteria.")
            return
        
        # Format and send email
        html_body = format_email_body(filtered_jobs)
        subject = f"🔍 Daily Job Search Digest — {datetime.now().strftime('%A, %B %d')}"
        
        # Get email recipient from config or default
        to_email = config.get("emailTo", "mtorres253@gmail.com")
        
        if send_email(subject, html_body, to_email):
            print(f"✓ Digest delivered to {to_email}")
        
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
