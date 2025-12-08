def get_stock_data(ticker):
    stock_data = {
        'Fundamental': f"""Recent 10-Q report for {ticker} shows revenue growth of 12% YoY.
            Earnings per share increased to $1.45, beating analyst expectations of $1.38.
            The company maintains a strong balance sheet with a debt-to-equity ratio of 0.45.
            Free cash flow improved by 18% compared to the previous quarter.
            Management guidance for next quarter suggests continued growth momentum.""",

        'Technical': f"""Technical analysis for {ticker}: Current price is $155.23, trading above
            the 50-day moving average of $148.50 and 200-day moving average of $142.10.
            RSI indicator at 62 suggests neutral momentum with slight bullish bias.
            MACD shows positive divergence with recent crossover above signal line.
            Volume trends indicate increasing institutional interest.
            Key resistance level at $160, support at $150.""",

        'Sentiment': f"""Market sentiment for {ticker} is moderately positive based on recent news.
            Analyst ratings: 15 Buy, 8 Hold, 2 Sell with average price target of $165.
            Social media sentiment analysis shows 68% positive mentions in the past week.
            Recent product launch announcement received favorable coverage in financial media.
            Insider trading activity shows modest buying by executives.
            Options market implied volatility at 22%, slightly below historical average."""
    }

    return stock_data


def get_macro_data():
    macro_data = """Current Macroeconomic Environment:

    MARKET INDICES:
    - S&P 500: 4,785.23 (+0.8% today, +18.5% YTD)
    - Nasdaq Composite: 15,234.56 (+1.2% today, +22.3% YTD)
    - Dow Jones Industrial: 37,654.89 (+0.5% today, +12.7% YTD)
    - VIX Volatility Index: 13.45 (low volatility environment)

    INTEREST RATES & BONDS:
    - Federal Funds Rate: 5.25-5.50% (last FOMC meeting held rates steady)
    - 10-Year Treasury Yield: 4.35% (down 5 basis points this week)
    - 2-Year Treasury Yield: 4.68% (yield curve still inverted)
    - Corporate Bond Spreads: Investment grade at 125 bps, narrowing trend

    ECONOMIC INDICATORS:
    - GDP Growth: Q3 estimate at 2.8% annualized, showing resilient economy
    - Unemployment Rate: 3.9% (near full employment levels)
    - Core PCE Inflation: 3.2% YoY (moderating but above Fed's 2% target)
    - Consumer Confidence Index: 102.5 (stable consumer sentiment)
    - ISM Manufacturing PMI: 48.3 (contraction territory but improving)

    FEDERAL RESERVE POLICY:
    - Current stance: Data-dependent approach with rates on hold
    - Market expectations: 60% probability of first rate cut in Q2 next year
    - Fed guidance emphasizes need to see sustained progress on inflation

    SECTOR PERFORMANCE:
    - Technology: Outperforming with AI-related stocks leading
    - Energy: Moderate gains with oil prices stabilizing around $78/barrel
    - Financials: Benefiting from higher interest rate environment
    - Consumer Discretionary: Mixed signals reflecting cautious spending
    - Healthcare: Defensive positioning attracting flows amid uncertainty

    GLOBAL CONTEXT:
    - US Dollar Index (DXY): 103.45 (strong dollar environment)
    - Oil (WTI Crude): $78.23/barrel (stable range)
    - Gold: $2,045/ounce (safe haven demand moderate)
    - European markets showing resilience despite energy concerns
    - Asian markets mixed with China policy stimulus providing support
    """

    return macro_data
