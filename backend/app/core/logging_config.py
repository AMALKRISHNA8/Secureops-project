"""
Structured logging configuration for SecureOps.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler

from app.core.config import settings


def setup_logging() -> logging.Logger:
    """
    Configure application-wide logging with console and rotating file handlers.
    Returns the root application logger.
    """
    logger = logging.getLogger("secureops")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Prevent duplicate handlers on reload
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating file handler (5MB per file, keep 3 backups)
    try:
        file_handler = RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except (OSError, PermissionError):
        logger.warning("Could not create log file, using console only")

    return logger


# Initialize logger on import
logger = setup_logging()
