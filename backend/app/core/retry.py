import asyncio
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

async def invoke_with_retry(
    chain: Any,
    input_data: Dict[str, Any],
    max_retries: int = 5,
    base_delay: int = 10,  # Start with 10s
    max_delay: int = 60,   # Cap at 60s per user request (technically user asked for "60 days" lol)
) -> Any:
    """
    Invoke a LangChain chain with retry logic for 429 Rate Limit errors.
    """
    retries = 0
    current_delay = base_delay

    while True:
        try:
            return await chain.ainvoke(input_data)
        except Exception as e:
            error_msg = str(e).lower()
            if "rate limit" in error_msg or "429" in error_msg:
                retries += 1
                if retries > max_retries:
                    logger.error(f"Rate limit exceeded. Max retries ({max_retries}) reached. Error: {e}")
                    raise e
                
                # User requested "wait for 60 days print in log and retyr again"
                # We interpret this as a significant wait. 
                # Groq usually resets fast, but if we are hitting hard limits, we wait.
                
                wait_time = min(current_delay * retries, max_delay)
                logger.warning(f"Rate limit hit. Waiting {wait_time} seconds before retry {retries}/{max_retries}...")
                print(f"Rate limit hit. Waiting {wait_time} seconds before retry {retries}/{max_retries}...") # Print to stdout as requested
                
                await asyncio.sleep(wait_time)
            else:
                # Not a rate limit error, raise immediately
                raise e
