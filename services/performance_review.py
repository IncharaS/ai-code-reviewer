import re
from typing import Dict


def performance_review(path: str) -> Dict:
    patterns = {
        "inefficient loop append": r"\.append\(",
        "string concat in loop": r"\+=\s*\"",
        "nested loop": r"for .*:\s*\n\s*for",
    }

    issues = []

    with open(path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines, start=1):
        for msg, pat in patterns.items():
            if re.search(pat, line):
                issues.append({
                    "issue": msg,
                    "line": i,
                    "code": line.strip()
                })

    return {
        "file": path,
        "issue_count": len(issues),
        "issues": issues,
    }
