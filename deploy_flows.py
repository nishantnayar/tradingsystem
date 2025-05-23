import sys
from pathlib import Path
import os
from datetime import timedelta

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from loguru import logger
from prefect import flow

# Import the flow function directly
from src.data.data_manager import market_data_collection_flow
from src.utils.logger import setup_logging


def deploy_market_data_collection():
    """Deploy the market data collection flow."""
    try:
        # Deploy the flow using the new API
        # Cron format: minute hour day_of_month month day_of_week
        # 0 13-21 * * 1-5 means:
        # - Run at minute 0
        # - Every hour from 13 to 21 UTC (8 AM to 4 PM EST)
        # - Every day of the month
        # - Every month
        # - Only on weekdays (1-5, where 1=Monday, 5=Friday)
        market_data_collection_flow.serve(
            name="market-data-collection",
            version="1.0.0",
            tags=["market-data"],
            cron="1 13-21 * * 1-5",  # Run at 1 minute past each hour from 8 AM to 4 PM EST, Monday-Friday
            description="Collects market data during market hours (8 AM - 4 PM EST, Monday-Friday)"
        )

        logger.info("Successfully deployed market data collection flow")

    except Exception as e:
        logger.error(f"Failed to deploy market data collection flow: {str(e)}")
        raise


def main():
    """Main function to deploy all flows."""
    try:
        # Initialize logging
        setup_logging()
        
        logger.info("Starting flow deployments...")
        
        # Deploy market data collection flow
        deploy_market_data_collection()
        
        logger.info("All flows deployed successfully")
        
    except Exception as e:
        logger.error(f"Error deploying flows: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 