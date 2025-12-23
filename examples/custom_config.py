from src.tradingagents.graph.trading_graph import TradingAgentsGraph
from src.tradingagents.config import DEFAULT_CONFIG
from datetime import datetime

def main():
    config = DEFAULT_CONFIG.copy()
    config["max_debate_rounds"] = 3
    config["max_risk_discuss_rounds"] = 2
    config["data_vendors"]["fundamental_data"] = "yfinance"

    print("Initializing with custom config...")
    print(f"Debate rounds: {config['max_debate_rounds']}")
    print(f"Risk discussion rounds: {config['max_risk_discuss_rounds']}")

    graph = TradingAgentsGraph(
        selected_analysts=["market", "fundamentals"],
        config=config,
        debug=True
    )

    ticker = "NVDA"
    trade_date = datetime.now().strftime("%Y-%m-%d")

    print(f"\nAnalyzing {ticker} with extended debate...")
    result = graph.run(ticker=ticker, trade_date=trade_date)

    print("\n" + "="*80)
    print("BULL vs BEAR DEBATE:")
    print("="*80)
    print(result["investment_debate_state"]["history"])

    print("\n" + "="*80)
    print("FINAL RECOMMENDATION:")
    print("="*80)
    print(result.get("final_recommendation", "No recommendation"))

if __name__ == "__main__":
    main()
