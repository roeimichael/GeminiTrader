# Complete Guide: Understanding the Multi-Agent Trading System

## Table of Contents
1. [How Multi-Agent Systems Work with Gemini](#how-multi-agent-systems-work-with-gemini)
2. [Communication Mechanism (API Calls Explained)](#communication-mechanism)
3. [Complete File Structure Explained](#complete-file-structure)
4. [How to Use This System](#how-to-use-this-system)
5. [Practical Examples](#practical-examples)

---

## How Multi-Agent Systems Work with Gemini

### YES, You Can Build Different "Personas" with Gemini!

**Short Answer:** Absolutely! Each agent is just Gemini with a different system prompt. You create a "Technical Indicator Guy" and a "Financial Information Guy" by giving them different instructions.

### How It Works in This Project

Each agent is created like this:

```python
def create_market_analyst(llm):  # llm = Gemini
    system_message = """You are a trading assistant tasked with analyzing
    financial markets. Your role is to select the most relevant indicators..."""

    # Create a prompt template with this persona
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="messages")
    ])

    # Bind tools to the LLM
    chain = prompt | llm.bind_tools(tools)

    # When invoked, Gemini acts as this persona
    result = chain.invoke(state["messages"])
```

**What Happens:**
1. You call `create_market_analyst(gemini_model)` - this returns a function
2. That function sends a request to Gemini API with:
   - System prompt: "You are a trading assistant..."
   - Tools: `get_stock_data`, `get_indicators`
   - Conversation history from previous agents
3. Gemini responds AS the market analyst
4. Next agent gets called with updated conversation history

### Example Agents in This Project

| Agent | Persona/Role | System Prompt Summary | Tools Available |
|-------|--------------|----------------------|-----------------|
| **Market Analyst** | Technical indicator expert | "You are a trading assistant analyzing financial markets. Select the most relevant indicators..." | `get_stock_data`, `get_indicators` |
| **Fundamentals Analyst** | Financial statements expert | "You are a researcher analyzing fundamental information. Analyze financial documents, company profile..." | `get_fundamentals`, `get_balance_sheet`, `get_cashflow`, `get_income_statement` |
| **News Analyst** | News & current events expert | "Analyze recent news and world affairs affecting the company..." | `get_news`, `get_global_news` |
| **Social Media Analyst** | Sentiment analysis expert | "Analyze social media sentiment and public perception..." | Social sentiment tools |
| **Bull Researcher** | Optimistic investor | "You are a Bull Analyst advocating for investing. Build a strong case emphasizing growth potential..." | No tools - debates based on analyst reports |
| **Bear Researcher** | Pessimistic investor | "You are a Bear Analyst finding risks. Build a case emphasizing risks, weaknesses..." | No tools - debates based on analyst reports |
| **Research Manager** | Investment decision maker | "Review all analyst reports and debate. Make final investment recommendation..." | No tools - synthesizes everything |
| **Trader** | Trade execution planner | "Convert investment decision into specific trade parameters..." | No tools - creates trade plan |
| **Risk Analysts** (3x) | Risky, Safe, Neutral perspectives | Each has different risk appetite prompts | No tools - debate risk management |
| **Risk Manager** | Final risk assessor | "Review risk debate and make final risk-adjusted recommendation..." | No tools - final synthesis |

---

## Communication Mechanism

### YES, Each Reply is a Separate API Request!

Here's exactly how agents "talk" to each other:

```
1. START
   ↓
2. Market Analyst API Call:
   Request to Gemini API:
   - System: "You are a trading assistant..."
   - Messages: [] (empty, first call)
   - Tools: [get_stock_data, get_indicators]

   Response from Gemini:
   - Tool call: get_stock_data(ticker="AAPL")
   ↓
3. Tool Execution (Local, not an API call):
   - Fetch AAPL stock data from yfinance
   - Return CSV data
   ↓
4. Market Analyst API Call #2:
   Request to Gemini API:
   - System: "You are a trading assistant..."
   - Messages: [Previous response, Tool result: "CSV data..."]
   - Tools: [get_stock_data, get_indicators]

   Response from Gemini:
   - Tool call: get_indicators(ticker="AAPL", indicators=["rsi", "macd"])
   ↓
5. Tool Execution:
   - Calculate RSI and MACD from data
   - Return indicator values
   ↓
6. Market Analyst API Call #3:
   Request to Gemini API:
   - Messages: [All previous messages + indicator results]

   Response from Gemini:
   - Text report: "Based on RSI of 65 and MACD crossover..."
   - DONE (no more tool calls)
   ↓
7. Fundamentals Analyst API Call:
   Request to Gemini API:
   - System: "You are a researcher analyzing fundamentals..."
   - Messages: [Market Analyst's ENTIRE conversation + final report]
   - Tools: [get_fundamentals, get_balance_sheet, ...]

   Response from Gemini:
   - Tool call: get_fundamentals(ticker="AAPL")

   ... (continues with tool calls until done)
   ↓
8. News Analyst API Call:
   Request to Gemini API:
   - System: "You are a news analyst..."
   - Messages: [Market report + Fundamentals report + history]

   ... and so on
```

### API Call Counter Example

For analyzing 1 stock with all agents:

| Phase | Agent | Typical API Calls |
|-------|-------|-------------------|
| **Data Collection** | Market Analyst | 3-4 calls (1 initial + 2-3 tool rounds) |
| | Social Analyst | 2-3 calls |
| | News Analyst | 2-3 calls |
| | Fundamentals Analyst | 3-5 calls |
| **Debate** | Bull Researcher | 1 call per debate round (default: 1) |
| | Bear Researcher | 1 call per debate round (default: 1) |
| **Decision** | Research Manager | 1 call (deep thinking model) |
| **Trade Planning** | Trader | 1 call |
| **Risk Debate** | Risky Analyst | 1 call per round |
| | Safe Analyst | 1 call per round |
| | Neutral Analyst | 1 call per round |
| **Final Risk** | Risk Manager | 1 call (deep thinking model) |
| **TOTAL** | | **~20-25 API calls per stock** |

### Cost Estimate (Gemini Pricing)

With `gemini-2.0-flash-exp` (free during experimental period):
- **Cost: $0** (completely free!)

With `gemini-1.5-flash`:
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens
- Typical per-stock analysis: ~50k input tokens, ~10k output tokens
- **Cost per stock: ~$0.007** (less than 1 cent)

With `gemini-1.5-pro` for all agents:
- Input: $1.25 per 1M tokens
- Output: $5.00 per 1M tokens
- **Cost per stock: ~$0.11**

**Current Config (Hybrid):**
- Quick agents use `gemini-2.0-flash-exp` (free)
- Deep thinking (Research Manager, Risk Manager) use `gemini-1.5-pro`
- **Total cost per stock: ~$0.002** (almost free!)

---

## Complete File Structure

### Overview

```
GeminiTrader/
├── main.py                          # Simple GUI for basic stock analysis
├── src/
│   ├── config/                      # Basic settings
│   ├── gemini_api/                  # Simple analysis engine
│   │   ├── simple_engine.py         # Simple 3-prompt analysis
│   │   └── prompt_manager.py        # Loads prompts from prompts.json
│   └── tradingagents/               # MULTI-AGENT SYSTEM (the complex one)
│       ├── config.py                # Configuration for TradingAgents
│       ├── agents/                  # All agent definitions
│       │   ├── analysts/            # Data collection agents
│       │   ├── researchers/         # Bull & Bear debate agents
│       │   ├── managers/            # Decision-making agents
│       │   ├── risk_mgmt/           # Risk debate agents
│       │   ├── trader/              # Trade planning agent
│       │   └── utils/               # Agent utilities, tools, memory
│       ├── dataflows/               # Data fetching system
│       │   ├── interface.py         # Routes to different data sources
│       │   ├── y_finance.py         # Yahoo Finance integration
│       │   ├── alpha_vantage*.py    # Alpha Vantage integrations
│       │   └── google.py            # Google News integration
│       └── graph/                   # Workflow orchestration
│           ├── trading_graph.py     # Main orchestrator (YOU START HERE)
│           ├── setup.py             # Builds the agent graph
│           ├── conditional_logic.py # Decision logic between agents
│           └── signal_processing.py # Final signal extraction
├── cli/                             # Command-line interface tools
├── prompts.json                     # Prompts for simple analysis
├── requirements.txt                 # All dependencies
├── .env                             # Your API keys (YOU CREATE THIS)
└── TRADINGAGENTS_README.md         # Technical documentation
```

### File-by-File Explanation

#### Core Entry Points

**`main.py`** - Simple GUI Application
- What: Basic stock analysis with 3 prompts (fundamental, technical, sentiment)
- Uses: Single Gemini model for quick analysis
- When to use: Quick stock checks, testing API
- NOT the multi-agent system

**`tradingagents/graph/trading_graph.py`** - Multi-Agent System Entry
- What: **THIS IS THE MAIN FILE** for the multi-agent system
- Class: `TradingAgentsGraph`
- What it does:
  1. Initializes Gemini models (quick & deep thinking)
  2. Creates all agent nodes
  3. Builds the workflow graph
  4. Orchestrates the entire analysis
- **You interact with this file to run multi-agent analysis**

#### Configuration Files

**`tradingagents/config.py`**
```python
DEFAULT_CONFIG = {
    "llm_provider": "google",              # Use Gemini
    "deep_think_llm": "gemini-1.5-pro",   # Complex decisions
    "quick_think_llm": "gemini-2.0-flash-exp",  # Fast analysis
    "max_debate_rounds": 1,                # Bull vs Bear rounds
    "max_risk_discuss_rounds": 1,          # Risk debate rounds
    "data_vendors": {
        "core_stock_apis": "yfinance",     # Free stock data
        "fundamental_data": "alpha_vantage",  # Fundamentals
        "news_data": "alpha_vantage",      # News feeds
    }
}
```
- **Modify this to:**
  - Change debate rounds (more = deeper analysis, more API calls)
  - Switch data sources
  - Change model versions

**`.env`** (You create this)
```bash
GOOGLE_API_KEY=your_actual_key_here
ALPHA_VANTAGE_API_KEY=your_key_here  # Optional
```

#### Agent Definitions

**`tradingagents/agents/analysts/`**
- `market_analyst.py`: Technical indicators expert
- `fundamentals_analyst.py`: Financial statements expert
- `news_analyst.py`: News analysis expert
- `social_media_analyst.py`: Sentiment expert

Each file:
- Defines the agent's system prompt (persona)
- Lists available tools
- Returns a function that makes API calls to Gemini

**`tradingagents/agents/researchers/`**
- `bull_researcher.py`: Builds bullish investment case
- `bear_researcher.py`: Builds bearish counter-case

These agents:
- Don't use tools
- Read all analyst reports
- Debate with each other
- Use memory to improve arguments

**`tradingagents/agents/managers/`**
- `research_manager.py`: Makes final investment decision (BUY/HOLD/SELL)
- `risk_manager.py`: Makes final risk assessment

These use the **deep thinking model** (`gemini-1.5-pro`) for complex reasoning.

**`tradingagents/agents/risk_mgmt/`**
- `aggresive_debator.py`: Argues for aggressive position sizing
- `conservative_debator.py`: Argues for conservative risk management
- `neutral_debator.py`: Provides balanced perspective

**`tradingagents/agents/trader/`**
- `trader.py`: Converts investment decision into trade plan (entry, exit, stop-loss, position size)

#### Agent Utilities

**`tradingagents/agents/utils/agent_utils.py`**
- Defines all tool functions agents can use
- Tools like `get_stock_data()`, `get_fundamentals()`, etc.
- These are wrappers that route to actual data sources

**`tradingagents/agents/utils/agent_states.py`**
- Defines the shared state structure
- `AgentState`: The message history and data all agents share
- `InvestDebateState`: Bull vs Bear debate tracking
- `RiskDebateState`: Risk debate tracking

**`tradingagents/agents/utils/memory.py`**
- `FinancialSituationMemory`: Stores past analysis for learning
- Helps agents remember similar situations
- Stored in `results/` directory

**`tradingagents/agents/utils/*_tools.py`**
- `core_stock_tools.py`: Stock price and volume tools
- `technical_indicators_tools.py`: RSI, MACD, Bollinger Bands, etc.
- `fundamental_data_tools.py`: Balance sheet, income statement, etc.
- `news_data_tools.py`: News fetching tools

#### Data Fetching System

**`tradingagents/dataflows/interface.py`** - **KEY FILE**
- Routes tool calls to appropriate data vendor
- Implements fallback logic (if alpha_vantage fails, try yfinance)
- Example: `route_to_vendor("get_stock_data", ticker="AAPL")`

**`tradingagents/dataflows/y_finance.py`**
- Yahoo Finance integration (FREE, no API key)
- Provides: stock prices, indicators, fundamentals, insider transactions

**`tradingagents/dataflows/alpha_vantage*.py`**
- Alpha Vantage integration (free tier: 25 calls/day)
- Provides: fundamentals, news, insider data
- More comprehensive than yfinance

**`tradingagents/dataflows/google.py`**
- Google News search integration
- Provides: recent news articles

#### Workflow Orchestration

**`tradingagents/graph/setup.py`** - `GraphSetup` class
- Builds the LangGraph workflow
- Connects agents in sequence
- Adds conditional edges (when to continue debate, when to use tools, etc.)

**`tradingagents/graph/conditional_logic.py`** - `ConditionalLogic` class
- Decides: Should analyst call more tools or move to next agent?
- Decides: Should bull/bear continue debating or move to manager?
- Decides: Should risk debate continue or finish?

**`tradingagents/graph/propagation.py`** - `Propagator` class
- Handles state updates as it flows through agents
- Ensures all agents see previous agents' work

**`tradingagents/graph/signal_processing.py`** - `SignalProcessor` class
- Extracts actionable trading signals from final recommendation
- Parses BUY/SELL/HOLD decisions
- Formats for downstream systems

#### Simple Analysis System (Different from Multi-Agent)

**`src/gemini_api/simple_engine.py`**
- Simple 3-prompt analysis (fundamental, technical, sentiment)
- Makes 3 API calls total
- Used by `main.py` GUI
- NOT the multi-agent system

**`prompts.json`**
- Stores prompts for simple analysis
- Format: `{"fundamental": "You are an expert...", ...}`

---

## How to Use This System

### Step 1: Setup Environment

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
cp .env.example .env

# 3. Edit .env and add your API key
nano .env
# Add: GOOGLE_API_KEY=your_actual_key_here

# 4. (Optional) Add Alpha Vantage key for better fundamental data
# Add: ALPHA_VANTAGE_API_KEY=your_key_here
```

### Step 2: Choose Your Approach

#### Option A: Simple Analysis (Quick Testing)

```bash
# Run the GUI
python main.py

# Click "Test API" to verify your key works
# Click "Run Analysis" to analyze stocks
# Click "Export CSV" when done
```

**What happens:**
- Makes 3 API calls per stock (fundamental, technical, sentiment)
- Fast and cheap
- Good for: Quick checks, testing, simple analysis

#### Option B: Multi-Agent Analysis (Deep Analysis)

Create a script `run_trading_agents.py`:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph

# Initialize the multi-agent system
graph = TradingAgentsGraph(
    selected_analysts=["market", "news", "fundamentals"],  # Choose which analysts
    debug=True  # See all agent communication
)

# Run analysis on a stock
result = graph.run(
    ticker="AAPL",
    trade_date="2025-12-22"
)

# Print final recommendation
print("\n" + "="*80)
print("FINAL RECOMMENDATION:")
print("="*80)
print(result["final_recommendation"])

# Access individual reports
print("\n" + "="*80)
print("MARKET ANALYST REPORT:")
print("="*80)
print(result["market_report"])

print("\n" + "="*80)
print("BULL vs BEAR DEBATE:")
print("="*80)
print(result["investment_debate_state"]["history"])

print("\n" + "="*80)
print("TRADE PLAN:")
print("="*80)
print(result["trade_plan"])
```

Run it:
```bash
python run_trading_agents.py
```

**What happens:**
- Makes ~20-25 API calls
- Analysts gather data
- Bull & Bear debate
- Research Manager decides
- Trader plans execution
- Risk debate happens
- Risk Manager gives final recommendation

### Step 3: Customize Configuration

Edit `tradingagents/config.py`:

```python
# More debate rounds = deeper analysis
"max_debate_rounds": 3,  # Bull vs Bear debate 3 times
"max_risk_discuss_rounds": 2,  # Risk debate twice

# Change data sources
"data_vendors": {
    "core_stock_apis": "yfinance",  # Free
    "fundamental_data": "yfinance",  # Switch from alpha_vantage to avoid rate limits
    "news_data": "google",  # Use Google News instead
}

# Use different models
"deep_think_llm": "gemini-1.5-pro-latest",
"quick_think_llm": "gemini-1.5-flash-latest",
```

### Step 4: Select Which Analysts to Use

You can run only specific analysts:

```python
# Minimal: Only technical analysis
graph = TradingAgentsGraph(
    selected_analysts=["market"]
)

# Balanced: Technical + Fundamentals
graph = TradingAgentsGraph(
    selected_analysts=["market", "fundamentals"]
)

# Comprehensive: All analysts
graph = TradingAgentsGraph(
    selected_analysts=["market", "social", "news", "fundamentals"]
)
```

**Trade-off:**
- More analysts = Better analysis but more API calls and time
- Fewer analysts = Faster but less comprehensive

---

## Practical Examples

### Example 1: Quick Technical Analysis Only

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph

# Just market analyst (technical indicators)
graph = TradingAgentsGraph(
    selected_analysts=["market"],
    debug=False  # Less verbose
)

result = graph.run(ticker="TSLA", trade_date="2025-12-22")
print(result["market_report"])
```

**API calls:** ~3-4
**Time:** ~10 seconds
**Cost:** Free (using flash-exp)

### Example 2: Full Analysis with Custom Config

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.config import DEFAULT_CONFIG

# Create custom config
config = DEFAULT_CONFIG.copy()
config["max_debate_rounds"] = 3  # More debate
config["max_risk_discuss_rounds"] = 2
config["data_vendors"]["fundamental_data"] = "yfinance"  # Avoid rate limits

# Initialize with custom config
graph = TradingAgentsGraph(
    selected_analysts=["market", "fundamentals"],
    config=config,
    debug=True
)

# Analyze
result = graph.run(ticker="NVDA", trade_date="2025-12-22")

# Save to file
with open("nvda_analysis.txt", "w") as f:
    f.write(result["final_recommendation"])
```

**API calls:** ~15 (fewer analysts but more debate rounds)
**Time:** ~30 seconds
**Cost:** ~$0.002

### Example 3: Batch Analysis of Multiple Stocks

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
import json
from datetime import datetime

# Initialize once
graph = TradingAgentsGraph(
    selected_analysts=["market", "fundamentals"],
    debug=False
)

# Analyze multiple stocks
stocks = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"]
results = {}

for ticker in stocks:
    print(f"\nAnalyzing {ticker}...")
    result = graph.run(ticker=ticker, trade_date=datetime.now().strftime("%Y-%m-%d"))
    results[ticker] = {
        "recommendation": result["final_recommendation"],
        "trade_plan": result.get("trade_plan", ""),
        "timestamp": datetime.now().isoformat()
    }

# Save to JSON
with open("batch_analysis.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nAll analysis complete! Results saved to batch_analysis.json")
```

**API calls:** ~20 per stock × 5 stocks = ~100 total
**Time:** ~2-3 minutes
**Cost:** ~$0.01 total

### Example 4: Understanding the Output

```python
result = graph.run(ticker="AAPL", trade_date="2025-12-22")

# Available fields in result:
print(result.keys())
# dict_keys(['messages', 'market_report', 'sentiment_report', 'news_report',
#            'fundamentals_report', 'investment_debate_state', 'investment_decision',
#            'trade_plan', 'risk_debate_state', 'final_recommendation'])

# Individual analyst reports
market_analysis = result["market_report"]
# Example: "Based on technical indicators, AAPL shows RSI at 65 (slightly overbought)..."

fundamentals = result["fundamentals_report"]
# Example: "AAPL's P/E ratio of 28.5 is above sector average. Revenue growth of 8%..."

# Debate history
debate = result["investment_debate_state"]["history"]
# Example:
# Bull Analyst: AAPL shows strong momentum with revenue growth and new product launches...
# Bear Analyst: However, the P/E ratio is elevated and there are regulatory risks...
# Bull Analyst: Those concerns are overblown because the iPhone 15 sales are...

# Final decision
decision = result["investment_decision"]
# Example: "BUY - High confidence based on strong fundamentals and technical momentum"

# Trade plan
trade = result["trade_plan"]
# Example: {
#   "action": "BUY",
#   "entry_price": 175.50,
#   "target_price": 190.00,
#   "stop_loss": 170.00,
#   "position_size": "5% of portfolio",
#   "timeframe": "3-6 months"
# }

# Final recommendation (synthesizes everything)
final = result["final_recommendation"]
# Example: "BUY AAPL - Moderate Risk
# - Entry: $175.50
# - Target: $190 (8.3% upside)
# - Stop Loss: $170 (3.1% downside)
# - Position Size: 3-5% of portfolio
# - Risk/Reward: 2.7:1
# ..."
```

---

## Advanced: How the Communication Actually Works

### Visual Example: One Stock Through The System

```
User: graph.run(ticker="AAPL", trade_date="2025-12-22")
│
├─ Phase 1: Data Collection
│  │
│  ├─ Market Analyst
│  │  ├─ API Call #1 to Gemini:
│  │  │  Prompt: "You are a trading assistant. Analyze AAPL technical indicators."
│  │  │  Response: [Tool call: get_stock_data(ticker="AAPL")]
│  │  │
│  │  ├─ Local Tool Execution:
│  │  │  Fetch AAPL data from yfinance → Returns CSV
│  │  │
│  │  ├─ API Call #2 to Gemini:
│  │  │  Prompt: "Here's the stock data: [CSV]. What indicators should we analyze?"
│  │  │  Response: [Tool call: get_indicators(ticker="AAPL", indicators=["rsi","macd"])]
│  │  │
│  │  ├─ Local Tool Execution:
│  │  │  Calculate RSI and MACD → Returns values
│  │  │
│  │  └─ API Call #3 to Gemini:
│  │     Prompt: "Here are the indicators: RSI=65, MACD=crossover up. Analyze."
│  │     Response: "Based on RSI of 65, AAPL is in bullish territory..." [DONE]
│  │     DONE: Market report saved to state
│  │
│  ├─ Fundamentals Analyst
│  │  ├─ API Call #4 to Gemini:
│  │  │  Prompt: "You are a fundamentals analyst. Previous analyst said: [market report].
│  │  │           Now analyze AAPL fundamentals."
│  │  │  Response: [Tool call: get_fundamentals(ticker="AAPL")]
│  │  │
│  │  ├─ Local Tool Execution:
│  │  │  Fetch fundamentals from alpha_vantage → Returns financial data
│  │  │
│  │  └─ API Call #5 to Gemini:
│  │     Prompt: "Here's the fundamental data: [JSON]. Analyze."
│  │     Response: "AAPL shows P/E of 28.5, revenue growth of 8%..." [DONE]
│  │     DONE: Fundamentals report saved to state
│  │
│  └─ (News and Social analysts run similarly... skipped for brevity)
│
├─ Phase 2: Investment Debate
│  │
│  ├─ Bull Researcher
│  │  └─ API Call #10 to Gemini:
│  │     Prompt: "You are a Bull Analyst. Here are all the reports:
│  │              Market: [report]
│  │              Fundamentals: [report]
│  │              News: [report]
│  │              Build a bullish case for investing in AAPL."
│  │     Response: "AAPL presents strong growth opportunity because: 1) Technical
│  │               momentum is positive with RSI showing strength, 2) Revenue growth
│  │               of 8% exceeds sector average..." [DONE]
│  │     DONE: Bull argument saved to debate state
│  │
│  ├─ Bear Researcher
│  │  └─ API Call #11 to Gemini:
│  │     Prompt: "You are a Bear Analyst. Here are the reports:
│  │              [all reports]
│  │              Bull's argument: [bull argument]
│  │              Counter the bull's case and find risks."
│  │     Response: "While the bull makes valid points, significant risks exist:
│  │               1) P/E of 28.5 is 15% above sector average suggesting overvaluation,
│  │               2) Regulatory pressures in EU could impact margins..." [DONE]
│  │     DONE: Bear argument saved to debate state
│  │
│  └─ (Debate rounds continue if max_debate_rounds > 1)
│
├─ Phase 3: Investment Decision
│  │
│  └─ Research Manager (uses DEEP THINKING MODEL: gemini-1.5-pro)
│     └─ API Call #12 to Gemini:
│        Prompt: "You are the Research Manager. Review everything:
│                 Market analysis: [report]
│                 Fundamentals: [report]
│                 Bull argument: [argument]
│                 Bear argument: [counter-argument]
│                 Make final investment decision: BUY, HOLD, or SELL."
│        Response: "DECISION: BUY
│                   After reviewing all analyses and debate, the bull case is stronger.
│                   While P/E is elevated, the technical momentum and revenue growth
│                   support a BUY recommendation with target of $190..." [DONE]
│        DONE: Investment decision saved to state
│
├─ Phase 4: Trade Execution Planning
│  │
│  └─ Trader
│     └─ API Call #13 to Gemini:
│        Prompt: "You are a Trader. Investment decision is: [BUY with target $190]
│                 Create specific trade plan with entry, exit, stop-loss, position size."
│        Response: "TRADE PLAN:
│                   - Action: BUY
│                   - Entry: $175.50 (current price)
│                   - Target: $190.00 (8.3% upside)
│                   - Stop Loss: $170.00 (3.1% downside)
│                   - Risk/Reward: 2.7:1
│                   - Position Size: 5% of portfolio
│                   - Timeframe: 3-6 months" [DONE]
│        DONE: Trade plan saved to state
│
├─ Phase 5: Risk Debate
│  │
│  ├─ Risky Analyst
│  │  └─ API Call #14 to Gemini:
│  │     Prompt: "You are a risky analyst. Trade plan is: [5% position]
│  │              Argue for aggressive position sizing."
│  │     Response: "Given the strong bull case and 2.7:1 risk/reward, we should
│  │               increase position to 8-10% for maximum returns..." [DONE]
│  │
│  ├─ Safe Analyst
│  │  └─ API Call #15 to Gemini:
│  │     Prompt: "You are a conservative analyst. Risky analyst says: [10% position]
│  │              Counter with conservative risk management."
│  │     Response: "10% is too aggressive given P/E concerns. Market volatility
│  │               suggests 3-4% maximum to preserve capital..." [DONE]
│  │
│  └─ Neutral Analyst
│     └─ API Call #16 to Gemini:
│        Prompt: "Risky says: [10%], Safe says: [3%]. Provide balanced perspective."
│        Response: "A moderate 5-6% position balances opportunity with risk..." [DONE]
│
└─ Phase 6: Final Risk Assessment
   │
   └─ Risk Manager (uses DEEP THINKING MODEL: gemini-1.5-pro)
      └─ API Call #17 to Gemini:
         Prompt: "You are Risk Manager. Review:
                  Trade plan: [plan]
                  Risk debate: [risky: 10%, safe: 3%, neutral: 5%]
                  Make final risk-adjusted recommendation."
         Response: "FINAL RECOMMENDATION: BUY AAPL - MODERATE RISK

                    Executive Summary:
                    - Action: BUY
                    - Entry Price: $175.50
                    - Target Price: $190.00 (8.3% upside)
                    - Stop Loss: $170.00 (3.1% downside)
                    - Position Size: 5% of portfolio (balanced risk)
                    - Expected Timeframe: 3-6 months
                    - Risk/Reward Ratio: 2.7:1

                    Analysis Synopsis:
                    Technical indicators show bullish momentum (RSI: 65, MACD crossover).
                    Fundamentals demonstrate solid revenue growth (8% YoY) though P/E
                    of 28.5 suggests some premium pricing. Bull/bear debate revealed
                    both growth opportunities and valuation concerns, with bull case
                    marginally stronger. Risk assessment recommends moderate 5% position
                    to balance upside potential with valuation risk.

                    Risk Factors:
                    - Elevated P/E ratio (15% above sector)
                    - Regulatory pressures in EU
                    - General market volatility

                    Recommendation: PROCEED WITH BUY at recommended position size." [DONE]

         DONE: Final recommendation returned to user

Total API Calls: 17
Total Time: ~45 seconds
Total Cost: ~$0.003 (with hybrid free/pro model setup)
```

---

## Key Takeaways

### Question 1: Can I use Gemini instead of GPT?
**YES!** The system already supports Gemini. It's configured in `config.py` with `"llm_provider": "google"`.

### Question 2: Can I set up different "personas" with prompts?
**YES!** Each agent has its own system prompt that defines its role:
- Market Analyst: "You are a trading assistant analyzing technical indicators..."
- Fundamentals Analyst: "You are a researcher analyzing fundamental information..."
- Bull Researcher: "You are a Bull Analyst advocating for investing..."
- Etc.

You can modify these prompts in the respective agent files.

### Question 3: Is each reply a separate API request?
**YES!** Every time an agent "speaks," it's a new API call to Gemini:
- Market Analyst analyzing data: API call
- Market Analyst getting tool results: Another API call
- Market Analyst writing final report: Another API call
- Fundamentals Analyst starting: New API call
- Bull Researcher arguing: API call
- Bear Researcher countering: API call
- Etc.

**Typical analysis: 20-25 API calls per stock**

### Question 4: How do I use this?
1. **Simple way:** Use `main.py` GUI for quick 3-prompt analysis
2. **Advanced way:** Use `TradingAgentsGraph` class from `trading_graph.py` for full multi-agent analysis

### Question 5: What does each file do?
- **Agents:** Define personas and prompts (`agents/` folder)
- **Tools:** Fetch data from various sources (`dataflows/` folder)
- **Graph:** Orchestrate the workflow (`graph/` folder)
- **Config:** Customize behavior (`config.py`)
- **Entry:** Start here (`trading_graph.py`)

---

## Next Steps

1. **Test basic setup:**
   ```bash
   python main.py  # Run simple GUI
   ```

2. **Run first multi-agent analysis:**
   ```python
   from tradingagents.graph.trading_graph import TradingAgentsGraph
   graph = TradingAgentsGraph(selected_analysts=["market"], debug=True)
   result = graph.run(ticker="AAPL", trade_date="2025-12-22")
   print(result["final_recommendation"])
   ```

3. **Experiment with configuration:**
   - Add more analysts
   - Increase debate rounds
   - Switch data vendors
   - Try different models

4. **Build your own use case:**
   - Batch analyze your portfolio
   - Create a daily analysis cron job
   - Build a trading bot on top of this
   - Add custom analysts for your strategy

---

## Support

For technical details about agent architecture, see `TRADINGAGENTS_README.md`.

For questions about specific files or functions, the code is well-commented - check the actual source files in `tradingagents/`.

Happy trading!
