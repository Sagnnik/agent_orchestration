from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class ResearchDepth(str, Enum):
    SHALLOW = "shallow"
    MODERATE = "moderate"
    DEEP = "deep"

class ConfidenceLevel(str, Enum):
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"

class QualityAction(str, Enum):
    APPROVE = "approve"
    REVISE = "revise"
    RESEARCH_MORE = "research_more"

class IssueSeverity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class SourceType(str, Enum):
    WIKIPEDIA = "wikipedia"
    WEB = "web"
    ARXIV = "arxiv"

class ResearchTool(str, Enum):
    WIKIPEDIA = "wikipedia"
    TAVILY = "tavily"
    ARXIV = "arxiv"
    #WEBSCRAPER = "webscraper"

# Models for Query Planner Node
class PlannedQuery(BaseModel):
    """A single query with assigned tools"""
    query: str = Field(description="The search query to execute")
    tools: List[ResearchTool] = Field(description="List of tools to be used for this query (wikipedia | tavily | arxiv )")

class QueryPlanOutput(BaseModel):
    """Output from the Query Planner node"""
    queries: List[PlannedQuery] = Field(description="List of 2-4 search queries with assigned tools")
    rationals: str = Field(description="Brief 1-2 sentence explanation of the research strategy and tool choices")
    #assigned_depth: ResearchDepth = Field(description="User declared research depth")

# Models for search and Gather Node
class SearchResult(BaseModel):
    """Individual search result from any tool"""
    title: str = Field(description="Title of the source")
    url: str = Field(description="URL of the source")
    content: str = Field(description= "Relevant excerpt from the source (truncated for the context)")
    raw_content: Optional[str] = Field(default=None, description="Full content for verification from (From markdowner tool)")
    score: Optional[float] = Field(default=None, description="Relevance score if available", ge=0.0, le=1.0)
    date: Optional[str] = Field(default=None, description="Publication or update date if available")
    metadata: Dict = Field(default_factory=dict, description="Tool specific metadata (authors, citations, DOI, etc.)")

class SearchQueryResult(BaseModel):
    """Results for a single search query"""
    query: str = Field(description="The search query that was executed")
    tool: ResearchTool = Field(description="The tool that was executed for this query (wikipedia | tavily | arxiv )") 
    source_type: SourceType = Field(description="Type of the sources returned (wikipedia | arxiv | web)")
    timestamp: datetime = Field(default_factory=datetime.now)
    results: List[SearchResult] = Field(description="List of Search Results")

class SearchGatherOutput(BaseModel):
    """Output from Search & Gather node"""
    search_results: List[SearchQueryResult] = Field(description="Results for all the executed search queries")

# Models for Synthesis and Citations Node
class Citations(BaseModel):
    """Individual citation mapping"""
    id: int = Field(description="citation number/ID")
    claim: str = Field(description="The specific claim made in the report")
    source_url: str = Field(description="URL of the source")
    source_type: SourceType = Field(description="Type of Source for quality assesment (wikipedia | arxiv | web)")
    quote: str = Field(description="Exact or paraphrased text from the source supporting the claim")
    confidence: ConfidenceLevel = Field(description="confidence level in this citation (high | medium | low)")

class SourceCount(BaseModel):
    """Count of sources by type"""
    source_type: str = Field(description="Type of source (arxiv, wikipedia, web)")
    count: int = Field(description="Number of sources of this type")

class SynthesisMetadata(BaseModel):
    """Metadata about the synthesized report"""
    word_count: int = Field(description="Approximate word count of the report")
    num_sources: int = Field(description="Number of unique sources cited")
    source_breakdown: List[SourceCount] = Field(
        description="Count of sources by type"
    )
    self_assesment: str = Field(description="Brief self-assessment of how well the resource covers the query")

class SynthesisOutput(BaseModel):
    """Output from Synthesis & Citation node"""
    report: str = Field(description="Complete markdown formatted research report with inline citations marker [1], [2], etc.")
    citations: List[Citations] = Field(description="List of all citations used in the report")
    metadata: SynthesisMetadata = Field(description="Metadata about the report")

# Quality Check Node
class QualityScores(BaseModel):
    """Quality assessment scores"""
    citation_accuracy: float = Field(description="Percentage of citations that were accurate (0-1)", ge=0.0, le=1.0)
    coverage: float = Field(description="How well the original query is answered (0-1)", ge=0.0, le=1.0)
    coherence: float = Field(description="Overall quality and coherence of the report", ge=0.0, le=1.0)

class CitationIssue(BaseModel):
    """Issue found with a specific citation"""
    citation_id: int = Field(description="ID of the problematic citation")
    problem: str = Field(description="Description of the problem")
    severity: IssueSeverity = Field(description="Severity of the issue (high | medium | low)")

class AdditionalQuery(BaseModel):
    """Query with tools for research_more action"""
    query: str = Field(description="Search query to fill information gap")
    tools: List[ResearchTool] = Field(description="Tools to use for this query (wikipedia | tavily | arxiv )")

class NextSteps(BaseModel):
    """Recommended next steps if quality check fails"""
    additional_queries: Optional[List[AdditionalQuery]] = Field(default=None, description="New search queries with tools to fill gaps (only if action is 'research_more')")
    revision_instructions: Optional[str] = Field(default=None, description="Specific instructions for revising the report (only if action is 'revise')")

class QualityCheckOutput(BaseModel):
    """Output from Quality Check node"""
    passed: bool = Field(description="Whether the report passes quality standards")
    scores: QualityScores = Field(description="Quality assessment scores")
    citation_issues: List[CitationIssue] = Field(description="List of citation problems found")
    coverage_gaps: List[str] = Field(description="Aspects of the query not adequately covered")
    action: QualityAction = Field(description="Recommended action to take (approve | revise | research_more)")
    next_steps: Optional[NextSteps] = Field(default=None, description="Specific next steps (only required if action is 'revise' or 'research_more')")

