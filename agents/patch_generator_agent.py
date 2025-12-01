from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types
from pydantic import BaseModel

class PatchOutput(BaseModel):
    updated_code: str
    description: str

def run_patch_generator(original_code: str, improvement_instructions: str) -> PatchOutput:
    """Stub for ADK — logic handled by LLM."""
    return PatchOutput(
        updated_code=original_code,
        description="Patch generated based on instructions."
    )

patch_generator_agent = Agent(
    name="patch_generator_agent",
    description="Generates improved code patches based on evaluator feedback.",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction=(
        "You are a patch generator.\n"
        "Input:\n"
        "- original_code: full source code\n"
        "- improvement_instructions: from the evaluator agent\n\n"
        "Your task:\n"
        "1. Apply the instructions precisely.\n"
        "2. Modify only the necessary lines.\n"
        "3. Maintain original formatting & comments.\n"
        "4. Never return only a function-call. Always send a final text message afterward.\n"
    ),
    tools=[run_patch_generator],
)
