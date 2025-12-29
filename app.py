"""
GeminiTrader FastAPI Backend

This is the main FastAPI application that exposes the multi-agent trading
analysis system via REST API endpoints.

Architecture:
- FastAPI handles HTTP requests
- ConversationManager orchestrates agent analysis
- TradingAgentsGraph executes multi-agent workflow
- Results returned as JSON

Run with:
    uvicorn app:app --reload --host 0.0.0.0 --port 8000

API Documentation (auto-generated):
    http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from tradingagents.conversation_manager import ConversationManager
from tradingagents.agent_pool import AgentPool, AgentRegistry
from tradingagents.logger_config import get_logger, enable_debug_mode, enable_production_mode

# Initialize logger
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GeminiTrader API",
    description="Multi-Agent Stock Analysis System with LangGraph",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state management
# In production, use Redis or database for multi-user support
sessions: Dict[str, Dict[str, Any]] = {}
default_session_id = "default"


# ============================================================================
# Request/Response Models
# ============================================================================

class AgentInfo(BaseModel):
    """Information about an available agent"""
    name: str
    description: str
    category: str
    requires_memory: bool


class InitPoolRequest(BaseModel):
    """Request to initialize agent pool"""
    selected_agents: List[str] = Field(
        ...,
        description="List of agent keys to initialize",
        example=["market_analyst", "fundamentals_analyst", "news_analyst"]
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session ID for multi-user support"
    )


class InitPoolResponse(BaseModel):
    """Response from pool initialization"""
    status: str
    message: str
    agent_count: int
    session_id: str
    agents: List[str]


class QueryRequest(BaseModel):
    """Request to analyze a stock"""
    query: str = Field(
        ...,
        description="User's question about the stock",
        example="What are your thoughts about investing in this stock?"
    )
    ticker: str = Field(
        ...,
        description="Stock ticker symbol",
        example="AAPL"
    )
    date: Optional[str] = Field(
        default=None,
        description="Analysis date in YYYY-MM-DD format",
        example="2024-01-15"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID to use specific agent pool"
    )


class QueryResponse(BaseModel):
    """Response from stock analysis"""
    status: str
    timestamp: str
    query: str
    ticker: str
    individual_responses: List[Dict[str, Any]]
    debate: List[Dict[str, Any]]
    final_verdict: Dict[str, Any]
    query_classification: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str
    active_sessions: int


class ErrorResponse(BaseModel):
    """Error response"""
    status: str = "error"
    message: str
    details: Optional[Dict[str, Any]] = None


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", tags=["General"])
async def root():
    """
    Root endpoint - API information
    """
    return {
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


@app.get("/api/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """
    Health check endpoint

    Returns system status and basic metrics.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(sessions)
    }


@app.get("/api/agents", response_model=Dict[str, AgentInfo], tags=["Agents"])
async def get_available_agents():
    """
    Get all available agents

    Returns a dictionary of all agents that can be initialized,
    including their names, descriptions, and capabilities.

    Example:
        {
            "market_analyst": {
                "name": "Market Analyst",
                "description": "Technical analysis expert",
                "category": "analysts",
                "requires_memory": false
            },
            ...
        }
    """
    try:
        agents = AgentRegistry.get_all_agents()
        logger.info(f"Fetched {len(agents)} available agents")
        return agents
    except Exception as e:
        logger.error(f"Error fetching agents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/initialize-pool", response_model=InitPoolResponse, tags=["Agents"])
async def initialize_pool(request: InitPoolRequest):
    """
    Initialize agent pool

    Creates a new agent pool with the selected agents. This must be called
    before sending queries.

    Args:
        request: InitPoolRequest with selected agent keys

    Returns:
        InitPoolResponse with initialization status

    Example request:
        {
            "selected_agents": ["market_analyst", "fundamentals_analyst"],
            "session_id": "user_123"
        }
    """
    session_id = request.session_id or default_session_id

    try:
        logger.info(f"Initializing pool for session {session_id} with agents: {request.selected_agents}")

        # Create new pool
        pool = AgentPool()

        # Add selected agents
        initialized_agents = []
        for agent_key in request.selected_agents:
            try:
                agent_info = AgentRegistry.get_agent(agent_key)
                pool.add_agent(agent_key, agent_info)
                initialized_agents.append(agent_key)
                logger.debug(f"Added agent: {agent_key}")
            except Exception as e:
                logger.warning(f"Failed to add agent {agent_key}: {e}")

        if not initialized_agents:
            raise HTTPException(
                status_code=400,
                detail="No valid agents could be initialized"
            )

        # Initialize all agents
        pool.initialize_all()

        # Create conversation manager
        conversation_manager = ConversationManager(pool)

        # Store in session
        sessions[session_id] = {
            "pool": pool,
            "conversation_manager": conversation_manager,
            "created_at": datetime.now().isoformat(),
            "agents": initialized_agents
        }

        logger.info(f"Pool initialized successfully for session {session_id}")

        return {
            "status": "success",
            "message": f"Successfully initialized {len(initialized_agents)} agents",
            "agent_count": len(initialized_agents),
            "session_id": session_id,
            "agents": initialized_agents
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initializing pool: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query", tags=["Analysis"])
async def query_agents(request: QueryRequest):
    """
    Send query to agents for stock analysis

    Executes the full multi-agent analysis workflow:
    1. Query classification (determine which agents needed)
    2. Ticker validation (fail-fast if invalid)
    3. Multi-agent analysis (parallel execution)
    4. Debate rounds (bull/bear, risk assessment)
    5. Final verdict generation

    Args:
        request: QueryRequest with query, ticker, and optional date

    Returns:
        Complete analysis including individual responses, debates, and final verdict

    Example request:
        {
            "query": "Should I invest in Apple?",
            "ticker": "AAPL",
            "date": "2024-01-15"
        }

    Note: This endpoint may take 10-60 seconds depending on the number of
    agents and complexity of the analysis.
    """
    session_id = request.session_id or default_session_id

    # Check if pool is initialized
    if session_id not in sessions:
        raise HTTPException(
            status_code=400,
            detail=f"Pool not initialized for session {session_id}. Call /api/initialize-pool first."
        )

    conversation_manager = sessions[session_id]["conversation_manager"]

    try:
        logger.info(f"Processing query for {request.ticker}: {request.query[:100]}")

        # Prepare context
        context = {
            "ticker": request.ticker.upper(),
            "date": request.date or datetime.now().strftime("%Y-%m-%d")
        }

        # Execute analysis
        result = conversation_manager.send_query_to_agents(request.query, context)

        # Check for errors in result
        if "error" in result:
            logger.warning(f"Analysis returned error: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])

        logger.info(f"Query completed successfully for {request.ticker}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history", tags=["Analysis"])
async def get_conversation_history(
    session_id: Optional[str] = None,
    limit: Optional[int] = 10
):
    """
    Get conversation history

    Returns the analysis history for a specific session.

    Args:
        session_id: Optional session ID (defaults to "default")
        limit: Maximum number of conversations to return (default: 10)

    Returns:
        List of previous analyses
    """
    session_id = session_id or default_session_id

    if session_id not in sessions:
        return []

    conversation_manager = sessions[session_id]["conversation_manager"]
    history = conversation_manager.get_conversation_history()

    # Return most recent first, limited
    return history[-limit:][::-1]


@app.delete("/api/history", tags=["Analysis"])
async def clear_history(session_id: Optional[str] = None):
    """
    Clear conversation history

    Deletes all conversation history for a session.

    Args:
        session_id: Optional session ID (defaults to "default")
    """
    session_id = session_id or default_session_id

    if session_id not in sessions:
        return {"status": "success", "message": "No history to clear"}

    conversation_manager = sessions[session_id]["conversation_manager"]
    conversation_manager.clear_history()

    logger.info(f"Cleared history for session {session_id}")

    return {"status": "success", "message": "History cleared"}


@app.delete("/api/session/{session_id}", tags=["Session"])
async def delete_session(session_id: str):
    """
    Delete a session

    Removes a session and cleans up resources.

    Args:
        session_id: Session ID to delete
    """
    if session_id in sessions:
        del sessions[session_id]
        logger.info(f"Deleted session: {session_id}")
        return {"status": "success", "message": f"Session {session_id} deleted"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@app.get("/api/sessions", tags=["Session"])
async def list_sessions():
    """
    List all active sessions

    Returns information about all active sessions.
    """
    return {
        "total": len(sessions),
        "sessions": {
            sid: {
                "created_at": data["created_at"],
                "agent_count": len(data["agents"]),
                "agents": data["agents"]
            }
            for sid, data in sessions.items()
        }
    }


@app.post("/api/debug/enable", tags=["Debug"])
async def enable_debug():
    """
    Enable debug logging

    Shows detailed logs including agent outputs and API calls.
    """
    enable_debug_mode()
    logger.info("Debug mode enabled")
    return {"status": "success", "message": "Debug logging enabled"}


@app.post("/api/debug/disable", tags=["Debug"])
async def disable_debug():
    """
    Disable debug logging

    Returns to production logging (INFO level only).
    """
    enable_production_mode()
    logger.info("Production mode enabled")
    return {"status": "success", "message": "Debug logging disabled"}


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Initialize on startup
    """
    logger.info("="*60)
    logger.info("GeminiTrader API Starting Up")
    logger.info("="*60)
    logger.info("FastAPI server initialized")
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("Health Check: http://localhost:8000/api/health")
    logger.info("="*60)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on shutdown
    """
    logger.info("GeminiTrader API shutting down")
    # Clean up sessions
    sessions.clear()


# ============================================================================
# Run with: uvicorn app:app --reload --host 0.0.0.0 --port 8000
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
