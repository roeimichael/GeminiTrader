from tradingagents.graph.trading_graph import TradingAgentsGraph
from datetime import datetime
import json

def main():
    print("Initializing Trading Agents...")

    graph = TradingAgentsGraph(
        selected_analysts=["market", "fundamentals"],
        debug=False
    )

    stocks = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"]
    trade_date = datetime.now().strftime("%Y-%m-%d")
    results = {}

    for ticker in stocks:
        print(f"\nAnalyzing {ticker}...")
        try:
            result = graph.run(ticker=ticker, trade_date=trade_date)
            results[ticker] = {
                "recommendation": result.get("final_recommendation", "No recommendation"),
                "trade_plan": result.get("trade_plan", ""),
                "timestamp": datetime.now().isoformat()
            }
            print(f"{ticker}: Success")
        except Exception as e:
            print(f"{ticker}: Error - {e}")
            results[ticker] = {"error": str(e)}

    output_file = f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main()
