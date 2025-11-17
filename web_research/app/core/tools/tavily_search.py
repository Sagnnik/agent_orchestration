import os
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

def tavily_search_tool(query: str, max_results:int=5) -> Dict[str, Any]:
    """
    A search engine optimized for comprehensive, accurate, and trusted results.
    """
    search_tool = TavilySearch(
        search_depth="advanced",
        max_results=max_results,
        include_answer=True,
        include_raw_content=False,
    )

    response = search_tool.invoke({"query": query})
    return response