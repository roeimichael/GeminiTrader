# GeminiTrader API Reference

**Version:** 1.0.0
**Base URL:** `http://localhost:8000`

Multi-Agent Stock Analysis System with LangGraph - Complete API Documentation

---

## Table of Contents

- [General Endpoints](#general-endpoints)
- [Agent Management](#agent-management)
- [Analysis Endpoints](#analysis-endpoints)
- [Session Management](#session-management)
- [Debug Endpoints](#debug-endpoints)
- [Data Models](#data-models)
- [Complete Examples](#complete-examples)

---

## General Endpoints

### GET `/`
**Serve Frontend UI**

Returns the main frontend HTML interface.

**Response:**
- HTML page with GeminiTrader interface

**Browser Access:**
```
http://localhost:8000
```

---

### GET `/api/info`
**Get API Information**

Returns API metadata and available endpoints.

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

**Example:**
```bash
curl http://localhost:8000/api/info
```

---

### GET `/api/health`
**Health Check**

Returns system health status and active session count.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00.123456",
  "active_sessions": 2
}
```

**Example:**
```bash
curl http://localhost:8000/api/health
```

---

## Agent Management

### GET `/api/agents`
**List Available Agents**

Returns all available agents with their descriptions and capabilities.

**Response:**
```json
{
  "analysts": {
    "market": {
      "name": "Market Analyst",
      "description": "Technical indicators and market trends expert",
      "category": "analysts",
      "requires_memory": false
    },
    "fundamentals": {
      "name": "Fundamentals Analyst",
      "description": "Financial statements and company fundamentals expert",
      "category": "analysts",
      "requires_memory": false
    },
    "news": {
      "name": "News Analyst",
      "description": "News and current events expert",
      "category": "analysts",
      "requires_memory": false
    },
    "social": {
      "name": "Social Media Analyst",
      "description": "Social sentiment and public perception expert",
      "category": "analysts",
      "requires_memory": false
    }
  },
  "researchers": {
    "bull": {
      "name": "Bull Researcher",
      "description": "Builds bullish investment cases",
      "category": "researchers",
      "requires_memory": true
    },
    "bear": {
      "name": "Bear Researcher",
      "description": "Builds bearish counter-arguments",
      "category": "researchers",
      "requires_memory": true
    }
  },
  "managers": {
    "research": {
      "name": "Research Manager",
      "description": "Makes final investment decisions",
      "category": "managers",
      "requires_memory": true
    },
    "risk": {
      "name": "Risk Manager",
      "description": "Final risk assessment and recommendation",
      "category": "managers",
      "requires_memory": true
    }
  },
  "risk_analysts": {
    "risky": {
      "name": "Risky Analyst",
      "description": "Argues for aggressive positioning",
      "category": "risk_analysts",
      "requires_memory": false
    },
    "safe": {
      "name": "Safe Analyst",
      "description": "Argues for conservative risk management",
      "category": "risk_analysts",
      "requires_memory": false
    },
    "neutral": {
      "name": "Neutral Analyst",
      "description": "Provides balanced perspective",
      "category": "risk_analysts",
      "requires_memory": false
    }
  },
  "trader": {
    "trader": {
      "name": "Trader",
      "description": "Creates executable trade plans",
      "category": "trader",
      "requires_memory": true
    }
  }
}
```

**Example:**
```bash
curl http://localhost:8000/api/agents
```

---

### POST `/api/initialize-pool`
**Initialize Agent Pool**

Creates a session with selected agents for analysis.

**Request Body:**
```json
{
  "selected_agents": [
    "market_analyst",
    "fundamentals_analyst",
    "news_analyst",
    "social_analyst"
  ],
  "session_id": "my-session-123"  // Optional, defaults to "default"
}
```

**Available Agent Keys:**
- `market_analyst` - Technical analysis
- `fundamentals_analyst` - Financial fundamentals
- `news_analyst` - News analysis
- `social_analyst` - Social sentiment
- `bull_researcher` - Bullish arguments
- `bear_researcher` - Bearish arguments
- `research_manager` - Investment decisions
- `risk_manager` - Risk assessment
- `risky_analyst` - Aggressive risk analysis
- `safe_analyst` - Conservative risk analysis
- `neutral_analyst` - Balanced risk analysis
- `trader` - Trade execution planning

**Response:**
```json
{
  "status": "success",
  "message": "Successfully initialized 4 agents",
  "agent_count": 4,
  "session_id": "my-session-123",
  "agents": [
    "market_analyst",
    "fundamentals_analyst",
    "news_analyst",
    "social_analyst"
  ]
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/initialize-pool \
  -H "Content-Type: application/json" \
  -d '{
    "selected_agents": ["market_analyst", "fundamentals_analyst"],
    "session_id": "test-session"
  }'
```

**Error Responses:**
- `400 Bad Request` - No valid agents could be initialized
- `500 Internal Server Error` - Initialization failed

---

## Analysis Endpoints

### POST `/api/query`
**Execute Stock Analysis**

Runs multi-agent analysis workflow for a specific stock.

**Request Body:**
```json
{
  "query": "Should I invest in this stock?",
  "ticker": "AAPL",
  "date": "2024-01-15",  // Optional, defaults to today
  "session_id": "my-session-123"  // Optional, defaults to "default"
}
```

**Required Fields:**
- `query` - Your question about the stock
- `ticker` - Stock ticker symbol (e.g., AAPL, MSFT, TSLA)

**Optional Fields:**
- `date` - Analysis date in YYYY-MM-DD format
- `session_id` - Session to use (must be initialized first)

**Response:**
```json
{
  "status": "success",
  "timestamp": "2024-01-15T10:30:00.123456",
  "query": "Should I invest in this stock?",
  "ticker": "AAPL",
  "query_classification": {
    "selected_agents": ["market", "fundamentals", "news", "social"],
    "reasoning": "Comprehensive analysis requested requiring all perspectives",
    "complexity": "complex",
    "estimated_cost": "high",
    "method": "llm_classification"
  },
  "individual_responses": [
    {
      "agent": "Market Analyst",
      "category": "analysts",
      "perspective": "Technical analysis and market indicators",
      "response": "Based on technical analysis, AAPL shows strong momentum with RSI at 65..."
    },
    {
      "agent": "Fundamentals Analyst",
      "category": "analysts",
      "perspective": "Financial statements and company fundamentals",
      "response": "Apple's fundamentals remain strong with P/E ratio of 28.5..."
    }
  ],
  "debate": [
    {
      "round": 1,
      "topic": "Investment Opportunity Debate (Bull vs Bear)",
      "exchanges": [
        {
          "speaker": "Bull Researcher",
          "statement": "Strong technical indicators and solid fundamentals support a buy..."
        },
        {
          "speaker": "Bear Researcher",
          "statement": "However, valuation concerns and market headwinds suggest caution..."
        },
        {
          "speaker": "Research Manager (Judge)",
          "statement": "Based on the debate, I recommend BUY with moderate position sizing..."
        }
      ]
    },
    {
      "round": 2,
      "topic": "Trade Execution Plan",
      "exchanges": [
        {
          "speaker": "Trader",
          "statement": "Execute entry at current levels with 5% position size, stop loss at..."
        }
      ]
    },
    {
      "round": 3,
      "topic": "Risk Assessment Debate",
      "exchanges": [
        {
          "speaker": "Aggressive Risk Analyst",
          "statement": "Given the opportunity, recommend 10% portfolio allocation..."
        },
        {
          "speaker": "Conservative Risk Analyst",
          "statement": "Market volatility suggests limiting exposure to 3%..."
        },
        {
          "speaker": "Neutral Risk Analyst",
          "statement": "A balanced 5-7% allocation seems appropriate..."
        },
        {
          "speaker": "Risk Manager (Judge)",
          "statement": "Final recommendation: BUY with 5% allocation, tight stop loss..."
        }
      ]
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
    "final_trade_decision": "Based on comprehensive multi-agent analysis: BUY AAPL...",
    "investment_plan": "Entry: Current levels, Position: 5%, Stop Loss: $170...",
    "summary": "ANALYSIS FOR AAPL\n\nFINAL CONSENSUS: BUY\n\nAfter comprehensive analysis..."
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the risks of investing in this stock?",
    "ticker": "TSLA",
    "date": "2024-01-15"
  }'
```

**Error Responses:**
- `400 Bad Request` - Pool not initialized or ticker validation failed
- `500 Internal Server Error` - Analysis execution failed

**Notes:**
- Analysis typically takes 30-60 seconds
- Requires agent pool to be initialized first
- Results are automatically saved to conversation history

---

### GET `/api/history`
**Get Conversation History**

Retrieves conversation history for a session.

**Query Parameters:**
- `session_id` (optional) - Session ID, defaults to "default"
- `limit` (optional) - Number of recent queries to return, defaults to 10

**Response:**
```json
[
  {
    "status": "success",
    "timestamp": "2024-01-15T10:30:00.123456",
    "query": "Should I invest in this stock?",
    "ticker": "AAPL",
    "context": {
      "ticker": "AAPL",
      "date": "2024-01-15"
    },
    "individual_responses": [...],
    "debate": [...],
    "final_verdict": {...},
    "query_classification": {...}
  }
]
```

**Example:**
```bash
# Get last 10 queries for default session
curl http://localhost:8000/api/history

# Get last 5 queries for specific session
curl "http://localhost:8000/api/history?session_id=my-session&limit=5"
```

**Notes:**
- Returns empty array if no history exists
- Results are ordered by most recent first
- Each entry contains full analysis results

---

### DELETE `/api/history`
**Clear Conversation History**

Clears all conversation history for a session.

**Query Parameters:**
- `session_id` (optional) - Session ID, defaults to "default"

**Response:**
```json
{
  "status": "success",
  "message": "History cleared"
}
```

**Example:**
```bash
# Clear history for default session
curl -X DELETE http://localhost:8000/api/history

# Clear history for specific session
curl -X DELETE "http://localhost:8000/api/history?session_id=my-session"
```

---

## Session Management

### GET `/api/sessions`
**List Active Sessions**

Returns all active sessions with their details.

**Response:**
```json
{
  "total": 2,
  "sessions": {
    "default": {
      "created_at": "2024-01-15T10:00:00.123456",
      "agent_count": 4,
      "agents": [
        "market_analyst",
        "fundamentals_analyst",
        "news_analyst",
        "social_analyst"
      ]
    },
    "my-session-123": {
      "created_at": "2024-01-15T10:15:00.123456",
      "agent_count": 2,
      "agents": [
        "market_analyst",
        "fundamentals_analyst"
      ]
    }
  }
}
```

**Example:**
```bash
curl http://localhost:8000/api/sessions
```

---

### DELETE `/api/session/{session_id}`
**Delete Session**

Deletes a specific session and cleans up resources.

**Path Parameters:**
- `session_id` - The session ID to delete

**Response:**
```json
{
  "status": "success",
  "message": "Session my-session-123 deleted"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/session/my-session-123
```

**Error Responses:**
- `404 Not Found` - Session does not exist

---

## Debug Endpoints

### POST `/api/debug/enable`
**Enable Debug Mode**

Enables detailed debug logging in the backend.

**Response:**
```json
{
  "status": "success",
  "message": "Debug logging enabled"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/debug/enable
```

**Notes:**
- Shows detailed logs in backend console
- Useful for troubleshooting and development
- Logs include: agent execution, API calls, state transitions

---

### POST `/api/debug/disable`
**Disable Debug Mode**

Disables debug logging (production mode).

**Response:**
```json
{
  "status": "success",
  "message": "Debug logging disabled"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/debug/disable
```

---

## Data Models

### AgentInfo
Information about an available agent.

```json
{
  "name": "string",
  "description": "string",
  "category": "string",
  "requires_memory": boolean
}
```

### InitPoolRequest
Request to initialize agent pool.

```json
{
  "selected_agents": ["string"],
  "session_id": "string | null"
}
```

### InitPoolResponse
Response from pool initialization.

```json
{
  "status": "string",
  "message": "string",
  "agent_count": number,
  "session_id": "string",
  "agents": ["string"]
}
```

### QueryRequest
Request to analyze a stock.

```json
{
  "query": "string",
  "ticker": "string",
  "date": "string | null",
  "session_id": "string | null"
}
```

### HealthResponse
Health check response.

```json
{
  "status": "string",
  "version": "string",
  "timestamp": "string",
  "active_sessions": number
}
```

---

## Complete Examples

### Example 1: Basic Stock Analysis

```bash
# Step 1: Check API health
curl http://localhost:8000/api/health

# Step 2: Get available agents
curl http://localhost:8000/api/agents

# Step 3: Initialize agent pool
curl -X POST http://localhost:8000/api/initialize-pool \
  -H "Content-Type: application/json" \
  -d '{
    "selected_agents": [
      "market_analyst",
      "fundamentals_analyst",
      "news_analyst"
    ]
  }'

# Step 4: Run analysis
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Should I buy this stock?",
    "ticker": "AAPL"
  }'

# Step 5: View history
curl http://localhost:8000/api/history
```

### Example 2: Multi-Session Analysis

```bash
# Create session 1 for conservative analysis
curl -X POST http://localhost:8000/api/initialize-pool \
  -H "Content-Type: application/json" \
  -d '{
    "selected_agents": ["fundamentals_analyst", "safe_analyst"],
    "session_id": "conservative"
  }'

# Create session 2 for aggressive analysis
curl -X POST http://localhost:8000/api/initialize-pool \
  -H "Content-Type: application/json" \
  -d '{
    "selected_agents": ["market_analyst", "risky_analyst"],
    "session_id": "aggressive"
  }'

# Run analysis in conservative session
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Is this a safe long-term investment?",
    "ticker": "MSFT",
    "session_id": "conservative"
  }'

# Run analysis in aggressive session
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the short-term trading opportunity?",
    "ticker": "TSLA",
    "session_id": "aggressive"
  }'

# List all sessions
curl http://localhost:8000/api/sessions
```

### Example 3: Using PowerShell (Windows)

```powershell
# Initialize pool
$body = @{
    selected_agents = @("market_analyst", "fundamentals_analyst")
    session_id = "powershell-session"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/initialize-pool" `
    -ContentType "application/json" -Body $body

# Run query
$query = @{
    query = "Should I invest in this stock?"
    ticker = "AAPL"
    session_id = "powershell-session"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/query" `
    -ContentType "application/json" -Body $query
```

### Example 4: Using Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Initialize pool
init_response = requests.post(
    f"{BASE_URL}/api/initialize-pool",
    json={
        "selected_agents": ["market_analyst", "fundamentals_analyst"],
        "session_id": "python-session"
    }
)
print(init_response.json())

# Run analysis
query_response = requests.post(
    f"{BASE_URL}/api/query",
    json={
        "query": "What are the growth prospects?",
        "ticker": "NVDA",
        "session_id": "python-session"
    }
)
result = query_response.json()

# Print final verdict
print(f"Recommendation: {result['final_verdict']['overall_recommendation']}")
print(f"Confidence: {result['final_verdict']['confidence_level']}")
print(result['final_verdict']['summary'])
```

---

## Interactive API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

These interfaces allow you to:
- Explore all endpoints
- Test API calls directly in the browser
- View request/response schemas
- Download OpenAPI specification

---

## Rate Limits & Performance

- **Analysis Duration:** 30-60 seconds per query
- **Concurrent Sessions:** Unlimited
- **API Rate Limits:** None (limited by external data providers)
- **Caching:** 24-hour TTL for data vendor responses

---

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

Error response format:
```json
{
  "status": "error",
  "message": "Error description",
  "details": {
    "additional": "context"
  }
}
```

---

## Authentication

Currently, the API does not require authentication. For production deployment, consider adding:
- API key authentication
- OAuth2 / JWT tokens
- Rate limiting per user
- IP whitelisting

---

## Changelog

**Version 1.0.0** (Current)
- Initial release
- 11 API endpoints
- Multi-agent analysis system
- Session management
- Query history
- Debug controls
