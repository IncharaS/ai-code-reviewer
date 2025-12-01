print("Running PR Intake test...\n")

import asyncio
from google.adk.runners import InMemoryRunner
from agents.pr_intake_agent import pr_intake_agent

async def main():
    runner = InMemoryRunner(agent=pr_intake_agent)
    response = await runner.run_debug(
        "Here is a diff:\n+++ b/app/user.py\n--- a/app/user.py\n"
    )
    print(response)

asyncio.run(main())
