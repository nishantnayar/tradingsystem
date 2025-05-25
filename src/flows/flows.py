from datetime import datetime
import sys
from pathlib import Path
from typing import Optional

from prefect import flow, get_run_logger
from prefect_dask import DaskTaskRunner

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.flows.hourly_data_collection import hourly_data_collection_flow
from src.utils.config import get_config


def generate_flow_run_name(flow_prefix: str) -> str:
    """Generate a descriptive flow run name for debugging."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    return f"{flow_prefix}-{timestamp}"


@flow(
    name="Trading System Orchestrator",
    flow_run_name=lambda: generate_flow_run_name("trading-system"),
    task_runner=DaskTaskRunner(cluster_kwargs={"n_workers": 3, "processes": False})
)
def trading_system_flow(
    run_hourly: bool = True,
    run_daily: bool = False,
    test_mode: bool = False
):
    """
    Main orchestrator flow that manages all trading system flows.
    
    Args:
        run_hourly: Whether to run hourly data collection
        run_daily: Whether to run daily maintenance tasks
        test_mode: Whether to run in test mode with limited symbols
    """
    logger = get_run_logger()
    logger.info("Starting Trading System Orchestrator")
    
    try:
        # Load configuration
        config = get_config()
        
        # Run hourly data collection if requested
        if run_hourly:
            logger.info("Starting hourly data collection flow")
            hourly_data_collection_flow()
            logger.info("Hourly data collection flow completed")
        
        # TODO: Add daily maintenance flow when implemented
        if run_daily:
            logger.info("Daily maintenance flow not yet implemented")
            # daily_maintenance_flow()
        
        logger.info("Trading System Orchestrator completed successfully")
        
    except Exception as e:
        logger.error(f"Error in Trading System Orchestrator: {str(e)}")
        raise


if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="Run trading system flows")
    parser.add_argument("--hourly", action="store_true", help="Run hourly data collection")
    parser.add_argument("--daily", action="store_true", help="Run daily maintenance")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    
    args = parser.parse_args()
    
    # If no specific flow is requested, run hourly by default
    if not (args.hourly or args.daily):
        args.hourly = True
    
    trading_system_flow(
        run_hourly=args.hourly,
        run_daily=args.daily,
        test_mode=args.test
    ) 