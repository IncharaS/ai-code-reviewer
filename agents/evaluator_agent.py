from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from pydantic import BaseModel
from typing import Optional
from memory.memory_manager import load_past_reviews


# --------------------------------------------------
# MODELS
# --------------------------------------------------

class EvaluationOutput(BaseModel):
    style_score: int
    correctness_score: int
    security_score: int
    performance_score: int
    overall_score: float
    should_retry: bool
    improvement_instructions: str
    comments: str
    trend: str


# --------------------------------------------------
# TOOL FUNCTION
# --------------------------------------------------

def run_evaluate(report: str, file: str, trend: str) -> EvaluationOutput:
    """
    The LLM actually computes the scores and decisions.
    This function just returns the schema that LLM will fill.
    """

    return EvaluationOutput(
        style_score=0,
        correctness_score=0,
        security_score=0,
        performance_score=0,
        overall_score=0.0,
        should_retry=False,
        improvement_instructions="",
        comments="",
        trend=trend,
    )


# --------------------------------------------------
# AGENT
# --------------------------------------------------

evaluator_agent = Agent(
    name="evaluator_agent",
    description="LLM judge that scores reviews, applies rubric, and uses memory trends.",
    model=Gemini(model="gemini-2.5-flash-lite"),

    instruction=(
        "You are the Evaluator Agent.\n\n"
        "INPUT YOU WILL RECEIVE:\n"
        "- report: JSON string containing style/correctness/security/performance results.\n"
        "- file: the file path being evaluated.\n"
        "- trend: preview of past reviews for this file.\n\n"

        "YOUR TASKS:\n"
        "1. Parse the report.\n"
        "2. Assign scores 1–10 for:\n"
        "   - style, correctness, security, performance.\n"
        "3. Compute overall_score = average of the four.\n"
        "4. Look at 'trend' (past reviews) and describe improvement/regression.\n"
        "5. Decide should_retry:\n"
        "     - True if overall_score < 7.\n"
        "     - False otherwise.\n"
        "6. If should_retry == True, generate concise improvement_instructions.\n"
        "7. ALWAYS return output ONLY via run_evaluate tool call.\n"
    ),

    tools=[run_evaluate],
)
