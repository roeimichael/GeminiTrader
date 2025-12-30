"""
GeminiTrader FastAPI Backend

Run with: uvicorn app:app --reload --host 0.0.0.0 --port 8000
API Documentation: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from contextlib import asynccontextmanager
import uuid

from tradingagents.conversation_manager import ConversationManager
from tradingagents.agent_pool import AgentPool, AgentRegistry
from tradingagents.logger_config import get_logger, enable_debug_mode, enable_production_mode

logger = get_logger(__name__)

sessions: Dict[str, dict] = {}
default_session_id = "default"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("="*60)
    logger.info("GeminiTrader API Starting Up")
    logger.info("="*60)
    logger.info("FastAPI server initialized")
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("Health Check: http://localhost:8000/api/health")
    logger.info("="*60)
    yield
    # Shutdown
    logger.info("GeminiTrader API shutting down")
    sessions.clear()

app = FastAPI(
    title="GeminiTrader API",
    description="Multi-Agent Stock Analysis System with LangGraph",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        json_schema_extra={"example": ["market_analyst", "fundamentals_analyst", "news_analyst"]}
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
        json_schema_extra={"example": "What are your thoughts about investing in this stock?"}
    )
    ticker: str = Field(
        ...,
        description="Stock ticker symbol",
        json_schema_extra={"example": "AAPL"}
    )
    date: Optional[str] = Field(
        default=None,
        description="Analysis date in YYYY-MM-DD format",
        json_schema_extra={"example": "2024-01-15"}
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
    individual_responses: List[dict]
    debate: List[dict]
    final_verdict: dict
    query_classification: dict


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
    details: Optional[dict] = None

@app.get("/", tags=["General"])
async def root():
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
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(sessions)
    }


@app.get("/api/agents", tags=["Agents"])
async def get_available_agents():
    """Get all available agents with their descriptions and capabilities"""
    try:
        agents_dict = AgentRegistry.get_all_agents()

        serializable_agents = {}
        for category, agents in agents_dict.items():
            serializable_agents[category] = {}
            for agent_id, agent_info in agents.items():
                serializable_agents[category][agent_id] = {
                    "name": agent_info["name"],
                    "description": agent_info["description"],
                    "requires_memory": agent_info["requires_memory"]
                }

        logger.info(f"Fetched {sum(len(agents) for agents in serializable_agents.values())} available agents")
        return serializable_agents
    except Exception as e:
        logger.error(f"Error fetching agents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/initialize-pool", response_model=InitPoolResponse, tags=["Agents"])
async def initialize_pool(request: InitPoolRequest):
    """Initialize agent pool with selected agents"""
    session_id = request.session_id or default_session_id

    try:
        logger.info(f"Initializing pool for session {session_id} with agents: {request.selected_agents}")

        pool = AgentPool()

        agent_mapping = {
            "market_analyst": ("analysts", "market"),
            "fundamentals_analyst": ("analysts", "fundamentals"),
            "news_analyst": ("analysts", "news"),
            "social_analyst": ("analysts", "social"),
            "bull_researcher": ("researchers", "bull"),
            "bear_researcher": ("researchers", "bear"),
            "research_manager": ("managers", "research"),
            "risk_manager": ("managers", "risk"),
            "risky_analyst": ("risk_analysts", "risky"),
            "safe_analyst": ("risk_analysts", "safe"),
            "neutral_analyst": ("risk_analysts", "neutral"),
            "trader": ("trader", "trader"),
        }

        initialized_agents = []
        for agent_key in request.selected_agents:
            try:
                if agent_key not in agent_mapping:
                    logger.warning(f"Unknown agent key: {agent_key}")
                    continue

                category, agent_id = agent_mapping[agent_key]
                pool.add_agent(category, agent_id)
                initialized_agents.append(agent_key)
                logger.debug(f"Added agent: {agent_key} ({category}/{agent_id})")
            except Exception as e:
                logger.warning(f"Failed to add agent {agent_key}: {e}")

        if not initialized_agents:
            raise HTTPException(
                status_code=400,
                detail="No valid agents could be initialized"
            )

        conversation_manager = ConversationManager(pool)

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
    """Execute multi-agent stock analysis workflow"""
    session_id = request.session_id or default_session_id

    if session_id not in sessions:
        raise HTTPException(
            status_code=400,
            detail=f"Pool not initialized for session {session_id}. Call /api/initialize-pool first."
        )

    conversation_manager = sessions[session_id]["conversation_manager"]

    try:
        logger.info(f"Processing query for {request.ticker}: {request.query[:100]}")

        context = {
            "ticker": request.ticker.upper(),
            "date": request.date or datetime.now().strftime("%Y-%m-%d")
        }

        result = conversation_manager.send_query_to_agents(request.query, context)

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
    """Get conversation history for a session"""
    session_id = session_id or default_session_id

    if session_id not in sessions:
        return []

    conversation_manager = sessions[session_id]["conversation_manager"]
    history = conversation_manager.get_conversation_history()

    return history[-limit:][::-1]


@app.delete("/api/history", tags=["Analysis"])
async def clear_history(session_id: Optional[str] = None):
    """Clear conversation history for a session"""
    session_id = session_id or default_session_id

    if session_id not in sessions:
        return {"status": "success", "message": "No history to clear"}

    conversation_manager = sessions[session_id]["conversation_manager"]
    conversation_manager.clear_history()

    logger.info(f"Cleared history for session {session_id}")

    return {"status": "success", "message": "History cleared"}


@app.delete("/api/session/{session_id}", tags=["Session"])
async def delete_session(session_id: str):
    """Delete a session and clean up resources"""
    if session_id in sessions:
        del sessions[session_id]
        logger.info(f"Deleted session: {session_id}")
        return {"status": "success", "message": f"Session {session_id} deleted"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@app.get("/api/sessions", tags=["Session"])
async def list_sessions():
    """List all active sessions"""
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
    """Enable debug logging"""
    enable_debug_mode()
    logger.info("Debug mode enabled")
    return {"status": "success", "message": "Debug logging enabled"}


@app.post("/api/debug/disable", tags=["Debug"])
async def disable_debug():
    """Disable debug logging"""
    enable_production_mode()
    logger.info("Production mode enabled")
    return {"status": "success", "message": "Debug logging disabled"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


