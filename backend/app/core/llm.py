
from typing import Any
from app.core import get_settings

def get_llm(temperature: float = 0.5, model_name: str = None) -> Any:
    """
    Get the configured LLM based on available API keys.
    Returns a LangChain ChatModel (ChatGroq or ChatOpenAI).
    Prioritizes Groq if available, otherwise falls back to OpenAI.
    """
    settings = get_settings()
    
    # Check for Groq (preferred)
    if settings.groq_api_key:
        from langchain_groq import ChatGroq
        return ChatGroq(
            api_key=settings.groq_api_key,
            model_name=model_name or "openai/gpt-oss-120b",
            temperature=temperature,
        )
    
    # Check for OpenAI (fallback)
    if settings.openai_api_key:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=settings.openai_api_key,
            model_name=model_name or "gpt-4-turbo-preview",
            temperature=temperature,
        )
        
    raise ValueError("No valid API key found. Please set GROQ_API_KEY or OPENAI_API_KEY.")

