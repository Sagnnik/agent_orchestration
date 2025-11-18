import redis
import os
import asyncio
from core.graph import create_graph
from core.llm_response_models import ResearchDepth
from langgraph.checkpoint.redis import RedisSaver
from langgraph.checkpoint.memory import MemorySaver
from uuid import UUID

def run_agent(
    thread_id:UUID, 
    query:str, 
    max_iteration:int=2, 
    depth:str=None, 
    model_provider:str="openai", 
    model_name:str="gpt-4o-mini"
):
    
    if depth is None:
        research_depth = ResearchDepth.MODERATE
    else: 
        depth_mapping = {
            "shallow": ResearchDepth.SHALLOW,
            "moderate": ResearchDepth.MODERATE,
            "deep": ResearchDepth.DEEP
        }
        research_depth = depth_mapping.get(depth.lower())

    #REDIS_URL = os.getenv("REDIS_URL")

    try:
        #checkpointer = RedisSaver.from_conn_string(REDIS_URL)
        #checkpointer.setup()
        
        checkpointer = MemorySaver()
        app = create_graph(checkpointer=checkpointer, model_name=model_name, model_provider=model_provider)
        

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

        result = asyncio.run(app.ainvoke(initial_state, config=config))
        
        return result
    except Exception as e:
        raise Exception(f"Error running research graph: {str(e)}")
    # finally:
    #     if 'checkpointer' in locals():
    #         checkpointer.conn.close()


async def run_agent_streaming(
    thread_id:UUID, 
    query:str, 
    max_iteration:int=2, 
    depth:str=None, 
    model_provider:str="openai", 
    model_name:str="gpt-4o-mini"
):
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

    #REDIS_URL = os.getenv("REDIS_URL")

    try:
        #checkpointer = RedisSaver.from_conn_string(REDIS_URL)
        #checkpointer.setup()

        checkpointer = MemorySaver()
        app = create_graph(checkpointer=checkpointer, model_name=model_name, model_provider=model_provider)
        
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

        async for event in app.astream_events(input=initial_state, config=config, version="v2"):
            #parse the raw events to get the node names and content
            event_type = event.get('event')

            if event_type == "on_chain_start":
                node_name = event.get("name", "Unknown")
                yield {"type": "node_start", "node": node_name}

            elif event_type == "on_chain_end":
                node_name = event.get("name", "Unknown")
                yield {"type": "node_end", "node": node_name}

            elif event_type == "on_chat_model_stream":
                content = event['data']['chunk'].content
                if content:
                    yield {"type": "token", "content": content}
    
    except Exception as e:
        yield {"type": "error", "message": str(e)}
    # finally:
    #     if 'checkpointer' in locals():
    #         checkpointer.conn.close()


           

