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

def get_repo_root() -> Path:
    """
    Get the repository root directory.
    
    Returns:
        Path: Repository root directory
    """
    return Path(__file__).parent.parent.parent

def cleanup_old_logs(log_dir: Path, max_logs: int) -> None:
    """
    Clean up old log files keeping only the most recent ones.
    
    Args:
        log_dir: Directory containing log files
        max_logs: Maximum number of log files to keep
    """
    log_files = sorted(
        glob.glob(str(log_dir / "*.log*")),
        key=os.path.getmtime,
        reverse=True
    )
    
    # Remove excess log files
    for old_log in log_files[max_logs:]:
        try:
            os.remove(old_log)
        except Exception as e:
            print(f"Failed to remove old log file {old_log}: {e}")

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
        cleanup_old_logs(log_dir, log_config['max_logs'])
        
        # Add file logger
        log_file = log_dir / log_config['log_file']
        logger.add(
            log_file,
            format=log_config['format'],
            level=log_config['level'],
            rotation=log_config['rotation'],
            retention=log_config['retention'],
            compression=log_config['compression']
        )
        
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
