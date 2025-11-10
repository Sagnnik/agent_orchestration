SEARCH_GATHER_INSTRUCTIONS = """
## Search & Gather Processing Rules

### Tool Selection & Execution
Execute each query using the tools specified by the planner:

**Wikipedia API:**
- Use for background/definitions (usually first query)
- Extract summary + main content sections
- Keep response concise (~800 tokens max per article)

**Tavily Search:**
- Parameters: max_results=5-7, search_depth="advanced" for deep research
- Include_raw_content: True for citation verification
- Default tool for general web searches

**arXiv API:**
- Search query format: `all:quantum computing` or `ti:neural networks`
- Fetch top 5-7 papers, max_results=7
- Include: title, authors, abstract, PDF URL, publication date
- Prioritize recent papers (2023-2025) unless historical context needed

**Semantic Scholar API:**
- Use for broader academic coverage beyond arXiv
- Parameters: query, limit=5-7, fields=title,abstract,authors,year,citationCount,url
- Filter by relevance score and citation count

**Jina Reader (Automatic Follow-up):**
- After getting results, identify top 2-3 most relevant URLs
- Use Jina to fetch full content: `https://r.jina.ai/{url}`
- Prioritize: academic papers, in-depth articles, primary sources
- Skip: news snippets, short blog posts (Tavily summary sufficient)

### Result Processing
1. **Combine results from all tools** into unified format:
   - source_type: "wikipedia" | "web" | "arxiv" | "semantic_scholar"
   - title, url, content, date, metadata
   
2. **For each result:**
   - Store full raw_content for verification
   - Truncate display content to ~500 chars
   - Tag with source_type for synthesis context
   - Preserve citations/DOIs for academic sources

### Quality Filtering
Remove results that are:
- Paywalled without abstracts
- Score < 0.5 (for scored results)
- Clearly outdated for time-sensitive queries  
- Duplicate content

### Context Optimization
- Keep top 3-5 results per query
- Prioritize: academic papers > full articles > web snippets
- Total context to synthesis: ~3000-4000 tokens
- Include mix of source types when available
"""