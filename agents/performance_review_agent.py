from typing import List
from pydantic import BaseModel, Field
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from services.performance_review import performance_review

class PerformanceInput(BaseModel):
    path: str

class PerformanceIssue(BaseModel):
    issue: str
    line: int
    code: str

class PerformanceOutput(BaseModel):
    file: str
    issue_count: int
    issues: List[PerformanceIssue] = Field(default_factory=list)

def run_performance_review(request: PerformanceInput) -> PerformanceOutput:
    report = performance_review(request.path)

    issues = [
        PerformanceIssue(
            issue=i["issue"],
            line=i["line"],
            code=i["code"]
        )
        for i in report["issues"]
    ]

    return PerformanceOutput(
        file=report["file"],
        issue_count=len(issues),
        issues=issues
    )

performance_review_agent = Agent(
    name="performance_review_agent",
    description="Analyzes code performance issues.",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction=(
        "You MUST call run_performance_review using this exact JSON schema:\n"
        "{ \"request\": { \"path\": \"<full file path>\" } }\n"
        "Never invent or modify file paths.Never return only a function-call. RULE: Always send a final text message afterward."
        "Summarize the issues briefly."
        "Example:"
        "Style review completed. Found N issues. The issues:"
    ),
    tools=[run_performance_review],
)
