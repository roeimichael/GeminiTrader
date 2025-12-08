class Settings:
    GEMINI_MODEL = 'gemini-2.5-flash'
    ANALYSIS_TIME_UTC = '13:00'
    OUTPUT_CSV_FILENAME = 'stock_analysis_results.csv'
    LOG_FILE_NAME = 'gemini_trader.log'
    DEFAULT_TICKERS = [
        'AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'AVGO', 'ADBE', 'CRM', 'INTC', 'AMD',
        'UNH', 'JNJ', 'LLY', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'PFE', 'BMY',
        'JPM', 'BAC', 'WFC', 'GS', 'MS', 'BLK', 'SCHW', 'AXP', 'C', 'USB',
        'AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW', 'BKNG', 'CMG',
        'XOM', 'CVX', 'COP', 'SLB', 'BA', 'CAT', 'UNP', 'RTX', 'HON', 'GE'
    ]
