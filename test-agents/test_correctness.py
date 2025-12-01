print("Running correctness test...")

import asyncio
from google.adk.runners import InMemoryRunner
from agents.correctness_review_agent import correctness_review_agent

async def main():
    runner = InMemoryRunner(agent=correctness_review_agent)
    response = await runner.run_debug(
        "Review path: C:/Users/incha/Downloads/ai-code-reviewer/main.py"
    )
    print(response)

asyncio.run(main())
