import json
import subprocess
from typing import List, Dict


def correctness_review(path: str) -> Dict:
    """Runs pylint for static correctness analysis."""

    try:
        result = subprocess.run(
            ["pylint", path, "-f", "json"],
            capture_output=True,
            text=True,
            check=False
        )

        output = result.stdout.strip()
        issues = json.loads(output) if output else []

        return {
            "file": path,
            "issue_count": len(issues),
            "issues": issues,
        }

    except Exception as e:
        return {
            "file": path,
            "issue_count": 1,
            "issues": [{"type": "error", "message": str(e)}],
        }
