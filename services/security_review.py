import re
from typing import Dict


def security_review(path: str) -> Dict:
    """Simple static scan for common security issues."""

    insecure_patterns = {
        "eval() usage": r"\beval\(",
        "exec() usage": r"\bexec\(",
        "pickle load": r"pickle\.load",
        "hardcoded password": r"(password|passwd)\s*=",
    }

    issues = []

    with open(path, "r") as f:
        lines = f.readlines()

    for idx, line in enumerate(lines, start=1):
        for issue, pattern in insecure_patterns.items():
            if re.search(pattern, line):
                issues.append({
                    "issue": issue,
                    "line": idx,
                    "code": line.strip()
                })

    return {
        "file": path,
        "issue_count": len(issues),
        "issues": issues,
    }
