#!/usr/bin/env python3
"""
Match resume snippets against parsed job description keywords.
Score snippets based on keyword overlap.

Usage:
    python match_snippets.py job_parsed.json snippets.json
    python match_snippets.py job_parsed.json snippets.json --output matches.json
    python match_snippets.py job_parsed.json snippets.json --min-score 40
"""

import json
import sys
import argparse
from typing import List, Dict, Tuple
from collections import Counter


def load_json(filepath: str) -> Dict:
    """Load JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load {filepath}: {e}")


def normalize_keyword(keyword: str) -> str:
    """Normalize keyword for matching (lowercase, remove extra spaces)."""
    return keyword.lower().strip()


def score_snippet(snippet_text: str, job_keywords: List[str], job_keywords_set: set) -> Tuple[float, List[str]]:
    """
    Score a snippet based on keyword overlap with job description.
    
    Returns:
        Tuple of (score as 0-100, list of matched keywords)
    """
    snippet_words = snippet_text.lower().split()
    matched = []
    
    # Check for exact keyword matches
    for keyword in job_keywords:
        keyword_lower = normalize_keyword(keyword)
        # Check exact phrase match
        if keyword_lower in snippet_text.lower():
            matched.append(keyword)
        # Check word-by-word match for multi-word keywords
        elif len(keyword_lower.split()) == 1 and keyword_lower in snippet_words:
            matched.append(keyword)
    
    # Calculate score
    if len(job_keywords) == 0:
        score = 0.0
    else:
        # Score = (matched keywords / total job keywords) * 100
        score = (len(matched) / len(job_keywords)) * 100.0
    
    return score, matched


def match_snippets(
    job_data: Dict,
    snippets_data: Dict,
    min_score: int = 30
) -> List[Dict]:
    """
    Match snippets against job description and return ranked results.
    
    Args:
        job_data: Parsed job description (from parse_job_description.py)
        snippets_data: Snippets library
        min_score: Minimum relevance score to include (0-100)
    
    Returns:
        List of matched snippets with scores, ranked highest first
    """
    job_keywords = job_data.get("all_keywords", [])
    job_keywords_set = set(normalize_keyword(k) for k in job_keywords)
    
    if not job_keywords:
        print("Warning: No keywords found in job description", file=sys.stderr)
    
    snippets = snippets_data.get("resume_snippets", [])
    
    # Score each snippet
    scored_snippets = []
    for snippet in snippets:
        snippet_text = snippet.get("text", "")
        score, matched = score_snippet(snippet_text, job_keywords, job_keywords_set)
        
        # Only include if above threshold
        if score >= min_score:
            scored_snippets.append({
                **snippet,
                "relevance_score": round(score, 1),
                "matched_keywords": matched,
                "match_count": len(matched)
            })
    
    # Sort by score (highest first), then by match count
    scored_snippets.sort(
        key=lambda x: (x["relevance_score"], x["match_count"]),
        reverse=True
    )
    
    return scored_snippets


def main():
    parser = argparse.ArgumentParser(
        description="Match snippets against job description keywords"
    )
    parser.add_argument("job_file", help="Parsed job description JSON")
    parser.add_argument("snippets_file", help="Snippets library JSON")
    parser.add_argument("--output", help="Output JSON file (default: stdout)")
    parser.add_argument("--min-score", type=int, default=30,
                       help="Minimum relevance score (0-100, default: 30)")
    parser.add_argument("--verbose", action="store_true",
                       help="Print debug info to stderr")
    
    args = parser.parse_args()
    
    try:
        job_data = load_json(args.job_file)
        snippets_data = load_json(args.snippets_file)
        
        if args.verbose:
            print(f"Job keywords extracted: {len(job_data.get('all_keywords', []))}", file=sys.stderr)
            print(f"Snippets loaded: {len(snippets_data.get('resume_snippets', []))}", file=sys.stderr)
        
        matched = match_snippets(job_data, snippets_data, min_score=args.min_score)
        
        if args.verbose:
            print(f"Snippets matching threshold ({args.min_score}%+): {len(matched)}", file=sys.stderr)
        
        result = {
            "job_source": job_data.get("source_type", "unknown"),
            "job_keywords_count": job_data.get("total_keywords", 0),
            "min_score_threshold": args.min_score,
            "matched_snippets_count": len(matched),
            "matched_snippets": matched
        }
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Matched snippets saved to {args.output}", file=sys.stderr)
        else:
            print(json.dumps(result, indent=2))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
