import pandas as pd
from backend.schemas import HistoricalData, SignalResponse, IndicatorValues
from backend.trading.indicators import apply_all_indicators
import math

class StrategyConfig:
    rsi_overbought = 70.0
    rsi_bullish_min = 50.0
    rsi_oversold = 30.0
    rsi_bearish_max = 50.0

def generate_signal(symbol: str, history: HistoricalData, config: StrategyConfig = None) -> SignalResponse:
    if config is None:
        config = StrategyConfig()

    if len(history.data) < 50:
        return SignalResponse(
            symbol=symbol,
            signal="HOLD",
            price=0.0,
            timestamp="",
            indicators=IndicatorValues(),
            reasons=["Insufficient historical data (less than 50 candles)."]
        )

    # Convert to DataFrame
    # Twelve Data returns newest first by default in 'values', so we reverse it to chronological order.
    # We rely on datetime string sorting just in case, or simply reverse the list.
    df = pd.DataFrame([vars(candle) for candle in history.data])
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values(by='datetime', ascending=True).reset_index(drop=True)

    df = apply_all_indicators(df)
    
    # Get the latest candle
    latest = df.iloc[-1]
    
    price = float(latest['close'])
    timestamp = str(latest['datetime'])
    
    def safe_float(val):
        return None if math.isnan(val) else float(val)

    indicators = IndicatorValues(
        ema20=safe_float(latest['ema20']),
        ema50=safe_float(latest['ema50']),
        rsi=safe_float(latest['rsi']),
        macd=safe_float(latest['macd']),
        macd_signal=safe_float(latest['macd_signal']),
        atr=safe_float(latest['atr'])
    )

def evaluate_row_signal(latest: pd.Series, price: float, config: StrategyConfig) -> tuple[str, list[str]]:
    signal = "HOLD"
    reasons = []

    if pd.isna(latest['ema50']) or pd.isna(latest['rsi']) or pd.isna(latest['macd']):
        return "HOLD", ["Indicators are not fully computed (likely insufficient data history)."]

    is_bullish_price = price > latest['ema20']
    is_bullish_trend = latest['ema20'] > latest['ema50']
    is_bullish_macd = latest['macd'] > latest['macd_signal']
    is_bullish_rsi = config.rsi_bullish_min <= latest['rsi'] <= config.rsi_overbought

    is_bearish_price = price < latest['ema20']
    is_bearish_trend = latest['ema20'] < latest['ema50']
    is_bearish_macd = latest['macd'] < latest['macd_signal']
    is_bearish_rsi = config.rsi_oversold <= latest['rsi'] <= config.rsi_bearish_max

    if is_bullish_price and is_bullish_trend and is_bullish_macd and is_bullish_rsi:
        signal = "BUY"
        reasons.append(f"Price ({price:.2f}) is above EMA20 ({latest['ema20']:.2f}).")
        reasons.append(f"EMA20 ({latest['ema20']:.2f}) is above EMA50 ({latest['ema50']:.2f}).")
        reasons.append("MACD is bullish (MACD > Signal).")
        reasons.append(f"RSI ({latest['rsi']:.1f}) is in the bullish range (50-70).")
    elif is_bearish_price and is_bearish_trend and is_bearish_macd and is_bearish_rsi:
        signal = "SELL"
        reasons.append(f"Price ({price:.2f}) is below EMA20 ({latest['ema20']:.2f}).")
        reasons.append(f"EMA20 ({latest['ema20']:.2f}) is below EMA50 ({latest['ema50']:.2f}).")
        reasons.append("MACD is bearish (MACD < Signal).")
        reasons.append(f"RSI ({latest['rsi']:.1f}) is in the bearish range (30-50).")
    else:
        signal = "HOLD"
        reasons.append("Trend and momentum conditions are not fully aligned.")
        if not is_bullish_price and not is_bearish_price:
            reasons.append("Price is testing the EMA20 boundary.")
        if latest['rsi'] > config.rsi_overbought:
            reasons.append(f"RSI ({latest['rsi']:.1f}) indicates overbought conditions.")
        if latest['rsi'] < config.rsi_oversold:
            reasons.append(f"RSI ({latest['rsi']:.1f}) indicates oversold conditions.")

    return signal, reasons

def generate_signal(symbol: str, history: HistoricalData, config: StrategyConfig = None) -> SignalResponse:
    if config is None:
        config = StrategyConfig()

    if len(history.data) < 50:
        return SignalResponse(
            symbol=symbol,
            signal="HOLD",
            price=0.0,
            timestamp="",
            indicators=IndicatorValues(),
            reasons=["Insufficient historical data (less than 50 candles)."]
        )

    df = pd.DataFrame([vars(candle) for candle in history.data])
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values(by='datetime', ascending=True).reset_index(drop=True)

    df = apply_all_indicators(df)
    latest = df.iloc[-1]
    
    price = float(latest['close'])
    timestamp = str(latest['datetime'])
    
    def safe_float(val):
        return None if math.isnan(val) else float(val)

    indicators = IndicatorValues(
        ema20=safe_float(latest['ema20']),
        ema50=safe_float(latest['ema50']),
        rsi=safe_float(latest['rsi']),
        macd=safe_float(latest['macd']),
        macd_signal=safe_float(latest['macd_signal']),
        atr=safe_float(latest['atr'])
    )

    signal, reasons = evaluate_row_signal(latest, price, config)

    return SignalResponse(
        symbol=symbol,
        signal=signal,
        price=price,
        timestamp=timestamp,
        indicators=indicators,
        reasons=reasons
    )
