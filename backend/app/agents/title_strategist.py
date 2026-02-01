"""Title Strategist Agent - Generates SEO-aware titles."""

from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser

from app.core import get_logger, get_settings
from app.core.parsing import parse_with_pydantic

settings = get_settings()
logger = get_logger(__name__)


class TitleSuggestion(BaseModel):
    title: str = Field(description="The SEO-optimized title text")
    description: str = Field(description="Brief explanation of the angle and appeal")
    search_intent: str = Field(description="Search intent: informational, navigational, transactional, or commercial")
    difficulty: int = Field(description="Estimated keyword difficulty score 1-10")


class TitleList(BaseModel):
    titles: List[TitleSuggestion] = Field(description="List of 5-7 title suggestions")


TITLE_GENERATION_PROMPT = """You are an expert SEO strategist. Analyze the topic and generate 5-7 SEO-optimized title suggestions.

## Input
- **Topic**: {topic}
- **Target Audience**: {target_audience}
- **Content Goal**: {goal}
- **Tone**: {tone}
- **Expertise Level**: {expertise_level}

## Requirements
1. Each title must be unique
2. Titles should be 50-60 characters
3. Avoid clickbait
4. Include primary keywords naturally
5. Match the specified tone

{format_instructions}
"""

def create_title_chain(llm):
    """Create the Title Strategist Chain."""
    parser = PydanticOutputParser(pydantic_object=TitleList)
    
    prompt = ChatPromptTemplate.from_template(TITLE_GENERATION_PROMPT)
    
    # Partial format instructions into the prompt template
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    
    chain = prompt | llm | StrOutputParser() | (lambda x: parse_with_pydantic(x, TitleList))
    return chain
