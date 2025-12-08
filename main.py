import os
import queue
from dotenv import load_dotenv
from src.core.logger_setup import setup_logger
from src.gui.app_gui import AppGUI


def run_analysis_immediately():
    logger = setup_logger()
    logger.info("Run Now button clicked - analysis triggered manually")


def start_scheduler():
    pass


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

    gui = AppGUI(log_queue)

    logger.info("Launching GUI...")
    gui.start_loop(scheduler_func=start_scheduler, run_now_func=run_analysis_immediately)

    logger.info("GeminiTrader application closed")


if __name__ == '__main__':
    main()
