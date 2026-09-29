from pydantic import BaseModel
from typing import List, Optional

class Quote(BaseModel):
    symbol: str
    price: float
    timestamp: int
    is_live: bool = False
    source: str = "Twelve Data"

class OHLCV(BaseModel):
    datetime: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class HistoricalData(BaseModel):
    symbol: str
    interval: str
    data: List[OHLCV]
    is_cached: bool = False

class IndicatorValues(BaseModel):
    ema20: Optional[float] = None
    ema50: Optional[float] = None
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    atr: Optional[float] = None

class SignalResponse(BaseModel):
    symbol: str
    signal: str
    price: float
    timestamp: str
    indicators: IndicatorValues
    reasons: List[str]

class RiskConfig(BaseModel):
    initial_capital: float = 100000.0
    risk_per_trade_percent: float = 1.0
    max_daily_loss_percent: float = 3.0
    max_portfolio_exposure_percent: float = 50.0
    max_open_positions: int = 5
    stop_loss_atr_multiplier: float = 2.0
    take_profit_risk_reward_ratio: float = 2.0

class PortfolioContext(BaseModel):
    account_equity: float
    daily_realized_pnl: float
    daily_unrealized_pnl: float
    total_portfolio_exposure: float
    open_positions_count: int

class RiskAssessment(BaseModel):
    approved: bool
    reason: str
    quantity: int = 0
    entry_price: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    risk_amount: float = 0.0

class BacktestConfig(BaseModel):
    initial_capital: float = 100000.0
    fee_percentage: float = 0.1
    slippage_percentage: float = 0.05
    risk_config: RiskConfig = RiskConfig()

class BacktestRequest(BaseModel):
    symbol: str
    interval: str = "1day"
    outputsize: int = 500
    config: BacktestConfig = BacktestConfig()

class TradeRecord(BaseModel):
    symbol: str
    side: str
    quantity: int
    entry_timestamp: str
    exit_timestamp: str
    entry_price: float
    exit_price: float
    fees: float
    pnl: float
    return_percentage: float
    exit_reason: str

class EquityPoint(BaseModel):
    timestamp: str
    equity: float

class BacktestMetrics(BaseModel):
    initial_capital: float
    final_capital: float
    total_pnl: float
    total_return_percent: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate_percent: float
    average_winning_trade: float
    average_losing_trade: float
    profit_factor: float
    max_drawdown_percent: float
    sharpe_ratio: float

class BacktestResult(BaseModel):
    symbol: str
    configuration: BacktestConfig
    metrics: BacktestMetrics
    trades: List[TradeRecord]
    equity_curve: List[EquityPoint]

class PaperOrderRequest(BaseModel):
    symbol: str
    side: str
    quantity: int
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class PositionResponse(BaseModel):
    symbol: str
    quantity: int
    average_entry_price: float
    current_price: float
    unrealized_pnl: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class PortfolioResponse(BaseModel):
    cash: float
    portfolio_value: float
    realized_pnl: float
    unrealized_pnl: float
    total_return: float
    open_positions: List[PositionResponse]

class AIChatRequest(BaseModel):
    message: str
    symbol: Optional[str] = None

class AIChatResponse(BaseModel):
    reply: str
