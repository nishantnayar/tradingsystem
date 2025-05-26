from datetime import datetime
import sys
from pathlib import Path
from prefect import flow, get_run_logger
from loguru import logger
from prefect.client.orchestration import get_client
import asyncio

# Add project root to Python path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
    colorize=True,
    backtrace=True,
    diagnose=True
)

# Import after path setup
from src.data.data_manager import collect_market_data, store_market_data
from src.data.yahoo_finance_loader import YahooFinanceDataLoader


def generate_flow_run_name(flow_prefix: str) -> str:
    return f"{flow_prefix}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


@flow(flow_run_name=lambda: generate_flow_run_name("data-ingestion"))
def data_ingestion_subflow():
    """Main flow for data ingestion."""
    logger = get_run_logger()
    logger.info("Starting data ingestion flow...")

    try:
        logger.debug("Starting market data collection...")
        data = collect_market_data()
        logger.debug(f"Collected data for symbols: {list(data.keys())}")

        logger.debug("Starting market data storage...")
        store_market_data(data)

        logger.info("Data ingestion flow completed successfully")
    except Exception as e:
        logger.error(f"Error in data ingestion flow: {str(e)}")
        raise


@flow(flow_run_name=lambda: generate_flow_run_name("data-ingestion-yahoo-company"))
def data_ingestion_yahoo_company_subflow():
    """Main flow for data ingestion."""
    logger = get_run_logger()
    logger.info("Starting yahoo company data ingestion flow...")

    try:
        loader = YahooFinanceDataLoader()
        loader.run()
        logger.info("Yahoo Data ingestion flow completed successfully")
    except Exception as e:
        logger.error(f"Error in Yahoo data ingestion flow: {str(e)}")
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
    # Simple main block since deployments will be handled by prefect.yaml
    logger.info("Running flows directly (not for deployment)")

    if not asyncio.run(check_prefect_server()):
        logger.error("Cannot connect to Prefect server")
        sys.exit(1)

    # Run flows directly if needed
    data_ingestion_subflow()
    data_ingestion_yahoo_company_subflow()