#!/usr/bin/env python3
"""
Job search aggregator: queries Indeed and other accessible sources.
Returns deduplicated results as JSON.
"""

import json
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import urllib.parse
import xml.etree.ElementTree as ET

# Load config
CONFIG_PATH = Path(__file__).parent.parent / "job-search-config.json"
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

# Use /tmp for Lambda compatibility (read-only filesystem in Lambda)
# Fall back to local results dir if not in Lambda
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    RESULTS_DIR = Path("/tmp") / "job-search-results"
else:
    RESULTS_DIR = Path(__file__).parent.parent / "results"
    
RESULTS_DIR.mkdir(exist_ok=True)

# User agent to avoid blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}



def search_ycombinator() -> tuple[List[Dict[str, Any]], str]:
    """
    Search Y Combinator Jobs for startup jobs.
    Focuses on startup-funded companies, including civic tech, gov tech, etc.
    Returns (jobs_list, status_message)
    """
    jobs = []
    status = ""
    search_params = config["searches"][0]
    
    try:
        print("  Searching Y Combinator Jobs (Startup jobs - civic tech, etc)...")
        
        # Build search keywords
        keywords = search_params["keywords"][:2]  # Use first 2 keywords
        
        # Y Combinator Jobs RSS feed
        url = "https://ycombinator.com/jobs/rss"
        
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        # Parse RSS feed
        root = ET.fromstring(response.content)
        
        # Extract items from RSS
        items = root.findall(".//item")
        
        for item in items[:20]:  # Limit to 20 results
            try:
                title_elem = item.find("title")
                description_elem = item.find("description")
                link_elem = item.find("link")
                
                if title_elem is None:
                    continue
                
                title = title_elem.text or "Unknown"
                description = description_elem.text if description_elem is not None else ""
                link = link_elem.text if link_elem is not None else ""
                
                # Extract company name from title (format: "Company Name - Job Title")
                if " - " in title:
                    company, job_title = title.split(" - ", 1)
                else:
                    company = "Unknown"
                    job_title = title
                
                # Filter by keywords (loose match)
                title_lower = job_title.lower()
                matches_keywords = any(kw.lower() in title_lower for kw in keywords)
                
                if not matches_keywords:
                    continue  # Skip jobs that don't match keywords
                
                job_obj = {
                    "source": "ycombinator",
                    "jobId": f"yc_{hash(title + company) % 999999}",
                    "title": job_title,
                    "company": company,
                    "location": "Remote or On-site",
                    "salary": "Not specified",
                    "snippet": description[:200],
                    "url": link,
                    "scrapedAt": datetime.utcnow().isoformat()
                }
                jobs.append(job_obj)
            except Exception as e:
                continue
        
        status = f"✓ Y Combinator: Found {len(jobs)} jobs"
        print(f"  {status}")
        
    except requests.exceptions.HTTPError as e:
        status = f"✗ Y Combinator: HTTP {e.response.status_code}"
        print(f"  {status}")
    except requests.exceptions.Timeout:
        status = "✗ Y Combinator: Request timeout"
        print(f"  {status}")
    except requests.exceptions.ConnectionError:
        status = "✗ Y Combinator: Connection error"
        print(f"  {status}")
    except Exception as e:
        status = f"✗ Y Combinator: {type(e).__name__}"
        print(f"  {status}")
    
    return jobs, status


def search_jsearch() -> tuple[List[Dict[str, Any]], str]:
    """
    Search JSearch API (OpenWeb Ninja) for job listings.
    Indexes LinkedIn, Indeed, Glassdoor, ZipRecruiter, Google for Jobs, and more.
    Returns (jobs_list, status_message)
    """
    jobs = []
    status = ""
    search_params = config["searches"][0]
    
    try:
        # Load JSearch credentials
        secrets_path = Path.home() / ".openclaw" / "secrets" / "jsearch_credentials.json"
        if not secrets_path.exists():
            status = "⚠️  JSearch: Credentials not found"
            print(f"  {status}")
            return jobs, status
        
        with open(secrets_path, "r") as f:
            jsearch_creds = json.load(f)
        
        api_key = jsearch_creds.get("api_key")
        api_host = jsearch_creds.get("api_host", "jsearch.p.rapidapi.com")
        api_url = jsearch_creds.get("api_url", "https://jsearch.p.rapidapi.com/search")
        
        if not api_key:
            status = "⚠️  JSearch: API key not configured"
            print(f"  {status}")
            return jobs, status
        
        print("  Searching JSearch (LinkedIn, Indeed, Glassdoor, ZipRecruiter, etc)...")
        
        # Build JSearch query
        keywords = " ".join(search_params["keywords"][:2])  # Use first 2 keywords
        location = search_params["locations"][0].split(",")[0]  # City name only
        
        params = {
            "query": keywords,
            "location": location,
            "page": "1",
            "num_pages": "1",
            "date_posted": "week",  # Options: anytime, today, 3days, week, month
            "employment_type": "FULLTIME",
            "country": "US"
        }
        
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": api_host
        }
        
        response = requests.get(api_url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        job_list = data.get("data", [])
        
        for job in job_list[:15]:  # Limit to 15 results
            try:
                # Extract salary range if available
                salary_str = "Not specified"
                salary_min = job.get("job_salary_min")
                salary_max = job.get("job_salary_max")
                
                if salary_min and salary_max:
                    salary_str = f"${salary_min:,} - ${salary_max:,}"
                elif salary_min:
                    salary_str = f"${salary_min:,}+"
                elif salary_max:
                    salary_str = f"Up to ${salary_max:,}"
                
                job_obj = {
                    "source": "jsearch",
                    "jobId": f"jsearch_{job.get('job_id', '')}",
                    "title": job.get("job_title", "Unknown"),
                    "company": job.get("employer_name", "Unknown"),
                    "location": job.get("job_location", location),
                    "salary": salary_str,
                    "snippet": job.get("job_description", "")[:200],
                    "url": job.get("job_apply_link", ""),
                    "scrapedAt": datetime.utcnow().isoformat()
                }
                jobs.append(job_obj)
            except Exception as e:
                continue
        
        status = f"✓ JSearch: Found {len(jobs)} jobs"
        print(f"  {status}")
        
    except requests.exceptions.Timeout:
        status = "✗ JSearch: Request timeout (API may be slow)"
        print(f"  {status}")
    except requests.exceptions.ConnectionError:
        status = "✗ JSearch: Connection error (check internet)"
        print(f"  {status}")
    except json.JSONDecodeError:
        status = "✗ JSearch: Invalid API response"
        print(f"  {status}")
    except Exception as e:
        status = f"✗ JSearch: {type(e).__name__}: {str(e)[:80]}"
        print(f"  {status}")
    
    return jobs, status

def deduplicate_jobs(all_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate jobs across sources."""
    seen = {}
    deduped = []
    
    for job in all_jobs:
        # Normalize title and company for comparison
        key = (job["title"].lower(), job["company"].lower())
        if key not in seen:
            seen[key] = job
            deduped.append(job)
    
    return deduped

def main():
    print("🔍 Starting job search...")
    print(f"Config: {config['searches'][0]['name']}")
    print(f"Criteria: {', '.join(config['searches'][0]['keywords'][:2])} | ${config['searches'][0]['salaryMin']}-${config['searches'][0]['salaryMax']}")
    print()
    
    all_jobs = []
    search_status = []  # Track which searches succeeded/failed
    
    # Y Combinator Jobs search disabled (RSS endpoint not currently available)
    # Will revisit in future if needed
    # yc_jobs, yc_status = search_ycombinator()
    # all_jobs.extend(yc_jobs)
    # search_status.append(yc_status)
    
    # Run JSearch (LinkedIn, Indeed, Glassdoor, ZipRecruiter, etc)
    jsearch_jobs, jsearch_status = search_jsearch()
    all_jobs.extend(jsearch_jobs)
    search_status.append(jsearch_status)
    
    # Deduplicate
    jobs = deduplicate_jobs(all_jobs)
    
    # Save results with status info
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = RESULTS_DIR / f"raw_results_{timestamp}.json"
    
    with open(output_file, "w") as f:
        json.dump({
            "searchedAt": datetime.utcnow().isoformat(),
            "totalFound": len(jobs),
            "searchStatus": search_status,  # Include search success/failure info
            "jobs": jobs
        }, f, indent=2)
    
    print(f"\n{'='*50}")
    print(f"Search Summary:")
    print(f"  Total jobs found: {len(jobs)}")
    for status in search_status:
        print(f"  {status}")
    print(f"{'='*50}")
    print(f"📁 Saved to: {output_file}")
    
    return output_file

if __name__ == "__main__":
    main()
