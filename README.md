# GeminiTrader

A sophisticated multi-agent stock analysis system built with FastAPI, LangGraph, and Google Gemini. GeminiTrader uses specialized AI agents to analyze stocks from multiple perspectives (technical, fundamental, news, sentiment) and provides comprehensive investment recommendations through structured debates and risk assessment.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [API Reference](#api-reference)
- [System Flow](#system-flow)
- [Agent System](#agent-system)
- [Configuration](#configuration)
- [Development](#development)

## Overview

GeminiTrader is a backend API that orchestrates multiple AI agents to perform comprehensive stock analysis. The system features:

- **Multi-Agent Analysis**: Specialized agents for market analysis, fundamentals, news, and social sentiment
- **Intelligent Query Classification**: Automatically selects relevant agents based on user queries
- **Debate-Based Decision Making**: Bull/bear debates and risk assessment through structured discussions
- **Modular Data Sources**: Pluggable vendor system supporting yfinance, Alpha Vantage, OpenAI, and Google
- **Production-Ready API**: FastAPI backend with session management and comprehensive logging
- **Advanced Caching**: Disk-based caching to optimize API usage and reduce costs

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend / Client                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend (app.py)                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  API Endpoints                                        │  │
│  │  - /api/agents       - /api/initialize-pool          │  │
│  │  - /api/query        - /api/history                  │  │
│  │  - /api/sessions     - /api/health                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Conversation Manager                       │
│  ┌─────────────────┐  ┌──────────────────────────────────┐ │
│  │ Query Classifier│  │   TradingAgentsGraph (LangGraph)│ │
│  │  - Keyword Match│  │   - Analyst Agents (Phase 1)    │ │
│  │  - LLM Analysis │  │   - Investment Debate (Phase 2) │ │
│  │  - Agent Select │  │   - Trader Planning (Phase 3)   │ │
│  └─────────────────┘  │   - Risk Debate (Phase 4)       │ │
│                        │   - Final Decision (Phase 5)    │ │
│                        └──────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Flow Layer                           │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Interface  │  │    Cache     │  │   Validation     │  │
│  │  - Routing  │  │  - Disk TTL  │  │  - Ticker Check  │  │
│  │  - Fallback │  │  - 24h Cache │  │  - Fail Fast     │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Vendors                             │
│  ┌──────────┐ ┌───────────────┐ ┌────────┐ ┌────────────┐ │
│  │ yfinance │ │ Alpha Vantage │ │ OpenAI │ │   Google   │ │
│  └──────────┘ └───────────────┘ └────────┘ └────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Backend Components

#### Core Modules

- **app.py**: FastAPI application with REST API endpoints
- **agent_pool.py**: Agent registry and pool management
- **conversation_manager.py**: Orchestrates multi-agent conversations
- **query_classifier.py**: Intelligent query routing to relevant agents
- **trading_graph.py**: LangGraph workflow for multi-agent analysis

#### Data Layer

- **dataflows/interface.py**: Vendor routing with fallback support
- **dataflows/cache.py**: Disk-based caching system (24h TTL)
- **dataflows/validation.py**: Fail-fast ticker validation
- **dataflows/vendors/**: Implementation for each data provider

#### Agent System

- **agents/analysts/**: Market, fundamentals, news, social media analysts
- **agents/researchers/**: Bull and bear researchers for debates
- **agents/managers/**: Research and risk managers (judges)
- **agents/trader/**: Trade execution planner
- **agents/risk_mgmt/**: Aggressive, conservative, neutral risk analysts

## Installation

### Prerequisites

- Python 3.9+
- Google API Key (for Gemini)
- Optional: Alpha Vantage API Key, OpenAI API Key

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd GeminiTrader

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export GOOGLE_API_KEY="your-google-api-key"
export ALPHA_VANTAGE_API_KEY="your-alpha-vantage-key"  # Optional
export OPENAI_API_KEY="your-openai-key"  # Optional

# Run the server
uvicorn app:app --reload --host localhost --port 8082
```

The API will be available at:
- API: `http://localhost:8082`
- Interactive Docs: `http://localhost:8082/docs`
- ReDoc: `http://localhost:8082/redoc`

## API Reference

### General Endpoints

#### `GET /`
Root endpoint providing API information and available endpoints.

**Response:**
```json
{
  "name": "GeminiTrader API",
  "version": "1.0.0",
  "description": "Multi-Agent Stock Analysis System",
  "documentation": "/docs",
  "health": "/api/health",
  "endpoints": {
    "agents": "/api/agents",
    "initialize": "/api/initialize-pool",
    "query": "/api/query",
    "history": "/api/history"
  }
}
```

#### `GET /api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00",
  "active_sessions": 2
}
```

### Agent Management

#### `GET /api/agents`
Get all available agents with their descriptions and capabilities.

**Response:**
```json
{
  "analysts": {
    "market": {
      "name": "Market Analyst",
      "description": "Technical indicators and market trends expert",
      "requires_memory": false
    },
    "fundamentals": {...},
    "news": {...},
    "social": {...}
  },
  "researchers": {...},
  "managers": {...},
  "risk_analysts": {...},
  "trader": {...}
}
```

#### `POST /api/initialize-pool`
Initialize an agent pool for a session.

**Request:**
```json
{
  "selected_agents": ["market_analyst", "fundamentals_analyst", "news_analyst"],
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Successfully initialized 3 agents",
  "agent_count": 3,
  "session_id": "default",
  "agents": ["market_analyst", "fundamentals_analyst", "news_analyst"]
}
```

### Analysis Endpoints

#### `POST /api/query`
Execute multi-agent stock analysis workflow.

**Request:**
```json
{
  "query": "What are your thoughts about investing in this stock?",
  "ticker": "AAPL",
  "date": "2024-01-15",
  "session_id": "default"
}
```

**Response:**
```json
{
  "status": "success",
  "timestamp": "2024-01-15T10:30:00",
  "query": "What are your thoughts...",
  "ticker": "AAPL",
  "individual_responses": [
    {
      "agent": "Market Analyst",
      "category": "analysts",
      "perspective": "Technical analysis and market indicators",
      "response": "Detailed analysis..."
    }
  ],
  "debate": [
    {
      "round": 1,
      "topic": "Investment Opportunity Debate (Bull vs Bear)",
      "exchanges": [...]
    },
    {
      "round": 2,
      "topic": "Trade Execution Plan",
      "exchanges": [...]
    },
    {
      "round": 3,
      "topic": "Risk Assessment Debate",
      "exchanges": [...]
    }
  ],
  "final_verdict": {
    "timestamp": "2024-01-15 10:30:00",
    "ticker": "AAPL",
    "trade_date": "2024-01-15",
    "overall_recommendation": "BUY",
    "confidence_level": "High",
    "sentiment_breakdown": {
      "bullish": 3,
      "bearish": 0,
      "neutral": 1,
      "bullish_percentage": 75.0
    },
    "final_trade_decision": "Full decision text...",
    "investment_plan": "Detailed plan...",
    "summary": "Analysis summary..."
  },
  "query_classification": {
    "selected_agents": ["market", "fundamentals", "news"],
    "reasoning": "Query requires comprehensive analysis",
    "complexity": "complex",
    "estimated_cost": "high",
    "method": "llm_classification"
  }
}
```

### History & Session Management

#### `GET /api/history?session_id=default&limit=10`
Get conversation history for a session.

**Response:**
```json
[
  {
    "status": "success",
    "timestamp": "2024-01-15T10:30:00",
    "query": "...",
    "ticker": "AAPL",
    "individual_responses": [...],
    "debate": [...],
    "final_verdict": {...}
  }
]
```

#### `DELETE /api/history?session_id=default`
Clear conversation history for a session.

#### `GET /api/sessions`
List all active sessions.

**Response:**
```json
{
  "total": 2,
  "sessions": {
    "default": {
      "created_at": "2024-01-15T10:00:00",
      "agent_count": 4,
      "agents": ["market_analyst", "fundamentals_analyst", "news_analyst", "social_analyst"]
    }
  }
}
```

#### `DELETE /api/session/{session_id}`
Delete a session and clean up resources.

### Debug Endpoints

#### `POST /api/debug/enable`
Enable debug logging for detailed diagnostics.

#### `POST /api/debug/disable`
Disable debug logging (production mode).

## System Flow

### Complete Analysis Flow

```
1. CLIENT REQUEST
   ↓
2. API ENDPOINT (/api/query)
   ↓
3. CONVERSATION MANAGER
   ↓
4. QUERY CLASSIFIER
   │
   ├─→ Keyword Matching (fast path)
   │   └─→ Select agents based on keywords
   │
   └─→ LLM Classification (complex queries)
       └─→ Gemini analyzes query and selects relevant agents
   ↓
5. TICKER VALIDATION
   │
   ├─→ Check ticker format
   ├─→ Validate data accessibility
   └─→ Fail-fast if invalid
   ↓
6. TRADING AGENTS GRAPH (LangGraph)
   │
   ├─→ PHASE 1: Parallel Analyst Execution
   │   ├─→ Market Analyst (if selected)
   │   ├─→ Fundamentals Analyst (if selected)
   │   ├─→ News Analyst (if selected)
   │   └─→ Social Media Analyst (if selected)
   │
   ├─→ PHASE 2: Investment Debate
   │   ├─→ Bull Researcher (builds bullish case)
   │   ├─→ Bear Researcher (builds bearish case)
   │   └─→ Research Manager (judges debate, makes decision)
   │
   ├─→ PHASE 3: Trade Planning
   │   └─→ Trader (creates executable trade plan)
   │
   ├─→ PHASE 4: Risk Assessment Debate
   │   ├─→ Aggressive Risk Analyst
   │   ├─→ Conservative Risk Analyst
   │   ├─→ Neutral Risk Analyst
   │   └─→ Risk Manager (judges, final recommendation)
   │
   └─→ PHASE 5: Final Decision & Formatting
   ↓
7. RESULT FORMATTING
   ↓
8. RESPONSE TO CLIENT
```

### Data Flow

```
AGENT REQUESTS DATA
   ↓
DATAFLOW INTERFACE (route_to_vendor)
   ↓
CHECK CACHE (24h TTL)
   │
   ├─→ CACHE HIT: Return cached data
   │
   └─→ CACHE MISS
       ↓
   VENDOR ROUTING
       │
       ├─→ PRIMARY VENDOR (from config)
       │   ├─→ SUCCESS: Cache & return
       │   └─→ FAILURE: Try next vendor
       │
       └─→ FALLBACK VENDORS (automatic)
           ├─→ Try each vendor in sequence
           ├─→ Rate limit handling
           └─→ Error recovery
```

## Agent System

### Agent Categories

#### 1. Analysts (Phase 1)
Gather data and perform specialized analysis:

- **Market Analyst**: Technical indicators, price trends, moving averages, RSI, MACD, Bollinger Bands
- **Fundamentals Analyst**: Financial statements, P/E ratio, revenue, earnings, balance sheet analysis
- **News Analyst**: Recent news, company announcements, events, insider transactions
- **Social Media Analyst**: Sentiment analysis from social media, Reddit, public perception

#### 2. Researchers (Phase 2)
Build opposing investment cases:

- **Bull Researcher**: Constructs bullish arguments based on analyst reports
- **Bear Researcher**: Constructs bearish counter-arguments
- **Research Manager**: Judges the debate and makes initial investment decision

#### 3. Trader (Phase 3)
Creates executable trade plans:

- **Trader**: Develops detailed trade execution strategy based on research manager's decision

#### 4. Risk Analysts (Phase 4)
Debate risk management approach:

- **Aggressive Risk Analyst**: Argues for high-risk, high-reward positioning
- **Conservative Risk Analyst**: Argues for risk-averse approach
- **Neutral Risk Analyst**: Provides balanced perspective
- **Risk Manager**: Final judge, produces ultimate recommendation (BUY/SELL/HOLD)

### Agent Memory System

Agents with `requires_memory: true` maintain conversation memory to:
- Learn from past decisions
- Reference previous analyses
- Improve recommendations over time
- Avoid repeating mistakes

Memory-enabled agents:
- Bull Researcher
- Bear Researcher
- Research Manager
- Risk Manager
- Trader

## Configuration

### Environment Variables

```bash
# Required
GOOGLE_API_KEY=your-google-api-key

# Optional (for additional data sources)
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
OPENAI_API_KEY=your-openai-key
FINNHUB_API_KEY=your-finnhub-key
```

### Data Vendor Configuration

Edit `tradingagents/config.py`:

```python
DEFAULT_CONFIG = {
    "llm_provider": "google",
    "deep_think_llm": "gemini-1.5-pro",      # For complex reasoning
    "quick_think_llm": "gemini-2.0-flash-exp", # For fast analysis

    # Category-level defaults
    "data_vendors": {
        "core_stock_apis": "yfinance",
        "technical_indicators": "yfinance",
        "fundamental_data": "alpha_vantage",
        "news_data": "alpha_vantage",
    },

    # Tool-level overrides
    "tool_vendors": {
        # Example: "get_news": "openai"
    },

    # Debate settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
}
```

### Available Vendors by Category

| Category | Available Vendors |
|----------|------------------|
| Core Stock APIs | yfinance, alpha_vantage, local |
| Technical Indicators | yfinance, alpha_vantage, local |
| Fundamental Data | alpha_vantage, openai, local |
| News Data | alpha_vantage, openai, google, local |

### Caching Configuration

The system uses disk-based caching with a 24-hour TTL to:
- Reduce API costs
- Improve response times
- Avoid rate limits during development

Cache location: `tradingagents/dataflows/data_cache/*.json`

To clear cache:
```python
from tradingagents.dataflows.cache import get_cache
get_cache().clear_all()
```

## Development

### Project Structure

```
GeminiTrader/
├── app.py                          # FastAPI application
├── tradingagents/
│   ├── agent_pool.py               # Agent registry & pool management
│   ├── conversation_manager.py     # Conversation orchestration
│   ├── query_classifier.py         # Query routing logic
│   ├── config.py                   # Configuration
│   ├── logger_config.py            # Logging setup
│   │
│   ├── agents/                     # Agent implementations
│   │   ├── analysts/               # Market, fundamentals, news, social
│   │   ├── researchers/            # Bull, bear researchers
│   │   ├── managers/               # Research & risk managers
│   │   ├── trader/                 # Trade execution planner
│   │   ├── risk_mgmt/              # Risk assessment agents
│   │   └── utils/                  # Shared utilities, memory, tools
│   │
│   ├── graph/                      # LangGraph workflow
│   │   ├── trading_graph.py        # Main graph orchestration
│   │   ├── setup.py                # Graph setup & node creation
│   │   ├── conditional_logic.py    # Routing logic
│   │   ├── propagation.py          # State propagation
│   │   └── signal_processing.py    # Decision processing
│   │
│   └── dataflows/                  # Data layer
│       ├── interface.py            # Vendor routing
│       ├── cache.py                # Caching system
│       ├── validation.py           # Ticker validation
│       ├── config.py               # Data config
│       ├── alpha_vantage.py        # Alpha Vantage impl
│       ├── y_finance.py            # yfinance impl
│       ├── openai.py               # OpenAI impl
│       ├── google.py               # Google News impl
│       └── local.py                # Local data impl
│
├── frontend/                       # Frontend application (separate)
└── requirements.txt                # Python dependencies
```

### Logging

The system uses a centralized logging configuration:

```python
from tradingagents.logger_config import get_logger

logger = get_logger(__name__)

logger.debug("Detailed diagnostic info")
logger.info("High-level workflow events")
logger.warning("Recoverable issues")
logger.error("Failures requiring attention")
```

**Log Levels:**
- **DEBUG**: Vendor calls, cache hits/misses, detailed execution
- **INFO**: Phase transitions, high-level workflow, agent selection
- **WARNING**: Fallbacks, rate limits, recoverable errors
- **ERROR**: Validation failures, unrecoverable errors

Enable debug mode:
```bash
POST /api/debug/enable
```

### Testing

```bash
# Run the development server
uvicorn app:app --reload

# Test health endpoint
curl http://localhost:8082/api/health

# Get available agents
curl http://localhost:8082/api/agents

# Initialize pool
curl -X POST http://localhost:8082/api/initialize-pool \
  -H "Content-Type: application/json" \
  -d '{"selected_agents": ["market_analyst", "fundamentals_analyst"]}'

# Run analysis
curl -X POST http://localhost:8082/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Should I invest in this stock?",
    "ticker": "AAPL",
    "date": "2024-01-15"
  }'
```

### Adding New Agents

1. Create agent file in appropriate category:
```python
# tradingagents/agents/analysts/new_analyst.py
def create_new_analyst(llm, memory=None):
    def new_analyst_node(state):
        # Implementation
        return {"messages": [result], "custom_report": response}
    return new_analyst_node
```

2. Register in `agent_pool.py`:
```python
"new": {
    "name": "New Analyst",
    "description": "Description of capabilities",
    "factory": create_new_analyst,
    "requires_memory": False
}
```

3. Add to graph workflow in `graph/setup.py`

### Adding New Data Vendors

1. Implement vendor methods:
```python
# tradingagents/dataflows/new_vendor.py
def get_stock_data_new_vendor(ticker: str, period: str = "1mo"):
    # Implementation
    return data
```

2. Register in `dataflows/interface.py`:
```python
VENDOR_METHODS = {
    "get_stock_data": {
        "new_vendor": get_stock_data_new_vendor,
        # ...
    }
}
```

3. Configure in `config.py`:
```python
"data_vendors": {
    "core_stock_apis": "new_vendor",
}
```

## Best Practices

### API Usage
- Always initialize an agent pool before running queries
- Use session IDs for multi-user scenarios
- Clear history periodically to avoid memory bloat
- Monitor active sessions via `/api/sessions`

### Performance
- Cache is enabled by default (24h TTL)
- Use query classifier to minimize unnecessary agent executions
- Consider using only necessary agents for specific queries
- Enable debug mode only when troubleshooting

### Data Vendors
- Start with free vendors (yfinance, google)
- Add paid vendors (Alpha Vantage, OpenAI) as needed
- Configure fallback chains for reliability
- Monitor rate limits in logs

### Error Handling
- All endpoints return structured error responses
- Ticker validation fails fast before expensive operations
- Vendor fallbacks handle rate limits automatically
- Session not found errors indicate need to initialize pool

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]

## Support

For issues, questions, or contributions, please [open an issue](your-repo-url/issues).
