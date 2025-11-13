import os
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

def tavily_search_tool(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    A search engine optimized for comprehensive, accurate, and trusted results.
    """
    query = state.get("query", "")
    max_results = state.get("max_results", 5)
    
    search_tool = TavilySearch(
        search_depth="advanced",
        max_results=max_results,
        include_answer=True,
        include_raw_content=False,
    )

    response = search_tool.invoke({"query": query})
    return response