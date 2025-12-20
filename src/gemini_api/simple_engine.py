import google.generativeai as genai
from src.gemini_api.prompt_manager import (
    FUNDAMENTAL_PROMPT_TEMPLATE,
    TECHNICAL_PROMPT_TEMPLATE,
    SENTIMENT_PROMPT_TEMPLATE
)


class SimpleAnalysisEngine:
    def __init__(self, api_key, model_name):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def _extract_score(self, response_text):
        if 'SCORE:' in response_text:
            score_part = response_text.split('SCORE:')[1].strip()
            score_str = score_part.split()[0].strip()
            return int(score_str)
        return None

    def analyze_stock(self, ticker, stock_data):
        scores = {'fundamental_score': None, 'technical_score': None, 'sentiment_score': None}

        try:
            prompt = FUNDAMENTAL_PROMPT_TEMPLATE.format(TICKER=ticker, FUNDAMENTAL_DATA=stock_data['Fundamental'])
            response = self.model.generate_content(prompt)
            scores['fundamental_score'] = self._extract_score(response.text)
        except:
            pass

        try:
            prompt = TECHNICAL_PROMPT_TEMPLATE.format(TICKER=ticker, TECHNICAL_DATA=stock_data['Technical'])
            response = self.model.generate_content(prompt)
            scores['technical_score'] = self._extract_score(response.text)
        except:
            pass

        try:
            prompt = SENTIMENT_PROMPT_TEMPLATE.format(TICKER=ticker, SENTIMENT_DATA=stock_data['Sentiment'])
            response = self.model.generate_content(prompt)
            scores['sentiment_score'] = self._extract_score(response.text)
        except:
            pass

        return scores
