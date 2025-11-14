#state_graph.py
from core.llm_response_models import QueryPlanOutput, SearchQueryResult, SynthesisOutput, QualityCheckOutput, ResearchDepth
from typing import Annotated, TypedDict, Optional, List
import operator

class ResearchState(TypedDict):
    original_query: str
    depth: ResearchDepth
    search_plan: Optional[QueryPlanOutput]
    search_results: Annotated[List[SearchQueryResult], operator.add] 
    synthesis: Optional[SynthesisOutput]  
    quality_check: Optional[QualityCheckOutput]  
    action: Optional[str]
    thinking_logs: Annotated[List[str], operator.add]
    iteration_count: int
    max_iterations: int
    is_complete: bool
    