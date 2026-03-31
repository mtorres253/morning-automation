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


def extract_header(resume_content):
    """
    Extract name and contact info from resume.
    Returns the first few lines before first ## section.
    """
    lines = resume_content.split('\n')
    header_lines = []
    for line in lines:
        if line.startswith('##'):
            break
        header_lines.append(line)
    return '\n'.join(header_lines).strip()


def extract_summaries(resume_content):
    """
    Extract all summary paragraphs with their content.
    Returns list of (summary_title, summary_text) tuples.
    """
    # Find section: "## Summary / Intro Paragraph Variations"
    match = re.search(
        r'## Summary.*?Variations\n(.*?)(?=^## |\Z)',
        resume_content,
        re.MULTILINE | re.DOTALL
    )
    if not match:
        return []
    
    summaries_text = match.group(1)
    # Split by bold headings like **General product leader — ...**
    parts = re.split(r'\*\*(.+?)\*\*', summaries_text)
    
    summaries = []
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        content = parts[i+1].strip() if i+1 < len(parts) else ""
        # Extract just the summary text (before the asterisks)
        content = re.sub(r'\*\(.+?\)\*', '', content).strip()
        if content:
            summaries.append((title, content))
    
    return summaries


def extract_all_skills(resume_content):
    """
    Extract the master skills list from resume.
    Returns a list of individual skill strings.
    """
    # Find section: "## Skills and Capabilities List"
    # Pattern: find the section header, then content until next ## heading
    match = re.search(
        r'## Skills and Capabilities List.*?\n(.*?)(?=^## |\Z)',
        resume_content,
        re.MULTILINE | re.DOTALL
    )
    if not match:
        return []
    
    skills_text = match.group(1).strip()
    # Remove separator lines (---)
    lines = [line for line in skills_text.split('\n') if line.strip() and line.strip() != '---']
    full_text = ' '.join(lines)
    
    # Split by comma and clean up each skill
    raw_skills = [s.strip() for s in full_text.split(',')]
    # Remove empty strings
    skills = [s for s in raw_skills if s]
    
    return skills


def extract_keywords(job_description):
    """
    Extract key skills, technologies, and concepts from job description.
    Returns set of keywords (lowercased).
    """
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'be', 'have', 'has', 'are',
        'you', 'your', 'we', 'our', 'will', 'would', 'should', 'must', 'may',
        'can', 'could', 'this', 'that', 'these', 'those', 'about', 'through'
    }
    
    words = re.findall(r'\b[a-z0-9+#./-]+\b', job_description.lower())
    
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
    Returns list of (title, header_info, bullets_only) tuples.
    """
    experiences = []
    lines = resume_content.split('\n')
    current_exp = None
    current_header_lines = []
    current_bullets = []
    
    for i, line in enumerate(lines):
        # Look for role titles (### Role — Company)
        if line.startswith('### ') and ' — ' in line:
            if current_exp:
                # Save previous experience
                full_content = '\n'.join(current_header_lines) + '\n' + '\n'.join(current_bullets)
                experiences.append((current_exp, full_content, current_bullets))
            
            current_exp = line.lstrip('### ').strip()
            current_header_lines = [line]
            current_bullets = []
        elif current_exp:
            if line.startswith('- ') or line.startswith('* '):
                # This is a bullet point
                current_bullets.append(line)
            elif line.strip() == '':
                # Blank line between header and bullets or between bullets
                if current_bullets:
                    # We've started bullets, blank lines between them are OK
                    pass
                elif current_header_lines:
                    # Still in header section
                    pass
            elif not line.startswith('#'):
                # Non-bullet, non-heading line (like date line *...)
                if not current_bullets:
                    # Still in header section
                    current_header_lines.append(line)
    
    # Don't forget the last experience
    if current_exp:
        full_content = '\n'.join(current_header_lines) + '\n' + '\n'.join(current_bullets)
        experiences.append((current_exp, full_content, current_bullets))
    
    return experiences


def trim_bullets(bullets, max_count=6):
    """Keep only the most relevant bullets (up to max_count)."""
    return bullets[:max_count]


def create_draft_resume(resume_content, job_description, output_file=None):
    """
    Create a refined draft resume.
    Structure: Header → Summary → Skills → Work History (top 6 bullets each)
    """
    keywords = extract_keywords(job_description)
    
    # 1. Extract and include header
    header = extract_header(resume_content)
    draft = header + "\n\n"
    
    # 2. Find and include best summary
    summaries = extract_summaries(resume_content)
    if summaries:
        summary_scores = [
            (title, text, score_content_relevance(title + ' ' + text, keywords))
            for title, text in summaries
        ]
        summary_scores.sort(key=lambda x: x[2], reverse=True)
        best_title, best_text, score = summary_scores[0]
        draft += f"## Summary\n\n{best_text}\n\n"
    
    # 3. Build custom skills list (top 20-25 most relevant from inventory)
    all_skills = extract_all_skills(resume_content)
    if all_skills:
        # Score each skill based on keyword overlap
        skill_scores = [
            (skill, score_content_relevance(skill, keywords))
            for skill in all_skills
        ]
        # Sort by relevance and take top 20-25
        skill_scores.sort(key=lambda x: x[1], reverse=True)
        top_skills = [skill for skill, score in skill_scores[:25] if skill.strip() and skill != '---']
        
        # Format as comma-separated list
        skills_text = ", ".join(top_skills)
        draft += f"## Skills\n\n{skills_text}\n\n"
    
    # 4. Extract and score work experiences
    experiences = extract_work_experience(resume_content)
    scored_exp = [
        (exp_title, exp_content, bullets, score_content_relevance(exp_content, keywords))
        for exp_title, exp_content, bullets in experiences
    ]
    scored_exp.sort(key=lambda x: x[3], reverse=True)
    
    # 5. Build work history with top bullets only
    draft += "## Work History\n\n"
    for exp_title, exp_content, bullets, score in scored_exp:
        # Extract header lines: role title and dates
        lines = exp_content.split('\n')
        header_lines = [lines[0]]  # Role line (### Role — Company)
        for i in range(1, len(lines)):
            if lines[i].startswith('*'):
                header_lines.append(lines[i])  # Date line (*dates*)
                break
        
        # Get only the first max_count bullets
        trimmed_bullets = trim_bullets(bullets, max_count=6)
        
        # Write the section
        draft += '\n'.join(header_lines) + '\n'
        draft += '\n'.join(trimmed_bullets) + '\n\n'
    
    # 6. Add education and certifications if present
    if 'Education' in resume_content:
        edu_match = re.search(
            r'## Education\n(.*?)(?=^## |\Z)',
            resume_content,
            re.MULTILINE | re.DOTALL
        )
        if edu_match:
            draft += "## Education\n\n"
            draft += edu_match.group(1).strip() + "\n\n"
    
    if 'Certifications' in resume_content:
        cert_match = re.search(
            r'## Certifications\n(.*?)(?=^## |\Z)',
            resume_content,
            re.MULTILINE | re.DOTALL
        )
        if cert_match:
            draft += "## Certifications\n\n"
            draft += cert_match.group(1).strip() + "\n\n"
    
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
    print(f"  - Work experiences evaluated and ranked")


if __name__ == "__main__":
    main()
