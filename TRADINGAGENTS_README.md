# TradingAgents Framework - Agent Communication Flow

## Overview

The TradingAgents framework is a multi-agent system that analyzes stocks using AI-powered agents working in a coordinated workflow. Each agent specializes in a specific aspect of stock analysis, and they communicate through a structured graph-based architecture powered by LangGraph.

## Architecture

### LLM Configuration

The framework now uses **Google Gemini** as its primary LLM provider:

- **Quick Thinking LLM**: `gemini-2.0-flash-exp` - Used for rapid analysis tasks
- **Deep Thinking LLM**: `gemini-1.5-pro` - Used for complex reasoning and final decisions

Configuration is managed in `src/tradingagents/default_config.py`.

### API Keys Required

Set these in your `.env` file:

```bash
# Required for TradingAgents LLM
GOOGLE_API_KEY=your_google_api_key_here

# Optional for additional data sources
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
```

## Agent Communication Workflow

The agents communicate in a **sequential pipeline with debate mechanisms**, orchestrated by LangGraph. Here's the complete flow:

### Phase 1: Data Collection (Analysts)

Analysts run in sequence based on configuration. Default order:

```
START → Market Analyst → Social Media Analyst → News Analyst → Fundamentals Analyst
```

Each analyst:
1. **Receives** the current state containing ticker symbol and previous analysis
2. **Uses tools** to fetch relevant data (stock prices, indicators, news, fundamentals)
3. **Analyzes** the data using Gemini (quick thinking model)
4. **Outputs** structured findings added to the shared state
5. **Passes control** to the next analyst

**Tool Usage Pattern:**
- Analyst invokes tools → Tools execute → Results returned to analyst → Analyst continues or moves to next agent
- Each analyst has access to specific tools:
  - **Market Analyst**: `get_stock_data`, `get_indicators`
  - **Social Media Analyst**: Social sentiment tools
  - **News Analyst**: `get_news`, `get_global_news`
  - **Fundamentals Analyst**: `get_fundamentals`, `get_balance_sheet`, `get_cashflow`, `get_income_statement`

### Phase 2: Research & Debate (Bull vs Bear)

After all analysts complete, the research phase begins with **debate rounds**:

```
Bull Researcher ⇄ Bear Researcher
```

**Debate Process:**
1. **Bull Researcher** analyzes all analyst findings and builds a bullish case
2. **Bear Researcher** receives bull's arguments and builds a bearish counter-case
3. They **debate back and forth** (configurable rounds, default: 1)
4. Each uses the **quick thinking LLM** and has access to **memory** to track positions

**Communication:**
- Bull and Bear read each other's arguments from shared state
- Each maintains separate memory to build stronger positions over rounds
- Conditional logic determines when to stop debating and move to manager

### Phase 3: Investment Decision (Research Manager)

```
Research Manager (Deep Thinking LLM)
```

The Research Manager:
1. **Reviews** all analyst reports
2. **Considers** both bull and bear arguments
3. **Makes final investment recommendation** using deep thinking LLM (gemini-1.5-pro)
4. **Outputs** decision to shared state
5. Uses **memory** to maintain consistency across analysis sessions

### Phase 4: Trade Execution Planning (Trader)

```
Trader Agent
```

The Trader:
1. **Takes** the investment recommendation
2. **Formulates** specific trade parameters (entry/exit, position size, timeframe)
3. **Outputs** executable trading plan
4. Uses **memory** to track trading decisions

### Phase 5: Risk Analysis & Debate (Risk Management)

Final phase involves **three risk perspectives** debating:

```
Risky Analyst → Safe Analyst → Neutral Analyst → (cycle or finish)
```

**Risk Debate Process:**
1. **Risky Analyst** argues for aggressive position sizing
2. **Safe Analyst** counters with conservative risk management
3. **Neutral Analyst** provides balanced perspective
4. They **debate in rounds** (default: 1)
5. Each uses **quick thinking LLM**

### Phase 6: Final Risk Decision (Risk Manager)

```
Risk Manager (Deep Thinking LLM) → END
```

The Risk Manager:
1. **Reviews** all risk debate arguments
2. **Makes final risk assessment** using deep thinking LLM
3. **Outputs** final risk-adjusted recommendation
4. **END** - Workflow complete

## State Management

All agents share a common `AgentState` that flows through the graph:

```python
AgentState = {
    "ticker": str,              # Stock ticker being analyzed
    "messages": List[Message],   # All agent communications
    "analyst_reports": dict,     # Reports from each analyst
    "bull_arguments": List,      # Bull researcher positions
    "bear_arguments": List,      # Bear researcher positions
    "investment_decision": str,  # Research manager decision
    "trade_plan": dict,          # Trader's execution plan
    "risk_arguments": dict,      # Risk debate arguments
    "final_recommendation": str  # Final output
}
```

## Memory System

Certain agents have **persistent memory** across sessions:

- **Bull Memory**: Tracks bull researcher's historical positions
- **Bear Memory**: Tracks bear researcher's historical positions
- **Trader Memory**: Remembers past trading decisions
- **Investment Judge Memory**: Research manager's decision history
- **Risk Manager Memory**: Risk assessment history

Memory is implemented via `FinancialSituationMemory` class and stored in the results directory.

## Data Source Routing

The framework supports **multiple data vendors** with automatic fallback:

### Configurable Data Sources

In `default_config.py`, you can configure:

```python
"data_vendors": {
    "core_stock_apis": "yfinance",       # OHLCV data
    "technical_indicators": "yfinance",  # Technical analysis
    "fundamental_data": "alpha_vantage", # Company fundamentals
    "news_data": "alpha_vantage",        # News feeds
}
```

### Supported Vendors

- **yfinance**: Free, no API key required
- **alpha_vantage**: Free tier available, API key required
- **google**: Google News search
- **local**: Cached/local data sources
- **openai**: Can be used for fundamental analysis (requires OpenAI key)

### Fallback System

If a vendor fails (rate limits, errors), the system automatically falls back to alternative vendors:

```
Primary Vendor → Fallback Vendor 1 → Fallback Vendor 2 → Error
```

## Conditional Logic

The workflow uses **conditional edges** to determine agent transitions:

1. **Tool Continuation**: Analysts check if they need more tool calls
2. **Debate Continuation**: Bull/Bear and Risk debates check round limits
3. **Error Handling**: Failures trigger fallbacks or retries

Implemented in `src/tradingagents/graph/conditional_logic.py`.

## Signal Processing

The framework includes signal processing for final output:

- Extracts actionable trading signals from final recommendation
- Formats signals for downstream systems
- Handles buy/sell/hold decisions with confidence scores

## Running the Framework

### Basic Usage

```python
from src.tradingagents.graph.trading_graph import TradingAgentsGraph

# Initialize with default config
graph = TradingAgentsGraph(
    selected_analysts=["market", "social", "news", "fundamentals"],
    debug=True
)

# Run analysis for a ticker
result = graph.run(ticker="AAPL")

# Access final recommendation
print(result["final_recommendation"])
```

### Custom Configuration

```python
from src.tradingagents.default_config import DEFAULT_CONFIG

# Modify config
custom_config = DEFAULT_CONFIG.copy()
custom_config["max_debate_rounds"] = 3
custom_config["data_vendors"]["news_data"] = "google"

# Initialize with custom config
graph = TradingAgentsGraph(
    selected_analysts=["market", "fundamentals"],  # Only use 2 analysts
    config=custom_config,
    debug=False
)
```

## Project Structure

```
src/tradingagents/
├── agents/
│   ├── analysts/           # Market, News, Social, Fundamentals analysts
│   ├── managers/           # Research and Risk managers
│   ├── researchers/        # Bull and Bear researchers
│   ├── risk_mgmt/          # Risky, Safe, Neutral debators
│   ├── trader/             # Trade execution planning
│   └── utils/
│       ├── agent_states.py # State definitions
│       ├── agent_utils.py  # Tool definitions
│       ├── memory.py       # Memory system
│       └── *_tools.py      # Tool implementations
├── dataflows/
│   ├── interface.py        # Vendor routing system
│   ├── y_finance.py        # yfinance integration
│   ├── alpha_vantage*.py   # Alpha Vantage integrations
│   ├── google.py           # Google News integration
│   └── config.py           # Config management
├── graph/
│   ├── trading_graph.py    # Main orchestrator
│   ├── setup.py            # Graph construction
│   ├── conditional_logic.py# Decision logic
│   ├── propagation.py      # State propagation
│   ├── reflection.py       # Agent reflection
│   └── signal_processing.py# Signal extraction
└── default_config.py       # Default configuration
```

## Key Features

1. **Multi-Agent Collaboration**: Specialized agents work together
2. **Debate Mechanisms**: Bull vs Bear, Risky vs Safe discussions
3. **Memory Persistence**: Agents learn from past decisions
4. **Tool Abstraction**: Unified interface for multiple data sources
5. **Automatic Fallbacks**: Resilient data fetching
6. **LangGraph Orchestration**: Reliable workflow management
7. **Gemini Integration**: Powered by Google's latest AI models

## Debug Mode

Enable debug mode to see detailed agent communication:

```python
graph = TradingAgentsGraph(debug=True)
```

This will print:
- Agent transitions
- Tool calls and results
- Debate rounds
- State updates
- Vendor fallback sequences

## Extending the Framework

### Add Custom Analyst

1. Create analyst in `src/tradingagents/agents/analysts/`
2. Define tools in `src/tradingagents/agents/utils/agent_utils.py`
3. Update `setup.py` to include in graph
4. Add to `selected_analysts` parameter

### Add Custom Data Vendor

1. Implement vendor in `src/tradingagents/dataflows/`
2. Add to `VENDOR_METHODS` in `interface.py`
3. Update `data_vendors` config
4. Tools will automatically use new vendor

## Performance Considerations

- **Quick thinking LLM** (gemini-2.0-flash-exp): Fast responses, lower cost
- **Deep thinking LLM** (gemini-1.5-pro): Complex reasoning, higher quality
- **Debate rounds**: More rounds = deeper analysis but slower execution
- **Tool caching**: Data is cached to avoid redundant API calls
- **Vendor fallbacks**: May increase latency if primary vendor fails

## Example Output Structure

```python
{
    "ticker": "AAPL",
    "analyst_reports": {
        "market": "Technical indicators show...",
        "fundamentals": "Revenue growth of...",
        "news": "Recent announcements...",
        "social": "Sentiment analysis shows..."
    },
    "debate_summary": {
        "bull_case": "Strong growth potential because...",
        "bear_case": "Risks include..."
    },
    "investment_decision": "BUY - High confidence",
    "trade_plan": {
        "action": "BUY",
        "entry": 175.50,
        "target": 190.00,
        "stop_loss": 170.00,
        "position_size": "5% of portfolio"
    },
    "risk_assessment": {
        "risk_level": "MODERATE",
        "suggested_position": "3-5% allocation"
    },
    "final_recommendation": "BUY AAPL - Moderate Risk, 5% allocation..."
}
```

## Troubleshooting

### Common Issues

1. **GOOGLE_API_KEY not found**: Ensure `.env` file is in project root with correct key
2. **Alpha Vantage rate limit**: Free tier has 25 calls/day - use yfinance fallback
3. **Import errors**: Run `pip install -r requirements.txt`
4. **Memory errors**: Check that results directory exists and is writable

### Getting Help

- Check configuration in `src/tradingagents/default_config.py`
- Enable debug mode to see detailed logs
- Review agent state at each step
- Verify API keys are correctly set

## License

This framework integrates the TradingAgents library into GeminiTrader for stock analysis using Google Gemini AI.
