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
from prefect_sqlalchemy import SqlAlchemyConnector
import os

from src.data.data_manager import collect_market_data, store_market_data


def generate_flow_run_name(flow_prefix: str) -> str:
    return f"{flow_prefix}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


@flow(flow_run_name=lambda: generate_flow_run_name("data-ingestion"))
async def data_ingestion_subflow():
    """Main flow for data ingestion."""
    logger = get_run_logger()
    logger.info("Starting data ingestion flow...")

    try:
        # Load database connector from Prefect block
        connector = await SqlAlchemyConnector.load("tradingsystemdb")
        connection_info = connector.connection_info

        # Set environment variables for backward compatibility
        os.environ["DB_USER"] = connection_info.username
        os.environ["DB_PASSWORD"] = connection_info.password
        os.environ["DB_HOST"] = connection_info.host
        os.environ["DB_PORT"] = str(connection_info.port)
        os.environ["DB_NAME"] = connection_info.database

        # Debug log the connection details (excluding password)
        logger.debug(f"Database connection details: host={connection_info.host}, port={connection_info.port}, user={connection_info.username}, database={connection_info.database}")

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
