#!/usr/bin/env python3
"""
Resume Matcher Script

Matches a job description against resume and cover letter content.
Outputs a draft resume and cover letter using only original content.

Usage:
    python3 match_resume.py <job_description_file> <resume_file> <cover_letter_file> [output_dir]
"""

import sys
import json
import re
from pathlib import Path
from collections import defaultdict


def read_file(filepath):
    """Read a markdown file."""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)


def parse_sections(content):
    """
    Parse markdown content into sections.
    Returns dict: {section_name: content}
    """
    sections = defaultdict(str)
    current_section = "intro"
    lines = content.split('\n')
    
    for line in lines:
        # Match heading levels 1-3
        if line.startswith('# ') and not line.startswith('# #'):
            current_section = line.lstrip('#').strip().lower()
        elif line.startswith('## '):
            current_section = line.lstrip('#').strip().lower()
        elif line.startswith('### '):
            current_section = line.lstrip('#').strip().lower()
        
        sections[current_section] += line + '\n'
    
    return sections


def extract_keywords(job_description):
    """
    Extract key skills, technologies, and concepts from job description.
    Returns set of keywords (lowercased).
    """
    # Remove common non-meaningful words
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'be', 'have', 'has', 'are',
        'you', 'your', 'we', 'our', 'will', 'would', 'should', 'must', 'may',
        'can', 'could', 'this', 'that', 'these', 'those', 'about', 'through'
    }
    
    # Split into words and phrases
    words = re.findall(r'\b[a-z0-9+#./-]+\b', job_description.lower())
    
    # Filter: keep words 3+ chars or common tech terms
    keywords = set()
    for word in words:
        if len(word) >= 3 and word not in stopwords:
            keywords.add(word)
    
    return keywords


def score_content_relevance(content, keywords):
    """
    Score how relevant a piece of content is to keywords.
    Returns relevance score (0-1).
    """
    if not content or not keywords:
        return 0
    
    content_lower = content.lower()
    matches = sum(1 for kw in keywords if kw in content_lower)
    
    return min(1.0, matches / (len(keywords) * 0.5)) if keywords else 0


def extract_work_experience(resume_content):
    """
    Extract individual work experiences from resume.
    Returns list of (title, content) tuples.
    """
    experiences = []
    lines = resume_content.split('\n')
    current_exp = None
    current_content = []
    
    for line in lines:
        # Look for role titles (### Role — Company)
        if line.startswith('### ') and ' — ' in line:
            if current_exp:
                experiences.append((current_exp, '\n'.join(current_content)))
            current_exp = line.lstrip('### ').strip()
            current_content = [line]
        elif current_exp:
            current_content.append(line)
    
    if current_exp:
        experiences.append((current_exp, '\n'.join(current_content)))
    
    return experiences


def create_draft_resume(resume_content, job_description, output_file=None):
    """
    Create a draft resume tailored to job description.
    Uses only original content from resume.
    """
    keywords = extract_keywords(job_description)
    
    # Extract intro/header
    intro_match = re.search(r'^(?:# .+\n)+(.+?)(?:^##|\Z)', resume_content, re.MULTILINE)
    header = intro_match.group(0) if intro_match else ""
    
    # Extract work experiences
    experiences = extract_work_experience(resume_content)
    
    # Score and sort experiences by relevance
    scored_exp = [
        (exp_title, exp_content, score_content_relevance(exp_content, keywords))
        for exp_title, exp_content in experiences
    ]
    scored_exp.sort(key=lambda x: x[2], reverse=True)
    
    # Build draft resume
    draft = header + "\n\n"
    draft += "## Work History (Ordered by Relevance)\n\n"
    
    for exp_title, exp_content, score in scored_exp:
        draft += exp_content + "\n\n"
    
    # Add other sections (Skills, Education, etc.) if they exist
    sections = parse_sections(resume_content)
    for section_name, section_content in sections.items():
        if section_name not in ['intro', 'work history', 'employment']:
            draft += f"\n## {section_name.title()}\n\n"
            draft += section_content + "\n"
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(draft)
        print(f"✓ Draft resume written to: {output_file}")
    
    return draft


def create_draft_cover_letter(cover_letter_content, job_description, output_file=None):
    """
    Create a draft cover letter tailored to job description.
    Uses only original content from cover letters.
    """
    keywords = extract_keywords(job_description)
    
    # Extract paragraphs/sections
    paragraphs = re.split(r'\n\n+', cover_letter_content.strip())
    
    # Score each paragraph
    scored_paras = [
        (para, score_content_relevance(para, keywords))
        for para in paragraphs if para.strip()
    ]
    
    # Sort by relevance
    scored_paras.sort(key=lambda x: x[1], reverse=True)
    
    # Build draft cover letter
    draft = "# Cover Letter (Customized)\n\n"
    draft += "\n\n".join([para for para, score in scored_paras[:5]])  # Top 5 relevant paragraphs
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(draft)
        print(f"✓ Draft cover letter written to: {output_file}")
    
    return draft


def main():
    if len(sys.argv) < 4:
        print("Usage: python3 match_resume.py <job_desc> <resume_file> <cover_letter_file> [output_dir]")
        sys.exit(1)
    
    job_desc_path = sys.argv[1]
    resume_path = sys.argv[2]
    cover_letter_path = sys.argv[3]
    output_dir = sys.argv[4] if len(sys.argv) > 4 else "."
    
    # Create output directory if needed
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Read files
    job_description = read_file(job_desc_path)
    resume_content = read_file(resume_path)
    cover_letter_content = read_file(cover_letter_path)
    
    # Create drafts
    resume_draft = create_draft_resume(
        resume_content,
        job_description,
        f"{output_dir}/resume_draft.md"
    )
    
    cover_letter_draft = create_draft_cover_letter(
        cover_letter_content,
        job_description,
        f"{output_dir}/cover_letter_draft.md"
    )
    
    print(f"\n✓ Matching complete!")
    print(f"  - Keywords extracted: {len(extract_keywords(job_description))} total")
    print(f"  - Resume experiences scored: {len(resume_content.count('###'))} total")


if __name__ == "__main__":
    main()
