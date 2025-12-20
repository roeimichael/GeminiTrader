class Settings:
    GEMINI_MODEL = 'gemini-2.5-flash'
    OUTPUT_CSV_FILENAME = 'stock_analysis_results.csv'

    # 50 stocks across 5 sectors (10 stocks per sector)
    DEFAULT_TICKERS = [
        # Technology
        'AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'AVGO', 'ADBE', 'CRM', 'ORCL', 'CSCO',
        # Healthcare
        'UNH', 'JNJ', 'LLY', 'ABBV', 'MRK', 'TMO', 'ABT', 'PFE', 'AMGN', 'GILD',
        # Financial
        'JPM', 'BAC', 'WFC', 'GS', 'MS', 'BLK', 'SCHW', 'AXP', 'C', 'V',
        # Consumer
        'AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'WMT', 'COST', 'PG',
        # Energy/Industrial
        'XOM', 'CVX', 'COP', 'BA', 'CAT', 'UNP', 'RTX', 'HON', 'GE', 'LMT'
    ]
