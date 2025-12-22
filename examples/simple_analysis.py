from tradingagents.graph.trading_graph import TradingAgentsGraph
from datetime import datetime

def main():
    print("Initializing Trading Agents...")

    graph = TradingAgentsGraph(
        selected_analysts=["market", "fundamentals"],
        debug=True
    )

    ticker = "AAPL"
    trade_date = datetime.now().strftime("%Y-%m-%d")

    print(f"\nAnalyzing {ticker}...")
    result = graph.run(ticker=ticker, trade_date=trade_date)

    print("\n" + "="*80)
    print("FINAL RECOMMENDATION:")
    print("="*80)
    print(result.get("final_recommendation", "No recommendation"))

    print("\n" + "="*80)
    print("TRADE PLAN:")
    print("="*80)
    print(result.get("trade_plan", "No trade plan"))

if __name__ == "__main__":
    main()
