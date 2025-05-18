"""
Database models for the trading system.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Log(Base):
    """Model for storing application logs."""
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    level = Column(String(10), nullable=False)
    message = Column(Text, nullable=False)
    module = Column(String(100), nullable=False)
    function = Column(String(100), nullable=False)
    line_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, **kwargs):
        # Convert timestamp to datetime if it's not already
        if 'timestamp' in kwargs and not isinstance(kwargs['timestamp'], datetime):
            kwargs['timestamp'] = datetime.fromisoformat(str(kwargs['timestamp']))
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Log(timestamp='{self.timestamp}', level='{self.level}', message='{self.message}')>"

class Symbol(Base):
    """Model for managing trading symbols."""
    __tablename__ = "symbols"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Symbol(symbol='{self.symbol}', is_active={self.is_active})>"

class MarketData(Base):
    """Model for storing market data."""
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<MarketData(symbol='{self.symbol}', timestamp='{self.timestamp}')>" 