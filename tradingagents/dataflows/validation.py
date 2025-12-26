"""
Fail-fast validation for ticker data

This module provides validation functions that check data integrity BEFORE
starting expensive multi-agent workflows. This prevents:
- Wasting API calls on invalid tickers
- 12 agents debating about non-existent stocks
- Hallucination due to missing data
- Unnecessary LLM costs

Philosophy: Fail fast, fail loud, fail cheap.
"""

from typing import Optional, Dict, Any
from .interface import route_to_vendor


class TickerValidationError(Exception):
    """Raised when ticker validation fails"""
    pass


def validate_ticker_data(ticker: str, date: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate that a ticker has accessible data before running agents

    This is a CRITICAL fail-fast check that prevents:
    - Invalid tickers from spinning up 12 agents
    - Wasted API calls and LLM costs
    - Agent hallucination due to missing data

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL", "MSFT")
        date: Optional trade date (for historical data validation)

    Returns:
        Dictionary with validation results and sample data

    Raises:
        TickerValidationError: If ticker is invalid or data unavailable

    Example:
        try:
            validation = validate_ticker_data("AAPL")
            # Safe to proceed with full agent analysis
        except TickerValidationError as e:
            # Abort immediately, inform user
            return {"error": str(e)}
    """
    # Validate ticker format
    if not ticker:
        raise TickerValidationError("Ticker is empty or None")

    ticker = ticker.strip().upper()

    if not ticker.isalnum():
        raise TickerValidationError(f"Invalid ticker format: '{ticker}' (must be alphanumeric)")

    if len(ticker) > 5:
        # Most tickers are 1-5 characters (some exceptions like BRKA, but rare)
        print(f"WARNING: Unusually long ticker '{ticker}' - this might be invalid")

    # Try to fetch basic stock data
    try:
        print(f"VALIDATION: Checking if ticker '{ticker}' has accessible data...")
        stock_data = route_to_vendor("get_stock_data", ticker, period="1mo")

        # Check if we got valid data
        if stock_data is None:
            raise TickerValidationError(f"Ticker '{ticker}' returned None - likely invalid or delisted")

        if isinstance(stock_data, str):
            # Check for error messages in string responses
            error_indicators = ["error", "not found", "invalid", "failed", "unavailable"]
            stock_data_lower = stock_data.lower()
            if any(indicator in stock_data_lower for indicator in error_indicators):
                raise TickerValidationError(f"Ticker '{ticker}' data fetch failed: {stock_data[:200]}")

            # If it's a string but not an error, it might be formatted data
            if len(stock_data) < 50:
                # Too short to be real data
                raise TickerValidationError(f"Ticker '{ticker}' returned insufficient data (only {len(stock_data)} chars)")

        print(f"VALIDATION_SUCCESS: Ticker '{ticker}' has accessible data ✓")

        return {
            "valid": True,
            "ticker": ticker,
            "sample_data": stock_data if isinstance(stock_data, str) else str(stock_data)[:500],
            "message": f"Ticker '{ticker}' validated successfully"
        }

    except TickerValidationError:
        # Re-raise our own errors
        raise

    except Exception as e:
        # Catch any API errors and convert to validation error
        error_msg = str(e)
        if "404" in error_msg or "not found" in error_msg.lower():
            raise TickerValidationError(f"Ticker '{ticker}' not found (404)")
        elif "401" in error_msg or "403" in error_msg or "unauthorized" in error_msg.lower():
            raise TickerValidationError(f"API authentication failed - check your API keys")
        elif "rate limit" in error_msg.lower():
            raise TickerValidationError(f"API rate limit exceeded - try again later or use cached data")
        else:
            raise TickerValidationError(f"Failed to validate ticker '{ticker}': {error_msg}")


def validate_before_analysis(ticker: str, date: Optional[str] = None,
                             abort_on_failure: bool = True) -> bool:
    """
    Convenience wrapper for validation with automatic error handling

    Args:
        ticker: Stock ticker to validate
        date: Optional trade date
        abort_on_failure: If True, raises exception on failure. If False, returns False.

    Returns:
        True if validation passed, False if failed (when abort_on_failure=False)

    Raises:
        TickerValidationError: If validation fails and abort_on_failure=True
    """
    try:
        validate_ticker_data(ticker, date)
        return True
    except TickerValidationError as e:
        if abort_on_failure:
            raise
        else:
            print(f"VALIDATION_FAILED: {e}")
            return False
