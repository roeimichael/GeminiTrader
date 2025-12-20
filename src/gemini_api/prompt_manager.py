import json
import os


class PromptManager:
    def __init__(self, prompts_file='prompts.json'):
        self.prompts_file = prompts_file
        self.prompts = self._load_prompts()

    def _load_prompts(self):
        try:
            with open(self.prompts_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompts file not found: {self.prompts_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in prompts file: {e}")

    def get_fundamental_prompt(self, ticker):
        return self.prompts['fundamental'].format(ticker=ticker)

    def get_technical_prompt(self, ticker):
        return self.prompts['technical'].format(ticker=ticker)

    def get_sentiment_prompt(self, ticker):
        return self.prompts['sentiment'].format(ticker=ticker)

    def get_macro_prompt(self):
        return self.prompts['macro']
