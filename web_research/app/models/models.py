from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class ResearchDepth(str, Enum):
    SHALLOW = "shallow"
    MODERATE = "moderate"
    DEEP = "deep"

class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = Field(default=5)
    depth: Optional[ResearchDepth] = Field(default=ResearchDepth.MODERATE)

class SearchOutput(BaseModel):
    response: str
 