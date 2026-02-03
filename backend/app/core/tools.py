"""Tools for agents."""

from typing import Optional, List
from pydantic import BaseModel, Field
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import Tool

from app.core import get_settings

settings = get_settings()

def get_search_tool() -> Optional[Tool]:
    """
    Get the configured search tool.
    Returns a LangChain Tool for web search using Serper.
    """
    if not settings.serper_api_key:
        return None
        
    search = GoogleSerperAPIWrapper(serper_api_key=settings.serper_api_key)
    
    return Tool(
        name="search",
        func=search.run,
        description="Useful for when you need to answer questions about verify facts, or find upt-to-date information. Input should be a search query."
    )
