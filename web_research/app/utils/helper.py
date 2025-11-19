from app.models.models import ResearchDepth
from datetime import datetime, timezone
from langgraph.checkpoint.memory import MemorySaver
from app.core.graph import create_graph
from app.services.cache import store_task_status, get_task_status

def get_research_depth(depth:str) ->ResearchDepth:
    if depth is None:
        return ResearchDepth.MODERATE
    
    mapping = {
        "shallow":ResearchDepth.SHALLOW,
        "moderate": ResearchDepth.MODERATE,
        "deep": ResearchDepth.DEEP
    }
    return mapping.get(depth.lower(), ResearchDepth.MODERATE)


async def run_research_agent(
    task_id: str,
    thread_id: str,
    query: str,
    max_iteration: int,
    depth: str,
    model_provider: str,
    model_name: str
):
    try:
        await store_task_status(task_id, "processing", {
            "thread_id": thread_id,
            "query": query
        })

        research_depth = get_research_depth(depth)

        checkpointer = MemorySaver()
        app_graph = create_graph(
            checkpointer=checkpointer,
            model_name=model_name,
            model_provider=model_provider
        )

        config = {"configurable": {"thread_id": thread_id}}
        initial_state = {
            "original_query": query,
            "depth": research_depth,
            "iteration_count": 0,
            "max_iterations": max_iteration,
            "is_complete": False,
            "search_results": [],
        }

        result = await app_graph.ainvoke(initial_state, config=config)

        final_result = {
            "thread_id": thread_id,
            "query": query,
            "report": result.get('synthesis').get('report') if result.get('synthesis') else None,
            "citations": result.get('synthesis').get('citations') if result.get('synthesis') else None,
            "iterations": result.get('iteration_count', 0),
            "search_results_count": len(result.get("search_results", [])),
            "depth": depth
        }

        await store_task_status(task_id, "completed", {
            "thread_id": thread_id,
            "query": query,
            "completed_at": datetime.now(timezone.utc),
            "result": final_result
        })

    except Exception as e:
        await store_task_status(task_id, "failed", {
            "thread_id": thread_id,
            "query": query,
            "completed_at": datetime.now(timezone.utc),
            "error": str(e)
        })