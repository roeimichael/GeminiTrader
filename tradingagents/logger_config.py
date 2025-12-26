"""
Centralized Logging Configuration for TradingAgents

This module provides a clean, professional logging setup that replaces
scattered print() statements throughout the codebase.

Philosophy:
- INFO: High-level workflow (graph started, verdict reached)
- DEBUG: Detailed outputs (agent responses, API calls, state transitions)
- WARNING: Recoverable issues (rate limits, fallbacks)
- ERROR: Failures that need attention

Benefits:
- Clean console output for production
- Detailed debugging when needed
- Easy to redirect logs to file
- Timestamp and module tracking
"""

import logging
import sys
from pathlib import Path
from typing import Optional


# Color codes for terminal output (ANSI escape sequences)
class LogColors:
    """ANSI color codes for pretty terminal output"""
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for different log levels"""

    LEVEL_COLORS = {
        logging.DEBUG: LogColors.CYAN,
        logging.INFO: LogColors.GREEN,
        logging.WARNING: LogColors.YELLOW,
        logging.ERROR: LogColors.RED,
        logging.CRITICAL: LogColors.RED + LogColors.BOLD,
    }

    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if record.levelno in self.LEVEL_COLORS:
            levelname_color = (
                f"{self.LEVEL_COLORS[record.levelno]}{levelname}{LogColors.RESET}"
            )
            record.levelname = levelname_color

        return super().format(record)


def setup_logger(
    name: str = "tradingagents",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    colorize: bool = True
) -> logging.Logger:
    """
    Set up a logger with consistent formatting

    Args:
        name: Logger name (typically module name)
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path to write logs to
        colorize: Whether to use colored output (disable for file logging)

    Returns:
        Configured logger instance

    Usage:
        logger = setup_logger(__name__)
        logger.info("Analysis started")
        logger.debug("Raw API response: %s", response)
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger

    # Console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    if colorize:
        # Use colored formatter for console
        console_format = "%(levelname)s | %(name)s | %(message)s"
        console_formatter = ColoredFormatter(console_format)
    else:
        # Plain formatter
        console_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        console_formatter = logging.Formatter(console_format)

    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_format = "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
        file_formatter = logging.Formatter(file_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger for a specific module

    This is the primary function modules should use:

    Usage:
        from tradingagents.logger_config import get_logger
        logger = get_logger(__name__)

        logger.info("High-level workflow event")
        logger.debug("Detailed diagnostic info")
        logger.warning("Recoverable issue (fallback triggered)")
        logger.error("Something failed that needs attention")

    Args:
        name: Module name (use __name__)

    Returns:
        Logger instance configured with default settings
    """
    return logging.getLogger(name)


def set_global_log_level(level: int):
    """
    Change log level for all tradingagents loggers

    Args:
        level: Logging level (logging.DEBUG, logging.INFO, etc.)

    Usage:
        # Show all debug output
        set_global_log_level(logging.DEBUG)

        # Only show important info
        set_global_log_level(logging.WARNING)
    """
    logger = logging.getLogger("tradingagents")
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


def enable_debug_mode():
    """
    Enable debug mode - show all detailed logs

    Useful for development and troubleshooting
    """
    set_global_log_level(logging.DEBUG)
    logger = get_logger(__name__)
    logger.info("Debug mode ENABLED - showing all detailed logs")


def enable_production_mode():
    """
    Enable production mode - only show important logs

    Keeps console clean for end users
    """
    set_global_log_level(logging.INFO)
    logger = get_logger(__name__)
    logger.info("Production mode ENABLED - hiding debug details")


# Initialize the root logger for the package
_root_logger = setup_logger(
    name="tradingagents",
    level=logging.INFO,
    colorize=True
)


# Convenience function for quick logging without setup
def log_info(message: str):
    """Quick logging for one-off info messages"""
    _root_logger.info(message)


def log_debug(message: str):
    """Quick logging for one-off debug messages"""
    _root_logger.debug(message)


def log_warning(message: str):
    """Quick logging for one-off warning messages"""
    _root_logger.warning(message)


def log_error(message: str):
    """Quick logging for one-off error messages"""
    _root_logger.error(message)


# Example usage documentation
if __name__ == "__main__":
    # Demo the logging system
    print("\n" + "="*70)
    print("LOGGING SYSTEM DEMO")
    print("="*70 + "\n")

    logger = get_logger("demo")

    logger.debug("This is a DEBUG message (detailed diagnostics)")
    logger.info("This is an INFO message (high-level workflow)")
    logger.warning("This is a WARNING message (recoverable issue)")
    logger.error("This is an ERROR message (needs attention)")

    print("\n" + "="*70)
    print("Enabling debug mode...")
    print("="*70 + "\n")

    enable_debug_mode()
    logger.debug("Now you can see debug messages!")

    print("\n" + "="*70)
    print("Back to production mode...")
    print("="*70 + "\n")

    enable_production_mode()
    logger.debug("This debug message is hidden")
    logger.info("But info messages still show")
