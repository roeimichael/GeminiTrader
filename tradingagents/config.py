import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": os.getenv("TRADINGAGENTS_DATA_DIR", "./data"),  # Use ./data by default instead of hardcoded path
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "llm_provider": "google",
    "deep_think_llm": "gemini-1.5-pro",
    "quick_think_llm": "gemini-2.0-flash-exp",
    "backend_url": "",  # Not needed for Google Gemini
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Data vendor configuration
    # Category-level configuration (default for all tools in category)
    "data_vendors": {
        "core_stock_apis": "yfinance",       # Options: yfinance, alpha_vantage, local
        "technical_indicators": "yfinance",  # Options: yfinance, alpha_vantage, local
        "fundamental_data": "alpha_vantage", # Options: openai, alpha_vantage, local
        "news_data": "yfinance",             # Options: yfinance (for get_news), local (for get_global_news)
    },
    # Tool-level configuration (takes precedence over category-level)
    "tool_vendors": {
        # Override specific news methods that don't have yfinance implementation
        "get_global_news": "local",           # Only openai/local available, local doesn't need API key
        "get_insider_sentiment": "local",     # Only local available
        # Example: "get_stock_data": "alpha_vantage",  # Override category default
    },
}
