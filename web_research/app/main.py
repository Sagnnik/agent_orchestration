from fastapi import FastAPI
from config import get_settings
from logger import logger


app = FastAPI()

@app.get("/info")
async def info():
    settings = get_settings()
    return {
        "app_name": settings.app_name,
        "debug_mode": settings.debug
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 
