"""
Database manager module for handling PostgreSQL connections and operations.
"""
from contextlib import contextmanager
from typing import Generator, Optional, Dict, Any
import os
from pathlib import Path
import yaml
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from loguru import logger
from dotenv import load_dotenv

from src.database.models import Base


class DatabaseManager:
    """Manages database connections and operations."""

    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure only one database connection."""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the database manager if not already initialized."""
        if self._initialized:
            return

        self.config_path = str(Path(__file__).parent.parent.parent / "config" / "config.yaml")
        self.engine = None
        self.SessionLocal = None

        # Load environment variables from .env file
        env_path = Path(__file__).parent.parent.parent / "config" / ".env"
        load_dotenv(env_path)

        self._load_config()
        self._initialize_connection()
        self._initialized = True

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
                f"{self.db_config['host']}:{self.db_config['port']}/{self.db_config['name']}"
            )

            self.engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=self.db_config.get('pool_size', 5),
                max_overflow=self.db_config.get('max_overflow', 10),
                pool_timeout=30,
                pool_recycle=1800
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

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a database session with automatic cleanup.

        Yields:
            Session: SQLAlchemy session object
        """
        if not self.SessionLocal:
            raise RuntimeError("Database connection not initialized")

        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

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

    def init_database(self) -> None:
        """Initialize database tables."""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")

            # Add unique constraint if it doesn't exist
            self._add_unique_constraint()
        except Exception as e:
            logger.error(f"Failed to initialize database tables: {e}")
            raise

    def _add_unique_constraint(self) -> None:
        """Add unique constraint to market_data table if it doesn't exist."""
        try:
            # Check if constraint already exists
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 1
                    FROM information_schema.table_constraints
                    WHERE constraint_name = 'uix_market_data_symbol_timestamp'
                    AND table_name = 'market_data'
                """))
                if not result.scalar():
                    # Read and execute the migration script
                    migration_path = Path(__file__).parent / "sql" / "add_unique_constraint.sql"
                    with open(migration_path, 'r') as f:
                        migration_sql = f.read()
                    conn.execute(text(migration_sql))
                    conn.commit()
                    logger.info("Added unique constraint to market_data table")
        except Exception as e:
            logger.error(f"Failed to add unique constraint: {e}")
            raise

    def close(self) -> None:
        """Close all database connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")
            self._initialized = False
            DatabaseManager._instance = None