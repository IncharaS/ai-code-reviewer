import json
from google.adk.agents import Agent, ParallelAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool

from agents.style_review_agent import style_review_agent
from agents.correctness_review_agent import correctness_review_agent
from agents.security_review_agent import security_review_agent
from agents.performance_review_agent import performance_review_agent
from agents.evaluator_agent import evaluator_agent
from agents.patch_generator_agent import patch_generator_agent

from memory.memory_manager import load_past_reviews, save_review


# --------------------------------------------------
# PARALLEL REVIEW TEAM
# --------------------------------------------------

parallel_review_team = ParallelAgent(
    name="parallel_review_team",
    description="Runs all four code review agents in parallel.",
    sub_agents=[
        style_review_agent,
        correctness_review_agent,
        security_review_agent,
        performance_review_agent,
    ],
)


# --------------------------------------------------
# RETRY MANAGER AGENT (LLM-driven)
# --------------------------------------------------

retry_manager_agent = Agent(
    name="retry_manager_agent",
    description="Handles evaluation, patching, retries, and memory updates.",
    model=Gemini(model="gemini-2.5-pro"),

    instruction=(
        "You are the Retry Manager.\n\n"

        "INPUT:\n"
        "- You receive the results of all four review agents.\n"

        "PROCESS:\n"
        "1. Combine the 4 review outputs into JSON with keys:\n"
        "      style, correctness, security, performance.\n\n"
        "2. Load memory (past reviews) using load_past_reviews(file).\n"
        "   You MUST create trend_preview = first 500 chars of past reviews JSON.\n\n"
        "3. Call evaluator_agent with EXACTLY:\n"
        "{\n"
        "   'report': <json string>,\n"
        "   'file': <path string>,\n"
        "   'trend': <trend_preview>\n"
        "}\n\n"

        "4. If evaluator.should_retry == True:\n"
        "       - Call patch_generator_agent with (original_code, improvement_instructions).\n"
        "       - Replace the working code with the patched version.\n"
        "       - Re-run parallel_review_team.\n"
        "       - Re-run evaluator_agent.\n"
        "       - Up to 3 retry cycles.\n\n"

        "5. Whether or not retry occurred, SAVE the final review to memory.\n"

        "OUTPUT:\n"
        "- Final combined reviews\n"
        "- Evaluator summary\n"
        "- Final patched code\n"
        "- Retry count\n\n"

        "RULES:\n"
        "- Only call tools.\n"
        "- When calling evaluator_agent, ALWAYS pass report, file, trend.\n"
        "- NEVER modify the file path.\n"
        "- After each tool call, output a small human-readable summary.\n"
    ),

    tools=[
        AgentTool(evaluator_agent),
        AgentTool(patch_generator_agent),
    ],
)


# --------------------------------------------------
# FULL PIPELINE: PARALLEL REVIEWS -> RETRY MANAGER
# --------------------------------------------------

coordinator_agent = Agent(
    name="coordinator_agent",
    description="Runs parallel review team and then retry manager.",
    model=Gemini(model="gemini-2.5-flash-lite"),

    instruction=(
        "You are the coordinator agent.\n\n"
        "PIPELINE:\n"
        "1. Call parallel_review_team using the provided file path.\n"
        "2. After reviews finish, send ALL results into retry_manager_agent.\n\n"
        "RULES:\n"
        "- You MUST forward the exact file path.\n"
        "- You MUST NOT rewrite or abbreviate the path.\n"
        "- Use ONLY tool calls.\n"
    ),

    tools=[
        AgentTool(parallel_review_team),
        AgentTool(retry_manager_agent),
    ],
)
