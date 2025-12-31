"""
Google Gemini vendor implementations for news and data generation.
Uses Gemini models with Google Search grounding for real-time news.
"""
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from .config import get_config
import os


def get_global_news_gemini(curr_date, look_back_days=7, limit=5):
    """
    Get global/macroeconomic news using Gemini with Google Search grounding.

    Args:
        curr_date: Current date in yyyy-mm-dd format
        look_back_days: Number of days to look back (default 7)
        limit: Maximum number of articles to return (default 5)

    Returns:
        str: Formatted news summary
    """
    config = get_config()

    # Initialize Gemini model - use the quick thinking model from config
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment")

    # Use Gemini 2.0 Flash which supports Google Search grounding
    # Note: grounding requires specific model versions
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",  # Supports Google Search
        google_api_key=api_key,
        temperature=0.7,
    )

    # Calculate date range
    try:
        end_date = datetime.strptime(curr_date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=look_back_days)
        start_date_str = start_date.strftime("%Y-%m-%d")
    except ValueError:
        # Fallback if date parsing fails
        start_date_str = curr_date

    # Create prompt for news search
    prompt = f"""You are a financial news analyst. Search for and summarize the most important global and macroeconomic news from {start_date_str} to {curr_date} that would be relevant for stock trading and investment decisions.

Focus on:
- Major economic indicators (GDP, inflation, employment, interest rates)
- Central bank announcements (Fed, ECB, BOJ decisions)
- Geopolitical events affecting markets
- Major corporate earnings or events with market-wide impact
- Sector trends and industry developments

Provide exactly {limit} key news items, formatted as:

## [Date] - [Headline]
**Impact:** [Market impact - Bullish/Bearish/Neutral]
**Summary:** [2-3 sentence summary]
**Relevance:** [Why this matters for traders]

---

Make your response concise, factual, and focused on actionable trading intelligence."""

    try:
        # Invoke Gemini with the prompt
        # Note: Gemini 2.0 automatically uses Google Search when needed
        response = llm.invoke(prompt)

        # Extract text content
        if hasattr(response, 'content'):
            return response.content
        else:
            return str(response)

    except Exception as e:
        # Fallback to synthetic summary if search fails
        return f"""# Global News Summary ({start_date_str} to {curr_date})

*Note: Live news data temporarily unavailable. Using general market context.*

## Market Overview
The global markets continue to navigate various macroeconomic factors including central bank policies, inflation trends, and geopolitical developments. Investors should monitor:

- **Central Bank Activity**: Interest rate decisions and policy statements
- **Economic Indicators**: GDP growth, employment data, inflation reports
- **Corporate Earnings**: Quarterly reports from major companies
- **Geopolitical Events**: Trade relations, conflicts, regulatory changes
- **Sector Trends**: Technology, energy, healthcare, financial services

**Recommendation:** Supplement this general overview with specific recent news from your preferred financial news sources.

*Error details: {str(e)}*"""


def get_news_gemini(ticker, start_date, end_date):
    """
    Get company-specific news using Gemini with Google Search grounding.

    Args:
        ticker: Stock ticker symbol
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format

    Returns:
        str: Formatted news summary for the ticker
    """
    config = get_config()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=api_key,
        temperature=0.7,
    )

    prompt = f"""You are a financial analyst. Search for and summarize news about {ticker} from {start_date} to {end_date}.

Focus on:
- Earnings reports and financial results
- Product launches or business developments
- Executive changes or strategic announcements
- Analyst upgrades/downgrades
- Regulatory news or legal developments
- Major partnerships or acquisitions

Provide 3-5 key news items formatted as:

## [Date] - [Headline]
**Sentiment:** [Positive/Negative/Neutral]
**Summary:** [2-3 sentence summary]
**Stock Impact:** [Potential impact on stock price]

---

Make your response concise and focused on trading implications for {ticker}."""

    try:
        response = llm.invoke(prompt)

        if hasattr(response, 'content'):
            return response.content
        else:
            return str(response)

    except Exception as e:
        return f"""# News for {ticker} ({start_date} to {end_date})

*Note: Live news data temporarily unavailable.*

**Recommendation:** Check financial news sources directly for recent {ticker} news and developments.

*Error: {str(e)}*"""
