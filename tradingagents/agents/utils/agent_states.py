from typing import Annotated, Sequence
from datetime import date, timedelta, datetime
from typing_extensions import TypedDict, Optional
from langchain_openai import ChatOpenAI
from tradingagents.agents import *
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, StateGraph, START, MessagesState


# Custom reducer for report fields to handle concurrent writes from parallel analysts
def merge_reports(existing: str, new: str) -> str:
    """
    Merge report updates, preferring non-empty values.
    This allows multiple analysts to write to their respective reports concurrently.
    """
    if new:
        return new
    return existing if existing else ""


# Custom reducer for debate state fields to handle concurrent writes
def merge_debate_state(existing, new):
    """
    Merge debate state updates, preferring non-empty/newer values.
    This allows multiple debate participants to update state concurrently.
    """
    if new:
        return new
    return existing if existing else None


# Researcher team state
class InvestDebateState(TypedDict):
    bull_history: Annotated[
        str, "Bullish Conversation history"
    ]  # Bullish Conversation history
    bear_history: Annotated[
        str, "Bearish Conversation history"
    ]  # Bullish Conversation history
    history: Annotated[str, "Conversation history"]  # Conversation history
    current_response: Annotated[str, "Latest response"]  # Last response
    judge_decision: Annotated[str, "Final judge decision"]  # Last response
    count: Annotated[int, "Length of the current conversation"]  # Conversation length


# Risk management team state
class RiskDebateState(TypedDict):
    risky_history: Annotated[
        str, "Risky Agent's Conversation history"
    ]  # Conversation history
    safe_history: Annotated[
        str, "Safe Agent's Conversation history"
    ]  # Conversation history
    neutral_history: Annotated[
        str, "Neutral Agent's Conversation history"
    ]  # Conversation history
    history: Annotated[str, "Conversation history"]  # Conversation history
    latest_speaker: Annotated[str, "Analyst that spoke last"]
    current_risky_response: Annotated[
        str, "Latest response by the risky analyst"
    ]  # Last response
    current_safe_response: Annotated[
        str, "Latest response by the safe analyst"
    ]  # Last response
    current_neutral_response: Annotated[
        str, "Latest response by the neutral analyst"
    ]  # Last response
    judge_decision: Annotated[str, "Judge's decision"]
    count: Annotated[int, "Length of the current conversation"]  # Conversation length


class AgentState(MessagesState):
    company_of_interest: Annotated[str, "Company that we are interested in trading"]
    trade_date: Annotated[str, "What date we are trading at"]

    sender: Annotated[str, "Agent that sent this message"]

    # research step - using merge_reports reducer to support parallel analyst execution
    market_report: Annotated[str, merge_reports]
    sentiment_report: Annotated[str, merge_reports]
    news_report: Annotated[str, merge_reports]
    fundamentals_report: Annotated[str, merge_reports]

    # researcher team discussion step - using merge_debate_state to support concurrent writes
    investment_debate_state: Annotated[InvestDebateState, merge_debate_state]
    investment_plan: Annotated[str, merge_reports]

    trader_investment_plan: Annotated[str, merge_reports]

    # risk management team discussion step - using merge_debate_state to support concurrent writes
    risk_debate_state: Annotated[RiskDebateState, merge_debate_state]
    final_trade_decision: Annotated[str, merge_reports]
