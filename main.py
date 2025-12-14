import os
import queue
import threading
from dotenv import load_dotenv
from src.config.settings import Settings
from src.core.logger_setup import setup_logger
from src.core.scheduler import DailyProcessor, start_scheduler
from src.gui.app_gui import AppGUI
from src.utils.api_key_manager import APIKeyManager


def main():
    load_dotenv()

    # Initialize API Key Manager
    try:
        api_key_manager = APIKeyManager()
    except ValueError as e:
        print(f"ERROR: {e}")
        exit(1)

    log_queue = queue.Queue()
    logger = setup_logger(gui_queue=log_queue)

    logger.info("GeminiTrader application starting...")
    logger.info(f"Loaded {api_key_manager.get_key_count()} Gemini API key(s) successfully")

    model_name = Settings.GEMINI_MODEL

    def run_analysis_immediately():
        logger.info("Run Now button clicked - starting analysis in background thread...")

        def run_analysis():
            analysis_logger = setup_logger(gui_queue=log_queue)
            DailyProcessor.run_daily_analysis(api_key_manager, model_name, analysis_logger)

        analysis_thread = threading.Thread(target=run_analysis, daemon=False)
        analysis_thread.start()
        logger.info("Analysis thread started")

    def scheduler_func():
        pass

    logger.info(f"Starting scheduler for daily analysis at {Settings.ANALYSIS_TIME_UTC} UTC...")
    scheduler_thread = threading.Thread(
        target=start_scheduler,
        args=(api_key_manager, model_name, log_queue),
        daemon=True
    )
    scheduler_thread.start()
    logger.info("Scheduler thread started successfully")

    gui = AppGUI(log_queue)

    logger.info("Launching GUI...")
    gui.start_loop(scheduler_func=scheduler_func, run_now_func=run_analysis_immediately)

    logger.info("GeminiTrader application closed")


if __name__ == '__main__':
    main()
