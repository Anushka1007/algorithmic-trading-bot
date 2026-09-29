import pytest
import pandas as pd
import numpy as np
from backend.schemas import HistoricalData, OHLCV
from backend.trading.indicators import calculate_ema, calculate_rsi, calculate_macd, calculate_atr, apply_all_indicators
from backend.trading.strategy import generate_signal, StrategyConfig

from datetime import datetime, timedelta

def generate_mock_history(size: int, trend: str = "flat") -> HistoricalData:
    data = []
    price = 100.0
    start_date = datetime(2021, 1, 1)
    for i in range(size):
        if trend == "bullish":
            price += 1.0
        elif trend == "bearish":
            price -= 1.0
        elif trend == "mixed":
            price += 1.0 if i < size/2 else -1.0
        # flat keeps price at 100.0
        
        current_date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        data.append(OHLCV(
            datetime=current_date,
            open=price - 0.5,
            high=price + 1.0,
            low=price - 1.0,
            close=price,
            volume=1000
        ))
    return HistoricalData(symbol="TEST", interval="1day", data=data)

def test_calculate_ema():
    series = pd.Series([10.0, 10.0, 10.0, 10.0])
    ema = calculate_ema(series, 2)
    assert round(ema.iloc[-1], 2) == 10.0

    series2 = pd.Series([10.0, 20.0, 30.0])
    ema2 = calculate_ema(series2, 2)
    assert ema2.iloc[-1] > 20.0

def test_calculate_rsi():
    bullish = pd.Series([10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24])
    rsi_bull = calculate_rsi(bullish, 14).iloc[-1]
    assert rsi_bull == 100.0

    bearish = pd.Series([24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10])
    rsi_bear = calculate_rsi(bearish, 14).iloc[-1]
    assert rsi_bear == 0.0

def test_calculate_macd():
    series = pd.Series(range(100))
    macd, signal = calculate_macd(series, 12, 26, 9)
    assert len(macd) == 100
    assert len(signal) == 100
    assert not pd.isna(macd.iloc[-1])
    assert not pd.isna(signal.iloc[-1])

def test_calculate_atr():
    df = pd.DataFrame({
        'high': [12, 12, 12],
        'low': [10, 10, 10],
        'close': [11, 11, 11]
    })
    atr = calculate_atr(df, 14)
    assert round(atr.iloc[-1], 2) == 2.0

def test_insufficient_data():
    short_history = generate_mock_history(20, "flat")
    signal = generate_signal("TEST", short_history)
    assert signal.signal == "HOLD"
    assert "Insufficient historical data" in signal.reasons[0]

def test_buy_signal():
    history = generate_mock_history(100, "bullish")
    config = StrategyConfig()
    config.rsi_overbought = 100.0
    signal = generate_signal("TEST", history, config)
    
    assert signal.signal == "BUY"
    assert "MACD is bullish" in str(signal.reasons)

def test_sell_signal():
    history = generate_mock_history(100, "bearish")
    config = StrategyConfig()
    config.rsi_oversold = 0.0
    signal = generate_signal("TEST", history, config)
    
    assert signal.signal == "SELL"
    assert "MACD is bearish" in str(signal.reasons)

def test_hold_signal_flat():
    history = generate_mock_history(100, "flat")
    signal = generate_signal("TEST", history)
    assert signal.signal == "HOLD"
    assert "Indicators are not fully computed" in signal.reasons[0]

def test_hold_signal_mixed():
    history = generate_mock_history(100, "mixed")
    signal = generate_signal("TEST", history)
    assert signal.signal == "HOLD"
    assert "Trend and momentum conditions are not fully aligned" in signal.reasons[0]

def test_lookahead_bias():
    history = generate_mock_history(100, "bullish")
    df = pd.DataFrame([vars(c) for c in history.data])
    df_full = apply_all_indicators(df)
    
    df_partial = apply_all_indicators(df.iloc[:-10])
    
    pd.testing.assert_series_equal(df_full['ema20'].iloc[:-10], df_partial['ema20'])
    pd.testing.assert_series_equal(df_full['rsi'].iloc[:-10], df_partial['rsi'])
