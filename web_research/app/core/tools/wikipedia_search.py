import wikipedia
from typing import List, Dict, Any

def wikipedia_search(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """Search using Wikipedia API"""
    try:
        # Search for pages
        search_results = wikipedia.search(query, results=max_results)
        
        results = []
        for page_title in search_results:
            try:
                # Get page summary
                page = wikipedia.page(page_title, auto_suggest=False)
                summary = wikipedia.summary(page_title, sentences=5, auto_suggest=False)
                
                results.append({
                    "title": page.title,
                    "url": page.url,
                    "snippet": summary,
                    "source": "wikipedia",
                    "metadata": {
                        "pageid": page.pageid,
                        "revision_id": page.revision_id,
                        "categories": page.categories[:5],  # Limit categories
                        "content_length": len(page.content)
                    }
                })
            except Exception as e:
                print(f"Error fetching Wikipedia page {page_title}: {str(e)}")
                continue
        
        return results
    except Exception as e:
        print(f"Error in Wikipedia search: {str(e)}")
        return []