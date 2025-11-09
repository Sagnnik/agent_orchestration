from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from workers.celery_app import run_agent, redis_client, search_task
from models import SearchRequest
from redis.asyncio import aioredis
import asyncio
import os

router = APIRouter()
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_async = aioredis.from_url(REDIS_URL, decode_response=True)


@router.post("/search")
async def search(req: SearchRequest):
    """ 
    Makes Blocking request to Agent directly
    Runs agent in a thread
    """
    try:
        final = await asyncio.to_thread(lambda: run_agent(req.query, req.max_results, req.depth))
        return JSONResponse({"status": "done", "result": final})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/async/")
async def async_search(req: SearchRequest):
    """ 
    Posts the Query to Redis Queue to be picked up by celery worker 
    returns a task_id and status
    """
    res = search_task.delay(req.query, req.max_results, req.depth)
    return JSONResponse({"task_id": res.id, "status": "queued"})

@router.get("/search/stream/{task_id}")
async def stream(task_id:str):
    """ SSE endpoint for streaming results from the redis cache (Pub/Sub) """
    pass

@router.get("/search/status/{task_id}")
async def search_status(task_id:str):
    """ Checks the task status """
    pass
