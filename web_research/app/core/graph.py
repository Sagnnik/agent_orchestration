from langgraph.graph import StateGraph, END
from core.state_graph import ResearchState
from core.prompts.planner_prompt import QUERY_PLANNER_PROMPT
from core.llm import get_llm

model = get_llm()
def planner(state: ResearchState) -> ResearchState:
    """Plans the Research Steps given the user query and search depth"""
    pass

