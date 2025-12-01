# agents/aggregator_agent.py

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
# from google.adk.tools import tool
from google.genai import types


class AggregatorInput(types.BaseModel):
    file: str
    style: dict
    correctness: dict
    security: dict
    performance: dict


class AggregatorOutput(types.BaseModel):
    file: str
    report: str


def run_aggregate_reviews(
    file: str,
    style: dict,
    correctness: dict,
    security: dict,
    performance: dict,
) -> AggregatorOutput:
    """Pass-through tool for structured input."""
    return AggregatorOutput(file=file, report="")
    

retry_cfg = types.HttpRetryOptions(
    attempts=3,
    exp_base=3,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

aggregator_agent = Agent(
    name="aggregator_agent",
    description="Combines multiple review results into one markdown report.",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_cfg),
    instruction=(
        "You combine all review results into a single clear Markdown report.\n\n"
        "Output format must be:\n"
        "# Code Review Report\n"
        "File: <file>\n\n"
        "## Style Issues\n"
        "- ...list...\n\n"
        "## Correctness Issues\n"
        "- ...list...\n\n"
        "## Security Issues\n"
        "- ...list...\n\n"
        "## Performance Issues\n"
        "- ...list...\n\n"
        "If any section has zero issues, write: 'No issues found.'\n"
        "Return ONLY the Markdown report text."
    ),
    tools=[run_aggregate_reviews],
)
