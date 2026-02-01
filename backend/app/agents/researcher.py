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


def create_researcher_chain(llm):
    """Create the Researcher Chain."""
    # We use PydanticOutputParser JUST to get the instructions
    parser = PydanticOutputParser(pydantic_object=ResearchFinding)
    
    prompt = ChatPromptTemplate.from_template(RESEARCH_PROMPT)
    
    # Partial format instructions into the prompt template
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    
    # Use StrOutputParser to get raw text, then our robust parser
    chain = prompt | llm | StrOutputParser() | (lambda x: parse_with_pydantic(x, ResearchFinding))
    return chain
