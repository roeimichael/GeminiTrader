"""
Query Classifier for Intelligent Agent Selection
"""

from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from tradingagents.config import DEFAULT_CONFIG
from tradingagents.logger_config import get_logger

logger = get_logger(__name__)


class QueryClassifier:
    """Lightweight classifier that routes queries to appropriate agents"""

    def __init__(self, config: Dict = None):
        self.config = config or DEFAULT_CONFIG

        self.llm = ChatGoogleGenerativeAI(
            model=self.config.get("quick_think_llm", "gemini-1.5-flash"),
            temperature=0.0
        )

        self.agent_capabilities = {
            "market": {
                "description": "Technical analysis, price charts, indicators (RSI, MACD, etc.)",
                "keywords": ["technical", "price", "chart", "indicator", "rsi", "macd", "support",
                           "resistance", "trend", "momentum", "volume", "moving average"]
            },
            "fundamentals": {
                "description": "Financial statements, P/E ratio, revenue, earnings, balance sheet",
                "keywords": ["fundamental", "p/e", "pe ratio", "earnings", "revenue", "profit",
                           "balance sheet", "cash flow", "income statement", "eps", "valuation",
                           "financial", "ratio", "debt", "assets"]
            },
            "news": {
                "description": "Recent news, events, announcements, company updates",
                "keywords": ["news", "announcement", "event", "update", "press release", "article",
                           "headline", "story", "report", "development"]
            },
            "social": {
                "description": "Social media sentiment, public perception, retail investor sentiment",
                "keywords": ["sentiment", "social", "twitter", "reddit", "forum", "public opinion",
                           "retail investor", "buzz", "trending", "community"]
            }
        }

    def classify_query(self, query: str, ticker: str = None) -> dict:
        """Classify user query and determine which agents are needed"""
        keyword_matches = self._keyword_matching(query)

        if len(keyword_matches) == 1 and self._is_simple_query(query):
            return {
                "selected_agents": keyword_matches,
                "reasoning": f"Simple query matched '{keyword_matches[0]}' category via keyword analysis",
                "complexity": "simple",
                "estimated_cost": "low",
                "method": "keyword_matching"
            }

        return self._llm_classification(query, ticker, keyword_matches)

    def _keyword_matching(self, query: str) -> List[str]:
        """Fast keyword-based matching as first pass"""
        query_lower = query.lower()
        matches = []

        for agent, info in self.agent_capabilities.items():
            if any(keyword in query_lower for keyword in info["keywords"]):
                matches.append(agent)

        return matches

    def _is_simple_query(self, query: str) -> bool:
        """Determine if query is simple (single question, no complexity)"""
        query_lower = query.lower()

        if query.count("?") == 1:
            if len(query.split()) < 15:
                return True

        complex_indicators = ["full analysis", "complete", "comprehensive", "all", "everything",
                            "detailed", "in-depth", "thorough"]

        if any(indicator in query_lower for indicator in complex_indicators):
            return False

        return False

    def _llm_classification(self, query: str, ticker: str,
                           keyword_matches: List[str]) -> dict:
        """Use LLM to classify query when keyword matching is insufficient"""
        prompt = f"""You are a query router for a multi-agent stock analysis system.

User Query: "{query}"
{f"Ticker: {ticker}" if ticker else ""}

Available Agent Categories:
{self._format_agent_capabilities()}

Keyword Pre-Analysis Suggests: {keyword_matches if keyword_matches else "None"}

Your Task:
1. Determine which agent categories are NECESSARY to answer this query
2. Be MINIMAL - only include agents that are truly needed
3. Consider the specific question being asked

Classification Rules:
- Simple factual questions ("What's the P/E ratio?") → 1 agent only
- Specific analysis ("Technical outlook?") → 1-2 agents
- "Full analysis" or "comprehensive" → All agents
- News/events focus → news + social
- Trading decision → market + fundamentals + news

Respond in this EXACT format:
AGENTS: [comma-separated list of: market, fundamentals, news, social]
REASONING: [one sentence explanation]
COMPLEXITY: [simple/medium/complex]

Example 1:
User: "What's the current P/E ratio for AAPL?"
AGENTS: fundamentals
REASONING: Simple factual question about valuation metric
COMPLEXITY: simple

Example 2:
User: "Should I buy MSFT? Give me a full analysis."
AGENTS: market, fundamentals, news, social
REASONING: Comprehensive analysis requested requiring all perspectives
COMPLEXITY: complex

Now classify the user's query:"""

        try:
            response = self.llm.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            return self._parse_llm_response(response_text)

        except Exception as e:
            logger.warning(f"LLM classification failed: {e}")
            logger.info(f"Falling back to keyword matches: {keyword_matches}")

            if keyword_matches:
                return {
                    "selected_agents": keyword_matches,
                    "reasoning": f"LLM classification failed, using keyword matches",
                    "complexity": "medium",
                    "estimated_cost": "medium",
                    "method": "fallback_keyword"
                }
            else:
                return {
                    "selected_agents": ["market", "fundamentals", "news", "social"],
                    "reasoning": "Classification uncertain, using all agents for safety",
                    "complexity": "complex",
                    "estimated_cost": "high",
                    "method": "fallback_all"
                }

    def _format_agent_capabilities(self) -> str:
        """Format agent capabilities for prompt"""
        lines = []
        for agent, info in self.agent_capabilities.items():
            lines.append(f"- {agent}: {info['description']}")
        return "\n".join(lines)

    def _parse_llm_response(self, response: str) -> dict:
        """Parse LLM classification response"""
        lines = response.strip().split("\n")

        agents = []
        reasoning = ""
        complexity = "medium"

        for line in lines:
            line = line.strip()
            if line.startswith("AGENTS:"):
                agents_str = line.replace("AGENTS:", "").strip()
                agents = [a.strip() for a in agents_str.split(",")]
                valid_agents = ["market", "fundamentals", "news", "social"]
                agents = [a for a in agents if a in valid_agents]
            elif line.startswith("REASONING:"):
                reasoning = line.replace("REASONING:", "").strip()
            elif line.startswith("COMPLEXITY:"):
                complexity = line.replace("COMPLEXITY:", "").strip().lower()

        if not agents:
            logger.warning("No valid agents parsed from LLM response, using all agents")
            agents = ["market", "fundamentals", "news", "social"]

        cost_map = {1: "low", 2: "medium", 3: "high", 4: "high"}
        estimated_cost = cost_map.get(len(agents), "medium")

        return {
            "selected_agents": agents,
            "reasoning": reasoning or "Classified via LLM analysis",
            "complexity": complexity,
            "estimated_cost": estimated_cost,
            "method": "llm_classification"
        }

    def print_classification(self, classification: dict, query: str):
        """Log classification results for debugging"""
        logger.info("="*60)
        logger.info("QUERY CLASSIFICATION")
        logger.info("="*60)
        logger.info(f"Query: {query}")
        logger.info(f"Selected Agents: {', '.join(classification['selected_agents'])}")
        logger.info(f"Reasoning: {classification['reasoning']}")
        logger.info(f"Complexity: {classification['complexity']}")
        logger.info(f"Estimated Cost: {classification['estimated_cost']}")
        logger.info(f"Method: {classification['method']}")
        logger.info("="*60)
