import asyncio
from google.adk.runners import InMemoryRunner
from agents.evaluator_agent import evaluator_agent

async def main():
    runner = InMemoryRunner(agent=evaluator_agent)

    sample_report = """
# Combined Review
Style: trailing spaces
Correctness: unused variable
Security: no issues
Performance: no issues
"""

    response = await runner.run_debug({
        "report": sample_report,
        "file": "main.py"
    })

    print(response)

asyncio.run(main())
