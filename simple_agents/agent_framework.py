import os
import json
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime

class Agent(ABC):
    def __init__(self, name: str, role: str, model_name: str = "gemini-2.0-flash-exp"):
        self.name = name
        self.role = role
        self.model_name = model_name
        self.api_key = None
        self._configure_model()

    def _configure_model(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")

    @abstractmethod
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def generate_response(self, prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]

class StockSelectorAgent(Agent):
    def __init__(self, name: str, role: str, selection_criteria: str):
        super().__init__(name, role)
        self.selection_criteria = selection_criteria
        self.selected_stocks = []

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        date = context.get('date', datetime.now().strftime("%Y-%m-%d"))

        prompt = f"""You are a {self.role}.

Your task: Select exactly 5 stocks to invest in for tomorrow ({date}).

Selection Criteria: {self.selection_criteria}

Rules:
1. Select exactly 5 stock tickers (e.g., AAPL, MSFT, GOOGL)
2. Provide brief reasoning for each pick
3. Focus on stocks likely to perform well tomorrow

Output format (JSON):
{{
  "stocks": [
    {{"ticker": "AAPL", "reason": "Strong technical momentum"}},
    {{"ticker": "MSFT", "reason": "Positive earnings outlook"}},
    ...
  ]
}}

Provide only the JSON output, no additional text."""

        response = self.generate_response(prompt)

        try:
            result = json.loads(response.strip().replace("```json", "").replace("```", ""))
            self.selected_stocks = result.get("stocks", [])
            return {
                "agent": self.name,
                "role": self.role,
                "selected_stocks": self.selected_stocks,
                "full_response": response
            }
        except json.JSONDecodeError:
            self.selected_stocks = []
            return {
                "agent": self.name,
                "role": self.role,
                "selected_stocks": [],
                "error": "Failed to parse response",
                "full_response": response
            }

class DebateAgent(Agent):
    def __init__(self, name: str, role: str):
        super().__init__(name, role)

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        all_selections = context.get('all_selections', [])
        debate_history = context.get('debate_history', [])

        selections_text = "\n".join([
            f"{sel['agent']} ({sel['role']}):\n" +
            "\n".join([f"  - {s['ticker']}: {s['reason']}" for s in sel['selected_stocks']])
            for sel in all_selections
        ])

        history_text = "\n".join([
            f"{entry['agent']}: {entry['argument']}"
            for entry in debate_history
        ])

        prompt = f"""You are a {self.role} participating in a stock selection debate.

Agent Selections:
{selections_text}

Previous Debate:
{history_text}

Your task: Argue for which 5 stocks the group should invest in tomorrow.
- Consider all agents' selections
- Provide strong arguments for your choices
- Challenge weak selections from other agents
- Be specific and data-driven

Output your argument as clear text (not JSON)."""

        response = self.generate_response(prompt)

        return {
            "agent": self.name,
            "role": self.role,
            "argument": response
        }

class ModeratorAgent(Agent):
    def __init__(self):
        super().__init__("Moderator", "Debate Moderator and Final Decision Maker", "gemini-1.5-pro")

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        all_selections = context.get('all_selections', [])
        debate_history = context.get('debate_history', [])

        selections_text = "\n".join([
            f"{sel['agent']} ({sel['role']}):\n" +
            "\n".join([f"  - {s['ticker']}: {s['reason']}" for s in sel['selected_stocks']])
            for sel in all_selections
        ])

        debate_text = "\n".join([
            f"{entry['agent']}: {entry['argument']}"
            for entry in debate_history
        ])

        prompt = f"""You are the Moderator and Final Decision Maker.

Agent Initial Selections:
{selections_text}

Debate Arguments:
{debate_text}

Your task: Make the final decision on which 5 stocks to invest in tomorrow.

Consider:
- Strength of arguments from each agent
- Consensus vs. outlier picks
- Risk/reward balance
- Diversity across selections

Output format (JSON):
{{
  "final_stocks": ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"],
  "reasoning": "Detailed explanation of why these 5 were chosen",
  "key_points": [
    "Point 1",
    "Point 2",
    "Point 3"
  ]
}}

Provide only the JSON output."""

        response = self.generate_response(prompt)

        try:
            result = json.loads(response.strip().replace("```json", "").replace("```", ""))
            return {
                "agent": self.name,
                "final_decision": result
            }
        except json.JSONDecodeError:
            return {
                "agent": self.name,
                "error": "Failed to parse response",
                "full_response": response
            }
