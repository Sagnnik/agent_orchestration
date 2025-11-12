import os
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from core.llm_response_models import ResearchDepth

load_dotenv()
"""
from langchain_tavily import TavilySearch

tool = TavilySearch(
    max_results=1,
    topic="general",
    # include_answer=False,
    # include_raw_content=False,
    # include_images=False,
    # include_image_descriptions=False,
    # search_depth="basic",
    # time_range="day",
    # include_domains=None,
    # exclude_domains=None,
    # country=None
    # include_favicon=False
)
    

Invoke directly with args:
tool.invoke({"query": "What happened at the last wimbledon"})

json
{
    'query': 'What happened at the last wimbledon',
    'follow_up_questions': None,
    'answer': None,
    'images': [],
    'results': [{'title': "Andy Murray pulls out of the men's singles draw at his last Wimbledon",
                'url': 'https://www.nbcnews.com/news/sports/andy-murray-wimbledon-tennis-singles-draw-rcna159912',
                'content': "NBC News Now LONDON — Andy Murray, one of the last decade's most successful ..."
                'score': 0.6755297,
                'raw_content': None
                }],
    'response_time': 1.31
}
"""
def tavily_search_tool(query: str, max_results: int = 5):
    """
    A search engine optimized for comprehensive, accurate, and trusted results. 
    Useful for when you need to answer questions about current events. 
    It not only retrieves URLs and snippets, but offers advanced search depths, 
    domain management, time range filters, and image search, this tool delivers 
    real-time, accurate, and citation-backed results."
    Input should be a search query.
    """
    
    search_tool = TavilySearch(
        search_depth="advanced",
        max_results=max_results,
        include_answer="advanced",
        include_raw_content=False,
    ) 

    response = search_tool.invoke({"query": query})

    return response
