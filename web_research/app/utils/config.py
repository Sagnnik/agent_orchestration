from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import AnyUrl
from functools import lru_cache
import os

class Settings(BaseSettings):
    app_name: str = "Web Researcher"
    redis_url: AnyUrl = "redis://localhost:6379/0"
    debug: bool = True

    class Config:
        env_file = ".env"

# @lru_cache()
def get_settings():
    return Settings()

