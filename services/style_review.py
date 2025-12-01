from tools.run_linter import run_flake8

def style_review(path: str) -> dict:
    """
    High-level style review service that wraps the linter tool
    and returns a clean, structured report.
    """

    issues = run_flake8(path)

    report = {
        "file": path,
        "issue_count": len(issues),
        "issues": []
    }

    for issue in issues:
        report["issues"].append({
            "line": issue.line,
            "column": issue.column,
            "code": issue.code,
            "message": issue.message
        })

    return report
