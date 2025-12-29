# GeminiTrader API

Multi-agent stock analysis system powered by Google Gemini AI, exposed via REST API.

## Overview

GeminiTrader is an intelligent trading analysis framework that uses multiple AI agents to analyze stocks from different perspectives. The system is built as a FastAPI backend, allowing any frontend (web, mobile, CLI) to consume the analysis capabilities.

## Features

- **Multi-agent analysis** with specialized roles (Market, Fundamentals, Technicals, Sentiment)
- **Bull vs Bear debate** mechanism for balanced analysis
- **Risk assessment** from multiple perspectives
- **Query classification** to optimize agent selection and reduce costs
- **Parallel execution** via LangGraph for 4x faster analysis
- **Data caching** with 24-hour TTL to minimize API calls
- **Fail-fast validation** to prevent wasted resources
- **REST API** for easy integration with any frontend
- **Session management** for multi-user support
- **Auto-generated documentation** at `/docs`

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your API keys:
# GOOGLE_API_KEY=your_gemini_api_key
```

### 3. Start the API Server

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access API Documentation

Open your browser to:
- **Interactive docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Usage

### Initialize Agent Pool

```bash
curl -X POST "http://localhost:8000/api/initialize-pool" \
  -H "Content-Type: application/json" \
  -d '{
    "selected_agents": ["market", "fundamentals", "technicals", "sentiment"]
  }'
```

### Analyze a Stock

```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Should I invest in AAPL?",
    "ticker": "AAPL",
    "date": "2025-12-29"
  }'
```

### Get Available Agents

```bash
curl "http://localhost:8000/api/agents"
```

## Architecture

```
┌─────────────┐
│   Frontend  │ (Web/Mobile/CLI - to be built)
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────────────────────────────────────┐
│           FastAPI Backend (app.py)          │
├─────────────────────────────────────────────┤
│  • Session Management                       │
│  • Request/Response Validation (Pydantic)   │
│  • CORS Middleware                          │
│  • Auto-generated Documentation             │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│      ConversationManager (Orchestrator)     │
├─────────────────────────────────────────────┤
│  • Query Classification (Phase -1)          │
│  • Ticker Validation (Phase 0)              │
│  • Agent Execution (Phase 1)                │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│    TradingAgentsGraph (Multi-Agent Core)    │
├─────────────────────────────────────────────┤
│  • LangGraph State Management               │
│  • Parallel Agent Execution                 │
│  • Bull/Bear Debate Mechanism               │
│  • Risk Assessment Aggregation              │
│  • Final Recommendation Synthesis           │
└─────────────────────────────────────────────┘
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/api/health` | GET | Health check |
| `/api/agents` | GET | List available agents |
| `/api/initialize-pool` | POST | Initialize agent pool for session |
| `/api/query` | POST | Analyze stock with multi-agent system |
| `/api/history` | GET | Get conversation history for session |
| `/docs` | GET | Interactive API documentation |
| `/redoc` | GET | ReDoc API documentation |

## Project Structure

```
GeminiTrader/
├── app.py                    # FastAPI backend (MAIN ENTRY POINT)
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (API keys)
├── tradingagents/           # Core multi-agent framework
│   ├── agents/              # Agent implementations
│   ├── graph/               # LangGraph workflow
│   ├── dataflows/           # Data fetching & caching
│   ├── conversation_manager.py  # Orchestration layer
│   ├── agent_pool.py        # Agent registry & management
│   ├── query_classifier.py  # Query classification
│   └── logger_config.py     # Centralized logging
└── project_documentation/   # Comprehensive documentation
    └── README.md            # Full project details
```

## Technology Stack

- **FastAPI** - Modern Python web framework
- **LangGraph** - State-based multi-agent orchestration
- **Google Gemini** - LLM for agent intelligence
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **yfinance** - Stock data
- **Redis** - Caching (optional)

## Development

### Running Tests

```bash
pytest tests/
```

### Development Mode (with auto-reload)

```bash
uvicorn app:app --reload --log-level debug
```

### Production Deployment

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

Or use Docker:

```bash
docker build -t geminitrader .
docker run -p 8000:8000 --env-file .env geminitrader
```

## Documentation

- **Full Documentation**: See `project_documentation/README.md`
- **API Documentation**: http://localhost:8000/docs (when server is running)

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]
