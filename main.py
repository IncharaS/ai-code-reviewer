import sys
import asyncio
from google.adk.runners import InMemoryRunner
from agents.review_coordinator_agent import coordinator_agent 


async def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_file>")
        return

    path = sys.argv[1]
    prompt = f"Please review the Python file at: {path}"

    runner = InMemoryRunner(agent=coordinator_agent)

    resp = await runner.run_debug(prompt)

    print("\n====== MODEL SUMMARY ======\n")
    # Find last event with text parts
    for event in resp:
        if hasattr(event, "content") and event.content and event.content.parts:
            for part in event.content.parts:
                if getattr(part, "text", None):
                    print(part.text)

    print("\n\n====== RAW EVENT PARTS ======\n")

    for event in resp:
        print(f"\n--- Event from: {event.author} ---")
        if hasattr(event, "content") and event.content:
            for part in (event.content.parts or []):
                print("PART:", part)
        else:
            print("NO CONTENT")
        print("---------------------------------")


if __name__ == "__main__":
    asyncio.run(main())
