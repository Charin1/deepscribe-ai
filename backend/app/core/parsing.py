import json
import re
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError
from langchain_core.exceptions import OutputParserException

T = TypeVar("T", bound=BaseModel)

def extract_json_from_text(text: str) -> str:
    """Extract JSON string from text that might contain markdown or comments."""
    text = text.strip()
    
    # Try to find markdown block first
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
        
    # Try to find generic { ... } block
    # We use a greedy match for the content to capture nested braces if possible, 
    # but strictly finding the first { and the last } is usually enough for well-formed JSON object
    
    # Finding first '{'
    start = text.find('{')
    # Finding last '}'
    end = text.rfind('}')
    
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    
    return text

def parse_with_pydantic(text: str, model_class: Type[T]) -> T:
    """Parse text into a Pydantic model using robust JSON extraction."""
    try:
        json_str = extract_json_from_text(text)
        data = json.loads(json_str)
        return model_class(**data)
    except (json.JSONDecodeError, ValidationError, Exception) as e:
        # Log the failed content for debugging if needed, or include in error
        raise OutputParserException(f"Failed to parse output for {model_class.__name__}: {str(e)}\nInput: {text[:500]}...")
