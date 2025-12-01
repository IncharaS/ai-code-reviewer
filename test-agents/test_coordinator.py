import asyncio
from google.adk.runners import InMemoryRunner
from agents.review_coordinator_agent import coordinator_agent

async def main():
    path = "C:/Users/incha/Downloads/ai-code-reviewer/main.py"
    runner = InMemoryRunner(agent=coordinator_agent)

    response = await runner.run_debug(f"Please review the file: {path}")

    print("\n=== FINAL OUTPUT ===\n")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
