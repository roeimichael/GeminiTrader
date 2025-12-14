import os
import time
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
from src.config.settings import Settings
from src.data.data_fetcher import get_stock_data, get_macro_data
from src.gemini_api.analysis_engine import GeminiAnalysisEngine
from src.utils.api_key_manager import APIKeyManager


def wait_for_rate_limit_reset(retry_delay):
    print(f"\n⏸️  Rate limit hit. Waiting {retry_delay} seconds before retry...")
    time.sleep(retry_delay)


def analyze_stock_with_retry(engine, ticker, max_retries=5):
    retries = 0
    base_delay = 20

    while retries < max_retries:
        try:
            stock_data = get_stock_data(ticker)
            scores = engine.analyze_stock(ticker, stock_data, verbose=False)

            if all(score is not None for score in scores.values()):
                return {
                    'Ticker': ticker,
                    'Fundamental_Score': scores['fundamental_score'],
                    'Technical_Score': scores['technical_score'],
                    'Sentiment_Score': scores['sentiment_score'],
                    'Status': 'Success'
                }
            else:
                print(f"  ⚠️  {ticker}: Some scores missing, retrying...")
                retries += 1

        except Exception as e:
            error_msg = str(e)

            if '429' in error_msg or 'quota' in error_msg.lower():
                retry_delay = base_delay * (2 ** retries)
                print(f"  ⚠️  {ticker}: Rate limit hit (attempt {retries + 1}/{max_retries})")
                wait_for_rate_limit_reset(retry_delay)
                retries += 1
            else:
                print(f"  ❌ {ticker}: Error - {error_msg}")
                return {
                    'Ticker': ticker,
                    'Fundamental_Score': None,
                    'Technical_Score': None,
                    'Sentiment_Score': None,
                    'Status': f'Error: {error_msg[:50]}'
                }

    return {
        'Ticker': ticker,
        'Fundamental_Score': None,
        'Technical_Score': None,
        'Sentiment_Score': None,
        'Status': 'Failed after retries'
    }


def run_overnight_analysis():
    print("=" * 100)
    print("🌙 OVERNIGHT STOCK ANALYSIS - GEMINI AI")
    print("=" * 100)

    start_time = datetime.now()
    print(f"\n🕐 Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    load_dotenv()

    # Initialize API Key Manager
    try:
        api_key_manager = APIKeyManager()
    except ValueError as e:
        print(f"\n❌ ERROR: {e}")
        return

    print(f"✓ Model: {Settings.GEMINI_MODEL}")
    print(f"✓ Using {api_key_manager.get_key_count()} API key(s)")

    tickers = Settings.DEFAULT_TICKERS[:100]
    total_tickers = len(tickers)

    print(f"\n📊 Analysis Plan:")
    print(f"  • Total Stocks: {total_tickers}")
    print(f"  • API Calls: {total_tickers * 3} stock calls + 1 macro call = {total_tickers * 3 + 1} total")
    print(f"  • Rate Limit: 5 requests/minute (12 second delays)")
    print(f"  • Estimated Time: {(total_tickers * 3 * 12) // 60} minutes ({(total_tickers * 3 * 12) // 3600} hours)")
    print(f"  • Daily Limit: 1,500 requests (using {total_tickers * 3 + 1})")

    print("\n🤖 Initializing Gemini Analysis Engine...")
    # Adjust rate limit delay based on number of API keys
    # With multiple keys, we can be more aggressive since we rotate on rate limits
    rate_delay = 12 if api_key_manager.get_key_count() == 1 else 6
    print(f"✓ Rate limit delay: {rate_delay} seconds (optimized for {api_key_manager.get_key_count()} key(s))")

    engine = GeminiAnalysisEngine(api_key_manager, Settings.GEMINI_MODEL, rate_limit_delay=rate_delay)
    print("✓ Engine ready\n")

    results = []
    success_count = 0
    error_count = 0

    print("=" * 100)
    print("🔄 STARTING STOCK ANALYSIS")
    print("=" * 100)

    for i, ticker in enumerate(tickers, 1):
        progress = (i / total_tickers) * 100
        print(f"\n[{i}/{total_tickers}] ({progress:.1f}%) Analyzing {ticker}...")

        result = analyze_stock_with_retry(engine, ticker)
        results.append(result)

        if result['Status'] == 'Success':
            print(f"  ✓ {ticker}: F={result['Fundamental_Score']}, "
                  f"T={result['Technical_Score']}, S={result['Sentiment_Score']}")
            success_count += 1
        else:
            print(f"  ❌ {ticker}: {result['Status']}")
            error_count += 1

        if i % 10 == 0:
            elapsed = (datetime.now() - start_time).total_seconds()
            remaining_tickers = total_tickers - i
            avg_time_per_ticker = elapsed / i
            est_remaining = (remaining_tickers * avg_time_per_ticker) / 60

            print(f"\n📈 Progress Update:")
            print(f"  • Completed: {i}/{total_tickers} ({progress:.1f}%)")
            print(f"  • Success: {success_count} | Errors: {error_count}")
            print(f"  • Elapsed: {elapsed / 60:.1f} minutes")
            print(f"  • Estimated Remaining: {est_remaining:.1f} minutes")

            temp_df = pd.DataFrame(results)
            temp_filename = f"overnight_progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            temp_df.to_csv(temp_filename, index=False)
            print(f"  • Progress saved to: {temp_filename}")

    print("\n" + "=" * 100)
    print("🌍 MACRO ANALYSIS")
    print("=" * 100)

    macro_summary = None
    try:
        macro_data = get_macro_data()
        print("Analyzing macro environment...")
        macro_summary = engine.analyze_macro(macro_data, verbose=False)

        if macro_summary:
            print("✓ Macro analysis complete\n")
            print("-" * 100)
            print(macro_summary)
            print("-" * 100)
        else:
            print("❌ Macro analysis failed")
    except Exception as e:
        print(f"❌ Macro analysis error: {e}")

    print("\n" + "=" * 100)
    print("💾 SAVING RESULTS")
    print("=" * 100)

    df = pd.DataFrame(results)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"overnight_analysis_{timestamp}.csv"
    df.to_csv(output_filename, index=False)

    end_time = datetime.now()
    duration = end_time - start_time

    print(f"\n✓ Results saved to: {output_filename}")

    successful_results = df[df['Status'] == 'Success']
    if len(successful_results) > 0:
        print(f"\n📊 Score Statistics (Successful Analyses):")
        print(f"  Fundamental - Mean: {successful_results['Fundamental_Score'].mean():.1f}, "
              f"Min: {successful_results['Fundamental_Score'].min()}, "
              f"Max: {successful_results['Fundamental_Score'].max()}")
        print(f"  Technical   - Mean: {successful_results['Technical_Score'].mean():.1f}, "
              f"Min: {successful_results['Technical_Score'].min()}, "
              f"Max: {successful_results['Technical_Score'].max()}")
        print(f"  Sentiment   - Mean: {successful_results['Sentiment_Score'].mean():.1f}, "
              f"Min: {successful_results['Sentiment_Score'].min()}, "
              f"Max: {successful_results['Sentiment_Score'].max()}")

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
    print(f"  • Total Stocks:     {total_tickers}")
    print(f"  • Successful:       {success_count} ({success_count / total_tickers * 100:.1f}%)")
    print(f"  • Errors:           {error_count} ({error_count / total_tickers * 100:.1f}%)")
    print(f"  • API Calls Made:   ~{success_count * 3 + error_count + 1}")

    print(f"\n📁 Output Files:")
    print(f"  • Stock Analysis: {output_filename}")
    if macro_summary:
        print(f"  • Macro Analysis: {macro_filename}")

    print("\n✅ OVERNIGHT ANALYSIS COMPLETE!")
    print("=" * 100)


if __name__ == '__main__':
    run_overnight_analysis()
