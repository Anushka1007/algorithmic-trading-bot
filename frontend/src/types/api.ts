export interface IndicatorValues {
  ema20: number | null;
  ema50: number | null;
  rsi: number | null;
  macd: number | null;
  macd_signal: number | null;
  atr: number | null;
}

export interface SignalResponse {
  symbol: string;
  signal: 'BUY' | 'SELL' | 'HOLD';
  price: number;
  timestamp: string;
  indicators: IndicatorValues;
  reasons: string[];
}

export interface OHLCV {
  datetime: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Quote {
  symbol: string;
  price: number;
  timestamp: number;
  is_live: boolean;
  source: string;
}

export interface HistoricalData {
  symbol: string;
  interval: string;
  data: OHLCV[];
  is_cached: boolean;
}

export interface PositionResponse {
  symbol: string;
  quantity: number;
  average_entry_price: number;
  current_price: number;
  unrealized_pnl: number;
  stop_loss: number | null;
  take_profit: number | null;
}

export interface PortfolioResponse {
  cash: number;
  portfolio_value: number;
  realized_pnl: number;
  unrealized_pnl: number;
  total_return: number;
  open_positions: PositionResponse[];
}

export interface OrderRequest {
  symbol: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  stop_loss?: number;
  take_profit?: number;
}

export interface Trade {
  id: number;
  symbol: string;
  side: string;
  quantity: number;
  price: number;
  fees: number;
  realized_pnl: number;
  timestamp: string;
}

export interface BacktestRequest {
  symbol: string;
  interval: string;
  outputsize: number;
  config: {
    initial_capital: number;
    fee_percentage: number;
    slippage_percentage: number;
  };
}

export interface BacktestMetrics {
  initial_capital: number;
  final_capital: number;
  total_pnl: number;
  total_return_percent: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate_percent: number;
  profit_factor: number;
  max_drawdown_percent: number;
  sharpe_ratio: number;
}

export interface BacktestResult {
  symbol: string;
  metrics: BacktestMetrics;
  trades: any[];
  equity_curve: any[];
}
