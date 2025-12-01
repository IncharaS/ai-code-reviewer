# test_security.py
print("Running security test...")

import asyncio
from google.adk.runners import InMemoryRunner
from agents.security_review_agent import security_review_agent


async def main():
    runner = InMemoryRunner(agent=security_review_agent)
    response = await runner.run_debug(
        "Review path: C:/Users/incha/Downloads/ai-code-reviewer/main.py"
    )
    print(response)


asyncio.run(main())
