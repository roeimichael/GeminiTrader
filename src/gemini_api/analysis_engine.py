import time
import google.generativeai as genai
from src.gemini_api.prompt_manager import (
    FUNDAMENTAL_PROMPT_TEMPLATE,
    TECHNICAL_PROMPT_TEMPLATE,
    SENTIMENT_PROMPT_TEMPLATE,
    MACRO_PROMPT_TEMPLATE
)
from src.utils.api_key_manager import APIKeyManager


class GeminiAnalysisEngine:
    def __init__(self, api_key_manager, model_name, rate_limit_delay=12):
        """
        Initialize the Gemini Analysis Engine.

        Args:
            api_key_manager: APIKeyManager instance or a single API key string (for backward compatibility)
            model_name: Name of the Gemini model to use
            rate_limit_delay: Delay in seconds between API calls
        """
        # Support both APIKeyManager and single API key (backward compatibility)
        if isinstance(api_key_manager, str):
            # Legacy mode: single API key
            self.api_key_manager = None
            self.single_api_key = api_key_manager
            genai.configure(api_key=api_key_manager)
            self.model = genai.GenerativeModel(model_name)
        else:
            # Multi-key mode
            self.api_key_manager = api_key_manager
            self.single_api_key = None
            self.current_key = self.api_key_manager.get_current_key()
            genai.configure(api_key=self.current_key)
            self.model = genai.GenerativeModel(model_name)

        self.model_name = model_name
        self.rate_limit_delay = rate_limit_delay
        self.call_count = 0

    def _rotate_api_key_if_needed(self):
        """Rotate to next API key if using multi-key mode."""
        if self.api_key_manager is None:
            return  # Single key mode, no rotation

        # Rotate key
        new_key = self.api_key_manager.get_next_key()
        if new_key != self.current_key:
            self.current_key = new_key
            genai.configure(api_key=self.current_key)
            self.model = genai.GenerativeModel(self.model_name)

    def _make_api_call(self, prompt, operation_name="API call"):
        """Make an API call with automatic key rotation on rate limit errors."""
        max_key_rotations = self.api_key_manager.get_key_count() if self.api_key_manager else 1
        attempts = 0

        while attempts < max_key_rotations:
            try:
                response = self.model.generate_content(prompt)
                self.call_count += 1
                return response
            except Exception as e:
                error_msg = str(e)
                if '429' in error_msg or 'quota' in error_msg.lower() or 'rate limit' in error_msg.lower():
                    if self.api_key_manager and attempts < max_key_rotations - 1:
                        print(f"  ⚠️  Rate limit hit during {operation_name}, rotating to next API key...")
                        self._rotate_api_key_if_needed()
                        attempts += 1
                        time.sleep(2)  # Brief pause before retry with new key
                        continue
                    else:
                        # No more keys to try or single key mode
                        raise
                else:
                    # Non-rate-limit error, raise immediately
                    raise

        raise Exception(f"Failed {operation_name} after trying all available API keys")

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
            response = self._make_api_call(fundamental_prompt, f"fundamental analysis for {ticker}")
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
            response = self._make_api_call(technical_prompt, f"technical analysis for {ticker}")
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
            response = self._make_api_call(sentiment_prompt, f"sentiment analysis for {ticker}")
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
            response = self._make_api_call(macro_prompt, "macro analysis")
            if verbose:
                print(f"\n[MACRO RAW RESPONSE]:\n{response.text}\n")
            time.sleep(self.rate_limit_delay)
            return response.text
        except Exception as e:
            print(f"Error analyzing macro data: {e}")
            return None
