# from datetime import datetime
# import sys
# from pathlib import Path
# from prefect import flow, get_run_logger
# from prefect.server.schemas.schedules import CronSchedule
# from loguru import logger
#
# # Add project root to Python path
# sys.path.append(str(Path(__file__).parent))
#
# # Configure logging
# logger.remove()  # Remove default handler
# logger.add(
#     sys.stdout,  # Use stdout instead of stderr
#     format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
#     level="DEBUG",  # Set to DEBUG level
#     colorize=True,
#     backtrace=True,
#     diagnose=True
# )
#
# # Import after path setup
# from src.data.data_manager import collect_market_data, store_market_data
#
#
# def generate_flow_run_name(flow_prefix: str) -> str:
#     return f"{flow_prefix}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
#
#
# @flow(flow_run_name=lambda: generate_flow_run_name("data-ingestion"))
# def data_ingestion_subflow():
#     """Main flow for data ingestion."""
#     logger = get_run_logger()
#     logger.info("Starting data ingestion flow...")
#
#     try:
#         # Collect market data
#         logger.debug("Starting market data collection...")
#         data = collect_market_data()
#         logger.debug(f"Collected data for symbols: {list(data.keys())}")
#
#         # Store market data
#         logger.debug("Starting market data storage...")
#         store_market_data(data)
#
#         logger.info("Data ingestion flow completed successfully")
#     except Exception as e:
#         logger.error(f"Error in data ingestion flow: {str(e)}")
#         raise
#
#
# if __name__ == "__main__":
#     logger.info("Starting trading deployment...")
#     data_ingestion_subflow.serve(
#         name="trading-data-ingestion",
#         cron="0 * * * *",
#         tags=["trading", "data-ingestion", "hourly"],
#         description="Hourly data ingestion flow for trading system"
#     )

from datetime import datetime
from prefect import flow, get_run_logger
from prefect.server.schemas.schedules import CronSchedule
from prefect.blocks.system import Secret
from prefect.context import get_run_context

from src.data.data_manager import collect_market_data, store_market_data


def generate_flow_run_name(flow_prefix: str) -> str:
    return f"{flow_prefix}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


@flow(flow_run_name=lambda: generate_flow_run_name("data-ingestion"))
async def data_ingestion_subflow():
    """Main flow for data ingestion."""
    logger = get_run_logger()
    logger.info("Starting data ingestion flow...")

    try:
        # Get database credentials from Prefect secrets
        db_user = await Secret.load("db-user")
        db_password = await Secret.load("db-password")
        db_host = await Secret.load("db-host")
        db_port = str(await Secret.load("db-port"))
        db_name = await Secret.load("db-name")

        # Set environment variables for database connection
        import os
        os.environ["DB_USER"] = str(db_user)
        os.environ["DB_PASSWORD"] = str(db_password)
        os.environ["DB_HOST"] = str(db_host)
        os.environ["DB_PORT"] = str(db_port)  # Ensure it's a string
        os.environ["DB_NAME"] = str(db_name)

        # Debug log the connection details (excluding password)
        logger.debug(f"Database connection details: host={db_host}, port={db_port}, user={db_user}, database={db_name}")

        # Collect market data
        data = await collect_market_data()
        
        # Store market data
        await store_market_data(data)
        
        logger.info("Data ingestion flow completed successfully")
    except Exception as e:
        logger.error(f"Error in data ingestion flow: {str(e)}")
        raise


if __name__ == "__main__":
    # This is now just the flow definition
    # Deployment will be handled via CLI or deployment YAML
    pass
