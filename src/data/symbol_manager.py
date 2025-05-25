from datetime import datetime
from typing import List, Optional
import sys
from pathlib import Path

from loguru import logger
from sqlalchemy.orm import Session
sys.path.append(str(Path(__file__).parent.parent))

from src.database.db_manager import DatabaseManager
from src.database.models import Symbol


class SymbolManager:
    """Manages trading symbols in the database."""

    @staticmethod
    def add_symbol(symbol: str, name: Optional[str] = None) -> Symbol:
        """Add a new symbol to the database."""
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
    def deactivate_symbol(symbol: str) -> bool:
        """Deactivate a symbol (mark as delisted)."""
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
    def get_active_symbols() -> List[str]:
        """Get list of active symbols."""
        logger.debug("Retrieving active symbols from database")
        db = DatabaseManager()
        with db.get_session() as session:
            symbols = session.query(Symbol).filter_by(is_active=True).all()
            symbol_list = [s.symbol for s in symbols]
            logger.debug(f"Found {len(symbol_list)} active symbols: {symbol_list}")
            return symbol_list

    @staticmethod
    def get_symbol_info(symbol: str) -> Optional[Symbol]:
        """Get detailed information about a symbol."""
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
    def update_symbol_name(symbol: str, name: str) -> bool:
        """Update the name of a symbol."""
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