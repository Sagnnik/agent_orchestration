from web_research.app.core.llm_response_models import QueryPlanOutput, SearchQueryResult, SynthesisOutput, QualityCheckOutput, ResearchDepth
from typing import Annotated, TypedDict, Optional, List
import operator

class ResearchState(TypedDict):
    original_query: str
    depth: ResearchDepth
    search_plan: Annotated[Optional[QueryPlanOutput], operator.add]
    search_results: Annotated[List[SearchQueryResult], operator.add] 
    synthesis: Annotated[Optional[SynthesisOutput], operator.add]
    quality_check: Annotated[Optional[QualityCheckOutput], operator.add]  
    iteration_count: int
    max_iterations: int
    is_complete: bool
    