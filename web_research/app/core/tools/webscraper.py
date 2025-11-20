import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
import re
import markdownify
from app.utils.logger import logger

def scrape_webpage(state: Dict[str, Any]) -> Dict[str, Any]:
    """Scrape content from a webpage using BeautifulSoup"""
    url = state.get("url", "")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title = soup.find('title')
        title_text = title.text.strip() if title else ""
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Try to find main content area
        main_content = None
        for tag in ['main', 'article', 'div.content', 'div.main-content', 'div.post-content']:
            main_content = soup.find(tag)
            if main_content:
                break
        
        if not main_content:
            main_content = soup.find('body')
        
        # Convert to markdown
        if main_content:
            markdown_content = markdownify.markdownify(str(main_content))
        else:
            markdown_content = ""
        
        # Clean up markdown
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)
        markdown_content = re.sub(r' {2,}', ' ', markdown_content)
        
        # Extract metadata
        metadata = {
            "url": url,
            "status_code": response.status_code,
            "content_type": response.headers.get('Content-Type', ''),
            "content_length": len(markdown_content)
        }
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata["description"] = meta_desc.get('content', '')
        
        # Extract meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            metadata["keywords"] = meta_keywords.get('content', '')
        
        return {
            "title": title_text,
            "url": url,
            "content": markdown_content,
            "source": "web_scraping",
            "metadata": metadata
        }
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return {
            "title": "",
            "url": url,
            "content": f"Error: {str(e)}",
            "source": "web_scraping",
            "metadata": {"error": str(e)}
        }