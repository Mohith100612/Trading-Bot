import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name: str) -> logging.Logger:
    """Configures a logger with both File and Console handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)

        # File Handler (rotating file up to 5MB, keep 3 backups)
        file_handler = RotatingFileHandler(
            "logs/trading_bot.log", maxBytes=5*1024*1024, backupCount=3
        )
        file_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.INFO)

        # We can keep stdout output light by only logging warnings/errors or specifically formatted CLI messages
        # I'll let typer/rich handle CLI display, so console handler here is minimal
        
        logger.addHandler(file_handler)

    return logger
