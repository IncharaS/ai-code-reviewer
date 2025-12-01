print("Running test...")

import asyncio
from google.adk.runners import InMemoryRunner
from agents.style_review_agent import style_review_agent

async def main():
    runner = InMemoryRunner(agent=style_review_agent)
    response = await runner.run_debug("Review path: C:/Users/incha/Downloads/ai-code-reviewer/main.py")
    print(response)

asyncio.run(main())
