# Simple Agents Framework

A modular, easy-to-extend agent framework for stock analysis and debate.

## Quick Start

```python
from simple_agents import StockSelectorAgent, ModeratorAgent, AgentOrchestrator

# Create agents
analyst1 = StockSelectorAgent(
    name="Fundamental Analyst",
    role="Fundamental Analysis Expert",
    selection_criteria="Focus on strong balance sheets and growing earnings"
)

analyst2 = StockSelectorAgent(
    name="Technical Analyst",
    role="Technical Analysis Expert",
    selection_criteria="Focus on technical momentum and chart patterns"
)

moderator = ModeratorAgent()

# Orchestrate
orchestrator = AgentOrchestrator()
orchestrator.add_agent(analyst1)
orchestrator.add_agent(analyst2)
orchestrator.set_moderator(moderator)

# Run analysis
results = orchestrator.run_full_analysis(num_debate_rounds=2)
orchestrator.print_summary()
```

## Adding New Agents

### Option 1: Use Existing StockSelectorAgent

```python
risk_analyst = StockSelectorAgent(
    name="Risk Analyst",
    role="Risk Management Expert",
    selection_criteria="""
    Focus on:
    - Low volatility stocks
    - Strong dividend yields
    - Defensive sectors
    - Stable earnings
    """
)

orchestrator.add_agent(risk_analyst)
```

### Option 2: Create Custom Agent Class

```python
from simple_agents import Agent

class SentimentAgent(Agent):
    def __init__(self, name: str):
        super().__init__(name, "Sentiment Analysis Expert")

    def analyze(self, context):
        prompt = f"""Analyze social media sentiment and select 5 stocks
        with the most positive sentiment for tomorrow."""

        response = self.generate_response(prompt)

        return {
            "agent": self.name,
            "analysis": response
        }

sentiment_agent = SentimentAgent("Sentiment Analyst")
orchestrator.add_agent(sentiment_agent)
```

## Architecture

### Base Classes

**Agent (Abstract)**
- Base class for all agents
- Handles Gemini API configuration
- Provides `generate_response()` method
- Requires `analyze()` implementation

**StockSelectorAgent**
- Selects 5 stocks based on criteria
- Returns structured JSON output
- Can participate in debates

**DebateAgent**
- Participates in multi-round debates
- Argues for specific stock selections
- Considers other agents' arguments

**ModeratorAgent**
- Makes final decision
- Synthesizes all arguments
- Returns consensus picks

### Orchestrator

**AgentOrchestrator**
- Manages agent lifecycle
- Runs multi-phase analysis:
  1. Selection Phase - Each agent picks stocks
  2. Debate Phase - Agents argue their cases
  3. Decision Phase - Moderator decides

## Workflow Example

```
1. Selection Phase
   Fundamental Analyst → [AAPL, MSFT, JNJ, PG, KO]
   Market Analyst → [NVDA, TSLA, AMD, GOOGL, META]
   News Analyst → [AAPL, NVDA, MSFT, AMZN, TSLA]

2. Debate Phase (2 rounds)
   Round 1:
     Fundamental: "AAPL has strong fundamentals..."
     Market: "NVDA shows breakout momentum..."
     News: "NVDA has positive AI news..."

   Round 2:
     Fundamental: "Counter NVDA - overvalued..."
     Market: "Support NVDA - technical strength..."
     News: "Add AMZN - AWS growth catalyst..."

3. Final Decision
   Moderator → [AAPL, NVDA, MSFT, TSLA, GOOGL]
   Reasoning: "Consensus on AAPL, NVDA, MSFT..."
```

## Extending with Custom Behavior

### Example: Contrarian Agent

```python
class ContrarianAgent(Agent):
    def __init__(self):
        super().__init__("Contrarian", "Contrarian Investor")

    def analyze(self, context):
        all_selections = context.get('all_selections', [])

        # Extract all tickers selected by others
        popular_picks = []
        for sel in all_selections:
            for stock in sel.get('selected_stocks', []):
                popular_picks.append(stock['ticker'])

        prompt = f"""You are a contrarian investor.
        Other analysts selected: {popular_picks}

        Select 5 stocks that others are ignoring but have potential.
        Avoid the popular picks."""

        response = self.generate_response(prompt)
        return {"agent": self.name, "argument": response}
```

### Example: Sector Rotation Agent

```python
class SectorRotationAgent(StockSelectorAgent):
    def __init__(self):
        super().__init__(
            name="Sector Rotation Analyst",
            role="Sector Rotation Expert",
            selection_criteria="""
            Identify the strongest sector for tomorrow based on:
            - Economic cycle position
            - Sector relative strength
            - Leading indicators

            Select 5 stocks from the strongest sector.
            """
        )
```

## Configuration

### Change Model

```python
agent = StockSelectorAgent(
    name="Analyst",
    role="Expert",
    selection_criteria="..."
)
agent.model_name = "gemini-1.5-pro"  # Use stronger model
agent._configure_model()
```

### Debate Rounds

```python
# Quick analysis (1 round)
orchestrator.run_full_analysis(num_debate_rounds=1)

# Deep analysis (5 rounds)
orchestrator.run_full_analysis(num_debate_rounds=5)
```

## Export Results

```python
orchestrator.export_results("my_analysis.json")
```

Results include:
- All agent selections
- Complete debate history
- Final decision with reasoning

## Tips

1. **Clear Criteria**: Give agents specific, measurable criteria
2. **Diverse Perspectives**: Add agents with different viewpoints
3. **Appropriate Rounds**: More rounds = deeper analysis but more API calls
4. **Model Selection**: Use flash for speed, pro for quality
5. **Modular Design**: Easy to add/remove agents without changing core code
