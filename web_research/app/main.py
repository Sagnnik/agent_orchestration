from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes
from app.utils.config import get_settings, Settings
from app.utils.logger import logger
from app.services.redis_client import get_redis_client, init_redis, close_redis
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    yield
    await close_redis()

app = FastAPI(lifespan=lifespan)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/info")
def info(settings: Settings = Depends(get_settings)):
    logger.info(f"Info endpoint called. Debug={settings.debug}")
    return {"app_name": settings.app_name, "debug": settings.debug}

@app.get("/health")
async def health_check():
    try:
        redis_client = get_redis_client()
        await redis_client.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "redis": "disconnected", "error": str(e)}
    
app.include_router(routes.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 
