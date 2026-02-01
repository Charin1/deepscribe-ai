"""Editor Agent - Polishes and finalizes content."""

from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser

from app.core import get_logger, get_settings
from app.core.parsing import parse_with_pydantic

settings = get_settings()
logger = get_logger(__name__)


class EditedContent(BaseModel):
    final_content: str = Field(description="The polished, final article in markdown")
    summary_of_changes: str = Field(description="Summary of key editing improvements made")
    word_count: int = Field(description="Final word count")


EDITING_PROMPT = """You are a senior editor. Polish and improve the following content.

## Original Content
{content}

## External Sources (Reference)
{sources}

## Topic Context
- **Topic**: {topic}
- **Target Audience**: {target_audience}
- **Goal**: {goal}
- **Tone**: {tone}
- **Expertise Level**: {expertise_level}

## Editing Guidelines
1. Improve clarity, flow, and readability
2. Ensure consistency in tone and style
3. Check for any hallucinations or unsupported claims
4. Verify all inline citations are preserved and formatted correctly
5. Maximize the "Insight" quality based on the goal
6. Ensure headings are logical and consistent

## Output Format
- Maintain all markdown formatting, including tables and lists.
- IMPORTANT: When returning the JSON object, ensure newlines in markdown tables are preserved as `\n`.
- Do not flatten tables.

{format_instructions}
"""


def create_editor_chain(llm):
    """Create the Editor Chain."""
    parser = PydanticOutputParser(pydantic_object=EditedContent)
    
    prompt = ChatPromptTemplate.from_template(EDITING_PROMPT)
    
    # Partial format instructions into the prompt template
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    
    chain = prompt | llm | StrOutputParser() | (lambda x: parse_with_pydantic(x, EditedContent))
    return chain
