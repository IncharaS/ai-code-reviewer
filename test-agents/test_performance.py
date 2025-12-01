# test_performance.py
print("Running performance test...")

import asyncio
from google.adk.runners import InMemoryRunner
from agents.performance_review_agent import performance_review_agent


async def main():
    runner = InMemoryRunner(agent=performance_review_agent)
    response = await runner.run_debug(
        "Review path: C:/Users/incha/Downloads/ai-code-reviewer/main.py"
    )
    print(response)


asyncio.run(main())
