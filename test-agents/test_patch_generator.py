import asyncio
from google.adk.runners import InMemoryRunner
from agents.patch_generator_agent import patch_generator_agent

async def main():
    print("Running patch generator test...")

    original_path = "C:/Users/incha/Downloads/ai-code-reviewer/main.py"
    code = open(original_path).read()

    instructions = """
    Please fix:
    - Line 12: remove trailing whitespace
    - Line 7: unused variable 'x'
    """

    prompt = f"""
Generate a patch.

Original code:

{code}

Instructions:
{instructions}
"""

    runner = InMemoryRunner(agent=patch_generator_agent)
    response = await runner.run_debug(prompt)
    print(response)

asyncio.run(main())