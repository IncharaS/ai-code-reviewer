# test_aggregator.py

print("Running aggregator test...\n")

import asyncio
from google.adk.runners import InMemoryRunner
from agents.aggregator_agent import aggregator_agent

async def main():
    runner = InMemoryRunner(agent=aggregator_agent)

    prompt = """
Aggregate these review results:

File: C:/path/to/file.py

Style:
{
  "issue_count": 1,
  "issues": [{"line": 10, "message": "Trailing whitespace"}]
}

Correctness:
{
  "issue_count": 1,
  "issues": [{"line": 5, "message": "Unused variable"}]
}

Security:
{
  "issue_count": 0,
  "issues": []
}

Performance:
{
  "issue_count": 0,
  "issues": []
}
"""

    response = await runner.run_debug(prompt)
    print(response)

asyncio.run(main())
