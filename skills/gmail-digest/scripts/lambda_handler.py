#!/usr/bin/env python3
"""
Lambda handler for gmail-digest
Calls format_and_deliver.py to fetch, format, and send email digest
"""

import subprocess
import json
import sys
from pathlib import Path

def lambda_handler(event, context):
    """Lambda entry point."""
    try:
        # Run format_and_deliver.py from same directory
        script_dir = Path(__file__).parent
        script_path = script_dir / "format_and_deliver.py"
        
        result = subprocess.run(
            ["python3", str(script_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout + result.stderr
        
        return {
            "statusCode": 200 if result.returncode == 0 else 500,
            "body": json.dumps({
                "success": result.returncode == 0,
                "output": output
            })
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "error": str(e)
            })
        }

if __name__ == "__main__":
    # For local testing
    result = lambda_handler({}, {})
    print(json.dumps(result, indent=2))
