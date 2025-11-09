import os
import json
from celery import Celery
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_BACKEND = os.getenv("CELERY_BACKEND_URL", REDIS_URL)

celery_app = Celery("researcher", broker=CELERY_BROKER, backend=CELERY_BACKEND)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    task_track_started=True,
    result_expires=3600,
    worker_prefetch_multiplier=1,
    task_ack_late=True,
    worker_max_tasks_per_child=100
)

redis_client = redis.Redis.from_url(REDIS_URL, decode_url=True)

def run_agent(query, max_result, depth, progress_fn):
    pass

@celery_app.task(bind=True)
def search_task(self, query, max_results, depth, task_id=None):
    """
    Celery task wrapper that runs the agent
    Publishes the progress to Redis Pub/Sub
    Stores the final result to Redis as well
    """

    pass
