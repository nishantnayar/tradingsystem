import sys
from pathlib import Path
import os

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from loguru import logger
from prefect import flow

# Import the flow function directly
from src.data.data_manager import market_data_collection_flow


def deploy_market_data_collection():
    """Deploy the market data collection flow."""
    try:
        # Deploy the flow using the new API
        market_data_collection_flow.serve(
            name="market-data-collection",
            version="1.0.0",
            cron="0 * * * *",  # Run every hour
            tags=["market-data", "production"],
            description="Collects market data from Alpaca API every hour"
        )
        
        logger.info("Successfully deployed market data collection flow")
        
    except Exception as e:
        logger.error(f"Failed to deploy market data collection flow: {str(e)}")
        raise


def main():
    """Main function to deploy all flows."""
    try:
        logger.info("Starting flow deployments...")
        
        # Deploy market data collection flow
        deploy_market_data_collection()
        
        logger.info("All flows deployed successfully")
        
    except Exception as e:
        logger.error(f"Error deploying flows: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 