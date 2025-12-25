"""
Conversation Manager for Agent Pool
Handles multi-agent conversations, debates, and consensus building
"""
import json
from typing import Dict, List, Any
from datetime import datetime


class ConversationManager:
    """Manages conversations and debates between agents in the pool"""

    def __init__(self, agent_pool):
        self.agent_pool = agent_pool
        self.conversation_history = []

    def send_query_to_agents(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send a query to all agents in the pool and orchestrate a debate

        Args:
            query: User's question/query
            context: Optional context (ticker, date, etc.)

        Returns:
            Dictionary with individual responses, debate, and final verdict
        """
        if not self.agent_pool or not self.agent_pool.active_agents:
            return {
                "error": "No agents in pool. Please initialize agents first.",
                "individual_responses": [],
                "debate": [],
                "final_verdict": ""
            }

        # Phase 1: Get individual responses from each agent
        individual_responses = self._collect_individual_responses(query, context)

        # Phase 2: Orchestrate debate between agents
        debate_rounds = self._orchestrate_debate(query, individual_responses, context)

        # Phase 3: Generate final consensus verdict
        final_verdict = self._generate_final_verdict(query, individual_responses, debate_rounds)

        # Save to history
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "context": context,
            "individual_responses": individual_responses,
            "debate": debate_rounds,
            "final_verdict": final_verdict
        }
        self.conversation_history.append(conversation)

        return conversation

    def _collect_individual_responses(self, query: str, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get initial response from each agent in the pool"""
        responses = []

        for key, agent_data in self.agent_pool.active_agents.items():
            agent_info = agent_data["info"]
            agent_name = agent_info["name"]
            agent_category = agent_data["category"]

            # Create a specialized prompt for each agent type
            specialized_prompt = self._create_specialized_prompt(
                query, agent_name, agent_category, agent_info["description"]
            )

            # Simulate agent response (in real implementation, would call the actual agent)
            response = self._get_agent_response(
                agent_data, specialized_prompt, context
            )

            responses.append({
                "agent": agent_name,
                "category": agent_category,
                "perspective": agent_info["description"],
                "response": response
            })

        return responses

    def _create_specialized_prompt(self, query: str, agent_name: str,
                                   category: str, description: str) -> str:
        """Create a specialized prompt for each agent type"""

        prompt = f"""You are {agent_name}, a specialized {description}.

User Query: {query}

Please provide your analysis from your specific perspective:
- Focus on your area of expertise ({description})
- Be concise but thorough
- Highlight key insights from your perspective
- State your recommendation clearly

Your response:"""

        return prompt

    def _get_agent_response(self, agent_data: Dict, prompt: str,
                           context: Dict[str, Any]) -> str:
        """
        Get response from a specific agent

        Note: This is a simplified version. In production, you would:
        1. Create a proper state object
        2. Call the agent's node function
        3. Parse the agent's response

        For now, we'll create a mock response based on agent type
        """
        agent_name = agent_data["info"]["name"]
        category = agent_data["category"]

        # Mock responses based on agent type
        # In production, replace with actual LLM calls through the agent
        if category == "analysts":
            if "Market" in agent_name:
                return self._mock_market_analyst_response(context)
            elif "Fundamentals" in agent_name:
                return self._mock_fundamentals_analyst_response(context)
            elif "News" in agent_name:
                return self._mock_news_analyst_response(context)
            elif "Social" in agent_name:
                return self._mock_social_analyst_response(context)
        elif category == "researchers":
            if "Bull" in agent_name:
                return self._mock_bull_researcher_response(context)
            elif "Bear" in agent_name:
                return self._mock_bear_researcher_response(context)
        elif category == "risk_analysts":
            if "Risky" in agent_name:
                return self._mock_risky_analyst_response(context)
            elif "Safe" in agent_name:
                return self._mock_safe_analyst_response(context)
            elif "Neutral" in agent_name:
                return self._mock_neutral_analyst_response(context)

        return f"As {agent_name}, I'm analyzing this from my perspective..."

    # Mock response generators (replace with actual agent calls)
    def _mock_market_analyst_response(self, context):
        return """From a technical analysis perspective:
- Price action shows consolidation above key support levels
- RSI indicates neutral momentum (around 50)
- Volume patterns suggest institutional accumulation
- Short-term outlook: BULLISH
Recommendation: Consider entry on pullback to support zone"""

    def _mock_fundamentals_analyst_response(self, context):
        return """From a fundamental analysis perspective:
- P/E ratio is reasonable compared to sector average
- Revenue growth remains strong at 12% YoY
- Profit margins expanding due to operational efficiency
- Balance sheet is solid with low debt-to-equity ratio
Recommendation: STRONG BUY for long-term investors"""

    def _mock_news_analyst_response(self, context):
        return """From a news and sentiment perspective:
- Recent earnings report exceeded expectations
- Positive coverage from major financial outlets
- Management guidance revised upward for next quarter
- No major regulatory or legal concerns
Recommendation: POSITIVE sentiment, good entry point"""

    def _mock_social_analyst_response(self, context):
        return """From a social media sentiment perspective:
- Retail investor sentiment is moderately positive (65% bullish)
- Discussion volume increased 40% over past week
- Key influencers are highlighting upcoming catalysts
- Options flow shows bullish positioning
Recommendation: Retail sentiment supports upward move"""

    def _mock_bull_researcher_response(self, context):
        return """Building the bullish case:
- Multiple positive catalysts aligning (earnings, product launch, sector rotation)
- Technical breakout from multi-month consolidation
- Strong institutional buying pressure
- Seasonal trends favor this sector
BULL CASE: Strong potential for 10-15% upside in coming weeks"""

    def _mock_bear_researcher_response(self, context):
        return """Building the bearish case:
- Overall market showing signs of topping
- Valuation stretched compared to historical averages
- Potential headwinds from macro factors (rates, inflation)
- Recent rally may be overdone, pullback likely
BEAR CASE: Risk of 5-10% correction, would wait for better entry"""

    def _mock_risky_analyst_response(self, context):
        return """From an aggressive risk perspective:
- Setup favors taking larger position size
- Risk/reward ratio is attractive (3:1)
- Momentum is building, don't miss the move
- Use stops below support to manage downside
AGGRESSIVE VIEW: Take full position, ride the momentum"""

    def _mock_safe_analyst_response(self, context):
        return """From a conservative risk perspective:
- Start with smaller position, scale in gradually
- Wait for confirmation of breakout/breakdown
- Preserve capital is priority
- Market conditions warrant caution
CONSERVATIVE VIEW: Small position, wait for better clarity"""

    def _mock_neutral_analyst_response(self, context):
        return """From a balanced risk perspective:
- Reasonable position size based on conviction level
- Diversify entry points over time (DCA approach)
- Balance upside potential with downside protection
- Adjust size based on market conditions
BALANCED VIEW: Moderate position, flexible approach"""

    def _orchestrate_debate(self, query: str, responses: List[Dict],
                           context: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Orchestrate a debate between agents about their different viewpoints

        Returns list of debate rounds with each agent's contribution
        """
        debate_rounds = []

        # Round 1: Agents present conflicting viewpoints
        debate_rounds.append({
            "round": 1,
            "topic": "Initial Position Statements",
            "exchanges": self._generate_position_statements(responses)
        })

        # Round 2: Agents challenge each other's assumptions
        debate_rounds.append({
            "round": 2,
            "topic": "Challenging Assumptions",
            "exchanges": self._generate_challenges(responses)
        })

        # Round 3: Finding common ground and disagreements
        debate_rounds.append({
            "round": 3,
            "topic": "Consensus Building",
            "exchanges": self._generate_consensus(responses)
        })

        return debate_rounds

    def _generate_position_statements(self, responses: List[Dict]) -> List[Dict[str, str]]:
        """Generate initial position statements for debate"""
        exchanges = []

        # Group by bullish vs bearish sentiment
        bullish_agents = []
        bearish_agents = []
        neutral_agents = []

        for resp in responses:
            response_text = resp["response"].upper()
            if "BULLISH" in response_text or "BUY" in response_text or "POSITIVE" in response_text:
                bullish_agents.append(resp["agent"])
            elif "BEARISH" in response_text or "SELL" in response_text or "NEGATIVE" in response_text:
                bearish_agents.append(resp["agent"])
            else:
                neutral_agents.append(resp["agent"])

        # Generate position statement
        if bullish_agents:
            exchanges.append({
                "speaker": "Bullish Coalition",
                "agents": bullish_agents,
                "statement": f"We ({', '.join(bullish_agents)}) see strong positive indicators suggesting this is a good opportunity. The fundamentals, technicals, and sentiment all align favorably."
            })

        if bearish_agents:
            exchanges.append({
                "speaker": "Bearish Coalition",
                "agents": bearish_agents,
                "statement": f"However, we ({', '.join(bearish_agents)}) urge caution. There are significant risks and potential headwinds that shouldn't be ignored."
            })

        if neutral_agents:
            exchanges.append({
                "speaker": "Balanced Perspective",
                "agents": neutral_agents,
                "statement": f"We ({', '.join(neutral_agents)}) see merit in both viewpoints and suggest a measured approach that considers both opportunities and risks."
            })

        return exchanges

    def _generate_challenges(self, responses: List[Dict]) -> List[Dict[str, str]]:
        """Generate challenges between different viewpoints"""
        return [
            {
                "speaker": "Bear Researcher",
                "statement": "While the bullish indicators are noted, we must consider that current valuations may already price in the positive news. What if the market is ahead of itself?"
            },
            {
                "speaker": "Market Analyst",
                "statement": "The technical setup suggests strong support at current levels. Even if there's a pullback, risk is well-defined, making this a favorable risk/reward setup."
            },
            {
                "speaker": "Risk Analyst",
                "statement": "Position sizing is crucial here. We need to balance conviction with prudent risk management. Not all-in, not sitting out completely."
            }
        ]

    def _generate_consensus(self, responses: List[Dict]) -> List[Dict[str, str]]:
        """Generate consensus-building discussion"""
        return [
            {
                "speaker": "Research Manager",
                "statement": "After hearing all perspectives, here's what we agree on: The opportunity exists, but risk management is key. We should have a position, but size it appropriately."
            },
            {
                "speaker": "Group Consensus",
                "statement": "Common ground: Take a position, but with defined risk parameters. Start with moderate size, scale based on price action. Set clear stop-loss levels. Monitor news and technical levels closely."
            }
        ]

    def _generate_final_verdict(self, query: str, responses: List[Dict],
                                debate: List[Dict]) -> Dict[str, Any]:
        """Generate final consensus verdict with all perspectives"""

        # Count sentiment
        bullish_count = sum(1 for r in responses if any(word in r["response"].upper()
                           for word in ["BULLISH", "BUY", "POSITIVE", "STRONG"]))
        bearish_count = sum(1 for r in responses if any(word in r["response"].upper()
                           for word in ["BEARISH", "SELL", "NEGATIVE", "CAUTION"]))

        total = len(responses)
        bullish_pct = (bullish_count / total * 100) if total > 0 else 0

        # Determine overall recommendation
        if bullish_pct >= 70:
            overall = "STRONG BUY"
            confidence = "High"
        elif bullish_pct >= 50:
            overall = "BUY"
            confidence = "Moderate"
        elif bullish_pct >= 30:
            overall = "HOLD / WAIT"
            confidence = "Low"
        else:
            overall = "AVOID / SELL"
            confidence = "Moderate"

        verdict = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "overall_recommendation": overall,
            "confidence_level": confidence,
            "sentiment_breakdown": {
                "bullish": bullish_count,
                "bearish": bearish_count,
                "neutral": total - bullish_count - bearish_count,
                "bullish_percentage": round(bullish_pct, 1)
            },
            "key_points": [
                "Multiple perspectives considered from technical, fundamental, and sentiment analysis",
                f"{bullish_count} out of {total} agents recommend positive action",
                "Risk management emphasized by all agents",
                "Timing considerations discussed thoroughly"
            ],
            "action_items": [
                "Define position size based on risk tolerance",
                "Set stop-loss levels below key support",
                "Monitor upcoming catalysts (earnings, news)",
                "Review position after initial entry"
            ],
            "summary": self._generate_summary_text(overall, bullish_pct, responses)
        }

        return verdict

    def _generate_summary_text(self, recommendation: str, bullish_pct: float,
                               responses: List[Dict]) -> str:
        """Generate human-readable summary"""

        summary = f"""
FINAL CONSENSUS: {recommendation}

After comprehensive analysis from {len(responses)} specialized agents and thorough debate,
here's our unified recommendation:

{bullish_pct:.0f}% of agents see this as a favorable opportunity. The consensus view is that
there is merit to taking a position, but with appropriate risk management.

KEY CONSIDERATIONS:
• Technical indicators suggest defined risk/reward setup
• Fundamentals support the investment thesis
• Sentiment is generally positive but not euphoric
• Timing appears reasonable given upcoming catalysts

RECOMMENDED ACTION:
Take a position sized appropriately to your risk tolerance. Use a scaled entry approach
if possible. Set stop-losses below key technical support levels. Monitor the position
actively, especially around earnings or major news events.

This recommendation reflects the collective wisdom of our agent pool, balancing
optimism with prudent risk management.
"""

        return summary.strip()

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Return all conversation history"""
        return self.conversation_history

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
