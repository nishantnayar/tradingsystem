"""
Prefect logging integration module.
"""
from typing import Dict, Any, Optional
import sys
from pathlib import Path
from loguru import logger
from prefect.logging import get_run_logger as prefect_get_run_logger
from prefect.logging.handlers import PrefectConsoleHandler
from prefect.exceptions import MissingContextError
import logging

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.utils.logger import setup_logging


class PrefectLogHandler(logging.Handler):
    """Custom Prefect log handler that integrates with our logging system."""
    
    def emit(self, record):
        """Emit a log record to our logging system."""
        try:
            # Convert log record to our format
            log_entry = {
                "timestamp": record.created,
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line_number": record.lineno
            }
            
            # Log using our logger
            if record.levelno >= 40:  # ERROR or higher
                logger.error(log_entry["message"])
            elif record.levelno >= 30:  # WARNING
                logger.warning(log_entry["message"])
            elif record.levelno >= 20:  # INFO
                logger.info(log_entry["message"])
            else:  # DEBUG
                logger.debug(log_entry["message"])
                
        except Exception as e:
            logger.error(f"Error in Prefect log handler: {str(e)}")


def setup_prefect_logging() -> Optional[Any]:
    """
    Set up Prefect logging to integrate with our logging system.
    Returns None if not in a Prefect context.
    """
    # Initialize our logging system
    setup_logging()
    
    try:
        # Get all relevant loggers
        loggers = [
            logging.getLogger(),  # Root logger
            logging.getLogger("prefect"),  # Prefect logger
            logging.getLogger("prefect.flow_runs"),  # Flow runs logger
            logging.getLogger("prefect.task_runs"),  # Task runs logger
            # logging.getLogger("prefect.flow_runs.runner"),  # Flow runner logger
            # logging.getLogger("prefect.flow_runs.worker"),  # Flow worker logger
            # logging.getLogger("prefect.flow_runs.worker.worker"),  # Worker logger
            # logging.getLogger("prefect.flow_runs.worker.worker.worker"),  # Nested worker logger
        ]
        
        # Create and configure our handler
        prefect_handler = PrefectLogHandler()
        prefect_handler.setLevel(logging.INFO)  # Capture all levels
        
        # Add handler to all loggers
        for logger_instance in loggers:
            logger_instance.addHandler(prefect_handler)
            logger_instance.setLevel(logging.INFO)  # Ensure all levels are captured
        
        # Try to get the Prefect logger for flow/task context
        prefect_logger = prefect_get_run_logger()
        
        return prefect_logger
    except MissingContextError:
        # Not in a Prefect context, return None
        return None 