#!/usr/bin/env python3
"""
Logging system for D3-Mind-Flow-Editor
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Colored log formatter for terminal output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}"
                f"{record.levelname}"
                f"{self.RESET}"
            )
        
        return super().format(record)


class AppLogger:
    """Application logger with file and console output"""
    
    def __init__(self, name: str = "D3MindFlowEditor", log_dir: Optional[str] = None):
        """Initialize logger
        
        Args:
            name: Logger name
            log_dir: Directory for log files. If None, uses default location.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Set up log directory
        if log_dir is None:
            home_dir = Path.home()
            self.log_dir = home_dir / ".d3_mind_flow_editor" / "logs"
        else:
            self.log_dir = Path(log_dir)
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up handlers
        self._setup_file_handler()
        self._setup_console_handler()
    
    def _setup_file_handler(self):
        """Set up file handler for logging to file"""
        # Create log file with timestamp
        log_file = self.log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Detailed format for file
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(file_handler)
    
    def _setup_console_handler(self):
        """Set up console handler for terminal output"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Colored format for console
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)
    
    def exception(self, message: str):
        """Log exception with traceback"""
        self.logger.exception(message)
    
    def get_logger(self) -> logging.Logger:
        """Get underlying logger instance"""
        return self.logger
    
    def set_level(self, level: str):
        """Set logging level
        
        Args:
            level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        numeric_level = getattr(logging, level.upper(), None)
        if isinstance(numeric_level, int):
            self.logger.setLevel(numeric_level)
        else:
            raise ValueError(f'Invalid log level: {level}')


# Global logger instance
logger = AppLogger()


# Convenience functions
def debug(message: str):
    """Log debug message"""
    logger.debug(message)


def info(message: str):
    """Log info message"""
    logger.info(message)


def warning(message: str):
    """Log warning message"""
    logger.warning(message)


def error(message: str):
    """Log error message"""
    logger.error(message)


def critical(message: str):
    """Log critical message"""
    logger.critical(message)


def exception(message: str):
    """Log exception with traceback"""
    logger.exception(message)