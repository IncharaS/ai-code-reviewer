# tools/parse_diff.py
def parse_diff(diff_text: str) -> dict:
    files = []
    for line in diff_text.split("\n"):
        if line.startswith("+++ b/"):
            filepath = line.replace("+++ b/", "").strip()
            files.append(filepath)
    return {"changed_files": files}
