# tools/list_files.py
import os

def list_files(directory: str) -> list[str]:
    files = []
    for root, _, filenames in os.walk(directory):
        for f in filenames:
            if f.endswith(".py"):   # You can extend later
                files.append(os.path.join(root, f))
    return files
