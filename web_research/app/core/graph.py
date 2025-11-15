#graph.py
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage
from langgraph.prebuilt import ToolNode
from core.state_graph import ResearchState
from core.prompts.planner_prompt import QUERY_PLANNER_PROMPT
from core.prompts.search_gather_prompt import SEARCH_GATHER_INSTRUCTIONS
from core.prompts.synthesis_citation_prompt import SYNTHESIS_PROMPT
from core.prompts.quality_check_prompt import QUALITY_CHECK_PROMPT
from core.llm_response_models import QueryPlanOutput, SearchGatherOutput, SynthesisOutput, QualityCheckOutput, ResearchTool, SearchQueryResult, SourceType
from core.llm import get_llm
from core.tools.tavily_search import tavily_search_tool
from core.tools.wikipedia_search import wikipedia_search
from core.tools.arxiv_search import arxiv_search
from core.tools.webscraper import scrape_webpage
from typing import Any, List 

def get_source_type(tool_name: ResearchTool) -> SourceType:
    """Map tool to source type"""
    mapping = {
        ResearchTool.TAVILY: SourceType.WEB,
        ResearchTool.WIKIPEDIA: SourceType.ENCYCLOPEDIA,
        ResearchTool.ARXIV: SourceType.ACADEMIC,
        ResearchTool.WEBSCRAPER: SourceType.WEB
    }
    return mapping.get(tool_name, SourceType.WEB)

def parse_tool_results(raw_results: Any, tool_name: ResearchTool):
    """Parse results from different tools into a unified format"""
    
    if tool_name == ResearchTool.TAVILY:
        if isinstance(raw_results, dict):
            results = raw_results.get('results', [])
            parsed = []
            for result in results:
                parsed.append({
                    "title": result.get('title', ''),
                    "url": result.get('url', ''),
                    "content": result.get('content', ''),
                    "score": result.get('score', 0.0)
                })
            return parsed
        return []
    
    elif tool_name in [ResearchTool.WIKIPEDIA, ResearchTool.ARXIV]:
        if isinstance(raw_results, list):
            return raw_results
        return []
    
    elif tool_name == ResearchTool.WEBSCRAPER:
        if isinstance(raw_results, dict):
            return [raw_results]
        return []
    
    return []

class ResearchGraph:
    def __init__(self, model):
        self.model = model

    def planner(self, state: ResearchState) -> ResearchState:
        """Plans the Research Steps given the user query and search depth"""
        prompt = QUERY_PLANNER_PROMPT.format(query= state['original_query'], depth=state['depth'])
        planner_model = self.model.with_structured_output(QueryPlanOutput)
        response = planner_model.invoke([prompt])
        thinking_logs = response.additional_kwargs.get("reasoning_content") or "No reasoning field found."
        return {"search_plan": response, "thinking_logs": [thinking_logs]}

    # No need for LLM to call the tools
    # def search_gather(state: ResearchState) -> ResearchState:
    #     """Create a search and gather agent that executes search using various tools"""
    #     prompt = SEARCH_GATHER_INSTRUCTIONS
    #     search_gather_model = tool_model.with_structured_output(SearchGatherOutput)
    #     response = search_gather_model.invoke([prompt] + [state['search_plan']])
    #     thinking_logs = response.additional_kwargs.get("reasoning_content") or "No reasoning field found."
    #     return {"search_results": [response], "thinking_logs": [thinking_logs]}

    # def tool_router(state:ResearchState):
    #     """
    #     Search and Gather node calls this tool node
    #     Available tools: Tavily_search, Wikipeddia, Arxiv, Webscraper 
    #     """
    #     last_msg = state['search_results'][-1]
    #     if isinstance(last_msg, AIMessage) and getattr(last_msg, "tool_calls", None):
    #         return "tool_node"
    #     else:
    #         return "synthesis_cite"
        
    # tool_node = ToolNode(tools=tools)

# Manual Tool Calling Node
    def search_gather(self, state:ResearchState) -> ResearchState:
        """Execute searches based on plan or additional queries"""
        if state.get('quality_check') and state['quality_check'].action == "research_more":
            queries_to_execute = state["quality_check"].next_steps.additional_queries
        else:
            queries_to_execute = state['search_plan'].queries

        all_results = []

        for planned_query in queries_to_execute:
            for tool_name in planned_query.tools:
                try:
                    if tool_name == ResearchTool.WEBSCRAPER:
                        tool_input = {"url": planned_query.query}
                    else:
                        tool_input = {"query": planned_query.query}
                    if tool_name == ResearchTool.TAVILY:
                        raw_results = tavily_search_tool(tool_input)
                    elif tool_name == ResearchTool.WIKIPEDIA:
                        raw_results = wikipedia_search(tool_input)
                    elif tool_name == ResearchTool.ARXIV:
                        raw_results = arxiv_search(tool_input)
                    elif tool_name == ResearchTool.WEBSCRAPER:
                        raw_results = scrape_webpage(tool_input)
                    else:
                        continue

                    search_result = SearchQueryResult(
                        query=planned_query.query,
                        tool=tool_name,
                        source_type=get_source_type(tool_name),
                        results=parse_tool_results(raw_results, tool_name)
                    )
                    all_results.append(search_result)

                except Exception as e:
                    print(f"Error executing {tool_name} for query '{planned_query.query}': {e}")
                    continue

        return {"search_results": all_results}

    def synthesis_cite(self, state: ResearchState) -> ResearchState:
        """Synthesize the report with proper citations"""
        original_query = state['original_query']
        search_results = state['search_results']
        prompt = SYNTHESIS_PROMPT.format(original_query= original_query, search_results= search_results)
        synthesis_model = self.model.with_structured_output(SynthesisOutput)
        response = synthesis_model.invoke([prompt])
        thinking_logs = response.additional_kwargs.get("reasoning_content") or "No reasoning field found."
        return {"synthesis": response, "thinking_logs": [thinking_logs]}

    def quality_checker(self, state:ResearchState) -> ResearchState:
        """Check the quality of the generated report"""
        original_query = state['original_query']
        report = state['synthesis'].report
        citations = state['synthesis'].citations
        search_results = state['search_results']
        prompt = QUALITY_CHECK_PROMPT.format(original_query=original_query, report=report, citations=citations, search_results=search_results)
        quality_model = self.model.with_structured_output(QualityCheckOutput)
        response = quality_model.invoke([prompt])
        thinking_logs = response.additional_kwargs.get("reasoning_content") or "No reasoning field found."
        return {
        "quality_check": response,
        "thinking_logs": [thinking_logs],
        "is_complete": response.passed,
        "iteration_count": state['iteration_count'] + 1,
        "action": response.action
    }

    def quality_router(self, state:ResearchState):
        """Router to route the flow from Quality Checker node to either search_gather or synthesis_cite node or END"""
        iteration = state['iteration_count']
        max_iteration = state['max_iterations']
        complete = state['is_complete']
        action = state.get('action')
        if iteration<max_iteration and not complete:
            if action == "revise":
                return "synthesis_cite"
            elif action == "research_more":
                return "search_gather"
        return "end"

def create_graph(model_provider: str="ollama", model_name:str='qwen3:4b'): 
    model = get_llm(provider=model_provider, model_name=model_name)
    # tools = [tavily_search_tool, wikipedia_search, arxiv_search, scrape_webpage]
    # tool_model = model.bind_tools(tools=tools)
    print("Loded model...")
    research_graph = ResearchGraph(model)
    graph = StateGraph(ResearchState)

    graph.add_node("planner", research_graph.planner)
    graph.add_node("search_gather", research_graph.search_gather)
    #graph.add_node("tool_node", tool_node)
    graph.add_node("synthesis_cite", research_graph.synthesis_cite)
    graph.add_node("quality_checker", research_graph.quality_checker)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "search_gather")
    # graph.add_conditional_edges(
    #     "search_gather", 
    #     tool_router, 
    #     {
    #         "tool_node":"tool_node", 
    #         "synthesis_cite":"synthesis_cite"
    #     })
    #graph.add_edge("tool_node", "search_gather")
    graph.add_edge("search_gather", "synthesis_cite")
    graph.add_edge("synthesis_cite", "quality_checker")
    graph.add_conditional_edges(
        "quality_checker", 
        research_graph.quality_router, 
        {
            "synthesis_cite": "synthesis_cite",
            "search_gather": "search_gather", 
            "end": END
        }
    )
    return graph








