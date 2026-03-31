#!/usr/bin/env python3
"""
Parse job description from URL or text and extract keywords, requirements, and technologies.

Usage:
    python parse_job_description.py --url "https://..."
    python parse_job_description.py --text "job description..."
    python parse_job_description.py --text "$(cat job.txt)" --output parsed.json
"""

import json
import re
import sys
import argparse
from urllib.parse import urlparse
from typing import Set, Dict, List
from html.parser import HTMLParser

# Common resume keywords to look for
RESUME_KEYWORDS = {
    "5+ years", "10+ years", "3+ years", "7+ years",
    "team", "leadership", "mentoring", "managing",
    "architect", "architecture", "design",
    "development", "developing", "developer",
    "engineer", "engineering",
    "python", "java", "javascript", "typescript", "rust", "go", "c++", "c#",
    "aws", "gcp", "azure", "cloud",
    "docker", "kubernetes", "k8s", "containers",
    "sql", "postgres", "mysql", "mongodb", "redis",
    "microservices", "rest", "api", "graphql",
    "react", "vue", "angular", "frontend",
    "git", "github", "gitlab", "bitbucket",
    "ci/cd", "jenkins", "github actions", "gitlab ci",
    "agile", "scrum", "kanban",
    "testing", "pytest", "junit", "mocha",
    "performance", "scalability", "optimization",
    "security", "encryption", "authentication",
    "fastapi", "django", "flask", "express",
    "machine learning", "ml", "ai", "llm",
    "data", "analytics", "warehouse", "pipeline",
}

class HTMLStripper(HTMLParser):
    """Simple HTML parser to extract text."""
    def __init__(self):
        super().__init__()
        self.text = []
    
    def handle_data(self, data):
        self.text.append(data)
    
    def get_text(self):
        return ' '.join(self.text)


def fetch_url(url: str) -> str:
    """Fetch content from URL."""
    try:
        import urllib.request
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        raise RuntimeError(f"Failed to fetch {url}: {e}")


def strip_html(html: str) -> str:
    """Remove HTML tags from content."""
    stripper = HTMLStripper()
    stripper.feed(html)
    return stripper.get_text()


def extract_keywords(text: str) -> Dict[str, List[str]]:
    """Extract keywords from job description."""
    text_lower = text.lower()
    
    # Extract common resume keywords that appear in text
    found_keywords = []
    for keyword in RESUME_KEYWORDS:
        if keyword in text_lower:
            found_keywords.append(keyword)
    
    # Extract capitalized phrases (likely tools, frameworks, or company-specific terms)
    capitalized = re.findall(r'\b([A-Z][a-zA-Z0-9+#]*(?:\s+[A-Z][a-zA-Z0-9+#]*)?)\b', text)
    # Filter out common words and very short phrases
    tech_terms = [
        t for t in set(capitalized) 
        if len(t) > 1 and t.lower() not in {'the', 'and', 'or', 'are', 'our', 'you', 'your', 'we', 'will', 'be', 'for', 'is', 'as', 'to', 'in', 'of', 'on', 'at'}
    ]
    
    # Extract version numbers and specific tech mentions
    versions = re.findall(r'([A-Za-z0-9+#]+)\s*(?:v\.?|version)\s*(\d+(?:\.\d+)*)', text)
    version_terms = [f"{name} {ver}" for name, ver in versions]
    
    # Extract years of experience mentions
    years = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|exp\.?)', text, re.IGNORECASE)
    years_terms = [f"{y}+ years" for y in years] if years else []
    
    # Extract job titles (heuristic: capitalized 2-3 word phrases)
    job_title_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b'
    job_titles = list(set(re.findall(job_title_pattern, text)))[:10]  # Limit to top 10
    
    return {
        "matched_keywords": found_keywords,
        "technologies": tech_terms[:20],  # Top 20 tech terms
        "years_of_experience": years_terms,
        "possible_job_titles": job_titles,
    }


def extract_requirements(text: str) -> List[str]:
    """Extract requirements/bullet points from job description."""
    # Look for requirements sections
    requirements = []
    
    # Match bullet points
    bullets = re.findall(r'(?:^|\n)\s*[-•*]\s+([^\n]+)', text, re.MULTILINE)
    requirements.extend([b.strip() for b in bullets if len(b.strip()) > 10])
    
    # Match numbered lists
    numbered = re.findall(r'(?:^|\n)\s*\d+\.\s+([^\n]+)', text, re.MULTILINE)
    requirements.extend([n.strip() for n in numbered if len(n.strip()) > 10])
    
    # Look for "Requirements" or "Must haves" sections
    sections = re.split(r'(Requirements|Must Haves|Qualifications|About You|What We\'re Looking For)', text, flags=re.IGNORECASE)
    if len(sections) > 2:
        section_text = sections[2][:1000]  # Take up to 1000 chars after section header
        # Find bullets in this section
        section_bullets = re.findall(r'[-•*]\s+([^\n]+)', section_text)
        requirements.extend([b.strip() for b in section_bullets if len(b.strip()) > 10])
    
    return list(set(requirements))[:15]  # Unique, limit to 15


def parse_job_description(source: str, is_url: bool = False) -> Dict:
    """Parse job description from URL or text."""
    if is_url:
        # Fetch and strip HTML
        html = fetch_url(source)
        text = strip_html(html)
    else:
        text = source
    
    # Clean up text
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    text = re.sub(r'[^\w\s\-+#.,:;()!?]', ' ', text)  # Remove special chars
    
    keywords = extract_keywords(text)
    requirements = extract_requirements(text)
    
    # Combine all keywords into a single searchable list
    all_keywords = (
        keywords["matched_keywords"] +
        keywords["technologies"] +
        keywords["years_of_experience"] +
        keywords["possible_job_titles"]
    )
    
    return {
        "source_type": "url" if is_url else "text",
        "all_keywords": all_keywords,
        "keywords_detail": keywords,
        "requirements": requirements,
        "total_keywords": len(all_keywords),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Parse job description and extract keywords"
    )
    parser.add_argument("--url", help="Job description URL")
    parser.add_argument("--text", help="Job description text")
    parser.add_argument("--output", help="Output JSON file (default: stdout)")
    
    args = parser.parse_args()
    
    if not args.url and not args.text:
        parser.error("Provide either --url or --text")
    
    if args.url and args.text:
        parser.error("Provide either --url or --text, not both")
    
    try:
        result = parse_job_description(args.url or args.text, is_url=bool(args.url))
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Parsed job description saved to {args.output}", file=sys.stderr)
        else:
            print(json.dumps(result, indent=2))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
