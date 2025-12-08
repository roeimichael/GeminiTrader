FUNDAMENTAL_PROMPT_TEMPLATE = """You are an expert financial analyst specializing in fundamental analysis.

Analyze the following fundamental data for {TICKER}:

{FUNDAMENTAL_DATA}

Based on this information, evaluate the company's fundamental strength considering:
- Revenue and earnings growth trends
- Profitability metrics and margins
- Balance sheet health (debt levels, liquidity)
- Cash flow generation and sustainability
- Management guidance and execution
- Valuation relative to growth prospects

Provide a comprehensive fundamental analysis score from 1-100, where:
- 1-20: Very weak fundamentals, significant concerns
- 21-40: Below average fundamentals, notable risks
- 41-60: Average fundamentals, mixed signals
- 61-80: Strong fundamentals, positive outlook
- 81-100: Exceptional fundamentals, highly attractive

Your response must contain ONLY the numeric score in the following format:
SCORE: <number between 1-100>"""


TECHNICAL_PROMPT_TEMPLATE = """You are an expert technical analyst specializing in chart patterns and technical indicators.

Analyze the following technical data for {TICKER}:

{TECHNICAL_DATA}

Based on this information, evaluate the technical position considering:
- Price action relative to moving averages (trend strength)
- Momentum indicators (RSI, MACD) and their signals
- Volume trends and institutional participation
- Support and resistance levels
- Overall trend direction and sustainability
- Risk/reward setup for potential trades

Provide a comprehensive technical analysis score from 1-100, where:
- 1-20: Very bearish technicals, strong sell signals
- 21-40: Bearish technicals, negative momentum
- 41-60: Neutral technicals, consolidation/indecision
- 61-80: Bullish technicals, positive momentum
- 81-100: Very bullish technicals, strong buy signals

Your response must contain ONLY the numeric score in the following format:
SCORE: <number between 1-100>"""


SENTIMENT_PROMPT_TEMPLATE = """You are an expert sentiment analyst specializing in market psychology and crowd behavior.

Analyze the following sentiment data for {TICKER}:

{SENTIMENT_DATA}

Based on this information, evaluate the market sentiment considering:
- Analyst ratings consensus and price target trends
- Social media sentiment and retail investor interest
- News coverage tone and media narrative
- Insider trading activity and confidence signals
- Options market positioning and expectations
- Overall market psychology toward this stock

Provide a comprehensive sentiment analysis score from 1-100, where:
- 1-20: Extremely negative sentiment, widespread pessimism
- 21-40: Negative sentiment, bearish consensus
- 41-60: Neutral sentiment, balanced views
- 61-80: Positive sentiment, bullish consensus
- 81-100: Extremely positive sentiment, widespread optimism

Your response must contain ONLY the numeric score in the following format:
SCORE: <number between 1-100>"""


MACRO_PROMPT_TEMPLATE = """You are an expert macroeconomic analyst specializing in market environments and economic cycles.

Analyze the following macroeconomic data:

{MACRO_DATA}

Based on this information, provide a concise summary of the current market environment covering:
- Overall market trend and risk appetite
- Interest rate environment and Federal Reserve policy impact
- Economic cycle position (expansion, peak, contraction, trough)
- Key risks and opportunities in the current environment
- Sector rotation themes and which areas are favored
- Overall market outlook for the near-term (1-3 months)

Provide a clear, actionable summary in 3-5 sentences that captures the essential market context for investment decisions."""
