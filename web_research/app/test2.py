from core.agent import run_agent_streaming
from uuid import uuid4
import asyncio

async def main():
    thread_id = uuid4().hex
    query = "What are the recent advancements in Quantum Computing?"
    async for event in run_agent_streaming(thread_id=thread_id, query=query):
        event_type = event.get("type")

        if event_type == "node_start":
            print(f"\nStarting Node: {event['node']}\n")

        elif event_type == "node_end":
            print(f"\nCompleted Node: {event['node']}\n")

        elif event_type == "token":
            print(event['content'], end='', flush=True)

        elif event_type == "error":
            print(f"\nError: {event['message']}")

asyncio.run(main())
        