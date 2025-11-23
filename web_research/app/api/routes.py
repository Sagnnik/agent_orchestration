from langgraph.checkpoint.memory import MemorySaver
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from app.core.graph import create_graph
from app.utils.helper import run_research_agent
from app.services.cache import get_task_status, store_task_status
from app.models.models import SearchRequest, TaskStatusResponse
from app.core.agent import run_agent_streaming
from app.utils.logger import logger
from uuid import uuid4
import asyncio
from typing import Dict
import json

running_research_task: Dict[str, asyncio.Task] = {}
router = APIRouter()

@router.post("/research")
async def research_sync(request: SearchRequest):
    """Synchronous endpoint; internal test use only; must stay connected"""

    try:
        thread_id = uuid4().hex
        logger.info(
            f"[research_sync] Started | thread_id={thread_id} | "
            f"query={request.query!r} | depth={request.depth} | "
            f"max_iter={request.max_iteration} | model={request.model_provider}:{request.model_name}"
        )
        research_depth = request.depth

        checkpointer = MemorySaver()
        app_graph = create_graph(
            checkpointer=checkpointer,
            model_name=request.model_name,
            model_provider=request.model_provider
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
        result = await app_graph.ainvoke(initial_state, config=config)

        logger.info(
            f"[research_sync] Completed | thread_id={thread_id} | "
            f"iterations={result.get('iteration_count', 0)} | "
            f"search_results={len(result.get('search_results', []))}"
        )

        return {
            "thread_id": str(thread_id),
            "query": request.query,
            "status": "completed",
            "report": result.get("synthesis", {}).get("report") if result.get("synthesis") else None,
            "citations": result.get("synthesis", {}).get("citations") if result.get("synthesis") else None,
            "iterations": result.get("iteration_count", 0),
            "search_results_count": len(result.get("search_results", []))
        }
    
    except Exception as e:
        logger.exception(f"[research_sync] Error | thread_id={thread_id}")
        raise HTTPException(status_code=500, detail=f"Error running research task: {str(e)}")

@router.post("/research/async")
async def research_async(request: SearchRequest, background_tasks: BackgroundTasks):
    """
    Non-Blocking
    Runs the agent as background task and return task_id
    CLient could disconnect and poll for results later
    """

    try:
        task_id = str(uuid4().hex)
        thread_id = str(uuid4().hex)

        logger.info(
            f"[research_async] Enqueue | task_id={task_id} | thread_id={thread_id} | "
            f"query={request.query!r} | depth={request.depth} | "
            f"max_iter={request.max_iteration} | model={request.model_provider}:{request.model_name}"
        )

        await store_task_status(task_id, "pending", {
            "thread_id": thread_id,
            "query": request.query
        })

        background_tasks.add_task(
            run_research_agent,
            task_id,
            thread_id,
            request.query,
            request.max_iteration,
            request.depth,
            request.model_provider,
            request.model_name
        )

        return {
            "task_id": task_id,
            "thread_id": thread_id,
            "status": "pending",
            "message": "Research task started. Use GET /research/status/{task_id} to check progress"
        }
    except Exception as e:
        logger.exception(f"[research_async] Error starting background task | task_id={task_id}")
        raise HTTPException(status_code=500, detail=f"Error starting research task: {str(e)}")
    
@router.get("/research/status/{task_id}", response_model=TaskStatusResponse)
async def get_research_status(task_id: str):
    """
    Check the status of the background research task
    status values: pending, processing, completed, failed
    """
    try:
        task_data = await get_task_status(task_id)

        if not task_data:
            logger.warning(f"[get_research_status] Task not found | task_id={task_id}")
            raise HTTPException(status_code=404, detail="Task Not Found")
        
        logger.debug(f"[get_research_status] Task status | task_id={task_id} | status={task_data.get('status')}")
        return TaskStatusResponse(**task_data)
    
    except Exception as e:
        logger.exception(f"[get_research_status] Error | task_id={task_id}")
        raise HTTPException(status_code=500, detail=f"Error retrieving task status: {str(e)}")
    

@router.post("/research/stream")
async def research_stream(request: SearchRequest):
    """Streaming generated tokens for chat app"""
    thread_id = uuid4().hex
    logger.info(
        f"[research_stream] Start stream | thread_id={thread_id} | "
        f"query={request.query!r} | depth={request.depth} | "
        f"max_iter={request.max_iteration} | model={request.model_provider}:{request.model_name}"
    )
    
    async def event_generator():
        current_task = asyncio.current_task()
        running_research_task[thread_id] = current_task
        try:
            yield f"data: {json.dumps({'type': 'started', 'thread_id': str(thread_id), 'query': request.query})}\n\n"

            async for event in run_agent_streaming(
                thread_id=thread_id,
                query=request.query,
                max_iteration=request.max_iteration,
                depth=request.depth,
                model_provider=request.model_provider,
                model_name=request.model_name,
                api_key = request.api_key
            ):
                event_type = event.get("type")
                
                if event_type == "node_start":
                    yield f"data: {json.dumps({'type': 'node_start', 'node': event['node']})}\n\n"
                
                elif event_type == "node_end":
                    yield f"data: {json.dumps({'type': 'node_end', 'node': event['node']})}\n\n"
                
                elif event_type == "token":
                    yield f"data: {json.dumps({'type': 'token', 'content': event['content']})}\n\n"
                
                elif event_type == "error":
                    yield f"data: {json.dumps({'type': 'error', 'error': event['message']})}\n\n"
                    return

            logger.info(f"[research_stream] Completed stream | thread_id={thread_id}")
            yield f"data: {json.dumps({'type': 'completed', 'thread_id': thread_id})}\n\n"

        except asyncio.CancelledError:
            logger.info(f"[research_stream] Stream cancelled | thread_id = {thread_id}")
            try:
                yield f"data: {json.dumps({'type': 'cancelled', 'thread_id': thread_id})}\n\n"
            except Exception:
                pass
            raise

        except Exception as e:
            logger.exception(f"[research_stream] Exception in event_generator | thread_id={thread_id}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

        finally:
            running_research_task.pop(thread_id, None)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.post("/research/cancel/{thread_id}")
async def cancel_research(thread_id: str):
    task = running_research_task.get(thread_id)
    if not task:
        return JSONResponse(
            status_code=404,
            content={"status": "not_found", "thread_id": thread_id},
        )
    if task.done():
        return {"status": "already_finished", "thread_id": thread_id}
    
    task.cancel()
    logger.info(f"[cancel research] Request Cancellation | thread_id={thread_id}")
    return {"status": "cancelled_requested", "thread_id": thread_id}


