import time
import threading
import pandas as pd
import schedule
from src.config.settings import Settings
from src.core.stock_list import get_sp500_tickers
from src.data.data_fetcher import get_stock_data, get_macro_data
from src.gemini_api.analysis_engine import GeminiAnalysisEngine
from src.core.logger_setup import setup_logger


class DailyProcessor:
    @staticmethod
    def run_daily_analysis(api_key, model_name, logger):
        logger.info("Initializing Gemini Analysis Engine...")
        engine = GeminiAnalysisEngine(api_key, model_name)
        logger.info(f"Analysis engine initialized with model: {model_name}")

        logger.info("Fetching ticker list...")
        tickers = get_sp500_tickers()
        logger.info(f"Retrieved {len(tickers)} tickers: {', '.join(tickers)}")

        logger.info("Fetching macro data...")
        macro_data = get_macro_data()
        logger.info("Macro data retrieved successfully")

        results = []

        logger.info("Starting stock analysis loop...")
        for ticker in tickers:
            try:
                stock_data = get_stock_data(ticker)
                scores = engine.analyze_stock(ticker, stock_data)

                if all(score is not None for score in scores.values()):
                    result = {
                        'Ticker': ticker,
                        'Fundamental_Score': scores['fundamental_score'],
                        'Technical_Score': scores['technical_score'],
                        'Sentiment_Score': scores['sentiment_score']
                    }
                    results.append(result)
                    logger.info(
                        f"SUCCESS: {ticker} - "
                        f"Fundamental: {scores['fundamental_score']}, "
                        f"Technical: {scores['technical_score']}, "
                        f"Sentiment: {scores['sentiment_score']}"
                    )
                else:
                    logger.error(
                        f"ERROR: Failed to analyze {ticker} - "
                        f"Some scores are missing: {scores}"
                    )

            except Exception as e:
                logger.error(f"ERROR: Exception while analyzing {ticker}: {e}")

        logger.info("Analyzing macro environment...")
        try:
            macro_summary = engine.analyze_macro(macro_data)
            if macro_summary:
                logger.info(f"Macro Analysis Summary: {macro_summary}")
            else:
                logger.error("ERROR: Failed to retrieve macro analysis summary")
        except Exception as e:
            logger.error(f"ERROR: Exception while analyzing macro data: {e}")

        if results:
            logger.info(f"Creating DataFrame with {len(results)} results...")
            df = pd.DataFrame(results)

            output_path = Settings.OUTPUT_CSV_FILENAME
            logger.info(f"Saving results to {output_path}...")
            df.to_csv(output_path, index=False)
            logger.info(f"Results successfully saved to {output_path}")
        else:
            logger.error("ERROR: No results to save - all analyses failed")

        logger.info("Daily analysis process completed")


def start_scheduler(api_key, model_name, log_queue):
    logger = setup_logger(gui_queue=log_queue)

    scheduled_time = Settings.ANALYSIS_TIME_UTC
    logger.info(f"Scheduling daily analysis to run at {scheduled_time} UTC")

    schedule.every().day.at(scheduled_time).do(
        DailyProcessor.run_daily_analysis,
        api_key=api_key,
        model_name=model_name,
        logger=logger
    )

    def run_scheduler():
        logger.info("Scheduler thread started")
        while True:
            schedule.run_pending()
            time.sleep(60)

    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Scheduler initialized and running in background thread")
