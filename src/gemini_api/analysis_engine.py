import time
import google.generativeai as genai
from src.gemini_api.prompt_manager import (
    FUNDAMENTAL_PROMPT_TEMPLATE,
    TECHNICAL_PROMPT_TEMPLATE,
    SENTIMENT_PROMPT_TEMPLATE,
    MACRO_PROMPT_TEMPLATE
)


class GeminiAnalysisEngine:
    def __init__(self, api_key, model_name, rate_limit_delay=12):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.rate_limit_delay = rate_limit_delay

    def _extract_score(self, response_text):
        try:
            if 'SCORE:' in response_text:
                score_part = response_text.split('SCORE:')[1].strip()
                score_str = score_part.split()[0].strip()
                score = int(score_str)
                if 1 <= score <= 100:
                    return score
                else:
                    raise ValueError(f"Score {score} out of valid range (1-100)")
            else:
                raise ValueError("SCORE: keyword not found in response")
        except (IndexError, ValueError) as e:
            raise ValueError(f"Failed to parse score from response: {e}")

    def analyze_stock(self, ticker, stock_data, verbose=False):
        scores = {
            'fundamental_score': None,
            'technical_score': None,
            'sentiment_score': None
        }

        fundamental_prompt = FUNDAMENTAL_PROMPT_TEMPLATE.format(
            TICKER=ticker,
            FUNDAMENTAL_DATA=stock_data['Fundamental']
        )
        try:
            response = self.model.generate_content(fundamental_prompt)
            if verbose:
                print(f"\n[FUNDAMENTAL RAW RESPONSE for {ticker}]:\n{response.text}\n")
            scores['fundamental_score'] = self._extract_score(response.text)
            time.sleep(self.rate_limit_delay)
        except (ValueError, Exception) as e:
            print(f"Error analyzing fundamental for {ticker}: {e}")

        technical_prompt = TECHNICAL_PROMPT_TEMPLATE.format(
            TICKER=ticker,
            TECHNICAL_DATA=stock_data['Technical']
        )
        try:
            response = self.model.generate_content(technical_prompt)
            if verbose:
                print(f"\n[TECHNICAL RAW RESPONSE for {ticker}]:\n{response.text}\n")
            scores['technical_score'] = self._extract_score(response.text)
            time.sleep(self.rate_limit_delay)
        except (ValueError, Exception) as e:
            print(f"Error analyzing technical for {ticker}: {e}")

        sentiment_prompt = SENTIMENT_PROMPT_TEMPLATE.format(
            TICKER=ticker,
            SENTIMENT_DATA=stock_data['Sentiment']
        )
        try:
            response = self.model.generate_content(sentiment_prompt)
            if verbose:
                print(f"\n[SENTIMENT RAW RESPONSE for {ticker}]:\n{response.text}\n")
            scores['sentiment_score'] = self._extract_score(response.text)
            time.sleep(self.rate_limit_delay)
        except (ValueError, Exception) as e:
            print(f"Error analyzing sentiment for {ticker}: {e}")

        return scores

    def analyze_macro(self, macro_data, verbose=False):
        macro_prompt = MACRO_PROMPT_TEMPLATE.format(MACRO_DATA=macro_data)

        try:
            response = self.model.generate_content(macro_prompt)
            if verbose:
                print(f"\n[MACRO RAW RESPONSE]:\n{response.text}\n")
            time.sleep(self.rate_limit_delay)
            return response.text
        except Exception as e:
            print(f"Error analyzing macro data: {e}")
            return None
