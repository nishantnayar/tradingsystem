"""
Logging configuration module for the trading system.
"""
import os
import sys
from pathlib import Path
import yaml
from loguru import logger
import glob
import time
from datetime import datetime, timedelta
import inspect
from sqlalchemy.orm import Session
from sqlalchemy import text
from queue import Queue
import threading
import atexit

from src.database.db_manager import DatabaseManager
from src.database.models import Log


def get_repo_root() -> Path:
    """
    Get the repository root directory.
    
    Returns:
        Path: Repository root directory
    """
    return Path(__file__).parent.parent.parent


def cleanup_old_logs(log_dir: Path, max_age_days: int) -> None:
    """
    Clean up old log files based on their age.
    
    Args:
        log_dir: Directory containing log files
        max_age_days: Maximum age of log files in days
    """
    cutoff_date = datetime.now() - timedelta(days=max_age_days)

    for log_file in log_dir.glob("*.log*"):
        try:
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_time < cutoff_date:
                log_file.unlink()
        except Exception as e:
            print(f"Failed to remove old log file {log_file}: {e}")


# Create a queue for database logging
log_queue = Queue()
stop_event = threading.Event()


def database_log_worker():
    """Worker thread for processing database logs."""
    db_manager = DatabaseManager()

    while not stop_event.is_set():
        try:
            # Get log entry from queue with timeout
            log_entry = log_queue.get(timeout=1)
            if log_entry is None:
                continue

            try:
                # Check if logs table exists
                with db_manager.get_session() as session:
                    result = session.execute(
                        text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'logs')"))
                    if not result.scalar():
                        print("Logs table does not exist yet. Skipping database logging.")
                        continue

                    session.add(log_entry)
                    session.commit()
            except Exception as e:
                print(f"Failed to log to database: {str(e)}")

        except Exception:
            # Timeout or other error, continue
            continue

    # Clean up database connection when worker stops
    db_manager.close()


def database_log_sink(message):
    """
    Custom sink for logging to database.
    
    Args:
        message: Loguru message object
    """
    try:
        # Get caller information
        frame = inspect.currentframe().f_back
        module = frame.f_globals.get('__name__', 'unknown')
        function = frame.f_code.co_name
        line_number = frame.f_lineno

        # Extract message details
        record = message.record
        log_entry = Log(
            timestamp=record["time"],
            level=record["level"].name,
            message=record["message"],
            module=module,
            function=function,
            line_number=line_number
        )

        # Add to queue for async processing
        log_queue.put(log_entry)

    except Exception as e:
        print(f"Failed to queue log entry: {str(e)}")


def setup_logging(config_path: str = None) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        config_path: Path to the logging configuration file. If None, uses default path.
    """
    if config_path is None:
        config_path = str(get_repo_root() / "config" / "config.yaml")

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            log_config = config['logging']

        # Remove default logger
        logger.remove()

        # Add console logger
        logger.add(
            sys.stderr,
            format=log_config['format'],
            level=log_config['level'],
            colorize=True
        )

        # Create log directory
        repo_root = get_repo_root()
        log_dir = Path(str(log_config['log_dir']).replace("${REPO_ROOT}", str(repo_root)))
        log_dir.mkdir(exist_ok=True)

        # Clean up old logs
        cleanup_old_logs(log_dir, log_config['max_age_days'])

        # Add file logger with date-based filename
        log_file = log_dir / f"{log_config['log_file'].replace('.log', '')}_{datetime.now().strftime('%Y-%m-%d')}.log"
        logger.add(
            log_file,
            format=log_config['format'],
            level=log_config['level'],
            rotation=log_config['rotation'],
            retention=log_config['retention'],
            compression=log_config['compression']
        )

        # Start database logging worker thread
        worker_thread = threading.Thread(target=database_log_worker, daemon=True)
        worker_thread.start()

        # Add database logger
        logger.add(
            database_log_sink,
            format=log_config['format'],
            level=log_config['level']
        )

        # Register cleanup function
        atexit.register(lambda: stop_event.set())

        logger.info("Logging configuration completed successfully")

    except Exception as e:
        print(f"Failed to set up logging: {e}")
        raise


def get_logger():
    """
    Get the configured logger instance.
    
    Returns:
        Logger: Configured loguru logger instance
    """
    return logger
