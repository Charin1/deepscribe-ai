"""Research Agent - Performs deep web research for content sections."""

from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser

from app.core import get_logger, get_settings
from app.core.parsing import parse_with_pydantic

settings = get_settings()
logger = get_logger(__name__)


class Source(BaseModel):
    url: str = Field(description="URL of the source", default="")
    title: str = Field(description="Title of the page/article", default="")
    domain_authority: int = Field(description="Estimated domain authority 0-100", default=50)
    freshness_score: float = Field(description="Freshness score 0.0-1.0 (1.0 = very recent)", default=0.5)
    credibility_assessment: str = Field(description="Assessment of source credibility")


class ResearchFinding(BaseModel):
    heading: str = Field(description="The section heading being researched")
    sources: List[Source] = Field(description="List of sources found")
    key_facts: List[str] = Field(description="List of specific facts extracted")
    statistics: List[str] = Field(description="List of statistics and data points")
    quotes: List[str] = Field(description="Relevant expert quotes")
    summary: str = Field(description="Summary of research findings for this section")


RESEARCH_PROMPT = """You are a deep research specialist. Research the following section thoroughly.

## Section Details
- **Heading**: {heading}
- **Key Points to Cover**: {key_points}
- **Context**: Part of article on "{topic}" for {target_audience}

## Research Requirements
1. Simulate finding 3-5 authoritative sources
2. Extract specific facts, statistics, and data points
3. Find relevant quotes from experts if available
4. Note the credibility and freshness of each source
5. Identify any conflicting information between sources

{format_instructions}
"""


from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from app.core.tools import get_search_tool

SEARCH_QUERY_PROMPT = """You are a research assistant. Generate 3 effective search queries to find detailed information about the following section.
Return ONLY the queries, one per line.

## Section Details
- **Heading**: {heading}
- **Key Points**: {key_points}
- **Topic**: {topic}
"""

SYNTHESIS_PROMPT = """You are a deep research specialist. I have performed web research for a section of a blog post.
Analyze the search results and extract valid, grounded information.

## Section Details
- **Heading**: {heading}
- **Topic**: {topic}
- **Key Points**: {key_points}

## Search Results
{search_results}

## Research Requirements
1. Use ONLY the provided search results. Do not hallucinate.
2. Extract specific facts, statistics, and data points.
3. Find relevant quotes if available in the text.
4. Assess credibility based on the source domains.
5. If search results are insufficient, state what is missing.

{format_instructions}
"""

def create_researcher_chain(llm):
    """Create the Researcher Chain with real web search."""
    search_tool = get_search_tool()
    
    # Parser for the final output
    parser = PydanticOutputParser(pydantic_object=ResearchFinding)
    format_instructions = parser.get_format_instructions()
    
    if not search_tool:
        # Fallback to simulation if no API key
        prompt = ChatPromptTemplate.from_template(RESEARCH_PROMPT)
        prompt = prompt.partial(format_instructions=format_instructions)
        return prompt | llm | StrOutputParser() | (lambda x: parse_with_pydantic(x, ResearchFinding))

    # Real Research Flow
    
    # 1. Generate Queries
    query_prompt = ChatPromptTemplate.from_template(SEARCH_QUERY_PROMPT)
    generate_queries = query_prompt | llm | StrOutputParser() | (lambda x: [q.strip() for q in x.split('\n') if q.strip()][:3])
    
    # 2. Execute Search
    def perform_search(inputs):
        queries = inputs["queries"]
        results = []
        for q in queries:
            try:
                res = search_tool.run(q)
                results.append(f"Query: {q}\nResult: {res}\n---\n")
            except Exception as e:
                logger.error(f"Search failed for query '{q}': {e}")
        return "\n".join(results)

    # 3. Synthesize
    synthesis_prompt = ChatPromptTemplate.from_template(SYNTHESIS_PROMPT)
    synthesis_prompt = synthesis_prompt.partial(format_instructions=format_instructions)
    
    chain = (
        RunnablePassthrough.assign(
            queries=lambda x: generate_queries.invoke(x)
        )
        | RunnablePassthrough.assign(
            search_results=lambda x: perform_search(x)
        )
        | synthesis_prompt
        | llm
        | StrOutputParser()
        | (lambda x: parse_with_pydantic(x, ResearchFinding))
    )
    
    return chain
