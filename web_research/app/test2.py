from core.agent import create_agent_streaming
import asyncio
from uuid import uuid4

async def main():
    thread_id = uuid4()
    print("=== State Updates ===")
    async for event in create_agent_streaming(
        thread_id=thread_id,
        query="What is quantum computing?",
        depth="moderate"
    ):
        print(f"Event: {event}")

asyncio.run(main())