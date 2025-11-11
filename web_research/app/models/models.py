from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    max_results: int = 5
    depth: str = 'basic'

class SearchOutput(BaseModel):
    response: str
 