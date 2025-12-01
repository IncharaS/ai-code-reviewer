from typing import List
from pydantic import BaseModel, Field
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from services.correctness_review import correctness_review


class CorrectnessIssue(BaseModel):
    type: str
    message: str
    line: int | None = None
    symbol: str | None = None


class CorrectnessOutput(BaseModel):
    file: str
    issue_count: int
    issues: List[CorrectnessIssue] = Field(default_factory=list)


def run_correctness_review(path: str) -> CorrectnessOutput:
    report = correctness_review(path)

    issues = [
        CorrectnessIssue(
            type=i.get("type", "unknown"),
            message=i.get("message", ""),
            line=i.get("line", None),
            symbol=i.get("symbol", None)
        )
        for i in report["issues"]
    ]

    return CorrectnessOutput(
        file=report["file"],
        issue_count=len(issues),
        issues=issues
    )


correctness_review_agent = Agent(
    name="correctness_review_agent",
    description="Analyzes code correctness using pylint.",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="""
1. Call run_correctness_review tool.
2. After receiving the tool result, RETURN IT EXACTLY AS JSON TEXT.Never return only a function-call. Always send a final text message afterward.
3. Do NOT generate your own commentary.
   Summarize the issues briefly.

Example:
"Style review completed. Found N issues. The issues are:"
""",
    tools=[run_correctness_review],
)
