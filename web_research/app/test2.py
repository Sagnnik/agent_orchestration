from core.graph import create_graph
from uuid import uuid4
from core.llm_response_models import ResearchDepth
from dotenv import load_dotenv
import asyncio
load_dotenv()

model_provider: str="openai"
model_name:str='gpt-4o-mini'


app = create_graph(model_provider, model_name)

thread_id = uuid4().hex
query = "Explain transformer architecture in AI"
research_depth = ResearchDepth.MODERATE

initial_state = {
    "original_query": query,
    "depth": research_depth,
    "iteration_count": 0,
    "max_iterations": 5, 
    "is_complete": False,
    "search_results": [],
}

try:
    print("Invoking app")
    print(f"Initial state: {initial_state}")
    result = app.invoke(initial_state, {"configurable": {"thread_id": thread_id}})
    print("=" * 50)
    print("FINAL RESULT:")
    print(result)
except Exception as e:
    print(f"Error occurred: {str(e)}")
    import traceback
    traceback.print_exc()

    # finally: 
    #     import requests
    #     try:
    #         requests.post("http://localhost:11434/api/generate", json={"model": model_name, "keep_alive": 0})
    #     except:
    #         pass