#!/usr/bin/env python3
"""
Generate formatted markdown resume or cover letter draft from matched snippets.

Usage:
    python generate_draft.py matches.json --type resume --output draft.md
    python generate_draft.py matches.json --type cover-letter --output letter.md
    python generate_draft.py matches.json --type resume --top-n 7
    python generate_draft.py matches.json --min-score 50 --output draft.json --format json
"""

import json
import sys
import argparse
from typing import List, Dict


def load_json(filepath: str) -> Dict:
    """Load JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load {filepath}: {e}")


def bold_keywords(text: str, keywords: List[str]) -> str:
    """Bold matched keywords in text."""
    if not keywords:
        return text
    
    # Sort by length (longest first) to avoid partial replacements
    keywords_sorted = sorted(set(k.lower() for k in keywords), key=len, reverse=True)
    
    result = text
    for keyword in keywords_sorted:
        # Case-insensitive replacement, preserve original case
        import re
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        # Find matches and bold them
        result = pattern.sub(lambda m: f"**{m.group()}**", result)
    
    return result


def group_snippets_by_category(snippets: List[Dict]) -> Dict[str, List[Dict]]:
    """Group snippets by category."""
    grouped = {}
    for snippet in snippets:
        category = snippet.get("category", "other")
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(snippet)
    return grouped


def category_order() -> Dict[str, int]:
    """Return preferred category ordering."""
    return {
        "experience": 1,
        "achievements": 2,
        "skills": 3,
        "leadership": 4,
        "other": 5,
    }


def format_category_title(category: str) -> str:
    """Convert category to nice title."""
    titles = {
        "experience": "Experience",
        "achievements": "Key Achievements",
        "skills": "Technical Skills",
        "leadership": "Leadership & Mentoring",
        "other": "Other",
    }
    return titles.get(category, category.title())


def generate_resume_markdown(
    matched_data: Dict,
    top_n: int = None,
    include_scores: bool = True
) -> str:
    """Generate markdown resume draft."""
    snippets = matched_data.get("matched_snippets", [])
    
    # Limit to top N
    if top_n:
        snippets = snippets[:top_n]
    
    if not snippets:
        return "# Resume Draft\n\nNo snippets matched the job description above the threshold.\n"
    
    # Calculate overall match score
    overall_score = round(sum(s["relevance_score"] for s in snippets) / len(snippets), 1)
    
    lines = []
    lines.append("# Tailored Resume Draft")
    lines.append("")
    lines.append(f"**Overall Match Score: {overall_score}%**")
    lines.append("")
    
    # Group by category
    grouped = group_snippets_by_category(snippets)
    order = category_order()
    
    # Sort categories
    sorted_categories = sorted(grouped.keys(), key=lambda c: order.get(c, 999))
    
    for category in sorted_categories:
        if not grouped[category]:
            continue
        
        lines.append(f"## {format_category_title(category)}")
        lines.append("")
        
        # Sort snippets in category by score
        category_snippets = sorted(grouped[category], key=lambda s: s["relevance_score"], reverse=True)
        
        for snippet in category_snippets:
            score = snippet.get("relevance_score", 0)
            matched = snippet.get("matched_keywords", [])
            text = snippet.get("text", "")
            
            # Bold the matched keywords
            bold_text = bold_keywords(text, matched)
            
            if include_scores:
                lines.append(f"**[{score}%]** {bold_text}")
            else:
                lines.append(f"- {bold_text}")
            lines.append("")
    
    return "\n".join(lines)


def generate_cover_letter_markdown(
    matched_data: Dict,
    include_scores: bool = True
) -> str:
    """Generate markdown cover letter draft."""
    snippets = matched_data.get("matched_snippets", [])
    
    if not snippets:
        return "# Cover Letter Draft\n\nNo snippets matched the job description.\n"
    
    # Calculate overall match
    overall_score = round(sum(s["relevance_score"] for s in snippets) / len(snippets), 1)
    
    lines = []
    lines.append("# Cover Letter Draft")
    lines.append("")
    lines.append(f"**Relevance Score: {overall_score}%**")
    lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # Opening
    lines.append("## Opening Paragraph")
    lines.append("")
    lines.append("[Personalize: Add company name, hiring manager name, and why you're excited about this role]")
    lines.append("")
    
    # Grab top achievements/experience for body
    top_snippets = sorted(snippets, key=lambda s: s["relevance_score"], reverse=True)[:3]
    
    lines.append("## Why I'm a Great Fit")
    lines.append("")
    
    for i, snippet in enumerate(top_snippets, 1):
        score = snippet.get("relevance_score", 0)
        matched = snippet.get("matched_keywords", [])
        text = snippet.get("text", "")
        title = snippet.get("title", "")
        
        bold_text = bold_keywords(text, matched)
        
        lines.append(f"### {title}")
        lines.append("")
        if include_scores:
            lines.append(f"**[Match: {score}%]** {bold_text}")
        else:
            lines.append(f"{bold_text}")
        lines.append("")
    
    lines.append("## Closing Paragraph")
    lines.append("")
    lines.append("[Personalize: Thank them for considering your application, express enthusiasm, and indicate next steps]")
    lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append("**Notes for refinement:**")
    lines.append("- Add personalization in opening and closing (company name, hiring manager, specific role details)")
    lines.append("- Feel free to reorder, combine, or split snippets as needed")
    lines.append("- Edit for flow and tone to match your voice")
    lines.append("- Remove or deemphasize low-scoring items")
    
    return "\n".join(lines)


def generate_json_output(matched_data: Dict, draft_type: str = "resume") -> Dict:
    """Generate structured JSON output for programmatic use."""
    snippets = matched_data.get("matched_snippets", [])
    
    return {
        "draft_type": draft_type,
        "job_source": matched_data.get("job_source", "unknown"),
        "job_keywords_count": matched_data.get("job_keywords_count", 0),
        "matched_snippets_count": len(snippets),
        "overall_score": round(sum(s["relevance_score"] for s in snippets) / len(snippets), 1) if snippets else 0,
        "snippets": snippets
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate resume or cover letter draft from matched snippets"
    )
    parser.add_argument("matches_file", help="Matched snippets JSON (from match_snippets.py)")
    parser.add_argument("--type", choices=["resume", "cover-letter"], default="resume",
                       help="Draft type (default: resume)")
    parser.add_argument("--output", help="Output file (default: stdout)")
    parser.add_argument("--top-n", type=int,
                       help="Use only top N snippets")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown",
                       help="Output format (default: markdown)")
    parser.add_argument("--no-scores", action="store_true",
                       help="Don't include relevance scores in output")
    
    args = parser.parse_args()
    
    try:
        matched_data = load_json(args.matches_file)
        
        if args.format == "json":
            output = json.dumps(generate_json_output(matched_data, args.type), indent=2)
        elif args.type == "cover-letter":
            output = generate_cover_letter_markdown(matched_data, include_scores=not args.no_scores)
        else:  # resume
            output = generate_resume_markdown(matched_data, top_n=args.top_n, include_scores=not args.no_scores)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Draft generated: {args.output}", file=sys.stderr)
        else:
            print(output)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
