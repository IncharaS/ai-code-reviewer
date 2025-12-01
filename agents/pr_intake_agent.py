from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
# from google.adk.tools import tool
from google.genai import types

from tools.read_file import read_file
from tools.list_files import list_files
from tools.parse_diff import parse_diff


def run_parse_diff(diff: str):
    return parse_diff(diff)

def run_read_file(path: str):
    return {"content": read_file(path)}


def run_list_files(path: str):
    return {"files": list_files(path)}

retry = types.HttpRetryOptions(
    attempts=3,
    exp_base=3,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

pr_intake_agent = Agent(
    name="pr_intake_agent",
    description="Extracts changed files, diffs, and metadata.",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry),
    instruction=(
        "Given either a file path, folder path, or diff text:\n\n"
        "If user gives a directory → call run_list_files.\n"
        "If user gives a file path → call run_read_file.\n"
        "If user provides diff text → call run_parse_diff.\n\n"
        "After the tool runs, summarize what was extracted and return just that.\n"
        "Summarize the issues briefly."
        "Example:"
        "Style review completed. Found N issues. The issues:"
    ),
    tools=[run_parse_diff, run_read_file, run_list_files],
)
