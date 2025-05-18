"""
Logging configuration module for the trading system.
"""
import os
import sys
from pathlib import Path
import yaml
from loguru import logger

def setup_logging(config_path: str = None) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        config_path: Path to the logging configuration file. If None, uses default path.
    """
    if config_path is None:
        config_path = str(Path(__file__).parent.parent.parent / "config" / "config.yaml")
    
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
        
        # Add file logger
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logger.add(
            log_dir / "trading_system_{time}.log",
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