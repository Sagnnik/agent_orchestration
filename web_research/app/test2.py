from core.agent import create_agent_streaming, create_agent
from core.graph import create_graph
import asyncio
from uuid import uuid4
from core.llm_response_models import ResearchDepth

# result = create_agent(
#     thread_id=uuid4(),
#     query="Explain transformer architecture in AI",
#     max_iteration=3,
#     depth="moderate",
#     model_provider="ollama"
# )
graph = create_graph()
app = graph.compile()

thread_id = uuid4().hex
query = "Explain transformer architecture in AI"
research_depth = ResearchDepth.MODERATE
# config = {"configurable": {
# "thread_id": str(thread_id)
# }}

initial_state = {
    "original_query": query,
    "depth": research_depth,
    "iteration_count": 0,
    "max_iterations": 5, 
    "is_complete": False,
    "search_results": [],
    "thinking_logs": []
}
try:
    result = app.invoke(initial_state)
    print(result)
except Exception as e:
    print(str(e))
    