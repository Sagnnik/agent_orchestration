SEARCH_GATHER_INSTRUCTIONS = """
## Search & Gather Processing Rules

### Search Execution
1. Execute each query from the search plan sequentially
2. Use Tavily API with these parameters:
   - max_results: 5-7 per query
   - search_depth: "advanced" for deep research, "basic" for shallow
   - include_raw_content: True (for citation verification)

### Result Processing
1. For each result:
   - Store full raw_content for later verification
   - Truncate 'content' field to ~500 chars for context efficiency
   - Preserve all metadata (title, url, score, date)
   - Filter out low-quality sources (score < 0.5)

### Quality Filtering
Remove results that are:
- Paywalled content without accessible excerpts
- Forum posts or social media (unless specifically needed)
- Clearly outdated for time-sensitive queries
- Duplicate content from same domain

### Context Optimization
- Keep top 3-5 results per query for synthesis
- Store complete results in state for verification
- Total context to synthesis: ~2000-3000 tokens max
"""