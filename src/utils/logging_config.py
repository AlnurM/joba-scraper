import os
import sys
from loguru import logger

from src.config import settings


def setup_logging():
    """Configure loguru logger."""
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(settings.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Remove default logger
    logger.remove()

    # Add console logger
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True
    )

    # Add file logger
    logger.add(
        settings.LOG_FILE,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.LOG_LEVEL,
        rotation="10 MB",  # Rotate when file reaches 10 MB
        compression="zip",  # Compress rotated logs
        retention="30 days",  # Keep logs for 30 days
        backtrace=True,  # Include backtrace in error logs
        diagnose=True,  # Include variables in error logs
    )

    logger.info("Logging configured successfully")


def get_logger(name):
    """Get a logger with the given name."""
    return logger.bind(name=name)