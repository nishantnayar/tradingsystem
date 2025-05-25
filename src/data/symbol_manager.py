from datetime import datetime
from typing import List, Optional
import sys
from pathlib import Path
import os
from prefect_sqlalchemy import SqlAlchemyConnector

from loguru import logger
from sqlalchemy.orm import Session
sys.path.append(str(Path(__file__).parent.parent))

from src.database.db_manager import DatabaseManager
from src.database.models import Symbol


class SymbolManager:
    """Manages trading symbols in the database."""

    @staticmethod
    async def _ensure_db_credentials():
        """Ensure database credentials are set in environment variables."""
        try:
            # Load database connector from Prefect block
            connector = SqlAlchemyConnector.load("tradingsystemdb")
            
            # Get connection info
            connection_info = connector.connection_info
            
            # Set environment variables for backward compatibility
            os.environ["DB_USER"] = connection_info["username"]
            os.environ["DB_PASSWORD"] = connection_info["password"]
            os.environ["DB_HOST"] = connection_info["host"]
            os.environ["DB_PORT"] = str(connection_info["port"])
            os.environ["DB_NAME"] = connection_info["database"]

            logger.debug(f"Database credentials set for host={connection_info['host']}, port={connection_info['port']}, user={connection_info['username']}, database={connection_info['database']}")
        except Exception as e:
            logger.error(f"Failed to set database credentials: {e}")
            raise

    @staticmethod
    async def add_symbol(symbol: str, name: Optional[str] = None) -> Symbol:
        """Add a new symbol to the database."""
        await SymbolManager._ensure_db_credentials()
        db = DatabaseManager()
        with db.get_session() as session:
            existing_symbol = session.query(Symbol).filter_by(symbol=symbol).first()
            if existing_symbol:
                if not existing_symbol.is_active:
                    existing_symbol.is_active = True
                    existing_symbol.end_date = None
                    session.commit()
                    logger.info(f"Reactivated symbol: {symbol}")
                    return existing_symbol
                logger.warning(f"Symbol already exists: {symbol}")
                return existing_symbol

            new_symbol = Symbol(
                symbol=symbol,
                name=name,
                is_active=True,
                start_date=datetime.utcnow()
            )
            session.add(new_symbol)
            session.commit()
            logger.info(f"Added new symbol: {symbol}")
            return new_symbol

    @staticmethod
    async def deactivate_symbol(symbol: str) -> bool:
        """Deactivate a symbol (mark as delisted)."""
        await SymbolManager._ensure_db_credentials()
        db = DatabaseManager()
        with db.get_session() as session:
            symbol_obj = session.query(Symbol).filter_by(symbol=symbol).first()
            if not symbol_obj:
                logger.warning(f"Symbol not found: {symbol}")
                return False

            symbol_obj.is_active = False
            symbol_obj.end_date = datetime.utcnow()
            session.commit()
            logger.info(f"Deactivated symbol: {symbol}")
            return True

    @staticmethod
    async def get_active_symbols() -> List[str]:
        """Get list of active symbols."""
        logger.debug("Retrieving active symbols from database")
        await SymbolManager._ensure_db_credentials()
        db = DatabaseManager()
        with db.get_session() as session:
            symbols = session.query(Symbol).filter_by(is_active=True).all()
            symbol_list = [s.symbol for s in symbols]
            logger.debug(f"Found {len(symbol_list)} active symbols: {symbol_list}")
            return symbol_list

    @staticmethod
    async def get_symbol_info(symbol: str) -> Optional[Symbol]:
        """Get detailed information about a symbol."""
        await SymbolManager._ensure_db_credentials()
        db = DatabaseManager()
        with db.get_session() as session:
            symbol_obj = session.query(Symbol).filter_by(symbol=symbol).first()
            if symbol_obj:
                # Create a new instance with the same data to avoid session binding issues
                return Symbol(
                    symbol=symbol_obj.symbol,
                    name=symbol_obj.name,
                    is_active=symbol_obj.is_active,
                    start_date=symbol_obj.start_date,
                    end_date=symbol_obj.end_date,
                    created_at=symbol_obj.created_at,
                    updated_at=symbol_obj.updated_at
                )
            return None

    @staticmethod
    async def update_symbol_name(symbol: str, name: str) -> bool:
        """Update the name of a symbol."""
        await SymbolManager._ensure_db_credentials()
        db = DatabaseManager()
        with db.get_session() as session:
            symbol_obj = session.query(Symbol).filter_by(symbol=symbol).first()
            if not symbol_obj:
                logger.warning(f"Symbol not found: {symbol}")
                return False

            symbol_obj.name = name
            session.commit()
            logger.info(f"Updated name for symbol {symbol}: {name}")
            return True 