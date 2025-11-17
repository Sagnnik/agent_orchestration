import arxiv
from typing import List, Dict, Any

def arxiv_search(query: str, max_results:int=5) -> List[Dict[str, Any]]:
    """Search using ArXiv API"""
    client = arxiv.Client()
    
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        results = []
        for paper in client.results(search):
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