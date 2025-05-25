import os
from pathlib import Path
from typing import Any, Dict

import yaml
from loguru import logger
from dotenv import load_dotenv


def get_config() -> Dict[str, Any]:
    """Load and parse the configuration file with environment variable substitution."""
    try:
        # Get the project root directory
        project_root = Path(__file__).parent.parent.parent
        logger.debug(f"Project root: {project_root}")
        
        # Load environment variables from .env file
        env_path = project_root / "config" / ".env"
        logger.debug(f"Loading .env file from: {env_path}")
        load_dotenv(env_path)
        
        # Load the config file
        config_path = project_root / "config" / "config.yaml"
        logger.debug(f"Config path: {config_path}")
        
        # Debug: Print current working directory and environment variables
        logger.debug(f"Current working directory: {os.getcwd()}")
        logger.debug("Environment variables:")
        for var in ["DB_USER", "DB_PASSWORD", "ALPACA_API_KEY", "ALPACA_SECRET_KEY"]:
            logger.debug(f"{var}: {'*' * 5 if os.getenv(var) else 'Not set'}")
        
        with open(config_path, "r") as f:
            config_content = f.read()
        
        # Check for required environment variables
        required_vars = ["DB_USER", "DB_PASSWORD", "ALPACA_API_KEY", "ALPACA_SECRET_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            error_msg = (
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                "Please set these variables in your environment or .env file:\n"
                "DB_USER=your_db_username\n"
                "DB_PASSWORD=your_db_password\n"
                "ALPACA_API_KEY=your_alpaca_api_key\n"
                "ALPACA_SECRET_KEY=your_alpaca_secret_key"
            )
            logger.error(error_msg)
            raise EnvironmentError(error_msg)
        
        # Replace environment variables
        config_content = os.path.expandvars(config_content)
        
        # Parse YAML
        config = yaml.safe_load(config_content)
        
        # Set REPO_ROOT in config if not already set
        if "REPO_ROOT" not in os.environ:
            os.environ["REPO_ROOT"] = str(project_root)
        
        return config
        
    except FileNotFoundError:
        logger.error(f"Configuration file not found at {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        raise


def update_config(config: Dict[str, Any]) -> None:
    """Update the configuration file with new values.
    
    Args:
        config: New configuration dictionary to save
        
    Note:
        This function will not update environment variables or sensitive data
        that should be stored in .env file.
    """
    try:
        # Get the project root directory
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"
        
        # Load current config to preserve environment variables
        current_config = get_config()
        
        # Update only non-sensitive settings
        for section in ["data_collection", "logging", "trading", "data", "ml"]:
            if section in config:
                current_config[section] = config[section]
        
        # Write updated config back to file
        with open(config_path, "w") as f:
            yaml.safe_dump(current_config, f, default_flow_style=False)
            
        logger.info("Configuration updated successfully")
        
    except Exception as e:
        logger.error(f"Error updating configuration: {str(e)}")
        raise 