from langgraph.graph import StateGraph, END
from core.state_graph import ResearchState
from core.prompts.planner_prompt import QUERY_PLANNER_PROMPT
from core.prompts.synthesis_citation_prompt import SYNTHESIS_PROMPT
from core.prompts.quality_check_prompt import QUALITY_CHECK_PROMPT
from core.llm_response_models import QueryPlanOutput, SynthesisOutput, QualityCheckOutput, SearchQueryResult, QualityAction, ResearchTool
from core.llm import get_llm
from core.utils import get_source_type, parse_tool_results, format_search_results
from core.tools.arxiv_search import arxiv_search
from core.tools.wikipedia_search import wikipedia_search
from core.tools.tavily_search import tavily_search_tool
import asyncio

TOOL_FUNCTIONS = {
    ResearchTool.TAVILY: tavily_search_tool,
    ResearchTool.WIKIPEDIA: wikipedia_search,
    ResearchTool.ARXIV: arxiv_search,
}

class ResearchGraph:
    def __init__(self, model):
        self.planner_model = model.with_structured_output(QueryPlanOutput)
        self.synthesis_model = model.with_structured_output(SynthesisOutput)
        self.quality_model = model.with_structured_output(QualityCheckOutput)
        self.base_model = model
    
    async def planner(self, state: ResearchState) -> ResearchState:
        """Plans the Research Steps given the user query and search depth"""
        #print("\nCalling the planner agent\n")
        prompt = QUERY_PLANNER_PROMPT.format(query=state['original_query'], depth=state['depth'])
        response = await self.planner_model.ainvoke([prompt])
        
        return {"search_plan": response}

    @staticmethod
    async def search_gather(state: ResearchState) -> ResearchState:
        """Execute searches based on plan or additional queries"""
        #print("\nCalling the search_gather agent\n")
        
        if state.get('quality_check') and state['quality_check'].next_steps and state['quality_check'].next_steps.additional_queries:
            queries_to_execute = state["quality_check"].next_steps.additional_queries
            #print(f"Executing {len(queries_to_execute)} additional queries from quality check")
        else:
            queries_to_execute = state['search_plan'].queries
            #print(f"Executing {len(queries_to_execute)} queries from search plan")

        all_results = []

        async def execute_search(planned_query, tool_name):
            try:
                if tool_name not in TOOL_FUNCTIONS:
                    return None
                
                loop = asyncio.get_event_loop()
                raw_results = await loop.run_in_executor(None, TOOL_FUNCTIONS[tool_name], planned_query.query)

                search_results = SearchQueryResult(
                    query=planned_query.query,
                    tool=tool_name,
                    source_type=get_source_type(tool_name),
                    results=parse_tool_results(raw_results, tool_name)
                )
                return search_results
            
            except Exception as e:
                #print(f"Error executing {tool_name} for query '{planned_query}'")
                return None
            
        tasks = []
        for planned_query in queries_to_execute:
            for tool_name in planned_query.tools:
                tasks.append(execute_search(planned_query, tool_name))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_results = [result for result in results if result is not None]

        return {"search_results": all_results}

    async def synthesis_cite(self, state: ResearchState) -> ResearchState:
        """Synthesize the report with proper citations"""
        original_query = state['original_query']
        search_results = state['search_results']
        formatted_results = format_search_results(search_results)
        
        prompt = SYNTHESIS_PROMPT.format(original_query=original_query, search_results=formatted_results)
        
        #print("\nCalling the synthesis agent \n")
        response = await self.synthesis_model.ainvoke([prompt])
        
        return {"synthesis": response}

    async def quality_checker(self, state: ResearchState) -> ResearchState:
        """Check the quality of the generated report"""
        
        original_query = state['original_query']
        report = state['synthesis'].report
        citations = state['synthesis'].citations
        search_results = state['search_results']
        current_iteration = state['iteration_count']
        max_iterations = state['max_iterations']
        
        prompt = QUALITY_CHECK_PROMPT.format(
            current_iteration = current_iteration,
            max_iterations = max_iterations,
            original_query=original_query, 
            report=report, 
            citations=citations, 
            search_results=search_results
        )

        #print("\nCalling the quality agent \n")
        response = await self.quality_model.ainvoke([prompt])

        return {
            "quality_check": response,
            "is_complete": response.passed,
            "iteration_count": state['iteration_count'] + 1,
            "action": response.action
        }

    @staticmethod
    def quality_router(state: ResearchState):
        """Router to route the flow from Quality Checker node to either search_gather or synthesis_cite node or END"""
        iteration = state['iteration_count']
        max_iteration = state['max_iterations']
        complete = state['is_complete']
        quality_check = state.get('quality_check')
        
        if iteration < max_iteration and not complete:
            has_additional_queries = quality_check and quality_check.next_steps and quality_check.next_steps.additional_queries and len(quality_check.next_steps.additional_queries) > 0

            if has_additional_queries:
                return "search_gather"
            
            action = quality_check.action if quality_check else None
            if action == QualityAction.REVISE:
                #print("Routing to synthesis_cite for revision")
                return "synthesis_cite"
            elif action == QualityAction.RESEARCH_MORE:
                #print("Routing to search_gather for more research")
                return "search_gather"
        
        #print("Routing to end")
        return "end"


def create_graph(checkpointer=None, model_provider: str="openai", model_name: str='gpt-4o-mini'): 
    model = get_llm(provider=model_provider, model_name=model_name)
    print(f"Loaded model: {model_provider}/{model_name}")

    rg = ResearchGraph(model)
    
    graph = StateGraph(ResearchState)

    graph.add_node("planner", rg.planner)
    graph.add_node("search_gather", ResearchGraph.search_gather)
    graph.add_node("synthesis_cite", rg.synthesis_cite)
    graph.add_node("quality_checker", rg.quality_checker)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "search_gather")
    graph.add_edge("search_gather", "synthesis_cite")
    graph.add_edge("synthesis_cite", "quality_checker")
    graph.add_conditional_edges(
        "quality_checker", 
        ResearchGraph.quality_router, 
        {
            "synthesis_cite": "synthesis_cite",
            "search_gather": "search_gather", 
            "end": END
        }
    )
    
    print("graph created...")
    if checkpointer:
        compiled = graph.compile(checkpointer=checkpointer)
    else:
        compiled = graph.compile()
    print("graph compiled...")
    return compiled