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
from tradingagents.graph.trading_graph import TradingAgentsGraph
from datetime import datetime

graph = TradingAgentsGraph(selected_analysts=["market", "fundamentals"])
result = graph.run(ticker="AAPL", trade_date=datetime.now().strftime("%Y-%m-%d"))
print(result["final_recommendation"])
```

See `examples/` for more usage patterns.

## Two Frameworks Available

### 1. Simple Agents (Recommended for Getting Started)
Clean, modular framework for custom agent debates. Perfect for stock selection and collaborative decision-making.

- Minimal dependencies (requests, dotenv)
- Easy to extend
- Fast setup
- Great for learning

```python
from simple_agents import StockSelectorAgent, AgentOrchestrator

analyst = StockSelectorAgent(name="Analyst", role="Expert",
                             selection_criteria="Focus on growth stocks")
orch = AgentOrchestrator().add_agent(analyst)
results = orch.run_full_analysis()
```

See **SIMPLE_AGENTS_GUIDE.md** for quick start.

### 2. TradingAgents (Advanced Multi-Agent System)
Comprehensive trading analysis with pre-built specialists.

See **COMPLETE_GUIDE.md** for details.

## Documentation

- **SIMPLE_AGENTS_GUIDE.md** - Quick start guide
- **COMPLETE_GUIDE.md** - Full TradingAgents system
- **TRADINGAGENTS_README.md** - Technical architecture
