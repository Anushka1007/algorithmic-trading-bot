from sqlalchemy import Column, Integer, String, Float, DateTime
from backend.database import Base
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    side = Column(String)
    quantity = Column(Integer)
    price = Column(Float, nullable=True)
    status = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    side = Column(String)
    quantity = Column(Integer)
    price = Column(Float)
    fees = Column(Float)
    realized_pnl = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Position(Base):
    __tablename__ = "positions"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    quantity = Column(Integer, default=0)
    average_entry_price = Column(Float, default=0.0)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)

class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    cash = Column(Float)
    portfolio_value = Column(Float)
    realized_pnl = Column(Float)
    unrealized_pnl = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
