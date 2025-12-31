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
    # Model fallback lists - tries models in order until one works
    # Analyst Agents (High Speed, Low Cost)
    "quick_think_llm_candidates": [
        "gemini-2.5-flash",          # ✅ Primary: Newest standard Flash
        "gemini-2.0-flash-001",      # ✅ Secondary: Stable previous gen (reliable)
        "gemini-flash-latest",       # ⚠️ Fallback: Generic alias
        "gemini-2.0-flash-lite",     # ⚡ Ultra-fast backup (good for simple signals)
    ],
    # Planner/Manager Agents (Deep Reasoning)
    "deep_think_llm_candidates": [
        "gemini-2.5-pro",            # ✅ Primary: Newest standard Pro
        "gemini-pro-latest",         # ✅ Secondary: Generic stable alias
        "gemini-2.0-flash-exp",      # ⚠️ Fallback: Smart but low rate limit (ok for planner)
    ],
    # Legacy single-model config (deprecated, use _candidates lists above)
    "deep_think_llm": "gemini-2.5-pro",
    "quick_think_llm": "gemini-2.5-flash",
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
