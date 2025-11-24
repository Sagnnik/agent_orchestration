from app.services.redis_client import get_redis_client
from datetime import datetime, timezone
from typing import Optional
import json
import hashlib


async def store_task_status(task_id:str, status:str, data:Optional[dict] = None):
    task_data = {
        "task_id":task_id,
        "status": status,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    if data:
        task_data.update(data)

    redis_client = get_redis_client()
    await redis_client.set(
        f"task:{task_id}",
        json.dumps(task_data).encode("utf-8"),
        ex=3600
    )

async def get_task_status(task_id:str):
    redis_client = get_redis_client()
    data = await redis_client.get(f"task:{task_id}")
    if data:
        return json.loads(data.decode('utf-8'))
    
    return None
