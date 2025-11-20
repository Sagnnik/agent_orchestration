import os
from langchain_tavily import TavilySearch
from app.utils.config import get_settings
from app.utils.logger import logger
from typing import Dict, Any

def tavily_search_tool(query: str, max_results:int=5) -> Dict[str, Any]:
    """
    A search engine optimized for comprehensive, accurate, and trusted results.
    """
    try:
        settings = get_settings()
        if not settings.tavily_api_key:
            logger.error("TAVILY_API_KEY is missing. Add it to .env or pass it in prod.")
            raise ValueError("TAVILY_API_KEY is required for Tavily search")
        
        search_tool = TavilySearch(
            api_key=settings.tavily_api_key,
            search_depth="advanced",
            max_results=max_results,
            include_answer=True,
            include_raw_content=False,
        )

        response = search_tool.invoke({"query": query})
        return response
    
    except Exception as e:
        logger.exception(f"Tavily search failed for query={query!r}: {e}")
        raise