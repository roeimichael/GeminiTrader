"""
Conversation Manager for Agent Pool
"""
import json
from typing import Dict, List, Optional
from datetime import datetime

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.config import DEFAULT_CONFIG
from tradingagents.dataflows.validation import validate_ticker_data, TickerValidationError
from tradingagents.query_classifier import QueryClassifier
from tradingagents.agents.utils.agent_states import AgentState
from tradingagents.logger_config import get_logger

logger = get_logger(__name__)


class ConversationManager:
    """Manages conversations and debates between agents in the pool"""

    def __init__(self, agent_pool):
        self.agent_pool = agent_pool
        self.conversation_history = []
        self.query_classifier = QueryClassifier(config=DEFAULT_CONFIG)
        selected_analysts = self._extract_selected_analysts()

        self.graph = TradingAgentsGraph(
            selected_analysts=selected_analysts,
            debug=False,
            config=DEFAULT_CONFIG
        )

    def _extract_selected_analysts(self) -> List[str]:
        """Extract list of selected analyst types from agent pool"""
        analysts = []

        if not self.agent_pool or not self.agent_pool.active_agents:
            return ["market", "social", "news", "fundamentals"]

        analyst_mapping = {
            "market_analyst": "market",
            "social_analyst": "social",
            "news_analyst": "news",
            "fundamentals_analyst": "fundamentals"
        }

        for key in self.agent_pool.active_agents.keys():
            if key in analyst_mapping:
                analysts.append(analyst_mapping[key])

        return analysts if analysts else ["market", "social", "news", "fundamentals"]

    def send_query_to_agents(self, query: str, context: Optional[Dict[str, str]] = None) -> dict:
        """Send user query to appropriate agents and orchestrate multi-agent analysis"""
        if not context or not context.get("ticker"):
            return {
                "error": "Please provide a ticker symbol in the context.",
                "individual_responses": [],
                "debate": [],
                "final_verdict": {
                    "summary": "Error: No ticker provided. Please specify a stock ticker to analyze."
                }
            }

        ticker = context.get("ticker", "").upper()
        trade_date = context.get("date", datetime.now().strftime("%Y-%m-%d"))

        logger.info("="*60)
        logger.info("PHASE -1: Query Classification")
        logger.info("="*60)

        classification = self.query_classifier.classify_query(query, ticker)
        selected_agents = classification["selected_agents"]

        logger.info(f"Query: {query[:100]}{'...' if len(query) > 100 else ''}")
        logger.info(f"Selected Agents: {', '.join(selected_agents)} ({len(selected_agents)}/4 possible)")
        logger.info(f"Reasoning: {classification['reasoning']}")
        logger.debug(f"Classification details: {classification}")
        logger.info("="*60)

        self.graph = TradingAgentsGraph(
            selected_analysts=selected_agents,
            debug=False,
            config=DEFAULT_CONFIG
        )

        try:
            logger.info("="*60)
            logger.info("PHASE 0: Pre-Flight Validation")
            logger.info("="*60)
            validation_result = validate_ticker_data(ticker, trade_date)
            logger.info(f"[PASS] Ticker '{ticker}' validated successfully")
            logger.debug(f"Validation result: {validation_result}")
            logger.info("="*60)
        except TickerValidationError as e:
            error_msg = f"Ticker validation failed: {str(e)}"
            logger.error(f"[FAIL] VALIDATION FAILED: {error_msg}")
            logger.info("="*60)
            return {
                "error": error_msg,
                "individual_responses": [],
                "debate": [],
                "final_verdict": {
                    "summary": f"Cannot analyze ticker '{ticker}': {str(e)}\n\n"
                              f"Please check:\n"
                              f"1. Ticker symbol is correct (e.g., 'AAPL', 'MSFT')\n"
                              f"2. Company is publicly traded\n"
                              f"3. API keys are configured correctly\n"
                              f"4. You have internet connectivity"
                }
            }

        try:
            logger.info("="*60)
            logger.info(f"PHASE 1: Running Multi-Agent Analysis")
            logger.info(f"Active Agents: {', '.join(selected_agents)} ({len(selected_agents)}/4)")
            logger.info("="*60)

            final_state, processed_signal = self.graph.propagate(ticker, trade_date)
            logger.debug(f"Graph execution complete. Signal: {processed_signal}")

            formatted_result = self._format_graph_results(query, ticker, trade_date, final_state)
            formatted_result["query_classification"] = classification

            conversation = {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "context": context,
                **formatted_result
            }
            self.conversation_history.append(conversation)

            return conversation

        except Exception as e:
            error_msg = f"Error executing analysis: {str(e)}"
            logger.error(f"Analysis execution failed: {error_msg}", exc_info=True)
            return {
                "error": error_msg,
                "individual_responses": [],
                "debate": [],
                "final_verdict": {
                    "summary": f"Analysis failed: {error_msg}"
                }
            }

    def _format_graph_results(self, query: str, ticker: str, trade_date: str, final_state: dict) -> dict:
        """Format the TradingAgentsGraph final state into conversation format"""
        individual_responses = []

        if final_state.get("market_report"):
            individual_responses.append({
                "agent": "Market Analyst",
                "category": "analysts",
                "perspective": "Technical analysis and market indicators",
                "response": final_state["market_report"]
            })

        if final_state.get("fundamentals_report"):
            individual_responses.append({
                "agent": "Fundamentals Analyst",
                "category": "analysts",
                "perspective": "Financial statements and company fundamentals",
                "response": final_state["fundamentals_report"]
            })

        if final_state.get("news_report"):
            individual_responses.append({
                "agent": "News Analyst",
                "category": "analysts",
                "perspective": "News and current events analysis",
                "response": final_state["news_report"]
            })

        if final_state.get("sentiment_report"):
            individual_responses.append({
                "agent": "Social Media Analyst",
                "category": "analysts",
                "perspective": "Social sentiment and public perception",
                "response": final_state["sentiment_report"]
            })

        debate_rounds = []

        investment_debate = final_state.get("investment_debate_state", {})
        if investment_debate:
            debate_rounds.append({
                "round": 1,
                "topic": "Investment Opportunity Debate (Bull vs Bear)",
                "exchanges": [
                    {
                        "speaker": "Bull Researcher",
                        "statement": investment_debate.get("bull_history", "No bull analysis available")
                    },
                    {
                        "speaker": "Bear Researcher",
                        "statement": investment_debate.get("bear_history", "No bear analysis available")
                    },
                    {
                        "speaker": "Research Manager (Judge)",
                        "statement": investment_debate.get("judge_decision", "No judge decision available")
                    }
                ]
            })

        if final_state.get("trader_investment_plan"):
            debate_rounds.append({
                "round": 2,
                "topic": "Trade Execution Plan",
                "exchanges": [
                    {
                        "speaker": "Trader",
                        "statement": final_state["trader_investment_plan"]
                    }
                ]
            })

        risk_debate = final_state.get("risk_debate_state", {})
        if risk_debate:
            debate_rounds.append({
                "round": 3,
                "topic": "Risk Assessment Debate",
                "exchanges": [
                    {
                        "speaker": "Aggressive Risk Analyst",
                        "statement": risk_debate.get("risky_history", "No risky analysis available")
                    },
                    {
                        "speaker": "Conservative Risk Analyst",
                        "statement": risk_debate.get("safe_history", "No safe analysis available")
                    },
                    {
                        "speaker": "Neutral Risk Analyst",
                        "statement": risk_debate.get("neutral_history", "No neutral analysis available")
                    },
                    {
                        "speaker": "Risk Manager (Judge)",
                        "statement": risk_debate.get("judge_decision", "No risk manager decision available")
                    }
                ]
            })

        final_verdict = self._generate_final_verdict_from_state(
            query, ticker, trade_date, final_state, individual_responses
        )

        return {
            "individual_responses": individual_responses,
            "debate": debate_rounds,
            "final_verdict": final_verdict
        }

    def _generate_final_verdict_from_state(self, query: str, ticker: str,
                                           trade_date: str, final_state: dict,
                                           individual_responses: List[dict]) -> dict:
        """Generate final verdict from the TradingAgentsGraph final state"""
        final_decision = final_state.get("final_trade_decision", "No decision available")
        investment_plan = final_state.get("investment_plan", "")

        bullish_count = 0
        bearish_count = 0
        neutral_count = 0

        for resp in individual_responses:
            response_text = resp["response"].upper()
            if any(word in response_text for word in ["BUY", "BULLISH", "POSITIVE", "STRONG BUY", "UPSIDE"]):
                bullish_count += 1
            elif any(word in response_text for word in ["SELL", "BEARISH", "NEGATIVE", "AVOID", "DOWNSIDE"]):
                bearish_count += 1
            else:
                neutral_count += 1

        total = len(individual_responses)
        bullish_pct = (bullish_count / total * 100) if total > 0 else 0

        if bullish_pct >= 70:
            overall = "STRONG BUY"
            confidence = "High"
        elif bullish_pct >= 50:
            overall = "BUY"
            confidence = "Moderate"
        elif bullish_pct >= 30:
            overall = "HOLD"
            confidence = "Low"
        else:
            overall = "AVOID / SELL"
            confidence = "Moderate"

        verdict = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": ticker,
            "trade_date": trade_date,
            "overall_recommendation": overall,
            "confidence_level": confidence,
            "sentiment_breakdown": {
                "bullish": bullish_count,
                "bearish": bearish_count,
                "neutral": neutral_count,
                "bullish_percentage": round(bullish_pct, 1)
            },
            "final_trade_decision": final_decision,
            "investment_plan": investment_plan,
            "summary": self._generate_summary_text(
                query, ticker, overall, bullish_pct,
                individual_responses, final_decision
            )
        }

        return verdict

    def _generate_summary_text(self, query: str, ticker: str, recommendation: str,
                               bullish_pct: float, responses: List[dict],
                               final_decision: str) -> str:
        """Generate human-readable summary"""
        summary = f"""
ANALYSIS FOR {ticker}
Query: {query}

FINAL CONSENSUS: {recommendation}

After comprehensive analysis from {len(responses)} specialized agents and multi-round debates,
here's our unified recommendation:

SENTIMENT ANALYSIS:
{bullish_pct:.0f}% of our analyst team sees this as a favorable opportunity.

AGENT PERSPECTIVES:
{self._summarize_agent_perspectives(responses)}

FINAL DECISION FROM TRADING SYSTEM:
{final_decision}

RECOMMENDATION:
This recommendation reflects the collective analysis of our multi-agent system,
including technical analysis, fundamental research, news sentiment, social media analysis,
and comprehensive risk assessment through multiple debate rounds.

Remember: This is an AI-generated analysis for informational purposes only.
Always conduct your own research and consult with financial advisors before making
investment decisions.
"""
        return summary.strip()

    def _summarize_agent_perspectives(self, responses: List[dict]) -> str:
        """Create a brief summary of each agent's perspective"""
        summaries = []
        for resp in responses:
            brief = resp["response"][:150].replace("\n", " ")
            if len(resp["response"]) > 150:
                brief += "..."
            summaries.append(f"• {resp['agent']}: {brief}")
        return "\n".join(summaries)

    def get_conversation_history(self) -> List[dict]:
        """Return all conversation history"""
        return self.conversation_history

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
