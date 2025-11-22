import asyncio
from app.utils.logger import logger
from typing import Optional
from langgraph.checkpoint.redis import RedisSaver
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from app.services.redis_client import get_redis_client
from app.core.graph import create_graph

graph_cache = {}
graph_locks = {}
redis_checkpointer = None
checkpointer_lock = asyncio.Lock()

async def get_redis_checkpointer():
    global redis_checkpointer

    if redis_checkpointer is not None:
        return redis_checkpointer
    
    async with checkpointer_lock:
        if redis_checkpointer is not None:
            return redis_checkpointer
        
        logger.info("Initializing Redis Checkpointer")

        redis_client = get_redis_client()

        redis_checkpointer = AsyncRedisSaver(redis_client=redis_client)

        logger.info("Redis checkpointer initialized")
        return redis_checkpointer
    
def get_graph_cache_key(model_provider: str, model_name:str) -> str:
    return f"graph:{model_provider}:{model_name}"

async def get_or_create_graph(
    model_provider:str,
    model_name:str,
    api_key: Optional[str] = None,
):
    cache_key = get_graph_cache_key(model_provider, model_name)

    if cache_key not in graph_locks:
        graph_locks[cache_key] = asyncio.Lock()

    lock = graph_locks[cache_key]

    # Flow:
    # A -> checks cache
    # B -> checks cache
    # if not found:
    # A -> accquires lock -> checks again -> creats graph -> stores in cache -> returns graph -> releases lock
    # B -> accquires lock -> checks again -> return graph from cache -> releases lock
    if cache_key in graph_cache:
        logger.info(f"Using cached graph for {cache_key}")
        return graph_cache[cache_key]
    
    async with lock:
        if cache_key in graph_cache:
            logger.info(f"Using cached graph for {cache_key} (after lock)")
            return graph_cache[cache_key]
        
        checkpointer = await get_redis_checkpointer()

        logger.info(f"Creating and caching new graph for {cache_key}")
        graph = create_graph(
            checkpointer=checkpointer,
            model_provider=model_provider,
            model_name=model_name,
            api_key=api_key
        )

        graph_cache[cache_key] = graph
        logger.info(f"Graph cached successfully for {cache_key}")

        return graph
    
def get_cached_stats():
    return {
        "cached_graphs": list(graph_cache.keys()),
        "cache_size": len(graph_cache),
        "redis_checkpointer_active": redis_checkpointer is not None
    }

async def close_redis_checkpointer():
    global redis_checkpointer
    if redis_checkpointer is not None:
        await redis_checkpointer.conn.close()
        logger.info("Redis checkpointer connection closed")
        