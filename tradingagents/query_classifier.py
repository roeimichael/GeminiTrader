"""
Query Classifier / Router Node for Intelligent Agent Selection

This module implements a "smart router" that determines which agents are needed
based on the user's query. This prevents running all 12 agents for simple questions.

Architecture Philosophy:
- Simple question ("What's the P/E ratio?") → Only Fundamentals Analyst
- Medium question ("Technical outlook?") → Only Market Analyst
- Complex question ("Full analysis") → All agents
- News-focused → News + Social analysts

This dramatically reduces:
- LLM API costs (fewer agents = fewer LLM calls)
- Latency (faster responses for simple queries)
- Data API costs (only fetch what's needed)
"""

from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from tradingagents.config import DEFAULT_CONFIG


class QueryClassifier:
    """
    Lightweight classifier that routes queries to appropriate agents

    Uses gemini-2.0-flash-exp (fast, cheap) to analyze query and determine
    which specialized agents are needed.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize query classifier with lightweight LLM

        Args:
            config: Configuration dictionary (uses DEFAULT_CONFIG if not provided)
        """
        self.config = config or DEFAULT_CONFIG

        # Use the quick/flash model for classification (speed is key)
        self.llm = ChatGoogleGenerativeAI(
            model=self.config.get("quick_think_llm", "gemini-2.0-flash-exp"),
            temperature=0.0  # Deterministic routing
        )

        # Define available agent categories and their capabilities
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

    def classify_query(self, query: str, ticker: str = None) -> Dict[str, Any]:
        """
        Classify user query and determine which agents are needed

        Args:
            query: User's question/query
            ticker: Optional ticker symbol for context

        Returns:
            Dictionary with:
            - selected_agents: List of agent categories needed
            - reasoning: Why these agents were selected
            - complexity: "simple", "medium", or "complex"
            - estimated_cost: Rough cost estimate
        """

        # Quick keyword-based pre-filtering (fast path)
        keyword_matches = self._keyword_matching(query)

        # If query is very simple and matches clear keywords, use fast path
        if len(keyword_matches) == 1 and self._is_simple_query(query):
            return {
                "selected_agents": keyword_matches,
                "reasoning": f"Simple query matched '{keyword_matches[0]}' category via keyword analysis",
                "complexity": "simple",
                "estimated_cost": "low",
                "method": "keyword_matching"
            }

        # For complex or ambiguous queries, use LLM classification
        return self._llm_classification(query, ticker, keyword_matches)

    def _keyword_matching(self, query: str) -> List[str]:
        """
        Fast keyword-based matching as first pass

        Args:
            query: User query

        Returns:
            List of agent categories that match keywords
        """
        query_lower = query.lower()
        matches = []

        for agent, info in self.agent_capabilities.items():
            if any(keyword in query_lower for keyword in info["keywords"]):
                matches.append(agent)

        return matches

    def _is_simple_query(self, query: str) -> bool:
        """
        Determine if query is simple (single question, no complexity)

        Args:
            query: User query

        Returns:
            True if query appears simple
        """
        # Simple heuristics
        query_lower = query.lower()

        # Single question mark = likely simple
        if query.count("?") == 1:
            # Short query = simple
            if len(query.split()) < 15:
                return True

        # Keywords indicating complexity
        complex_indicators = ["full analysis", "complete", "comprehensive", "all", "everything",
                            "detailed", "in-depth", "thorough"]

        if any(indicator in query_lower for indicator in complex_indicators):
            return False

        return False  # Default to LLM classification for safety

    def _llm_classification(self, query: str, ticker: str,
                           keyword_matches: List[str]) -> Dict[str, Any]:
        """
        Use LLM to classify query when keyword matching is insufficient

        Args:
            query: User query
            ticker: Ticker symbol
            keyword_matches: Results from keyword matching

        Returns:
            Classification result dictionary
        """

        # Build prompt for LLM
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
            # Call LLM
            response = self.llm.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)

            # Parse response
            return self._parse_llm_response(response_text)

        except Exception as e:
            # Fallback to keyword matches or all agents
            print(f"WARNING: LLM classification failed: {e}")
            print(f"Falling back to keyword matches: {keyword_matches}")

            if keyword_matches:
                return {
                    "selected_agents": keyword_matches,
                    "reasoning": f"LLM classification failed, using keyword matches",
                    "complexity": "medium",
                    "estimated_cost": "medium",
                    "method": "fallback_keyword"
                }
            else:
                # Ultimate fallback: use all agents
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

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM classification response

        Args:
            response: Raw LLM response text

        Returns:
            Parsed classification dictionary
        """
        lines = response.strip().split("\n")

        agents = []
        reasoning = ""
        complexity = "medium"

        for line in lines:
            line = line.strip()
            if line.startswith("AGENTS:"):
                agents_str = line.replace("AGENTS:", "").strip()
                # Parse comma-separated list
                agents = [a.strip() for a in agents_str.split(",")]
                # Validate agents
                valid_agents = ["market", "fundamentals", "news", "social"]
                agents = [a for a in agents if a in valid_agents]
            elif line.startswith("REASONING:"):
                reasoning = line.replace("REASONING:", "").strip()
            elif line.startswith("COMPLEXITY:"):
                complexity = line.replace("COMPLEXITY:", "").strip().lower()

        # Ensure at least one agent is selected
        if not agents:
            print("WARNING: No valid agents parsed from LLM response, using all agents")
            agents = ["market", "fundamentals", "news", "social"]

        # Estimate cost based on number of agents
        cost_map = {1: "low", 2: "medium", 3: "high", 4: "high"}
        estimated_cost = cost_map.get(len(agents), "medium")

        return {
            "selected_agents": agents,
            "reasoning": reasoning or "Classified via LLM analysis",
            "complexity": complexity,
            "estimated_cost": estimated_cost,
            "method": "llm_classification"
        }

    def print_classification(self, classification: Dict[str, Any], query: str):
        """
        Pretty-print classification results

        Args:
            classification: Classification result dictionary
            query: Original query
        """
        print("\n" + "="*60)
        print("QUERY CLASSIFICATION")
        print("="*60)
        print(f"Query: {query}")
        print(f"Selected Agents: {', '.join(classification['selected_agents'])}")
        print(f"Reasoning: {classification['reasoning']}")
        print(f"Complexity: {classification['complexity']}")
        print(f"Estimated Cost: {classification['estimated_cost']}")
        print(f"Method: {classification['method']}")
        print("="*60 + "\n")
