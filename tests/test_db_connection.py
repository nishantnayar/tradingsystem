"""
Test script to verify database connectivity.
"""
import sys
from pathlib import Path
import os
from dotenv import load_dotenv
from sqlalchemy import text

sys.path.append(str(Path(__file__).parent.parent))

from src.database.db_manager import DatabaseManager
from src.utils.logger import setup_logging


def test_database_connection():
    """Test database connection and basic operations."""
    # Setup logging
    setup_logging()

    # Load environment variables
    env_path = Path(__file__).parent.parent / "config" / ".env"
    if not env_path.exists():
        print(f"❌ Error: .env file not found at {env_path}")
        return

    load_dotenv(env_path)

    # Check if environment variables are set
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")

    if not db_user or not db_password:
        print("❌ Error: DB_USER or DB_PASSWORD not set in .env file")
        return

    print(f"Using database user: {db_user}")

    # Initialize database manager
    try:
        db_manager = DatabaseManager()
    except Exception as e:
        print(f"❌ Error initializing DatabaseManager: {str(e)}")
        return

    try:
        # Test connection
        if not db_manager.test_connection():
            print("❌ Database connection test failed")
            return
        print("✅ Database connection successful!")

        # Test session creation
        with db_manager.get_session() as session:
            # Execute a simple query
            result = session.execute(text("SELECT version();")).scalar()
            print(f"✅ PostgreSQL version: {result}")

    except Exception as e:
        print(f"❌ Error during database operations: {str(e)}")
    finally:
        db_manager.close()


if __name__ == "__main__":
    test_database_connection()
