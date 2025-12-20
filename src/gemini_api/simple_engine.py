import google.generativeai as genai
from src.gemini_api.prompt_manager import PromptManager


class SimpleAnalysisEngine:
    def __init__(self, api_key, model_name):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.prompt_manager = PromptManager()

    def _extract_score(self, response_text):
        if 'SCORE:' in response_text:
            score_part = response_text.split('SCORE:')[1].strip()
            score_str = score_part.split()[0].strip()
            return int(score_str)
        return None

    def analyze_stock(self, ticker):
        scores = {'fundamental_score': None, 'technical_score': None, 'sentiment_score': None}

        try:
            prompt = self.prompt_manager.get_fundamental_prompt(ticker)
            response = self.model.generate_content(prompt)
            scores['fundamental_score'] = self._extract_score(response.text)
        except:
            pass

        try:
            prompt = self.prompt_manager.get_technical_prompt(ticker)
            response = self.model.generate_content(prompt)
            scores['technical_score'] = self._extract_score(response.text)
        except:
            pass

        try:
            prompt = self.prompt_manager.get_sentiment_prompt(ticker)
            response = self.model.generate_content(prompt)
            scores['sentiment_score'] = self._extract_score(response.text)
        except:
            pass

        return scores

    def analyze_macro(self):
        try:
            prompt = self.prompt_manager.get_macro_prompt()
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return None
