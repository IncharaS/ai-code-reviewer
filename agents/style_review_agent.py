from typing import List
from pydantic import BaseModel, Field
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types
from services.style_review import style_review


class StyleReviewInput(BaseModel):
    path: str


class StyleIssue(BaseModel):
    line: int
    column: int
    code: str
    message: str


class StyleReviewOutput(BaseModel):
    file: str
    issue_count: int
    issues: List[StyleIssue] = Field(default_factory=list)


def run_style_review(path: str) -> StyleReviewOutput:
    report = style_review(path)
    return StyleReviewOutput(
        file=report["file"],
        issue_count=report["issue_count"],
        issues=[
            StyleIssue(
                line=i["line"],
                column=i["column"],
                code=i["code"],
                message=i["message"],
            )
            for i in report["issues"]
        ],
    )


style_review_agent = Agent(
    name="style_review_agent",
    description="Agent that analyzes Python style.",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction=(
    "1. Call the run_style_review tool.\n"
    "2. After receiving the result, ALWAYS return a plain-text summary like:\n"
    "'Style review completed. Issues: ...'\n"
    "Do NOT return only the function response. Always send a final text message afterward."
),
    tools=[run_style_review],
)
