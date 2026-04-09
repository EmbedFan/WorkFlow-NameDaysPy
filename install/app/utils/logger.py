"""
Utility module for logging configuration and management.

Provides centralized logging setup for the application.
"""

import logging
import logging.handlers
import atexit
from pathlib import Path
from typing import Optional

from app.constants import LOG_LEVEL, LOG_FORMAT, LOG_MAX_BYTES, LOG_BACKUP_COUNT, LOGS_DIR, APP_NAME


def setup_logging(
    logger_name: str = "NameDaysApp",
    log_dir: Optional[Path] = None,
    log_level: str = LOG_LEVEL,
) -> logging.Logger:
    """
    Configure and return a logger instance.
    
    Args:
        logger_name: Name of the logger
        log_dir: Directory for log files (uses default if None)
        log_level: Logging level (INFO, DEBUG, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    if log_dir is None:
        log_dir = LOGS_DIR
    
    # Ensure log directory exists
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)
    
    # File handler with rotation
    log_file = log_dir / f"{logger_name}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, log_level.upper()))
    
    # CRITICAL: Set to flush after every write instead of buffering
    class ImmediateFlushHandler(logging.handlers.RotatingFileHandler):
        def emit(self, record):
            super().emit(record)
            self.flush()
    
    file_handler = ImmediateFlushHandler(
        log_file,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, log_level.upper()))
    logger.addHandler(file_handler)
    
    # Console handler - explicitly set level to ensure all errors are captured
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    logger.addHandler(console_handler)
    
    # Ensure logs are flushed on exit
    atexit.register(lambda: [h.flush() for h in logger.handlers])
    atexit.register(lambda: [h.close() for h in logger.handlers])
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance by name, ensuring it's properly configured.
    
    Falls back to the main application logger if the child logger
    doesn't have handlers (ensuring logs always output even if
    setup_logging wasn't called for this specific module).
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance with handlers configured
    """
    logger = logging.getLogger(name)
    
    # If this logger has no handlers, use the main app logger instead
    if not logger.handlers:
        main_logger = logging.getLogger(APP_NAME)
        # If main logger also has no handlers, we have a serious config problem
        if not main_logger.handlers:
            # Create a basic fallback handler
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
            main_logger.addHandler(handler)
            main_logger.setLevel(logging.INFO)
        return main_logger
    
    return logger
