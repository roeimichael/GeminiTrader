"""
Fail-fast validation for ticker data
"""

from typing import Optional
from datetime import datetime, timedelta
from .interface import route_to_vendor
from tradingagents.logger_config import get_logger

logger = get_logger(__name__)


class TickerValidationError(Exception):
    """Raised when ticker validation fails"""
    pass


def validate_ticker_data(ticker: str, date: Optional[str] = None) -> dict:
    """
    Validate that a ticker has accessible data before running agents

    This function performs fail-fast validation to ensure a stock ticker
    is valid and has accessible data before starting expensive multi-agent
    analysis workflows.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL", "MSFT")
        date: Optional date for validation context (currently unused)

    Returns:
        dict: Validation result containing:
            - valid (bool): True if validation passed
            - ticker (str): The validated ticker symbol
            - sample_data (str): Sample of the data retrieved
            - message (str): Success message

    Raises:
        TickerValidationError: If ticker is invalid, not found, or data is inaccessible
    """
    if not ticker:
        raise TickerValidationError("Ticker is empty or None")

    ticker = ticker.strip().upper()

    if not ticker.isalnum():
        raise TickerValidationError(f"Invalid ticker format: '{ticker}' (must be alphanumeric)")

    if len(ticker) > 5:
        logger.warning(f"Unusually long ticker '{ticker}' - this might be invalid")

    try:
        logger.info(f"Checking if ticker '{ticker}' has accessible data...")

        # Calculate date range for validation (last 7 days for quick check)
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        stock_data = route_to_vendor("get_stock_data", ticker, start_date, end_date)

        if stock_data is None:
            raise TickerValidationError(f"Ticker '{ticker}' returned None - likely invalid or delisted")

        if isinstance(stock_data, str):
            error_indicators = ["error", "not found", "invalid", "failed", "unavailable"]
            stock_data_lower = stock_data.lower()
            if any(indicator in stock_data_lower for indicator in error_indicators):
                raise TickerValidationError(f"Ticker '{ticker}' data fetch failed: {stock_data[:200]}")

            if len(stock_data) < 50:
                raise TickerValidationError(f"Ticker '{ticker}' returned insufficient data (only {len(stock_data)} chars)")

        logger.info(f"Ticker '{ticker}' has accessible data [PASS]")

        return {
            "valid": True,
            "ticker": ticker,
            "sample_data": stock_data if isinstance(stock_data, str) else str(stock_data)[:500],
            "message": f"Ticker '{ticker}' validated successfully"
        }

    except TickerValidationError:
        raise

    except Exception as e:
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
        ticker: Stock ticker symbol to validate
        date: Optional date for validation context
        abort_on_failure: If True, raises exception on failure; if False, logs and returns False

    Returns:
        True if validation succeeds, False if validation fails and abort_on_failure is False

    Raises:
        TickerValidationError: If validation fails and abort_on_failure is True
    """
    try:
        validate_ticker_data(ticker, date)
        return True
    except TickerValidationError as e:
        if abort_on_failure:
            raise
        else:
            logger.error(f"Validation failed: {e}")
            return False
