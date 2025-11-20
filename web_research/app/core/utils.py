from app.core.llm_response_models import ResearchTool, SourceType, SearchQueryResult
from typing import Any, List

def get_source_type(tool_name: ResearchTool) -> SourceType:
    """Map tool to source type"""
    mapping = {
        ResearchTool.TAVILY: SourceType.WEB,
        ResearchTool.WIKIPEDIA: SourceType.WIKIPEDIA,
        ResearchTool.ARXIV: SourceType.ARXIV,
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
            parsed = []
            for result in raw_results:
                parsed.append({
                    "title": result.get('title', ''),
                    "url": result.get('url', ''),
                    "content": result.get('snippet', ''),
                    "source": result.get('source', ''),
                    "metadata": result.get('metadata', {})
                })
            return parsed
        return []
    
    return []

def format_search_results(search_results: List[SearchQueryResult]):
    """Format search results in a compact format for the LLM prompt"""
    formatted = []
    citation_id = 1
    
    for search_result in search_results:
        formatted.append(f"\n{'='*80}")
        formatted.append(f"Query: '{search_result.query}' | Tool: {search_result.tool.value} | Source: {search_result.source_type.value}")
        formatted.append(f"{'='*80}\n")
        
        for result in search_result.results:
            formatted.append(f"[{citation_id}] {result.title}")
            formatted.append(f"    URL: {result.url}")
            
            if result.date:
                formatted.append(f"    Date: {result.date}")
            if result.score is not None:
                formatted.append(f"    Score: {result.score:.2f}")
            
            content_preview = result.content.replace('\n', ' ')
            formatted.append(f"    Content: {content_preview}...")
            
            if result.metadata:
                meta_str = []
                if 'authors' in result.metadata and result.metadata['authors']:
                    authors = result.metadata['authors'][:2]
                    meta_str.append(f"Authors: {', '.join(authors)}")
                if 'published' in result.metadata:
                    meta_str.append(f"Published: {result.metadata['published']}")
                
                if meta_str:
                    formatted.append(f"    Metadata: {' | '.join(meta_str)}")
            
            formatted.append("")
            citation_id += 1
    
    return "\n".join(formatted)