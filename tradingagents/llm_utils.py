"""
LLM Utilities - Safe Model Initialization with Fallback
"""
import os
from typing import List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from google.genai.errors import ClientError
from tradingagents.logger_config import get_logger

logger = get_logger(__name__)


def create_gemini_model_with_fallback(
    model_candidates: List[str],
    api_key: Optional[str] = None,
    temperature: float = 0.7,
    max_retries: int = 6,
    **kwargs
) -> ChatGoogleGenerativeAI:
    """
    Safe Model Factory: Attempts to initialize a Gemini model with automatic fallback.

    Iterates through the candidate models and tests each one with a minimal invocation.
    Returns the first model that successfully responds. If all models fail, raises an error.

    Args:
        model_candidates: Ordered list of model names to try (e.g., ["gemini-1.5-flash-002", "gemini-1.5-flash-001"])
        api_key: Google API key (defaults to GOOGLE_API_KEY env var)
        temperature: Temperature for model generation (default: 0.7)
        max_retries: Maximum number of retries for rate limiting (default: 6)
        **kwargs: Additional arguments to pass to ChatGoogleGenerativeAI

    Returns:
        ChatGoogleGenerativeAI: Successfully initialized and tested model instance

    Raises:
        RuntimeError: If all candidate models fail initialization or testing
    """
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")

    if not model_candidates:
        raise ValueError("model_candidates list cannot be empty")

    last_error = None

    for model_name in model_candidates:
        try:
            logger.info(f"Attempting to initialize model: {model_name}")

            # Initialize the model
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=temperature,
                max_retries=max_retries,
                **kwargs
            )

            # Test with minimal invocation
            logger.debug(f"Testing model {model_name} with minimal invocation...")
            test_response = llm.invoke("Hello")

            # If we get here, the model works!
            logger.info(f"✓ Successfully initialized and tested model: {model_name}")
            return llm

        except ClientError as e:
            error_code = getattr(e, 'status_code', None) or getattr(e, 'code', None)

            # Handle specific error types
            if error_code == 404:
                logger.warning(f"✗ Model {model_name} not found (404), trying next candidate...")
                last_error = e
                continue
            elif error_code == 429:
                logger.warning(f"✗ Model {model_name} quota exhausted (429), trying next candidate...")
                last_error = e
                continue
            else:
                # Other client errors - log and try next
                logger.warning(f"✗ Model {model_name} failed with error {error_code}: {str(e)}")
                last_error = e
                continue

        except Exception as e:
            # Unexpected errors - log and try next
            logger.warning(f"✗ Unexpected error testing model {model_name}: {type(e).__name__}: {str(e)}")
            last_error = e
            continue

    # All models failed
    error_msg = (
        f"Failed to initialize any Gemini model. Tried {len(model_candidates)} candidates: {model_candidates}. "
        f"Last error: {type(last_error).__name__}: {str(last_error)}"
    )
    logger.error(error_msg)
    raise RuntimeError(error_msg)


def get_quick_thinking_llm(config: dict, **kwargs) -> ChatGoogleGenerativeAI:
    """
    Get a quick thinking LLM with automatic fallback.
    Uses config["quick_think_llm_candidates"] if available, falls back to config["quick_think_llm"].

    Args:
        config: Configuration dictionary
        **kwargs: Additional arguments to pass to the model

    Returns:
        ChatGoogleGenerativeAI: Initialized quick thinking model
    """
    candidates = config.get("quick_think_llm_candidates")

    # Fallback to legacy single-model config
    if not candidates:
        single_model = config.get("quick_think_llm", "gemini-1.5-flash")
        candidates = [single_model]
        logger.warning(f"Using legacy single-model config: {single_model}")

    return create_gemini_model_with_fallback(candidates, **kwargs)


def get_deep_thinking_llm(config: dict, **kwargs) -> ChatGoogleGenerativeAI:
    """
    Get a deep thinking LLM with automatic fallback.
    Uses config["deep_think_llm_candidates"] if available, falls back to config["deep_think_llm"].

    Args:
        config: Configuration dictionary
        **kwargs: Additional arguments to pass to the model

    Returns:
        ChatGoogleGenerativeAI: Initialized deep thinking model
    """
    candidates = config.get("deep_think_llm_candidates")

    # Fallback to legacy single-model config
    if not candidates:
        single_model = config.get("deep_think_llm", "gemini-1.5-pro")
        candidates = [single_model]
        logger.warning(f"Using legacy single-model config: {single_model}")

    return create_gemini_model_with_fallback(candidates, **kwargs)
