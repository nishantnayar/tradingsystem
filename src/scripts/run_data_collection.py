import sys
from pathlib import Path
import os

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Load environment variables from .env file
from dotenv import load_dotenv
from loguru import logger

# Debug: Print current working directory and .env file location
logger.debug(f"Current working directory: {os.getcwd()}")
env_path = project_root / "config" / ".env"
logger.debug(f"Looking for .env file at: {env_path}")

# Load environment variables
load_dotenv(env_path)

# Debug: Print environment variables
logger.debug("Environment variables after loading:")
for var in ["DB_USER", "DB_PASSWORD", "ALPACA_API_KEY", "ALPACA_SECRET_KEY"]:
    logger.debug(f"{var}: {'*' * 5 if os.getenv(var) else 'Not set'}")

from src.data.data_manager import market_data_collection_flow
from src.data.symbol_manager import SymbolManager

def main():
    try:
        # First, add some symbols to track
        symbols = [
            ("AAPL", "Apple Inc."),
            ("MSFT", "Microsoft Corporation"),
            ("GOOGL", "Alphabet Inc."),
            ("AMZN", "Amazon.com Inc."),
            ("META", "Meta Platforms Inc.")
        ]

        # Add symbols to the database
        for symbol, name in symbols:
            SymbolManager.add_symbol(symbol, name)
            logger.info(f"Added symbol: {symbol} ({name})")

        # Run the data collection flow
        logger.info("Starting data collection flow...")
        market_data_collection_flow()
        logger.info("Data collection completed successfully")

    except Exception as e:
        logger.error(f"Error in data collection: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 