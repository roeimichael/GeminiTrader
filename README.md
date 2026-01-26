# GeminiTrader

**A multi-agent AI stock analysis system that debates, reasons, and recommends trades — powered by Google Gemini.**

GeminiTrader isn't a single chatbot answering stock questions. It's an ensemble of specialized AI agents — analysts, researchers, debaters, traders, and risk managers — that collaborate through structured workflows to produce investment recommendations. Think of it as a virtual trading desk where every seat is filled by a purpose-built AI agent.

---

## What This Project Is

At its core, GeminiTrader takes a user's question about a stock (e.g., *"Should I invest in AAPL?"*) and runs it through a multi-phase analysis pipeline:

1. **Analysts** gather data — technical indicators, financial statements, news, social sentiment
2. **Researchers** debate — a bull makes the case for buying, a bear argues against it
3. **A manager judges** the debate and makes an initial investment decision
4. **A trader** turns that decision into a concrete execution plan (entry price, stop-loss, targets)
5. **Risk analysts** debate the risk profile — aggressive vs. conservative vs. balanced
6. **A risk manager** delivers the final verdict: **BUY**, **SELL**, or **HOLD**

The result is a structured, multi-perspective analysis rather than a single LLM's opinion.

---

## What's Included So Far

### Multi-Agent System (12 Specialized Agents)

| Phase | Agents | Role |
|-------|--------|------|
| **Analysis** | Market Analyst, Fundamentals Analyst, News Analyst, Social Media Analyst | Gather and interpret data from different domains |
| **Investment Debate** | Bull Researcher, Bear Researcher | Build opposing cases based on analyst reports |
| **Decision** | Research Manager | Judge the debate, produce an investment thesis |
| **Execution** | Trader | Create actionable trade plan with specific prices and sizing |
| **Risk Debate** | Aggressive, Conservative, Neutral Risk Analysts | Debate risk management approach |
| **Final Verdict** | Risk Manager | Final recommendation with risk-adjusted parameters |

### Intelligent Query Routing

Not every question needs all 12 agents. The system includes a two-stage query classifier:
- **Fast path**: keyword matching routes simple queries to relevant agents instantly
- **Complex path**: Gemini LLM analyzes the query and selects only the agents that are needed

This means asking *"What's AAPL's P/E ratio?"* won't spin up the news analyst or social sentiment agent.

### Pluggable Data Vendor System

The data layer abstracts away the source of financial data. You can swap providers without changing agent code:

| Data Category | Available Vendors |
|---------------|-------------------|
| Stock Prices & History | yfinance, Alpha Vantage, local fallback |
| Technical Indicators | yfinance, Alpha Vantage, local fallback |
| Fundamental Data | Alpha Vantage, OpenAI, local fallback |
| News & Events | yfinance, Google Gemini (with Search grounding), Alpha Vantage, local fallback |

Vendors are configured at the category level with optional per-tool overrides. If a primary vendor fails, the system automatically falls back to alternatives.

### Caching Layer

A disk-based cache with 24-hour TTL sits between agents and data vendors. This:
- Prevents redundant API calls during multi-agent runs
- Reduces costs during development and testing
- Handles rate limits gracefully by serving cached data

### Agent Memory

Key agents (researchers, managers, trader) maintain memory across sessions:
- They reference previous analyses to avoid repeating mistakes
- Past trade outcomes inform future recommendations
- Memory is implemented via `FinancialSituationMemory` with reflection capabilities

### Production REST API

A FastAPI backend exposes the full system over HTTP:
- **`POST /api/query`** — Run full multi-agent analysis
- **`POST /api/initialize-pool`** — Set up agents for a session
- **`GET /api/agents`** — List available agents and capabilities
- **`GET /api/health`** — Health check with active session count
- **`GET /api/history`** — Retrieve past analyses
- Session management, debug mode, structured error responses

### LLM Resilience

The system doesn't depend on a single model being available:
- Model candidate lists with automatic fallback (e.g., `gemini-2.5-pro` → `gemini-pro-latest` → `gemini-2.0-flash-exp`)
- Separate model tiers: "deep think" models for complex reasoning, "quick think" models for fast analysis
- Graceful error handling when models are rate-limited or unavailable

---

## How It's Currently Implemented

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend Framework** | FastAPI (Python) |
| **Agent Orchestration** | LangGraph (state machine-based workflow) |
| **LLM Abstraction** | LangChain |
| **Primary LLM** | Google Gemini (2.5-pro for deep analysis, 2.5-flash for quick tasks) |
| **Financial Data** | yfinance, Alpha Vantage, Finnhub |
| **News Grounding** | Google Gemini with Google Search integration |
| **Social Sentiment** | Reddit (PRAW), RSS feeds (FeedParser) |
| **Caching** | Custom disk-based JSON cache |
| **Technical Indicators** | stockstats library |
| **Data Processing** | Pandas |

### Architecture Overview

```
Client Request
       |
       v
  FastAPI Backend (app.py)
       |
       v
  Conversation Manager
       |
       +-- Query Classifier (keyword match or LLM-based)
       |
       v
  Ticker Validation (fail-fast)
       |
       v
  LangGraph Trading Workflow
       |
       +-- Phase 1: Analysts run in PARALLEL
       |     Market | Fundamentals | News | Social
       |
       +-- Phase 2: Sequential Bull/Bear debate
       |     Research Manager judges
       |
       +-- Phase 3: Trader builds execution plan
       |
       +-- Phase 4: Risk debate (Aggressive/Conservative/Neutral)
       |     Risk Manager delivers final verdict
       |
       v
  Structured JSON Response
```

### Key Design Decisions

- **Debate-driven decisions**: Rather than asking one LLM to make a call, the system forces explicit consideration of bull and bear cases. The manager sees both arguments before deciding.
- **Parallel analysts, sequential debates**: Data gathering runs in parallel for speed. Debates run sequentially because each phase depends on the previous one.
- **Fail-fast validation**: Ticker symbols are validated before any expensive LLM calls or API requests.
- **Vendor abstraction**: Agents don't know where their data comes from. The data flow layer handles routing, fallback, and caching transparently.
- **Configurable agent selection**: The query classifier prevents unnecessary work. A simple fundamentals question doesn't need sentiment analysis.

### Project Structure

```
GeminiTrader/
├── app.py                             # FastAPI server & API endpoints
├── requirements.txt                   # Python dependencies
├── agent_prompts.json                 # Agent role definitions & system prompts
│
├── tradingagents/
│   ├── conversation_manager.py        # Orchestrates the full analysis flow
│   ├── query_classifier.py            # Routes queries to relevant agents
│   ├── agent_pool.py                  # Agent registry and lifecycle
│   ├── config.py                      # System configuration & defaults
│   ├── llm_utils.py                   # LLM initialization with fallback
│   ├── prompt_manager.py              # Prompt template management
│   ├── logger_config.py               # Centralized logging
│   │
│   ├── agents/
│   │   ├── analysts/                  # Market, fundamentals, news, social
│   │   ├── researchers/               # Bull and bear case builders
│   │   ├── managers/                  # Research & risk debate judges
│   │   ├── trader/                    # Trade execution planner
│   │   ├── risk_mgmt/                 # Aggressive/conservative/neutral debaters
│   │   └── utils/                     # Memory, shared tools, state definitions
│   │
│   ├── graph/
│   │   ├── trading_graph.py           # Main LangGraph coordinator
│   │   ├── setup.py                   # Graph node & edge construction
│   │   ├── conditional_logic.py       # Phase routing logic
│   │   ├── propagation.py            # State forwarding between phases
│   │   ├── reflection.py             # Learning from past decisions
│   │   └── signal_processing.py      # Decision extraction & formatting
│   │
│   └── dataflows/
│       ├── interface.py               # Vendor routing & fallback logic
│       ├── cache.py                   # Disk-based cache (24h TTL)
│       ├── validation.py              # Ticker validation
│       ├── config.py                  # Vendor configuration
│       ├── y_finance.py               # yfinance implementation
│       ├── alpha_vantage*.py          # Alpha Vantage implementations
│       ├── google_gemini.py           # Gemini + Google Search grounding
│       ├── openai.py                  # OpenAI data implementation
│       └── local.py                   # Local/offline fallback
│
├── cli/                               # Command-line interface
└── project_documentation/             # Additional docs
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- A Google API key (for Gemini)
- Optional: Alpha Vantage, OpenAI, or Finnhub API keys for additional data sources

### Setup

```bash
# Clone and enter the project
git clone <repository-url>
cd GeminiTrader

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your API key
export GOOGLE_API_KEY="your-google-api-key"

# Optional: additional data sources
export ALPHA_VANTAGE_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export FINNHUB_API_KEY="your-key"

# Start the server
uvicorn app:app --reload --host localhost --port 8000
```

### Quick Test

```bash
# Check the server is running
curl http://localhost:8000/api/health

# Initialize agents
curl -X POST http://localhost:8000/api/initialize-pool \
  -H "Content-Type: application/json" \
  -d '{"selected_agents": ["market_analyst", "fundamentals_analyst", "news_analyst"]}'

# Run an analysis
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Should I invest in AAPL? Give me a comprehensive analysis.",
    "ticker": "AAPL",
    "date": "2024-01-15"
  }'
```

Interactive API docs are available at `http://localhost:8000/docs` (Swagger UI).

---

## Future Ideas to Explore

### Expanding the Agent System

- **Options Analyst**: An agent that evaluates options strategies (covered calls, protective puts, spreads) based on current volatility and the existing recommendation
- **Sector/Macro Analyst**: An agent that contextualizes individual stock analysis within broader sector rotation, macroeconomic trends, interest rate environment, and GDP data
- **Earnings Analyst**: A specialist that focuses specifically on upcoming earnings, historical earnings surprises, and guidance revisions
- **Insider Activity Analyst**: Deeper analysis of SEC filings, Form 4 data, and institutional ownership changes beyond the current basic insider sentiment

### Portfolio-Level Reasoning

Currently the system analyzes one stock at a time. Future versions could:
- Accept a portfolio and analyze correlations, concentration risk, and diversification gaps
- Suggest rebalancing based on current holdings and new analysis
- Track portfolio performance over time and adjust agent behavior accordingly
- Run comparative analysis ("Should I buy AAPL or MSFT?") with side-by-side debate

### Backtesting and Validation

- **Historical replay**: Run past stock data through the system and compare recommendations against actual outcomes
- **Agent accuracy tracking**: Score each agent's contributions over time — which analysts and researchers produce the most useful insights?
- **Confidence calibration**: Track whether "high confidence" calls actually outperform "medium confidence" ones

### Real-Time and Streaming

- **WebSocket support**: Stream analysis as it happens rather than waiting for the full pipeline to complete
- **Live market monitoring**: Set up watchlists where the system periodically re-evaluates positions
- **Alert system**: Trigger re-analysis when significant news breaks or price levels are hit
- **Intraday analysis**: Extend beyond daily data to support shorter timeframes

### Improved Data Sources

- **SEC EDGAR integration**: Direct access to 10-K, 10-Q, 8-K filings for fundamental analysis
- **Options chain data**: Feed implied volatility, put/call ratios, and unusual activity into analysis
- **Alternative data**: Satellite imagery, web traffic, app download metrics, credit card spending data
- **Crypto/forex support**: Extend beyond equities to other asset classes

### Frontend and User Experience

- **Interactive dashboard**: A web UI that visualizes the debate process, shows agent reasoning in real-time, and lets users drill into specific analyst reports
- **Agent configuration UI**: Let users enable/disable agents, adjust debate rounds, and set risk preferences without editing config files
- **Analysis history with search**: Full-text search over past analyses, comparison views, and trend tracking
- **Export formats**: PDF reports, email digests, integration with trading platforms

### Learning and Adaptation

- **Reinforcement from outcomes**: Feed actual trade outcomes back into the memory system so agents genuinely learn what works
- **User feedback loop**: Let users rate analyses and use that signal to improve prompt engineering and agent weighting
- **Dynamic agent weighting**: If the fundamentals analyst consistently provides better signals for tech stocks, weight that agent's input higher for similar future queries
- **Prompt evolution**: A/B test different agent prompts and systematically improve them based on output quality

### Infrastructure and Scalability

- **Redis-backed sessions**: Move from in-memory to persistent session storage for horizontal scaling
- **Job queue**: Offload long-running analyses to a task queue (Celery/RQ) so the API stays responsive
- **Rate limit management**: Smarter rate limit handling across vendors with token bucket algorithms
- **Observability**: OpenTelemetry tracing across the full agent pipeline for debugging and performance optimization
- **Containerization**: Docker and Docker Compose setup for easy deployment

### Research Directions

- **Multi-model ensemble**: Run the same analysis through different LLMs (Gemini, GPT-4, Claude) and compare their reasoning
- **Structured output schemas**: Move from free-text LLM responses to validated Pydantic models for more reliable downstream processing
- **Graph-of-thought reasoning**: Allow agents to share intermediate reasoning rather than just final reports
- **Adversarial testing**: Deliberately test the system with stocks that have recently had major events to measure response quality

---

## Configuration Reference

### Core Configuration (`tradingagents/config.py`)

```python
DEFAULT_CONFIG = {
    "llm_provider": "google",

    # Model candidates (tried in order)
    "quick_think_llm_candidates": [
        "gemini-2.5-flash",
        "gemini-2.0-flash-001",
        "gemini-flash-latest",
        "gemini-2.0-flash-lite",
    ],
    "deep_think_llm_candidates": [
        "gemini-2.5-pro",
        "gemini-pro-latest",
        "gemini-2.0-flash-exp",
    ],

    # Data vendor defaults by category
    "data_vendors": {
        "core_stock_apis": "yfinance",
        "technical_indicators": "yfinance",
        "fundamental_data": "alpha_vantage",
        "news_data": "yfinance",
    },

    # Per-tool vendor overrides (takes precedence)
    "tool_vendors": {
        "get_global_news": "google_gemini",
        "get_news": "google_gemini",
        "get_insider_sentiment": "local",
    },

    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
}
```

### Extending the System

**Adding a new agent:**
1. Create the agent in `tradingagents/agents/<category>/`
2. Register it in `agent_pool.py`
3. Wire it into the LangGraph workflow in `graph/setup.py`

**Adding a new data vendor:**
1. Implement vendor methods in `tradingagents/dataflows/`
2. Register methods in `dataflows/interface.py`
3. Add vendor name to relevant categories in `config.py`

---

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]
