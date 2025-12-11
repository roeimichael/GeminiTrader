import os
import time
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
from tqdm import tqdm
from src.config.settings import Settings
from src.data.data_fetcher import get_stock_data, get_macro_data
from src.gemini_api.analysis_engine import GeminiAnalysisEngine


def analyze_stock_with_infinite_retry(engine, ticker):
    attempt = 0
    wait_time = 30

    while True:
        attempt += 1
        try:
            stock_data = get_stock_data(ticker)
            scores = engine.analyze_stock(ticker, stock_data, verbose=False)

            if all(score is not None for score in scores.values()):
                return {
                    'Ticker': ticker,
                    'Fundamental_Score': scores['fundamental_score'],
                    'Technical_Score': scores['technical_score'],
                    'Sentiment_Score': scores['sentiment_score'],
                    'Status': 'Success',
                    'Attempts': attempt
                }
            else:
                time.sleep(wait_time)
                wait_time = min(wait_time * 1.5, 300)

        except Exception as e:
            error_msg = str(e)

            if '429' in error_msg or 'quota' in error_msg.lower() or 'rate limit' in error_msg.lower():
                if 'day' in error_msg.lower() or 'daily' in error_msg.lower():
                    wait_time = 300
                time.sleep(wait_time)
                wait_time = min(wait_time * 1.5, 600)
            else:
                time.sleep(wait_time)
                wait_time = min(wait_time * 1.5, 300)


def run_overnight_analysis():
    print("=" * 100)
    print("PERSISTENT OVERNIGHT STOCK ANALYSIS")
    print("=" * 100)

    start_time = datetime.now()
    print(f"\nStart Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in .env file")
        return

    model = Settings.GEMINI_MODEL
    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"Model: {model}")

    if 'gemini-2.5' in model.lower():
        print("\nWARNING: gemini-2.5-flash has only 20 requests/day limit")
        print("For 100 stocks, use gemini-1.5-flash (1,500 requests/day)")
        print("Change in src/config/settings.py: GEMINI_MODEL = 'gemini-1.5-flash'")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            return

    tickers = Settings.DEFAULT_TICKERS[:100]
    total_tickers = len(tickers)

    print(f"\nTotal Stocks: {total_tickers}")
    print(f"API Calls: {total_tickers * 3 + 1}")
    print(f"Model Daily Limit: {'1,500' if '1.5' in model else '20'} requests/day")

    engine = GeminiAnalysisEngine(api_key, model, rate_limit_delay=12)
    print("Engine initialized\n")

    results = []

    print("Starting stock analysis...")
    for ticker in tqdm(tickers, desc="Analyzing stocks", unit="stock"):
        result = analyze_stock_with_infinite_retry(engine, ticker)
        results.append(result)

        if (len(results) % 10 == 0):
            temp_filename = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            pd.DataFrame(results).to_csv(temp_filename, index=False)

    print("\nAnalyzing macro environment...")
    macro_summary = None
    macro_attempt = 0
    macro_wait = 30

    while macro_summary is None:
        macro_attempt += 1
        try:
            macro_data = get_macro_data()
            macro_summary = engine.analyze_macro(macro_data, verbose=False)

            if not macro_summary:
                time.sleep(macro_wait)
                macro_wait = min(macro_wait * 1.5, 300)
        except Exception:
            time.sleep(macro_wait)
            macro_wait = min(macro_wait * 1.5, 300)

    print("Macro analysis complete\n")

    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"overnight_analysis_{timestamp}.csv"
    df.to_csv(output_filename, index=False)

    end_time = datetime.now()
    duration = end_time - start_time

    print("=" * 100)
    print("RESULTS")
    print("=" * 100)
    print(f"\nFile saved: {output_filename}")
    print(f"\nScore Statistics:")
    print(f"  Fundamental - Mean: {df['Fundamental_Score'].mean():.1f}, "
          f"Min: {df['Fundamental_Score'].min()}, Max: {df['Fundamental_Score'].max()}")
    print(f"  Technical   - Mean: {df['Technical_Score'].mean():.1f}, "
          f"Min: {df['Technical_Score'].min()}, Max: {df['Technical_Score'].max()}")
    print(f"  Sentiment   - Mean: {df['Sentiment_Score'].mean():.1f}, "
          f"Min: {df['Sentiment_Score'].min()}, Max: {df['Sentiment_Score'].max()}")

    if 'Attempts' in df.columns:
        print(f"\nRetry Statistics:")
        print(f"  Total Retries: {df['Attempts'].sum() - len(df)}")
        print(f"  Average Attempts: {df['Attempts'].mean():.1f}")
        print(f"  Max Attempts: {df['Attempts'].max()}")

    if macro_summary:
        macro_filename = f"macro_analysis_{timestamp}.txt"
        with open(macro_filename, 'w') as f:
            f.write(f"Macro Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 100 + "\n\n")
            f.write(macro_summary)
        print(f"Macro file: {macro_filename}")

    print(f"\nDuration: {duration.total_seconds() / 60:.1f} minutes ({duration.total_seconds() / 3600:.2f} hours)")
    print(f"Stocks Analyzed: {len(results)}/{total_tickers}")
    print("\nANALYSIS COMPLETE")
    print("=" * 100)


if __name__ == '__main__':
    run_overnight_analysis()
