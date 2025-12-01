import subprocess
from dataclasses import dataclass
from typing import List


@dataclass
class LintIssue:
    file: str
    line: int
    column: int
    code: str
    message: str


def run_flake8(path: str) -> List[LintIssue]:
    """
    Run flake8 on the given file or directory and return structured issues.
    """
    # Format: line:col:code:message  (no file name here to avoid C: path issues)
    result = subprocess.run(
        [
            "flake8",
            "--format=%(row)d:%(col)d:%(code)s:%(text)s",
            path,
        ],
        capture_output=True,
        text=True,
    )

    issues: List[LintIssue] = []

    stdout = result.stdout.strip()
    if not stdout:
        return issues

    for line in stdout.splitlines():
        # Example: 10:5:E303:too many blank lines (2)
        parts = line.split(":", 3)
        if len(parts) != 4:
            # Unexpected output, skip this line
            continue

        line_part, col_part, code, message = parts

        try:
            issues.append(
                LintIssue(
                    file=path,
                    line=int(line_part),
                    column=int(col_part),
                    code=code.strip(),
                    message=message.strip(),
                )
            )
        except ValueError:
            # If something is weird, skip this line instead of crashing
            continue

    return issues
