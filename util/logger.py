import logging
import os
from functools import lru_cache

# Global logger instance
_app_logger = None

@lru_cache(maxsize=128)
def get_logger(name=None):

    global _app_logger
    
    # If no name provided, return the app logger
    if name is None:
        if _app_logger is None:
            # Create and configure the root logger
            _app_logger = logging.getLogger('search_issue_service')
        return _app_logger
    
    # Otherwise return a child logger
    return logging.getLogger(f'search_issue_service.{name}')

def setup_logging(level=None):
   
    # Determine log level from environment or use default
    if level is None:
        level_name = os.environ.get('LOG_LEVEL', 'INFO')
        level = getattr(logging, level_name.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicates
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create app logger as a child of root
    app_logger = get_logger()
    
    return app_logger

# Initialize the logger
logger = get_logger()