import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simple_agents.agent_framework import StockSelectorAgent, DebateAgent, ModeratorAgent
from simple_agents.orchestrator import AgentOrchestrator

def main():
    load_dotenv()

    print("="*80)
    print("STOCK SELECTION DEBATE SYSTEM")
    print("="*80)

    fundamental_agent = StockSelectorAgent(
        name="Fundamental Analyst",
        role="Fundamental Analysis Expert",
        selection_criteria="""
        Focus on companies with:
        - Strong balance sheets
        - Growing revenue and earnings
        - Reasonable valuation metrics (P/E, P/B)
        - Competitive advantages
        - Good management
        """
    )

    market_analyst = StockSelectorAgent(
        name="Market Analyst",
        role="Technical Analysis and Market Trends Expert",
        selection_criteria="""
        Focus on stocks with:
        - Positive technical momentum
        - Strong volume patterns
        - Breaking out or near support levels
        - Sector strength
        - Market sentiment alignment
        """
    )

    news_analyst = StockSelectorAgent(
        name="News Analyst",
        role="News and Catalyst Expert",
        selection_criteria="""
        Focus on stocks with:
        - Positive recent news or announcements
        - Upcoming catalysts (earnings, product launches, etc.)
        - Industry tailwinds
        - Analyst upgrades
        - Institutional buying
        """
    )

    moderator = ModeratorAgent()

    orchestrator = AgentOrchestrator()
    orchestrator.add_agent(fundamental_agent)
    orchestrator.add_agent(market_analyst)
    orchestrator.add_agent(news_analyst)
    orchestrator.set_moderator(moderator)

    results = orchestrator.run_full_analysis(num_debate_rounds=2)

    orchestrator.print_summary()

    orchestrator.export_results("stock_debate_results.json")

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
