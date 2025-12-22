# Simple Agents Framework - Quick Start Guide

## Overview

The Simple Agents framework is a clean, modular system for creating AI agents that debate and collaborate. Perfect for stock selection, analysis, or any multi-perspective decision-making.

## Why Use This Instead of TradingAgents?

| Feature | Simple Agents | TradingAgents |
|---------|--------------|---------------|
| **Complexity** | Minimal | Complex |
| **Dependencies** | 2 (requests, dotenv) | 20+ libraries |
| **Setup Time** | 1 minute | 10+ minutes |
| **Modularity** | Very easy to extend | Requires understanding LangGraph |
| **Learning Curve** | Low | High |
| **Use Case** | Custom agent debates | Pre-built trading analysis |

## Quick Example

```python
from simple_agents import StockSelectorAgent, ModeratorAgent, AgentOrchestrator

# Create 3 agents
fundamental = StockSelectorAgent(
    name="Fundamental Analyst",
    role="Fundamental Expert",
    selection_criteria="Focus on strong balance sheets"
)

technical = StockSelectorAgent(
    name="Technical Analyst",
    role="Technical Expert",
    selection_criteria="Focus on momentum and breakouts"
)

news = StockSelectorAgent(
    name="News Analyst",
    role="Catalyst Expert",
    selection_criteria="Focus on positive news catalysts"
)

# Create moderator
moderator = ModeratorAgent()

# Orchestrate
orch = AgentOrchestrator()
orch.add_agent(fundamental)
orch.add_agent(technical)
orch.add_agent(news)
orch.set_moderator(moderator)

# Run
results = orch.run_full_analysis(num_debate_rounds=2)
orch.print_summary()
```

## What Happens

```
Phase 1: Stock Selection
├─ Fundamental Analyst → [AAPL, MSFT, JNJ, PG, KO]
├─ Technical Analyst → [NVDA, TSLA, AMD, GOOGL, META]
└─ News Analyst → [AAPL, NVDA, MSFT, AMZN, TSLA]

Phase 2: Debate (2 rounds)
├─ Round 1
│  ├─ Fundamental: "AAPL has strongest fundamentals..."
│  ├─ Technical: "NVDA shows breakout pattern..."
│  └─ News: "NVDA has positive AI catalysts..."
└─ Round 2
   ├─ Fundamental: "Counter NVDA overvaluation..."
   ├─ Technical: "Support NVDA momentum..."
   └─ News: "Add AMZN for AWS growth..."

Phase 3: Final Decision
└─ Moderator → [AAPL, NVDA, MSFT, TSLA, GOOGL]
   Reasoning: "Consensus on tech leaders with balance of
   fundamentals and momentum..."
```

## Adding New Agents

### Method 1: Use StockSelectorAgent (Easiest)

```python
risk_analyst = StockSelectorAgent(
    name="Risk Analyst",
    role="Risk Management Expert",
    selection_criteria="""
    Select 5 low-risk stocks:
    - Low volatility
    - Strong dividends
    - Defensive sectors
    - Stable earnings
    """
)

orch.add_agent(risk_analyst)
```

### Method 2: Custom Agent Class

```python
from simple_agents import Agent

class SentimentAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Sentiment Analyst",
            role="Social Media Sentiment Expert"
        )

    def analyze(self, context):
        prompt = """Analyze social media sentiment.
        Select 5 stocks with most positive buzz."""

        response = self.generate_response(prompt)

        # Parse and return
        return {
            "agent": self.name,
            "selected_stocks": [...],
            "full_response": response
        }

sentiment = SentimentAgent()
orch.add_agent(sentiment)
```

## Real-World Examples

### Example 1: Sector Rotation

```python
sector_analyst = StockSelectorAgent(
    name="Sector Rotation Specialist",
    role="Macro Sector Expert",
    selection_criteria="""
    Identify the hottest sector for tomorrow:
    - Economic indicators
    - Sector relative strength
    - Rotation patterns

    Select 5 stocks from that sector.
    """
)
```

### Example 2: Contrarian Investor

```python
class ContrarianAgent(Agent):
    def analyze(self, context):
        # Get what others selected
        others = context.get('all_selections', [])
        popular = [s['ticker'] for sel in others
                   for s in sel['selected_stocks']]

        prompt = f"""Others picked: {popular}
        Select 5 stocks they're ignoring but have potential."""

        return {"agent": self.name, ...}
```

### Example 3: Multi-Timeframe

```python
day_trader = StockSelectorAgent(
    name="Day Trader",
    role="Intraday Expert",
    selection_criteria="High volume, volatile stocks for day trading"
)

swing_trader = StockSelectorAgent(
    name="Swing Trader",
    role="Multi-Day Expert",
    selection_criteria="Stocks setting up for 3-5 day moves"
)

position_trader = StockSelectorAgent(
    name="Position Trader",
    role="Long-term Expert",
    selection_criteria="Stocks for multi-week positions"
)
```

## Configuration

### Change Model

```python
agent = StockSelectorAgent(...)
agent.model_name = "gemini-1.5-pro"  # Smarter model
```

### Adjust Debate Rounds

```python
# Quick (1 round)
orch.run_full_analysis(num_debate_rounds=1)

# Standard (2 rounds)
orch.run_full_analysis(num_debate_rounds=2)

# Deep (5 rounds)
orch.run_full_analysis(num_debate_rounds=5)
```

### Export Results

```python
orch.export_results("my_analysis.json")
```

## Advanced: Custom Workflow

```python
# Manual control over phases
orch.run_selection_phase()
orch.run_debate_phase(num_rounds=3)
orch.run_final_decision()

# Access intermediate results
selections = orch.results['selections']
debate = orch.results['debate']
decision = orch.results['final_decision']
```

## Best Practices

1. **Specific Criteria**: Give agents clear, measurable criteria
2. **Diverse Perspectives**: Include agents with different viewpoints
3. **Appropriate Rounds**: Balance depth vs. API cost
   - 1 round: Quick consensus
   - 2 rounds: Standard debate
   - 3+ rounds: Deep analysis
4. **Model Selection**:
   - `gemini-2.0-flash-exp`: Fast, free (agents)
   - `gemini-1.5-pro`: Smart, paid (moderator)

## API Cost

With 3 agents, 2 debate rounds, 1 moderator:
- Selections: 3 API calls
- Debate: 6 API calls (3 agents × 2 rounds)
- Decision: 1 API call

**Total: ~10 API calls** = ~$0.001 with flash models

## Troubleshooting

### Missing API Key

```bash
cp .env.example .env
# Edit .env and add:
GOOGLE_API_KEY=your_actual_key_here
```

### Import Errors

```bash
pip install requests python-dotenv
```

### JSON Parse Errors

Gemini sometimes doesn't return valid JSON. The framework handles this gracefully and shows the raw response.

## Next Steps

1. **Run the example**: `python examples/stock_selection_debate.py`
2. **Modify criteria**: Edit agent selection criteria
3. **Add agents**: Create your own agent types
4. **Export results**: Save to JSON for later analysis

See `simple_agents/README.md` for full API documentation.
