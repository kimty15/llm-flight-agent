"""Simple logging configuration."""

import logging
import logging.handlers
import sys
from pathlib import Path
from src.core.config import settings

def get_logger(name: str) -> logging.Logger:
    """Get a simple logger with console and file output."""
    
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Simple formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    log_path = Path(settings.LOGS_DIR)
    log_path.mkdir(exist_ok=True)
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_path / "app.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger 