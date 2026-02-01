"""Content Planner Agent - Creates structured blog outlines."""

from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser

from app.core import get_logger, get_settings
from app.core.parsing import parse_with_pydantic

settings = get_settings()
logger = get_logger(__name__)


class SectionPlan(BaseModel):
    heading: str = Field(description="Section heading (H2 or H3)")
    section_type: str = Field(description="Type of section: 'introduction', 'body', 'conclusion'")
    key_points: List[str] = Field(description="List of 3-5 key talking points to cover")
    research_areas: List[str] = Field(description="Specific topics to research for this section")
    estimated_words: int = Field(description="Target word count for this section")
    order: int = Field(description="Order of the section in the outline")


class ContentPlan(BaseModel):
    sections: List[SectionPlan] = Field(description="Ordered list of sections for the blog post")


PLAN_GENERATION_PROMPT = """You are a senior content strategist. Create a detailed blog outline for the following:

## Input
- **Selected Title**: {title}
- **Topic**: {topic}
- **Target Audience**: {target_audience}
- **Content Goal**: {goal}
- **Tone**: {tone}
- **Expertise Level**: {expertise_level}
- **Target Word Count**: {word_count_min} - {word_count_max} words

## Requirements
1. Start with a compelling introduction hook
2. Organize content in logical, scannable sections
3. Use H2 for main sections, H3 for subsections
4. Include 3-5 key talking points per section
5. Suggest specific sources or research areas for each section
6. Allocate realistic word counts based on topic complexity
7. End with a strong conclusion and CTA

{format_instructions}
"""


def create_planner_chain(llm):
    """Create the Content Planner Chain."""
    parser = PydanticOutputParser(pydantic_object=ContentPlan)
    
    prompt = ChatPromptTemplate.from_template(PLAN_GENERATION_PROMPT)
    
    # Partial format instructions into the prompt template
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    
    chain = prompt | llm | StrOutputParser() | (lambda x: parse_with_pydantic(x, ContentPlan))
    return chain
