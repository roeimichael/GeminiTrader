import os
import time
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
from src.config.settings import Settings
from src.data.data_fetcher import get_stock_data, get_macro_data
from src.gemini_api.analysis_engine import GeminiAnalysisEngine


def analyze_stock_with_infinite_retry(engine, ticker, stock_num, total_stocks):
    attempt = 0
    wait_time = 30

    while True:
        attempt += 1
        try:
            print(f"\n[{stock_num}/{total_stocks}] Analyzing {ticker} (Attempt #{attempt})...")

            stock_data = get_stock_data(ticker)
            scores = engine.analyze_stock(ticker, stock_data, verbose=False)

            if all(score is not None for score in scores.values()):
                print(f"  ✓ SUCCESS: {ticker} - F={scores['fundamental_score']}, "
                      f"T={scores['technical_score']}, S={scores['sentiment_score']}")
                return {
                    'Ticker': ticker,
                    'Fundamental_Score': scores['fundamental_score'],
                    'Technical_Score': scores['technical_score'],
                    'Sentiment_Score': scores['sentiment_score'],
                    'Status': 'Success',
                    'Attempts': attempt
                }
            else:
                print(f"  ⚠️  {ticker}: Missing scores, retrying in {wait_time}s...")
                time.sleep(wait_time)
                wait_time = min(wait_time * 1.5, 300)

        except Exception as e:
            error_msg = str(e)

            if '429' in error_msg or 'quota' in error_msg.lower() or 'rate limit' in error_msg.lower():
                if 'day' in error_msg.lower() or 'daily' in error_msg.lower():
                    print(f"  ⚠️  {ticker}: DAILY quota limit hit!")
                    print(f"  ℹ️  Waiting 5 minutes before retry (attempt #{attempt})...")
                    wait_time = 300
                else:
                    print(f"  ⚠️  {ticker}: Rate limit hit (attempt #{attempt})")
                    print(f"  ℹ️  Waiting {wait_time} seconds...")

                time.sleep(wait_time)
                wait_time = min(wait_time * 1.5, 600)
            else:
                print(f"  ❌ {ticker}: Unexpected error - {error_msg[:100]}")
                print(f"  ℹ️  Retrying in {wait_time}s (attempt #{attempt})...")
                time.sleep(wait_time)
                wait_time = min(wait_time * 1.5, 300)


def run_overnight_analysis():
    print("=" * 100)
    print("🌙 PERSISTENT OVERNIGHT STOCK ANALYSIS - GEMINI AI")
    print("=" * 100)
    print("\n⚠️  IMPORTANT: This script will NOT stop until all 100 stocks are analyzed!")
    print("It will retry failed requests indefinitely with exponential backoff.\n")

    start_time = datetime.now()
    print(f"🕐 Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        print("\n❌ ERROR: GEMINI_API_KEY not found in .env file")
        return

    model = Settings.GEMINI_MODEL
    print(f"✓ API Key loaded: {api_key[:10]}...{api_key[-4:]}")
    print(f"✓ Model: {model}")

    if 'gemini-2.5' in model.lower():
        print("\n⚠️  WARNING: gemini-2.5-flash has only 20 requests/day limit!")
        print("⚠️  For 100 stocks, use gemini-1.5-flash (1,500 requests/day)")
        print("⚠️  Change in src/config/settings.py: GEMINI_MODEL = 'gemini-1.5-flash'")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            return

    tickers = Settings.DEFAULT_TICKERS[:100]
    total_tickers = len(tickers)

    print(f"\n📊 Analysis Plan:")
    print(f"  • Total Stocks: {total_tickers}")
    print(f"  • API Calls: {total_tickers * 3} + 1 macro = {total_tickers * 3 + 1} total")
    print(f"  • Strategy: Infinite retries with exponential backoff")
    print(f"  • Model Daily Limit: {'1,500' if '1.5' in model else '20'} requests/day")

    print("\n🤖 Initializing Gemini Analysis Engine...")
    engine = GeminiAnalysisEngine(api_key, model, rate_limit_delay=12)
    print("✓ Engine ready\n")

    results = []
    success_count = 0

    print("=" * 100)
    print("🔄 STARTING PERSISTENT STOCK ANALYSIS")
    print("=" * 100)

    for i, ticker in enumerate(tickers, 1):
        result = analyze_stock_with_infinite_retry(engine, ticker, i, total_tickers)
        results.append(result)
        success_count += 1

        if i % 10 == 0:
            elapsed = (datetime.now() - start_time).total_seconds() / 60
            avg_time_per_stock = elapsed / i
            remaining = (total_tickers - i) * avg_time_per_stock

            print(f"\n{'=' * 100}")
            print(f"📈 PROGRESS CHECKPOINT - {i}/{total_tickers} stocks completed ({i/total_tickers*100:.1f}%)")
            print(f"{'=' * 100}")
            print(f"  ⏱️  Elapsed: {elapsed:.1f} minutes")
            print(f"  ⏱️  Estimated Remaining: {remaining:.1f} minutes ({remaining/60:.1f} hours)")
            print(f"  ✓ Success: {success_count}/{i}")

            temp_filename = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            pd.DataFrame(results).to_csv(temp_filename, index=False)
            print(f"  💾 Progress saved: {temp_filename}\n")

    print("\n" + "=" * 100)
    print("🌍 ANALYZING MACRO ENVIRONMENT (WITH RETRIES)")
    print("=" * 100)

    macro_summary = None
    macro_attempt = 0
    macro_wait = 30

    while macro_summary is None:
        macro_attempt += 1
        try:
            print(f"Macro analysis attempt #{macro_attempt}...")
            macro_data = get_macro_data()
            macro_summary = engine.analyze_macro(macro_data, verbose=False)

            if macro_summary:
                print("✓ Macro analysis successful!\n")
                print("-" * 100)
                print(macro_summary)
                print("-" * 100)
            else:
                print(f"⚠️  Macro analysis returned None, retrying in {macro_wait}s...")
                time.sleep(macro_wait)
                macro_wait = min(macro_wait * 1.5, 300)
        except Exception as e:
            print(f"⚠️  Macro analysis error: {str(e)[:100]}")
            print(f"⚠️  Retrying in {macro_wait}s...")
            time.sleep(macro_wait)
            macro_wait = min(macro_wait * 1.5, 300)

    print("\n" + "=" * 100)
    print("💾 SAVING FINAL RESULTS")
    print("=" * 100)

    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"overnight_analysis_{timestamp}.csv"
    df.to_csv(output_filename, index=False)

    end_time = datetime.now()
    duration = end_time - start_time

    print(f"\n✓ Results saved to: {output_filename}")

    print(f"\n📊 Score Statistics:")
    print(f"  Fundamental - Mean: {df['Fundamental_Score'].mean():.1f}, "
          f"Min: {df['Fundamental_Score'].min()}, "
          f"Max: {df['Fundamental_Score'].max()}")
    print(f"  Technical   - Mean: {df['Technical_Score'].mean():.1f}, "
          f"Min: {df['Technical_Score'].min()}, "
          f"Max: {df['Technical_Score'].max()}")
    print(f"  Sentiment   - Mean: {df['Sentiment_Score'].mean():.1f}, "
          f"Min: {df['Sentiment_Score'].min()}, "
          f"Max: {df['Sentiment_Score'].max()}")

    if 'Attempts' in df.columns:
        print(f"\n📊 Retry Statistics:")
        print(f"  Total Retries: {df['Attempts'].sum() - len(df)}")
        print(f"  Average Attempts per Stock: {df['Attempts'].mean():.1f}")
        print(f"  Max Attempts for One Stock: {df['Attempts'].max()}")

    if macro_summary:
        macro_filename = f"macro_analysis_{timestamp}.txt"
        with open(macro_filename, 'w') as f:
            f.write(f"Macro Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 100 + "\n\n")
            f.write(macro_summary)
        print(f"✓ Macro analysis saved to: {macro_filename}")

    print("\n" + "=" * 100)
    print("📈 FINAL SUMMARY")
    print("=" * 100)
    print(f"\n🕐 Start Time:     {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🕐 End Time:       {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  Total Duration: {duration.total_seconds() / 60:.1f} minutes ({duration.total_seconds() / 3600:.2f} hours)")
    print(f"\n📊 Results:")
    print(f"  • Total Stocks Analyzed: {success_count}/{total_tickers} (100%)")
    print(f"  • All stocks successfully completed!")

    print(f"\n📁 Output Files:")
    print(f"  • Stock Analysis: {output_filename}")
    if macro_summary:
        print(f"  • Macro Analysis: {macro_filename}")

    print("\n✅ OVERNIGHT ANALYSIS COMPLETE - ALL STOCKS ANALYZED!")
    print("=" * 100)


if __name__ == '__main__':
    run_overnight_analysis()
