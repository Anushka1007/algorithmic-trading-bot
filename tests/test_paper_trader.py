import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend import models, schemas
from backend.trading.paper_trader import PaperTrader
from backend.schemas import Quote
from backend.data.twelve_data import TwelveDataClient

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class MockMarketClient:
    def __init__(self):
        self.mock_price = 100.0

    async def get_quote(self, symbol: str) -> Quote:
        return Quote(symbol=symbol, price=self.mock_price, timestamp=123456789)

@pytest_asyncio.fixture
async def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_market():
    return MockMarketClient()

@pytest.mark.asyncio
async def test_buy_order_and_persistence(db, mock_market):
    trader = PaperTrader(db, mock_market)
    trader.config.slippage_percentage = 0.0
    trader.config.fee_percentage = 0.0
    
    req = schemas.PaperOrderRequest(symbol="AAPL", side="BUY", quantity=100)
    await trader.execute_order(req)
    
    # Check persistence
    orders = db.query(models.Order).all()
    assert len(orders) == 1
    assert orders[0].symbol == "AAPL"
    assert orders[0].status == "FILLED"
    
    trades = db.query(models.Trade).all()
    assert len(trades) == 1
    assert trades[0].price == 100.0
    
    positions = db.query(models.Position).all()
    assert len(positions) == 1
    assert positions[0].quantity == 100
    
    snapshot = trader.get_portfolio_snapshot()
    assert snapshot.cash == trader.initial_capital - 10000.0

@pytest.mark.asyncio
async def test_insufficient_cash(db, mock_market):
    trader = PaperTrader(db, mock_market)
    trader.config.slippage_percentage = 0.0
    trader.config.fee_percentage = 0.0
    
    # 2000 * 100 = 200,000 > 100,000 initial capital
    req = schemas.PaperOrderRequest(symbol="AAPL", side="BUY", quantity=2000)
    with pytest.raises(ValueError, match="Insufficient cash"):
        await trader.execute_order(req)
        
    orders = db.query(models.Order).all()
    assert len(orders) == 1
    assert orders[0].status == "REJECTED"
    
    positions = db.query(models.Position).all()
    assert len(positions) == 0

@pytest.mark.asyncio
async def test_sell_order_and_pnl_update(db, mock_market):
    trader = PaperTrader(db, mock_market)
    trader.config.slippage_percentage = 0.0
    trader.config.fee_percentage = 0.0
    
    # Buy 100 @ 100.0
    await trader.execute_order(schemas.PaperOrderRequest(symbol="AAPL", side="BUY", quantity=100))
    
    # Price goes up to 110.0
    mock_market.mock_price = 110.0
    
    # Sell 50 @ 110.0
    await trader.execute_order(schemas.PaperOrderRequest(symbol="AAPL", side="SELL", quantity=50))
    
    positions = db.query(models.Position).all()
    assert len(positions) == 1
    assert positions[0].quantity == 50
    
    snapshot = trader.get_portfolio_snapshot()
    # PNL for 50 shares = 50 * (110 - 100) = 500
    assert snapshot.realized_pnl == 500.0

@pytest.mark.asyncio
async def test_stop_loss_take_profit_auto_close(db, mock_market):
    trader = PaperTrader(db, mock_market)
    trader.config.slippage_percentage = 0.0
    trader.config.fee_percentage = 0.0
    
    # Buy 100 @ 100.0 with SL 90.0 and TP 120.0
    await trader.execute_order(schemas.PaperOrderRequest(
        symbol="AAPL", side="BUY", quantity=100, stop_loss=90.0, take_profit=120.0
    ))
    
    # Price hits 120.0 (TP)
    mock_market.mock_price = 120.0
    
    # Update should trigger the sell
    await trader.update_prices_and_stops()
    
    # Position should be closed
    positions = db.query(models.Position).all()
    assert len(positions) == 0
    
    snapshot = trader.get_portfolio_snapshot()
    # PNL = 100 * (120 - 100) = 2000
    assert snapshot.realized_pnl == 2000.0

@pytest.mark.asyncio
async def test_portfolio_status_unrealized_pnl(db, mock_market):
    trader = PaperTrader(db, mock_market)
    trader.config.slippage_percentage = 0.0
    trader.config.fee_percentage = 0.0
    
    await trader.execute_order(schemas.PaperOrderRequest(symbol="AAPL", side="BUY", quantity=100))
    
    mock_market.mock_price = 105.0 # Price goes up by 5
    
    status = await trader.get_portfolio_status()
    
    assert status.unrealized_pnl == 500.0
    assert status.portfolio_value == trader.initial_capital + 500.0
    assert len(status.open_positions) == 1
    assert status.open_positions[0].current_price == 105.0
    assert status.open_positions[0].unrealized_pnl == 500.0
