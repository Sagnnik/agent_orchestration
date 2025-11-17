import redis
import os
from core.graph import create_graph
from core.llm_response_models import ResearchDepth
from langgraph.checkpoint.redis import RedisSaver
from langgraph.checkpoint.memory import MemorySaver
from uuid import UUID

def create_agent(thread_id:UUID, query:str, max_iteration:int=5, depth:str=None, model_provider:str="ollama"):
    
    if depth is None:
        research_depth = ResearchDepth.MODERATE
    else: 
        depth_mapping = {
            "shallow": ResearchDepth.SHALLOW,
            "moderate": ResearchDepth.MODERATE,
            "deep": ResearchDepth.DEEP
        }
        research_depth = depth_mapping.get(depth.lower())
    print("Creating graph ...")
    graph = create_graph(model_provider)
    print("Graph Built ...")

    #REDIS_URL = os.getenv("REDIS_URL")

    try:
        #checkpointer = RedisSaver.from_conn_string(REDIS_URL)
        #checkpointer.setup()
        checkpointer = MemorySaver()
        app = graph.compile(checkpointer=checkpointer)
        

        config = {"configurable": {
        "thread_id": str(thread_id)
        }}
        initial_state = {
            "original_query": query,
            "depth": research_depth,
            "iteration_count": 0,
            "max_iterations": max_iteration, 
            "is_complete": False,
            "search_results": [],
        }

        result = app.invoke(initial_state, config=config)
        
        return result
    except Exception as e:
        raise Exception(f"Error running research graph: {str(e)}")
    # finally:
    #     if 'checkpointer' in locals():
    #         checkpointer.conn.close()


async def create_agent_streaming(thread_id:UUID, query:str, max_iteration:int=5, depth:str=None, model_provider:str="ollama"):
    """Agent with streaming support"""
    if depth is None:
        research_depth = ResearchDepth.MODERATE
    else: 
        depth_mapping = {
            "shallow": ResearchDepth.SHALLOW,
            "moderate": ResearchDepth.MODERATE,
            "deep": ResearchDepth.DEEP
        }
        research_depth = depth_mapping.get(depth.lower())
    
    print("Creating graph ...")
    graph = create_graph(model_provider)
    print("Graph Built ...")

    #REDIS_URL = os.getenv("REDIS_URL")

    try:
        #checkpointer = RedisSaver.from_conn_string(REDIS_URL)
        #checkpointer.setup()
        checkpointer = MemorySaver()
        app = graph.compile(checkpointer=checkpointer)
        
        config = {"configurable": {
        "thread_id": str(thread_id)
        }}
        initial_state = {
            "original_query": query,
            "depth": research_depth,
            "iteration_count": 0,
            "max_iterations": max_iteration, 
            "is_complete": False,
            "search_results": [],
        }

        async for event in app.astream(initial_state, config=config):
            yield event
    
    except Exception as e:
        yield {"error": str(e)}
    # finally:
    #     if 'checkpointer' in locals():
    #         checkpointer.conn.close()


           

