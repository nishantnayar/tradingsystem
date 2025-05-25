from datetime import datetime
import sys
from pathlib import Path
from prefect import flow, get_run_logger
from prefect.server.schemas.schedules import CronSchedule
from loguru import logger
from prefect.client.orchestration import get_client
from prefect.settings import PREFECT_API_URL

# Add project root to Python path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,  # Use stdout instead of stderr
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",  # Set to DEBUG level
    colorize=True,
    backtrace=True,
    diagnose=True
)

# Import after path setup
from src.data.data_manager import collect_market_data, store_market_data


def generate_flow_run_name(flow_prefix: str) -> str:
    return f"{flow_prefix}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


@flow(flow_run_name=lambda: generate_flow_run_name("data-ingestion"))
def data_ingestion_subflow():
    """Main flow for data ingestion."""
    logger = get_run_logger()
    logger.info("Starting data ingestion flow...")

    try:
        # Collect market data
        logger.debug("Starting market data collection...")
        data = collect_market_data()
        logger.debug(f"Collected data for symbols: {list(data.keys())}")

        # Store market data
        logger.debug("Starting market data storage...")
        store_market_data(data)

        logger.info("Data ingestion flow completed successfully")
    except Exception as e:
        logger.error(f"Error in data ingestion flow: {str(e)}")
        raise


async def check_prefect_server():
    """Check if Prefect server is accessible."""
    try:
        async with get_client() as client:
            await client.read_flows()
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Prefect server: {str(e)}")
        return False


if __name__ == "__main__":
    logger.info("Starting trading deployment...")
    
    # Check Prefect server connection
    import asyncio
    if not asyncio.run(check_prefect_server()):
        logger.error("Cannot connect to Prefect server. Please ensure the server is running.")
        logger.info("To start the Prefect server, run: prefect server start")
        sys.exit(1)
    
    try:
        data_ingestion_subflow.serve(
            name="trading-data-ingestion",
            cron="0 * * * *",
            tags=["trading", "data-ingestion", "hourly"],
            description="Hourly data ingestion flow for trading system"
        )
    except Exception as e:
        logger.error(f"Failed to deploy flow: {str(e)}")
        sys.exit(1)