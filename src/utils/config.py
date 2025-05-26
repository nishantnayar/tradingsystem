import os
from pathlib import Path
from typing import Any, Dict

import yaml
from loguru import logger
from prefect.blocks.system import Secret


def get_config() -> Dict[str, Any]:
    """Load and parse the configuration file with Prefect secret substitution."""
    try:
        # Get the project root directory
        project_root = Path(__file__).parent.parent.parent
        logger.debug(f"Project root: {project_root}")
        
        # Load the config file
        config_path = project_root / "config" / "config.yaml"
        logger.debug(f"Config path: {config_path}")
        
        with open(config_path, "r") as f:
            config_content = f.read()
        
        # Load secrets from Prefect
        secrets = {
            "DB_USER": Secret.load("db-user").get(),
            "DB_PASSWORD": Secret.load("db-password").get(),
            "ALPACA_API_KEY": Secret.load("alpaca-api-key").get(),
            "ALPACA_SECRET_KEY": Secret.load("alpaca-secret-key").get()
        }
        
        # Replace environment variables with Prefect secrets
        for var, value in secrets.items():
            config_content = config_content.replace(f"${{{var}}}", value)
        
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