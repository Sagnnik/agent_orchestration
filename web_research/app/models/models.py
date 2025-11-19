from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class ResearchDepth(str, Enum):
    SHALLOW = "shallow"
    MODERATE = "moderate"
    DEEP = "deep"

class SearchRequest(BaseModel):
    query: str
    max_iteration: Optional[int] = Field(default=5)
    depth: Optional[ResearchDepth] = Field(default=ResearchDepth.MODERATE)
    model_provider: Optional[str] = Field(default="openai")
    model_name: Optional[str] = Field(default="gpt-4o-mini")

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None