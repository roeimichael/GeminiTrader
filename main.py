import os
import queue
import threading
from dotenv import load_dotenv
from src.config.settings import Settings
from src.core.logger_setup import setup_logger
from src.core.scheduler import DailyProcessor, start_scheduler
from src.gui.app_gui import AppGUI


def main():
    load_dotenv()

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment variables.")
        print("Please add GEMINI_API_KEY to your .env file.")
        exit(1)

    log_queue = queue.Queue()
    logger = setup_logger(gui_queue=log_queue)

    logger.info("GeminiTrader application starting...")
    logger.info("GEMINI_API_KEY loaded successfully")

    model_name = Settings.GEMINI_MODEL

    def run_analysis_immediately():
        """Run analysis immediately in a separate thread when button is clicked."""
        logger.info("Run Now button clicked - starting analysis in background thread...")

        def run_analysis():
            analysis_logger = setup_logger(gui_queue=log_queue)
            DailyProcessor.run_daily_analysis(api_key, model_name, analysis_logger)

        analysis_thread = threading.Thread(target=run_analysis, daemon=False)
        analysis_thread.start()
        logger.info("Analysis thread started")

    def scheduler_func():
        """Placeholder function called periodically by GUI event loop."""
        pass

    logger.info(f"Starting scheduler for daily analysis at {Settings.ANALYSIS_TIME_UTC} UTC...")
    scheduler_thread = threading.Thread(
        target=start_scheduler,
        args=(api_key, model_name, log_queue),
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
