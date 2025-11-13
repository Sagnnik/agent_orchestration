import arxiv
from typing import List, Dict, Any

def arxiv_search(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Search using ArXiv API"""
    query = state.get("query", "")
    max_results = state.get("max_results", 5)
    
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        results = []
        for paper in search.results():
            results.append({
                "title": paper.title,
                "url": paper.entry_id,
                "snippet": paper.summary,
                "source": "arxiv",
                "metadata": {
                    "authors": [author.name for author in paper.authors],
                    "published": paper.published.strftime("%Y-%m-%d") if paper.published else "",
                    "categories": paper.categories,
                    "primary_category": paper.primary_category,
                    "pdf_url": paper.pdf_url
                }
            })
        
        return results
    except Exception as e:
        print(f"Error in ArXiv search: {str(e)}")
        return []