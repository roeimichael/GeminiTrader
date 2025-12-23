# GeminiTrader

Multi-agent stock analysis system powered by Google Gemini AI.

## Overview

GeminiTrader is an intelligent trading analysis framework that uses multiple AI agents to analyze stocks from different perspectives. Each agent specializes in a specific aspect and they collaborate to reach investment decisions.

## Features

- Multi-agent analysis with specialized roles
- Bull vs Bear debate mechanism
- Risk assessment from multiple perspectives
- Powered by Google Gemini
- Multiple data sources with automatic fallback
- Configurable debate rounds
- Memory system for learning

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add GOOGLE_API_KEY=your_key
```

```python
from src.tradingagents.graph.trading_graph import TradingAgentsGraph
from datetime import datetime

graph = TradingAgentsGraph(selected_analysts=["market", "fundamentals"])
result = graph.run(ticker="AAPL", trade_date=datetime.now().strftime("%Y-%m-%d"))
print(result["final_recommendation"])
```

See `examples/` for more usage patterns and `AGENT_POOL_GUIDE.md` for modular agent management.

## TradingAgents Framework

Comprehensive multi-agent trading analysis system with specialized agents for different aspects of financial analysis. Features modular agent selection, debate mechanisms, and collaborative decision-making.

See **COMPLETE_GUIDE.md** for full documentation and **AGENT_POOL_GUIDE.md** for agent pool management.

## Documentation

- **AGENT_POOL_GUIDE.md** - Agent pool management and modular initialization
- **COMPLETE_GUIDE.md** - Full TradingAgents system documentation
- **TRADINGAGENTS_README.md** - Technical architecture details
