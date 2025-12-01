import json
import os

MEMORY_DIR = "memory/code_history.json"

os.makedirs(MEMORY_DIR, exist_ok=True)

def load_past_reviews(file: str):
    path = os.path.join(MEMORY_DIR, f"{os.path.basename(file)}.json")
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

def save_review(file: str, review: dict):
    path = os.path.join(MEMORY_DIR, f"{os.path.basename(file)}.json")

    history = []
    if os.path.exists(path):
        with open(path, "r") as f:
            history = json.load(f)

    history.append(review)

    with open(path, "w") as f:
        json.dump(history, f, indent=2)
