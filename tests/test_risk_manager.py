import pytest
import math
from backend.schemas import RiskConfig, PortfolioContext
from backend.trading.risk_manager import RiskManager

@pytest.fixture
def risk_manager():
    return RiskManager(RiskConfig())

@pytest.fixture
def default_portfolio():
    return PortfolioContext(
        account_equity=100000.0,
        daily_realized_pnl=0.0,
        daily_unrealized_pnl=0.0,
        total_portfolio_exposure=0.0,
        open_positions_count=0
    )

def test_buy_position_sizing(risk_manager, default_portfolio):
    # Risk = 100,000 * 1% = 1000
    # Stop distance = 2.0 (ATR) * 2.0 = 4.0
    # Position size = 1000 / 4.0 = 250
    assessment = risk_manager.evaluate_trade("BUY", 150.0, 2.0, default_portfolio)
    assert assessment.approved is True
    assert assessment.quantity == 250
    assert assessment.risk_amount == 1000.0

def test_sell_position_sizing(risk_manager, default_portfolio):
    assessment = risk_manager.evaluate_trade("SELL", 150.0, 2.0, default_portfolio)
    assert assessment.approved is True
    assert assessment.quantity == 250

def test_atr_based_stop_loss_buy(risk_manager, default_portfolio):
    assessment = risk_manager.evaluate_trade("BUY", 100.0, 5.0, default_portfolio)
    # Stop loss = 100 - (5.0 * 2.0) = 90
    assert assessment.stop_loss == 90.0

def test_atr_based_stop_loss_sell(risk_manager, default_portfolio):
    assessment = risk_manager.evaluate_trade("SELL", 100.0, 5.0, default_portfolio)
    # Stop loss = 100 + (5.0 * 2.0) = 110
    assert assessment.stop_loss == 110.0

def test_buy_take_profit(risk_manager, default_portfolio):
    assessment = risk_manager.evaluate_trade("BUY", 100.0, 5.0, default_portfolio)
    # risk_per_unit = 10
    # Take profit = 100 + (10 * 2.0) = 120
    assert assessment.take_profit == 120.0

def test_sell_take_profit(risk_manager, default_portfolio):
    assessment = risk_manager.evaluate_trade("SELL", 100.0, 5.0, default_portfolio)
    # risk_per_unit = 10
    # Take profit = 100 - (10 * 2.0) = 80
    assert assessment.take_profit == 80.0

def test_correct_risk_reward_calculation(default_portfolio):
    config = RiskConfig(take_profit_risk_reward_ratio=3.0)
    rm = RiskManager(config)
    assessment = rm.evaluate_trade("BUY", 100.0, 5.0, default_portfolio)
    assert assessment.take_profit == 130.0

def test_zero_atr_rejection(risk_manager, default_portfolio):
    assessment = risk_manager.evaluate_trade("BUY", 100.0, 0.0, default_portfolio)
    assert assessment.approved is False
    assert "ATR" in assessment.reason

def test_invalid_price_rejection(risk_manager, default_portfolio):
    assessment = risk_manager.evaluate_trade("BUY", -50.0, 5.0, default_portfolio)
    assert assessment.approved is False
    assert "price" in assessment.reason.lower()

def test_insufficient_account_equity(risk_manager):
    portfolio = PortfolioContext(
        account_equity=0.0,
        daily_realized_pnl=0.0,
        daily_unrealized_pnl=0.0,
        total_portfolio_exposure=0.0,
        open_positions_count=0
    )
    assessment = risk_manager.evaluate_trade("BUY", 100.0, 5.0, portfolio)
    assert assessment.approved is False
    assert "non-positive" in assessment.reason.lower()

def test_maximum_daily_loss_rejection(risk_manager):
    portfolio = PortfolioContext(
        account_equity=100000.0,
        daily_realized_pnl=-2000.0,
        daily_unrealized_pnl=-1100.0, # Total loss = -3100, Max allowed = -3000
        total_portfolio_exposure=0.0,
        open_positions_count=0
    )
    assessment = risk_manager.evaluate_trade("BUY", 100.0, 5.0, portfolio)
    assert assessment.approved is False
    assert "daily loss" in assessment.reason.lower()

def test_maximum_portfolio_exposure_rejection(risk_manager):
    portfolio = PortfolioContext(
        account_equity=100000.0,
        daily_realized_pnl=0.0,
        daily_unrealized_pnl=0.0,
        total_portfolio_exposure=45000.0, # Max allowed = 50000
        open_positions_count=1
    )
    # 250 units * 150 price = 37500 exposure. 45000 + 37500 = 82500 > 50000
    assessment = risk_manager.evaluate_trade("BUY", 150.0, 2.0, portfolio)
    assert assessment.approved is False
    assert "exposure" in assessment.reason.lower()

def test_maximum_open_positions_rejection(risk_manager):
    portfolio = PortfolioContext(
        account_equity=100000.0,
        daily_realized_pnl=0.0,
        daily_unrealized_pnl=0.0,
        total_portfolio_exposure=0.0,
        open_positions_count=5 # Max allowed is 5
    )
    assessment = risk_manager.evaluate_trade("BUY", 100.0, 5.0, portfolio)
    assert assessment.approved is False
    assert "open positions" in assessment.reason.lower()

def test_valid_trade_approval(risk_manager, default_portfolio):
    assessment = risk_manager.evaluate_trade("BUY", 100.0, 5.0, default_portfolio)
    assert assessment.approved is True
    assert assessment.quantity == 100 # 1000 risk / 10 risk_per_unit
    assert assessment.entry_price == 100.0

def test_invalid_unsupported_signal(risk_manager, default_portfolio):
    assessment = risk_manager.evaluate_trade("HOLD", 100.0, 5.0, default_portfolio)
    assert assessment.approved is False
    assert "Unsupported" in assessment.reason
