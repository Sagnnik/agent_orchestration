from langgraph.checkpoint.memory import MemorySaver
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from app.core.graph import create_graph
from app.utils.helper import get_research_depth
from app.services.cache import get_task_status
from app.models.models import SearchRequest, TaskStatusResponse
from redis.asyncio import aioredis
from uuid import uuid4, UUID
import json

router = APIRouter()

@router.post("/research")
async def research_sync(request: SearchRequest):
    """Synchronous endpoint; internal test use only; must stay connected"""

    # try:
    #     thread_id = uuid4().hex
    #     task = 

@router.post("/research/async")
async def research_async(request: SearchRequest, background_task: BackgroundTasks):
    """
    Non-Blocking
    Runs the agent as background task and return task_id
    CLient could disconnect and poll for results later
    """

    try:
        task_id = str(uuid4().hex)
        thread_id = uuid4().hex

        pass

    except Exception as e:
        pass


@router.post("/research/stream")
async def research_stream(request: SearchRequest):
    """Streaming generated tokens for chat app"""
    thread_id = uuid4().hex
    exclude_node_names = ['LangGraph', 'RunnableSequence', 'RunnableLambda']
    
    async def event_generator():
        try:
            research_depth = get_research_depth(request.depth)

            checkpointer = MemorySaver()
            app_graph = create_graph(
                checkpointer=checkpointer,
                model_provider=request.model_provider,
                model_name=request.model_name
            )

            config = {"configurable": {"thread_id": str(thread_id)}}
            initial_state = {
                "original_query": request.query,
                "depth": research_depth,
                "iteration_count": 0,
                "max_iterations": request.max_iteration,
                "is_complete": False,
                "search_results": [],
            }

            yield f"data: {json.dumps({'type': 'started', 'thread_id': str(thread_id), 'query': request.query})}\n\n"

            async for event in app_graph.ainvoke(input=initial_state, config=config, version="v2"):
                event_type = event.get('type')

                if event_type == "on_chain_start":
                    node = event.get("name", "Unknown")
                    if node in exclude_node_names:
                        continue
                    node_name = node
                    yield f"data: {json.dumps({'type': 'node_start', 'node': node_name})}\n\n"

                elif event_type == "on_chain_end":
                    node = event.get('name', 'Unknown')
                    if node in exclude_node_names:
                        continue
                    node_name=node
                    yield f"data: {json.dumps({'type': 'node_end', 'node': node_name})}\n\n"

                elif event_type == "on_chat_model_stream":
                    content = event.get("data").get("chunk").content
                    if content:
                        yield f"data: {json.dumps({'type':'token', 'content':content})}\n\n"

            final_result = await app_graph.aivoke(initial_state, config=config)

            complete_data = {
                'status': 'completed',
                'thread_id': thread_id,
                'report': final_result.get('synthesis').get('report') if final_result.get('synthesis') else None,
                'citations': final_result.get('synthesis').get('citations') if final_result.get('synthesis') else None,
                'iterations': final_result.get('iteration_count', 0)
            }

            yield f"data: {json.dumps(complete_data)}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers= {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no" # Disable nginx buffering
        }
    )



