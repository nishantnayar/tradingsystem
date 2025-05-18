"""
Database manager module for handling PostgreSQL connections and operations.
"""
from typing import Optional, Dict, Any
import os
from pathlib import Path
import yaml
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from loguru import logger
from dotenv import load_dotenv


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the database manager.
        
        Args:
            config_path: Path to the configuration file. If None, uses default path.
        """
        self.config_path = config_path or str(Path(__file__).parent.parent.parent / "config" / "config.yaml")
        self.engine = None
        self.SessionLocal = None
        
        # Load environment variables from .env file
        env_path = Path(__file__).parent.parent.parent / "config" / ".env"
        load_dotenv(env_path)
        
        self._load_config()
        self._initialize_connection()

    def _load_config(self) -> None:
        """Load database configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.db_config = config['database']

            # Replace environment variables
            self.db_config['user'] = os.getenv('DB_USER', self.db_config['user'])
            self.db_config['password'] = os.getenv('DB_PASSWORD', self.db_config['password'])

        except Exception as e:
            logger.error(f"Failed to load database configuration: {e}")
            raise

    def _initialize_connection(self) -> None:
        """Initialize database connection and session factory."""
        try:
            connection_string = (
                f"postgresql://{self.db_config['user']}:{self.db_config['password']}@"
                f"{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
            )

            self.engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=self.db_config['pool_size'],
                max_overflow=self.db_config['max_overflow']
            )

            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            logger.info("Database connection initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise

    def get_session(self) -> Session:
        """
        Get a new database session.
        
        Returns:
            Session: SQLAlchemy session object
        """
        if not self.SessionLocal:
            raise RuntimeError("Database connection not initialized")
        return self.SessionLocal()

    def test_connection(self) -> bool:
        """
        Test the database connection.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    def close(self) -> None:
        """Close all database connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")
