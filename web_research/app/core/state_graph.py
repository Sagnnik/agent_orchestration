from pydantic import BaseModel, Field
from typing import Optional, List
from models.llm_response_models import QueryPlanOutput, SearchQueryResult, SynthesisOutput, QualityCheckOutput, ResearchDepth

class ResearchState(BaseModel):
    original_query: str = Field(description="User's Original research query")
    original_depth: ResearchDepth = Field(description="User declared research depth ( 'shallow' | 'moderate' | 'deep' )")
    search_plan: Optional[QueryPlanOutput] = None
    search_results: List[SearchQueryResult] = Field(default_factory=list)
    synthesis: Optional[SynthesisOutput] = None
    quality_check: Optional[QualityCheckOutput] = None
    iteration_count: int = Field(default=0)
    max_iteration: int = Field(default=3)
    is_complete: bool = Field(default=False)
    