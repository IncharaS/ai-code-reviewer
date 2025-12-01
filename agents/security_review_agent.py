from typing import List
from pydantic import BaseModel, Field
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from services.security_review import security_review


class SecurityIssue(BaseModel):
    issue: str
    line: int
    code: str


class SecurityOutput(BaseModel):
    file: str
    issue_count: int
    issues: List[SecurityIssue] = Field(default_factory=list)


def run_security_review(path: str) -> SecurityOutput:
    report = security_review(path)

    issues = [
        SecurityIssue(
            issue=i["issue"],
            line=i["line"],
            code=i["code"],
        )
        for i in report["issues"]
    ]

    return SecurityOutput(
        file=report["file"],
        issue_count=len(issues),
        issues=issues
    )


security_review_agent = Agent(
    name="security_review_agent",
    description="Scans for insecure patterns.",
    model=Gemini(model="gemini-2.5-flash-lite"),

    instruction="""
    1. Call run_security_review tool.
    2. AFTER receiving tool output, respond with EXACT JSON in the final model message.
    Never return only a function-call. Always send a final text message afterward.
    Summarize the issues briefly.
    Example:
    Style review completed. Found N issues. The issues:
    """,

    tools=[run_security_review],
)
