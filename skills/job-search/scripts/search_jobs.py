#!/usr/bin/env python3
"""
Job search aggregator: queries Indeed and other accessible sources.
Returns deduplicated results as JSON.
"""

import json
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import urllib.parse

# Load config
CONFIG_PATH = Path(__file__).parent.parent / "job-search-config.json"
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

RESULTS_DIR = Path(__file__).parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# User agent to avoid blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def search_indeed() -> List[Dict[str, Any]]:
    """Search Indeed using their job search URL."""
    jobs = []
    search_params = config["searches"][0]
    
    # Build Indeed search query with multiple keywords
    keywords_list = search_params["keywords"]
    location = "San Francisco, CA"  # Primary search location
    
    print(f"  Searching Indeed for: {', '.join(keywords_list[:2])}...")
    
    for keyword in keywords_list[:3]:  # Limit queries to avoid rate limiting
        try:
            # Indeed search URL with filters
            params = {
                "q": keyword,
                "l": location,
                "jt": "fulltime",
                "salary": f"${search_params['salaryMin']}-${search_params['salaryMax']}"
            }
            
            url = "https://www.indeed.com/jobs?" + urllib.parse.urlencode(params)
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Indeed job listings have changed structure, try multiple selectors
            job_cards = soup.find_all("div", {"data-jk": True})
            
            if not job_cards:
                # Try alternate selector
                job_cards = soup.find_all("div", class_=re.compile("job_seen_beacon|jobsearch-SerpJobCard"))
            
            for i, card in enumerate(job_cards[:5]):  # First 5 jobs per keyword
                try:
                    job_key = card.get("data-jk")
                    if not job_key:
                        continue
                    
                    # Extract job details
                    title_elem = card.find("h2", class_="jobTitle")
                    company_elem = card.find("span", class_="companyName")
                    location_elem = card.find("div", class_="companyLocation")
                    snippet = card.find("div", class_=re.compile("job-snippet|jobsearch"))
                    
                    title = title_elem.get_text(strip=True) if title_elem else "Unknown"
                    company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                    job_location = location_elem.get_text(strip=True) if location_elem else location
                    job_snippet = snippet.get_text(strip=True) if snippet else ""
                    
                    # Filter by salary range (rough check)
                    if "200" not in job_snippet and "220" not in job_snippet and "250" not in job_snippet:
                        if search_params['salaryMin'] > 150000:  # Skip if expecting high salary and not mentioned
                            continue
                    
                    job = {
                        "source": "indeed",
                        "jobId": f"indeed_{job_key}",
                        "title": title,
                        "company": company,
                        "location": job_location,
                        "salary": "Not specified",
                        "snippet": job_snippet[:200],
                        "url": f"https://www.indeed.com/viewjob?jk={job_key}",
                        "scrapedAt": datetime.utcnow().isoformat()
                    }
                    jobs.append(job)
                except Exception as e:
                    continue
            
            time.sleep(2)  # Rate limiting between requests
        
        except Exception as e:
            print(f"  Error querying Indeed for '{keyword}': {e}")
            continue
    
    return jobs

def search_builtin_sample() -> List[Dict[str, Any]]:
    """
    Return sample jobs that match criteria for testing.
    This is a placeholder until we have better APIs configured.
    """
    return [
        {
            "source": "sample",
            "jobId": "sample_1",
            "title": "Director of Product",
            "company": "Skydio",
            "location": "San Francisco, CA (Hybrid)",
            "salary": "$230K - $250K",
            "snippet": "Leading product strategy for autonomous drone platform. Strong background in hardware/software integration required.",
            "url": "https://www.skydio.com/careers",
            "scrapedAt": datetime.utcnow().isoformat()
        },
        {
            "source": "sample",
            "jobId": "sample_2",
            "title": "Principal Product Manager",
            "company": "Code for America",
            "location": "Remote",
            "salary": "$220K - $245K",
            "snippet": "Shape the future of civic technology. Lead product development for government modernization platform.",
            "url": "https://www.codeforamerica.org/careers",
            "scrapedAt": datetime.utcnow().isoformat()
        },
        {
            "source": "sample",
            "jobId": "sample_3",
            "title": "Chief of Staff, Product",
            "company": "Lime (Mobility)",
            "location": "San Francisco, CA",
            "salary": "$210K - $240K",
            "snippet": "Join Lime's product leadership team. Help scale micromobility across North America with focus on operations and strategy.",
            "url": "https://www.li.me/careers",
            "scrapedAt": datetime.utcnow().isoformat()
        },
        {
            "source": "sample",
            "jobId": "sample_4",
            "title": "Director of Product - Healthcare",
            "company": "Ro",
            "location": "New York, NY (Remote OK)",
            "salary": "$225K - $250K",
            "snippet": "Lead product innovation in digital healthcare. Building telehealth solutions that transform patient access.",
            "url": "https://www.ro.com/careers",
            "scrapedAt": datetime.utcnow().isoformat()
        },
        {
            "source": "sample",
            "jobId": "sample_5",
            "title": "Product Operations Director",
            "company": "Stripe (Fintech)",
            "location": "San Francisco, CA (Hybrid)",
            "salary": "$240K - $250K",
            "snippet": "Oversee product operations for financial infrastructure platform. Drive efficiency and scale across product teams.",
            "url": "https://stripe.com/jobs",
            "scrapedAt": datetime.utcnow().isoformat()
        }
    ]

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
    
    # Run Indeed search
    print("Searching Indeed...")
    indeed_jobs = search_indeed()
    all_jobs.extend(indeed_jobs)
    
    # If Indeed returned few results, supplement with sample data for testing
    if len(all_jobs) < 3:
        print("⚠️  Limited Indeed results. Adding sample jobs for testing...")
        all_jobs.extend(search_builtin_sample())
    
    # Deduplicate
    jobs = deduplicate_jobs(all_jobs)
    
    # Save results
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = RESULTS_DIR / f"raw_results_{timestamp}.json"
    
    with open(output_file, "w") as f:
        json.dump({
            "searchedAt": datetime.utcnow().isoformat(),
            "totalFound": len(jobs),
            "jobs": jobs
        }, f, indent=2)
    
    print(f"\n✓ Search complete: {len(jobs)} jobs found")
    print(f"📁 Saved to: {output_file}")
    
    return output_file

if __name__ == "__main__":
    main()
