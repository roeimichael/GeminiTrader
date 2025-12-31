import os
from typing import Dict, List

from tradingagents.agents.analysts.market_analyst import create_market_analyst
from tradingagents.agents.analysts.fundamentals_analyst import create_fundamentals_analyst
from tradingagents.agents.analysts.news_analyst import create_news_analyst
from tradingagents.agents.analysts.social_media_analyst import create_social_media_analyst
from tradingagents.agents.researchers.bull_researcher import create_bull_researcher
from tradingagents.agents.researchers.bear_researcher import create_bear_researcher
from tradingagents.agents.managers.research_manager import create_research_manager
from tradingagents.agents.managers.risk_manager import create_risk_manager
from tradingagents.agents.risk_mgmt.aggresive_debator import create_risky_debator
from tradingagents.agents.risk_mgmt.conservative_debator import create_safe_debator
from tradingagents.agents.risk_mgmt.neutral_debator import create_neutral_debator
from tradingagents.agents.trader.trader import create_trader
from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.llm_utils import get_quick_thinking_llm, get_deep_thinking_llm
from tradingagents.config import DEFAULT_CONFIG

class AgentRegistry:
    """Registry of all available TradingAgents"""

    AGENT_TYPES = {
        "analysts": {
            "market": {
                "name": "Market Analyst",
                "description": "Technical indicators and market trends expert",
                "factory": create_market_analyst,
                "requires_memory": False
            },
            "fundamentals": {
                "name": "Fundamentals Analyst",
                "description": "Financial statements and company fundamentals expert",
                "factory": create_fundamentals_analyst,
                "requires_memory": False
            },
            "news": {
                "name": "News Analyst",
                "description": "News and current events expert",
                "factory": create_news_analyst,
                "requires_memory": False
            },
            "social": {
                "name": "Social Media Analyst",
                "description": "Social sentiment and public perception expert",
                "factory": create_social_media_analyst,
                "requires_memory": False
            }
        },
        "researchers": {
            "bull": {
                "name": "Bull Researcher",
                "description": "Builds bullish investment cases",
                "factory": create_bull_researcher,
                "requires_memory": True
            },
            "bear": {
                "name": "Bear Researcher",
                "description": "Builds bearish counter-arguments",
                "factory": create_bear_researcher,
                "requires_memory": True
            }
        },
        "managers": {
            "research": {
                "name": "Research Manager",
                "description": "Makes final investment decisions",
                "factory": create_research_manager,
                "requires_memory": True
            },
            "risk": {
                "name": "Risk Manager",
                "description": "Final risk assessment and recommendation",
                "factory": create_risk_manager,
                "requires_memory": True
            }
        },
        "risk_analysts": {
            "risky": {
                "name": "Risky Analyst",
                "description": "Argues for aggressive positioning",
                "factory": create_risky_debator,
                "requires_memory": False
            },
            "safe": {
                "name": "Safe Analyst",
                "description": "Argues for conservative risk management",
                "factory": create_safe_debator,
                "requires_memory": False
            },
            "neutral": {
                "name": "Neutral Analyst",
                "description": "Provides balanced perspective",
                "factory": create_neutral_debator,
                "requires_memory": False
            }
        },
        "trader": {
            "trader": {
                "name": "Trader",
                "description": "Creates executable trade plans",
                "factory": create_trader,
                "requires_memory": True
            }
        }
    }

    @classmethod
    def get_all_agents(cls) -> dict:
        """Get all available agents organized by category"""
        return cls.AGENT_TYPES

    @classmethod
    def get_agent_info(cls, category: str, agent_id: str) -> dict:
        """Get information about a specific agent"""
        return cls.AGENT_TYPES.get(category, {}).get(agent_id, {})

    @classmethod
    def list_all_agents(cls) -> List[dict]:
        """Get flat list of all agents with their category"""
        agents = []
        for category, agents_dict in cls.AGENT_TYPES.items():
            for agent_id, info in agents_dict.items():
                agents.append({
                    "category": category,
                    "id": agent_id,
                    **info
                })
        return agents


class AgentPool:
    """Pool of initialized agents ready for use"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.llm_quick = None
        self.llm_deep = None
        self.memories = {}
        self.active_agents = {}
        self._initialize_llms()

    def _initialize_llms(self):
        """Initialize Gemini LLM instances with automatic fallback"""
        # Merge user config with defaults
        config = {**DEFAULT_CONFIG, **self.config}

        # Use safe factory functions with model fallback
        self.llm_quick = get_quick_thinking_llm(config)
        self.llm_deep = get_deep_thinking_llm(config)

    def _get_or_create_memory(self, memory_name: str):
        """Get or create a memory instance"""
        if memory_name not in self.memories:
            self.memories[memory_name] = FinancialSituationMemory(
                memory_name,
                self.config
            )
        return self.memories[memory_name]

    def add_agent(self, category: str, agent_id: str):
        """Add an agent to the active pool"""
        agent_info = AgentRegistry.get_agent_info(category, agent_id)

        if not agent_info:
            raise ValueError(f"Unknown agent: {category}/{agent_id}")

        factory = agent_info["factory"]
        requires_memory = agent_info["requires_memory"]

        if requires_memory:
            memory = self._get_or_create_memory(f"{agent_id}_memory")
            if category in ["managers", "trader"]:
                agent = factory(self.llm_deep, memory)
            else:
                agent = factory(self.llm_quick, memory)
        else:
            agent = factory(self.llm_quick)

        key = f"{category}:{agent_id}"
        self.active_agents[key] = {
            "agent": agent,
            "info": agent_info,
            "category": category,
            "id": agent_id
        }

        return self

    def remove_agent(self, category: str, agent_id: str):
        """Remove an agent from the active pool"""
        key = f"{category}:{agent_id}"
        if key in self.active_agents:
            del self.active_agents[key]
        return self

    def get_active_agents(self) -> List[dict]:
        """Get list of all active agents"""
        return [
            {
                "category": data["category"],
                "id": data["id"],
                "name": data["info"]["name"],
                "description": data["info"]["description"]
            }
            for data in self.active_agents.values()
        ]

    def get_agent(self, category: str, agent_id: str):
        """Get a specific active agent"""
        key = f"{category}:{agent_id}"
        return self.active_agents.get(key, {}).get("agent")

    def clear(self):
        """Clear all active agents"""
        self.active_agents = {}
        return self
