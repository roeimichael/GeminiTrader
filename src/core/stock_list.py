from src.config.settings import Settings


def get_sp500_tickers():
    """
    Returns a list of S&P 500 stock tickers.

    Currently returns the default test tickers from settings.

    TODO: In a production version, this function would:
    - Fetch the real S&P 500 list from Wikipedia or an API
    - Parse and return all ~500 tickers
    - Handle errors and fallback to cached list
    """
    return Settings.DEFAULT_TICKERS
