"""INSIGHT Validator Agent - Ensures Inspiring, Novel, Structured, Informative, Grounded, Helpful, Trustworthy content."""

from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser

from app.core import get_logger, get_settings
from app.core.parsing import parse_with_pydantic

settings = get_settings()
logger = get_logger(__name__)


class InsightAssessment(BaseModel):
    insight_score_inspiring: int = Field(description="Score 0-100 for Inspiring")
    insight_score_novel: int = Field(description="Score 0-100 for Novel")
    insight_score_structured: int = Field(description="Score 0-100 for Structured")
    insight_score_informative: int = Field(description="Score 0-100 for Informative")
    insight_score_grounded: int = Field(description="Score 0-100 for Grounded")
    insight_score_helpful: int = Field(description="Score 0-100 for Helpful")
    insight_score_trustworthy: int = Field(description="Score 0-100 for Trustworthy")
    primary_insight: str = Field(description="What is the key nugget of novel wisdom?")
    feedback: List[str] = Field(description="Specific feedback for maximization")
    suggestions: List[str] = Field(description="Specific suggestions for enhancement")


INSIGHT_EVALUATION_PROMPT = """Evaluate the following content for I-N-S-I-G-H-T compliance:

## Content to Evaluate
{content}

## Topic Context
- **Topic**: {topic}
- **Target Audience**: {target_audience}
- **Content Goal**: {goal}

## Evaluation Criteria

### Inspiring (0-100)
- Does it captivate the reader?
- Is there an emotional or intellectual hook?

### Novel (0-100)
- Is there a unique angle or counter-intuitive insight?
- Does it avoid generic AI-sounding tropes?

### Structured (0-100)
- Is the flow logical?
- Are headings and formatting used effectively?

### Informative (0-100)
- Is the information density high?
- Are there specific details rather than generalities?

### Grounded (0-100)
- Are there examples, data, or real-world scenarios?
- Does it feel rooted in reality?

### Helpful (0-100)
- Does it directly address the reader's needs?
- Is the advice actionable?

### Trustworthy (0-100)
- Is the tone objective and balanced?
- Are claims credible?

{format_instructions}
"""


def create_insight_validator_chain(llm):
    """Create the INSIGHT Validator Chain."""
    parser = PydanticOutputParser(pydantic_object=InsightAssessment)
    
    prompt = ChatPromptTemplate.from_template(INSIGHT_EVALUATION_PROMPT)
    
    # Partial format instructions into the prompt template
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    
    chain = prompt | llm | StrOutputParser() | (lambda x: parse_with_pydantic(x, InsightAssessment))
    return chain
