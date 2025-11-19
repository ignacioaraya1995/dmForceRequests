"""
Logging configuration module for the Real Estate Data Processing Tool.
Provides centralized, professional logging with file and console handlers.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class LoggerConfig:
    """Manages application-wide logging configuration."""

    # Log format templates
    DETAILED_FORMAT = (
        '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s'
    )
    SIMPLE_FORMAT = '%(asctime)s | %(levelname)-8s | %(message)s'
    CONSOLE_FORMAT = '%(levelname)-8s | %(message)s'

    # Date format
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, log_dir: str = 'logs', log_level: str = 'INFO'):
        """
        Initialize logger configuration.

        Args:
            log_dir: Directory to store log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self._ensure_log_directory()

    def _ensure_log_directory(self) -> None:
        """Create log directory if it doesn't exist."""
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def setup_logger(
        self,
        name: str = __name__,
        console_output: bool = True,
        file_output: bool = True,
        detailed_console: bool = False
    ) -> logging.Logger:
        """
        Set up and configure a logger instance.

        Args:
            name: Logger name (typically __name__ of the calling module)
            console_output: Enable console (stdout) logging
            file_output: Enable file logging
            detailed_console: Use detailed format for console output

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(name)
        logger.setLevel(self.log_level)

        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()

        # Console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_format = self.DETAILED_FORMAT if detailed_console else self.CONSOLE_FORMAT
            console_formatter = logging.Formatter(console_format, self.DATE_FORMAT)
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        # File handler
        if file_output:
            log_filename = self._get_log_filename()
            file_handler = logging.FileHandler(log_filename, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
            file_formatter = logging.Formatter(self.DETAILED_FORMAT, self.DATE_FORMAT)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        # Prevent propagation to root logger
        logger.propagate = False

        return logger

    def _get_log_filename(self) -> Path:
        """
        Generate log filename with timestamp.

        Returns:
            Path to log file
        """
        timestamp = datetime.now().strftime('%Y%m%d')
        return self.log_dir / f'realestate_processor_{timestamp}.log'


# Global logger instance factory
_logger_config: Optional[LoggerConfig] = None


def get_logger(
    name: str = __name__,
    log_level: str = 'INFO',
    console_output: bool = True,
    file_output: bool = True
) -> logging.Logger:
    """
    Get a configured logger instance (convenience function).

    Args:
        name: Logger name (typically __name__ of the calling module)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Enable console logging
        file_output: Enable file logging

    Returns:
        Configured logger instance

    Example:
        >>> from src.utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started")
    """
    global _logger_config

    if _logger_config is None:
        _logger_config = LoggerConfig(log_level=log_level)

    return _logger_config.setup_logger(
        name=name,
        console_output=console_output,
        file_output=file_output
    )


# Convenience function for simple logging
def setup_basic_logging(level: str = 'INFO') -> None:
    """
    Set up basic logging configuration for simple scripts.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=LoggerConfig.SIMPLE_FORMAT,
        datefmt=LoggerConfig.DATE_FORMAT
    )
