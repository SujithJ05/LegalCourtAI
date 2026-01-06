"""LLM interaction utilities with retry logic and error handling."""
import time
from typing import Optional
from functools import lru_cache

import ollama

import config
from utils.logger import setup_logger


logger = setup_logger(__name__)


@lru_cache(maxsize=128)
def _cached_ollama_call(prompt: str, model: str, timeout: int) -> Optional[str]:
    """
    Cached LLM call to avoid duplicate requests.
    
    Args:
        prompt: The prompt (must be hashable for caching)
        model: Model name
        timeout: Timeout in seconds
    
    Returns:
        Generated text or None if failed
    """
    try:
        logger.debug(f"Making cached LLM request with model '{model}'")
        response = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            options={'timeout': timeout}
        )
        
        content = response.get('message', {}).get('content', '')
        if content:
            logger.debug(f"LLM response received (cached), length: {len(content)}")
            return content
        
        logger.warning("LLM returned empty response (cached call)")
        return None
        
    except Exception as e:
        logger.error(f"Cached LLM call failed: {e}")
        return None


def run_ollama(
    prompt: str,
    model: str = None,
    max_retries: int = None,
    timeout: int = None
) -> Optional[str]:
    """
    Run Ollama LLM with retry logic and error handling.
    
    Args:
        prompt: The prompt to send to the LLM
        model: Model name (defaults to config.OLLAMA_MODEL)
        max_retries: Maximum retry attempts (defaults to config.LLM_MAX_RETRIES)
        timeout: Timeout in seconds (defaults to config.LLM_TIMEOUT_SECONDS)
    
    Returns:
        Generated text or None if all retries failed
    """
    if model is None:
        model = config.OLLAMA_MODEL
    
    if max_retries is None:
        max_retries = config.LLM_MAX_RETRIES
    
    if timeout is None:
        timeout = config.LLM_TIMEOUT_SECONDS
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"LLM request attempt {attempt + 1}/{max_retries} with model '{model}'")
            
            # Try cached call first (only for non-first attempts to avoid stale cache)
            if attempt == 0:
                result = _cached_ollama_call(prompt, model, timeout)
                if result:
                    return result
            
            # Make the request with timeout (non-cached for retries)
            response = ollama.chat(
                model=model,
                messages=[{'role': 'user', 'content': prompt}],
                options={'timeout': timeout}
            )
            
            content = response.get('message', {}).get('content', '')
            
            if content:
                logger.debug(f"LLM response received successfully (length: {len(content)})")
                # Update cache with successful response
                _cached_ollama_call.cache_clear()  # Clear old cache
                _cached_ollama_call(prompt, model, timeout)  # Cache new result
                return content
            else:
                logger.warning(f"LLM returned empty response on attempt {attempt + 1}")
                last_error = "Empty response from LLM"
                
        except ollama.ResponseError as e:
            last_error = f"Ollama response error: {e}"
            logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {last_error}")
            
        except ollama.RequestError as e:
            last_error = f"Ollama request error: {e}"
            logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {last_error}")
            
        except TimeoutError as e:
            last_error = f"Timeout after {timeout} seconds"
            logger.warning(f"Attempt {attempt + 1}/{max_retries} timed out")
            
        except Exception as e:
            last_error = f"Unexpected error: {type(e).__name__}: {e}"
            logger.error(f"Attempt {attempt + 1}/{max_retries} failed with unexpected error: {last_error}")
        
        # Wait before retrying (exponential backoff)
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # 1, 2, 4 seconds
            logger.info(f"Waiting {wait_time}s before retry...")
            time.sleep(wait_time)
    
    logger.error(f"All {max_retries} attempts failed for model '{model}'. Last error: {last_error}")
    return None
