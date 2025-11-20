import redis.asyncio as aioredis
from app.utils.config import get_settings

redis_client = None
def get_redis_url() -> str:
    settings = get_settings()
    return str(settings.redis_url)

async def init_redis() -> None:
    global redis_client
    if redis_client is not None:
        return
    redis_client = await aioredis.from_url(get_redis_url(), decode_responses=True)
    await redis_client.ping()

async def close_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None

def get_redis_client() ->aioredis.Redis:
    assert redis_client is not None, "Redis Client is not initialized"
    return redis_client