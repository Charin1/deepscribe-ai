"""Writer Agent - Writes content section by section."""

from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser

from app.core import get_logger, get_settings
from app.core.parsing import parse_with_pydantic

settings = get_settings()
logger = get_logger(__name__)


class SectionContent(BaseModel):
    heading: str = Field(description="The section heading")
    content: str = Field(description="The written content in markdown format")
    word_count: int = Field(description="Actual word count of the written content")
    citations: List[str] = Field(description="List of citations used")


SECTION_WRITING_PROMPT = """You are an expert content writer. Write the following section based on the provided research.

## Section Details
- **Heading**: {heading}
- **Key Points to Cover**: {key_points}
- **Target Word Count**: {word_count} words
- **Tone**: {tone}
- **Expertise Level**: {expertise_level}

## Research Material
{research_content}

## Available Sources
{sources}

## Writing Guidelines
1. Start with a strong opening
2. Cover all key points naturally
3. Use inline citations for all facts [1], statistics [2], quotes [3]
4. Match the specified tone throughout
5. Use appropriate vocabulary for the expertise level
6. Include specific examples and data points
7. End with a smooth transition

## Output Format
Write the section content in markdown.
IMPORTANT: Return the response as a JSON object.
- When formatting markdown tables or multi-line text in JSON, you MUST use literal `\n` characters for newlines.
- Do not flatten tables into a single line.
- Example: "| Col 1 | Col 2 |\\n|---|---|\\n| Val 1 | Val 2 |"

{format_instructions}
"""


def create_writer_chain(llm):
    """Create the Writer Chain."""
    parser = PydanticOutputParser(pydantic_object=SectionContent)
    
    prompt = ChatPromptTemplate.from_template(SECTION_WRITING_PROMPT)
    
    # Partial format instructions into the prompt template
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    
    chain = prompt | llm | StrOutputParser() | (lambda x: parse_with_pydantic(x, SectionContent))
    return chain
