"""
NextPy Logging Utilities
Structured logging for debugging and monitoring
"""

import logging
from datetime import datetime
from typing import Any


class Logger:
    """Simple logging wrapper"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(f"{message} {self._format_kwargs(kwargs)}")
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(f"{message} {self._format_kwargs(kwargs)}")
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(f"{message} {self._format_kwargs(kwargs)}")
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(f"{message} {self._format_kwargs(kwargs)}")
    
    @staticmethod
    def _format_kwargs(kwargs: dict) -> str:
        """Format kwargs for logging"""
        if not kwargs:
            return ""
        return " | " + " ".join(f"{k}={v}" for k, v in kwargs.items())


def get_logger(name: str) -> Logger:
    """Get logger instance"""
    return Logger(name)
