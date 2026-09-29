import pytest
import pandas as pd
from datetime import datetime, timedelta
from backend.schemas import BacktestConfig, HistoricalData, OHLCV, RiskConfig
from backend.trading.backtester import BacktestEngine

def generate_custom_history(prices: list[float], highs: list[float] = None, lows: list[float] = None) -> HistoricalData:
    data = []
    start_date = datetime(2021, 1, 1)
    for i, p in enumerate(prices):
        h = highs[i] if highs else p + 1.0
        l = lows[i] if lows else p - 1.0
        
        current_date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        data.append(OHLCV(
            datetime=current_date,
            open=p,
            high=h,
            low=l,
            close=p,
            volume=1000
        ))
    return HistoricalData(symbol="TEST", interval="1day", data=data)

def generate_mock_history(size: int, trend: str = "flat") -> HistoricalData:
    prices = []
    price = 100.0
    for i in range(size):
        if trend == "bullish":
            price += 1.0
        elif trend == "bearish":
            price -= 1.0
        elif trend == "mixed":
            price += 1.0 if i < size/2 else -1.0
        prices.append(price)
    return generate_custom_history(prices)

def test_no_trade_scenario():
    # Flat history generates no signals
    history = generate_mock_history(100, "flat")
    engine = BacktestEngine(BacktestConfig())
    result = engine.run("TEST", history)
    
    assert result.metrics.total_trades == 0
    assert result.metrics.total_pnl == 0.0
    assert len(result.trades) == 0

def test_profitable_trade_and_end_of_backtest_exit():
    # Bullish history triggers a BUY, but because trend never breaks, it exits at the end of backtest.
    history = generate_mock_history(100, "bullish")
    
    config = BacktestConfig(fee_percentage=0.0, slippage_percentage=0.0)
    config.risk_config.max_portfolio_exposure_percent = 100.0
    # Make it impossible to hit SL/TP prematurely by giving a huge multiplier
    config.risk_config.stop_loss_atr_multiplier = 100.0
    config.risk_config.take_profit_risk_reward_ratio = 100.0
    
    engine = BacktestEngine(config)
    # We also need to hack the strategy config to allow RSI 100 to still be bullish
    engine.strategy_config.rsi_overbought = 100.0
    
    result = engine.run("TEST", history)
    
    # We should have exactly 1 trade that closed at the end
    assert result.metrics.total_trades == 1
    trade = result.trades[0]
    assert trade.exit_reason == "END_OF_BACKTEST"
    assert trade.pnl > 0
    assert result.metrics.winning_trades == 1

def test_take_profit_and_stop_loss():
    # Create custom history.
    # First 60 candles to build EMA
    prices = [100.0 + i * 0.1 for i in range(60)]
    
    # At index 59, it's a BUY signal because EMA20 > EMA50, price > EMA20.
    # Entry will be at index 60 OPEN.
    prices.append(106.0) # Index 60 open
    highs = [p + 1.0 for p in prices]
    lows = [p - 1.0 for p in prices]
    
    # Modify index 60 to have a huge high to hit TP
    highs[60] = 200.0
    
    history = generate_custom_history(prices, highs, lows)
    
    config = BacktestConfig(fee_percentage=0.0, slippage_percentage=0.0)
    config.risk_config.take_profit_risk_reward_ratio = 1.0
    engine = BacktestEngine(config)
    engine.strategy_config.rsi_overbought = 100.0
    
    result = engine.run("TEST", history)
    
    assert len(result.trades) >= 1
    assert result.trades[0].exit_reason == "TAKE_PROFIT"

def test_same_candle_sl_tp_conflict():
    prices = [100.0 + i * 0.1 for i in range(60)]
    prices.append(106.0) # Index 60 open
    
    highs = [p + 1.0 for p in prices]
    lows = [p - 1.0 for p in prices]
    
    # Modify index 60 to hit both TP and SL
    highs[60] = 200.0
    lows[60] = 10.0
    
    history = generate_custom_history(prices, highs, lows)
    
    config = BacktestConfig(fee_percentage=0.0, slippage_percentage=0.0)
    engine = BacktestEngine(config)
    engine.strategy_config.rsi_overbought = 100.0
    
    result = engine.run("TEST", history)
    
    # It must assume STOP_LOSS was hit first
    assert len(result.trades) >= 1
    assert result.trades[0].exit_reason == "STOP_LOSS"

def test_signal_exit():
    # 60 bullish candles, then massive drop to trigger SELL
    prices = [100.0 + i * 0.1 for i in range(60)]
    # Next 10 candles drop fast to cross EMAs
    prices.extend([106.0 - i * 5.0 for i in range(1, 11)])
    
    history = generate_custom_history(prices)
    
    config = BacktestConfig(fee_percentage=0.0, slippage_percentage=0.0)
    config.risk_config.stop_loss_atr_multiplier = 100.0 # prevent SL hit
    engine = BacktestEngine(config)
    engine.strategy_config.rsi_overbought = 100.0
    engine.strategy_config.rsi_oversold = 0.0
    
    result = engine.run("TEST", history)
    
    assert len(result.trades) >= 1
    # It should exit via signal because EMA crosses
    assert any(t.exit_reason == "SIGNAL_EXIT" for t in result.trades)

def test_fees_and_slippage():
    prices = [100.0 + i * 0.1 for i in range(60)]
    prices.append(106.0)
    history = generate_custom_history(prices)
    
    config_clean = BacktestConfig(fee_percentage=0.0, slippage_percentage=0.0)
    config_fees = BacktestConfig(fee_percentage=1.0, slippage_percentage=1.0) # 1% fee, 1% slippage
    
    engine_clean = BacktestEngine(config_clean)
    engine_clean.strategy_config.rsi_overbought = 100.0
    res_clean = engine_clean.run("TEST", history)
    
    engine_fees = BacktestEngine(config_fees)
    engine_fees.strategy_config.rsi_overbought = 100.0
    res_fees = engine_fees.run("TEST", history)
    
    trade_clean = res_clean.trades[0]
    trade_fees = res_fees.trades[0]
    
    # With 1% slippage, entry price should be exactly 1% higher
    assert round(trade_fees.entry_price, 2) == round(trade_clean.entry_price * 1.01, 2)
    # Fees should be > 0
    assert trade_fees.fees > 0.0

def test_metrics_no_nan_infinity():
    # Even with zero trades, metrics should be clean
    history = generate_mock_history(100, "flat")
    engine = BacktestEngine(BacktestConfig())
    result = engine.run("TEST", history)
    
    m = result.metrics
    import math
    assert not math.isnan(m.win_rate_percent)
    assert not math.isinf(m.profit_factor)
    assert not math.isnan(m.sharpe_ratio)
    assert m.sharpe_ratio == 0.0
    assert m.profit_factor == 0.0

def test_insufficient_cash():
    history = generate_mock_history(100, "bullish")
    
    config = BacktestConfig()
    # Risk 100% per trade means position sizing will try to use all cash
    # If we add slippage/fees, the cost will exceed cash
    config.risk_config.risk_per_trade_percent = 100.0
    config.fee_percentage = 5.0
    config.slippage_percentage = 5.0
    
    engine = BacktestEngine(config)
    engine.strategy_config.rsi_overbought = 100.0
    
    result = engine.run("TEST", history)
    
    # Should not be able to enter any trade because cash < cost + fees
    assert result.metrics.total_trades == 0
