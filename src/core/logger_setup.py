import logging
from src.config.settings import Settings


class QueueHandler(logging.Handler):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def emit(self, record):
        try:
            log_entry = self.format(record)
            self.queue.put(log_entry)
        except Exception:
            self.handleError(record)


def setup_logger(gui_queue=None):
    logger = logging.getLogger('STOCK_ANALYZER')
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    log_format = '%(asctime)s - %(levelname)s - %(module)s - %(message)s'
    formatter = logging.Formatter(log_format)

    file_handler = logging.FileHandler(Settings.LOG_FILE_NAME)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if gui_queue is not None:
        queue_handler = QueueHandler(gui_queue)
        queue_handler.setLevel(logging.INFO)
        queue_handler.setFormatter(formatter)
        logger.addHandler(queue_handler)

    return logger
