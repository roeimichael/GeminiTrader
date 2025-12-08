import os
from dotenv import load_dotenv
from src.config.settings import Settings
from src.data.data_fetcher import get_stock_data, get_macro_data
from src.gemini_api.analysis_engine import GeminiAnalysisEngine


def test_gemini_api():
    print("=" * 80)
    print("GEMINI API TEST SCRIPT")
    print("=" * 80)

    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in .env file")
        print("Please add your API key to the .env file:")
        print("GEMINI_API_KEY=your_actual_api_key_here")
        return

    print(f"\n✓ API Key loaded: {api_key[:10]}...{api_key[-4:]}")
    print(f"✓ Model: {Settings.GEMINI_MODEL}")

    print("\nInitializing Gemini Analysis Engine...")
    print("(Rate limiting: 12 second delay between API calls to avoid quota errors)")
    engine = GeminiAnalysisEngine(api_key, Settings.GEMINI_MODEL, rate_limit_delay=12)
    print("✓ Engine initialized successfully\n")

    test_tickers = Settings.DEFAULT_TICKERS[:3]
    print(f"Testing with first 3 tickers: {', '.join(test_tickers)}")
    print(f"Expected runtime: ~2 minutes (3 tickers × 3 calls × 12s delay = 108s + API time)\n")

    results = []

    for i, ticker in enumerate(test_tickers, 1):
        print("-" * 80)
        print(f"TEST {i}/3: Analyzing {ticker}")
        print("-" * 80)

        try:
            stock_data = get_stock_data(ticker)
            print(f"✓ Stock data retrieved for {ticker}")

            print(f"\n  Making 3 API calls (with 12s delays between each)...")
            scores = engine.analyze_stock(ticker, stock_data, verbose=True)

            if all(score is not None for score in scores.values()):
                results.append({
                    'ticker': ticker,
                    'fundamental': scores['fundamental_score'],
                    'technical': scores['technical_score'],
                    'sentiment': scores['sentiment_score']
                })
                print(f"  ✓ Fundamental Score: {scores['fundamental_score']}/100")
                print(f"  ✓ Technical Score:   {scores['technical_score']}/100")
                print(f"  ✓ Sentiment Score:   {scores['sentiment_score']}/100")
                print(f"\n  SUCCESS: {ticker} analyzed successfully!")
            else:
                print(f"  ✗ ERROR: Some scores missing for {ticker}")
                print(f"    Scores: {scores}")

        except Exception as e:
            print(f"  ✗ ERROR analyzing {ticker}: {e}")

        print()

    print("=" * 80)
    print("MACRO ANALYSIS TEST")
    print("=" * 80)

    try:
        print("Fetching macro data...")
        macro_data = get_macro_data()
        print("✓ Macro data retrieved")

        print("\nMaking API call: Macro Environment Analysis...")
        macro_summary = engine.analyze_macro(macro_data, verbose=True)

        if macro_summary:
            print("✓ Macro analysis successful\n")
            print("MACRO SUMMARY:")
            print("-" * 80)
            print(macro_summary)
            print("-" * 80)
        else:
            print("✗ ERROR: Macro analysis failed")

    except Exception as e:
        print(f"✗ ERROR in macro analysis: {e}")

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    if results:
        print(f"\nSuccessfully analyzed {len(results)}/{len(test_tickers)} tickers:\n")
        for result in results:
            print(f"  {result['ticker']:6} - Fundamental: {result['fundamental']:3}/100, "
                  f"Technical: {result['technical']:3}/100, "
                  f"Sentiment: {result['sentiment']:3}/100")

        print("\n✓ API TEST PASSED")
        print(f"\nTotal API calls made: {len(results) * 3 + 1}")
        print(f"  - Stock analysis: {len(results)} tickers × 3 calls = {len(results) * 3} calls")
        print(f"  - Macro analysis: 1 call")
    else:
        print("\n✗ API TEST FAILED - No successful analyses")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    test_gemini_api()
