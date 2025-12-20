import os
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
from tqdm import tqdm
from src.config.settings import Settings
from src.data.data_fetcher import get_stock_data
from src.gemini_api.simple_engine import SimpleAnalysisEngine


def main():
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    engine = SimpleAnalysisEngine(api_key, Settings.GEMINI_MODEL)
    tickers = Settings.DEFAULT_TICKERS
    results = []

    for ticker in tqdm(tickers, desc="Analyzing stocks", ncols=80):
        try:
            stock_data = get_stock_data(ticker)
            scores = engine.analyze_stock(ticker, stock_data)

            results.append({
                'Ticker': ticker,
                'Fundamental_Score': scores['fundamental_score'],
                'Technical_Score': scores['technical_score'],
                'Sentiment_Score': scores['sentiment_score']
            })
        except:
            results.append({
                'Ticker': ticker,
                'Fundamental_Score': None,
                'Technical_Score': None,
                'Sentiment_Score': None
            })

    df = pd.DataFrame(results)
    filename = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)

    print(f"\n{filename}")


if __name__ == '__main__':
    main()
