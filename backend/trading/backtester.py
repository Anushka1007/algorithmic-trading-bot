import pandas as pd
import numpy as np
import math
from typing import List

from backend.schemas import (
    BacktestConfig, BacktestResult, TradeRecord, EquityPoint, BacktestMetrics,
    HistoricalData, PortfolioContext
)
from backend.trading.indicators import apply_all_indicators
from backend.trading.strategy import evaluate_row_signal, StrategyConfig
from backend.trading.risk_manager import RiskManager

class BacktestEngine:
    def __init__(self, config: BacktestConfig = None):
        self.config = config or BacktestConfig()
        self.risk_manager = RiskManager(self.config.risk_config)
        self.strategy_config = StrategyConfig()

    def run(self, symbol: str, history: HistoricalData) -> BacktestResult:
        if len(history.data) == 0:
            return self._empty_result(symbol)

        df = pd.DataFrame([vars(candle) for candle in history.data])
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.sort_values(by='datetime', ascending=True).reset_index(drop=True)

        df = apply_all_indicators(df)

        equity = self.config.initial_capital
        cash = self.config.initial_capital
        
        trades: List[TradeRecord] = []
        equity_curve: List[EquityPoint] = []
        
        position_quantity = 0
        position_entry_price = 0.0
        position_entry_time = ""
        position_stop_loss = 0.0
        position_take_profit = 0.0

        daily_realized_pnl = 0.0

        pending_signal = None
        pending_quantity = 0
        pending_sl = 0.0
        pending_tp = 0.0

        pending_exit = False

        for i in range(len(df)):
            row = df.iloc[i]
            current_time = str(row['datetime'])
            open_price = float(row['open'])
            high_price = float(row['high'])
            low_price = float(row['low'])
            close_price = float(row['close'])

            # A. Execute pending EXITS from previous candle at OPEN
            if pending_exit and position_quantity > 0:
                exit_price = open_price * (1.0 - self.config.slippage_percentage / 100.0)
                fees = (position_quantity * exit_price) * (self.config.fee_percentage / 100.0)
                pnl = (exit_price - position_entry_price) * position_quantity - fees
                
                cash += (position_quantity * exit_price) - fees
                equity = cash
                daily_realized_pnl += pnl

                trades.append(TradeRecord(
                    symbol=symbol,
                    side="BUY",
                    quantity=position_quantity,
                    entry_timestamp=position_entry_time,
                    exit_timestamp=current_time,
                    entry_price=round(position_entry_price, 2),
                    exit_price=round(exit_price, 2),
                    fees=round(fees, 2),
                    pnl=round(pnl, 2),
                    return_percentage=round((pnl / (position_entry_price * position_quantity)) * 100.0, 2),
                    exit_reason="SIGNAL_EXIT"
                ))

                position_quantity = 0
                pending_exit = False

            # B. Execute pending ENTRIES from previous candle at OPEN
            elif pending_signal == "BUY" and position_quantity == 0:
                entry_price = open_price * (1.0 + self.config.slippage_percentage / 100.0)
                cost = entry_price * pending_quantity
                fees = cost * (self.config.fee_percentage / 100.0)
                
                if cash >= cost + fees:
                    cash -= (cost + fees)
                    position_quantity = pending_quantity
                    position_entry_price = entry_price
                    position_entry_time = current_time
                    position_stop_loss = pending_sl
                    position_take_profit = pending_tp
                
                pending_signal = None
                pending_quantity = 0

            # C. Intrabar checks (Stop Loss / Take Profit)
            if position_quantity > 0:
                sl_hit = low_price <= position_stop_loss
                tp_hit = high_price >= position_take_profit

                if sl_hit or tp_hit:
                    if sl_hit:
                        exit_price = position_stop_loss
                        reason = "STOP_LOSS"
                    else:
                        exit_price = position_take_profit
                        reason = "TAKE_PROFIT"
                    
                    fees = (position_quantity * exit_price) * (self.config.fee_percentage / 100.0)
                    pnl = (exit_price - position_entry_price) * position_quantity - fees
                    
                    cash += (position_quantity * exit_price) - fees
                    equity = cash
                    daily_realized_pnl += pnl

                    trades.append(TradeRecord(
                        symbol=symbol,
                        side="BUY",
                        quantity=position_quantity,
                        entry_timestamp=position_entry_time,
                        exit_timestamp=current_time,
                        entry_price=round(position_entry_price, 2),
                        exit_price=round(exit_price, 2),
                        fees=round(fees, 2),
                        pnl=round(pnl, 2),
                        return_percentage=round((pnl / (position_entry_price * position_quantity)) * 100.0, 2),
                        exit_reason=reason
                    ))
                    position_quantity = 0

            # D. Update Equity Curve at CLOSE
            current_value = position_quantity * close_price
            equity = cash + current_value
            equity_curve.append(EquityPoint(timestamp=current_time, equity=round(equity, 2)))

            # E. Generate Signals at CLOSE (for execution on next OPEN)
            if i < len(df) - 1:
                signal, reasons = evaluate_row_signal(row, close_price, self.strategy_config)
                
                if signal == "BUY" and position_quantity == 0:
                    portfolio = PortfolioContext(
                        account_equity=equity,
                        daily_realized_pnl=daily_realized_pnl,
                        daily_unrealized_pnl=0.0,
                        total_portfolio_exposure=0.0,
                        open_positions_count=0
                    )
                    
                    atr = float(row['atr']) if not pd.isna(row['atr']) else 0.0
                    
                    assessment = self.risk_manager.evaluate_trade(
                        signal="BUY",
                        entry_price=close_price, 
                        atr=atr,
                        portfolio=portfolio
                    )
                    
                    if assessment.approved:
                        pending_signal = "BUY"
                        pending_quantity = assessment.quantity
                        pending_sl = assessment.stop_loss
                        pending_tp = assessment.take_profit
                
                elif signal == "SELL" and position_quantity > 0:
                    pending_exit = True

        # End of backtest: Force close
        if position_quantity > 0:
            last_close = float(df.iloc[-1]['close'])
            last_time = str(df.iloc[-1]['datetime'])
            exit_price = last_close
            fees = (position_quantity * exit_price) * (self.config.fee_percentage / 100.0)
            pnl = (exit_price - position_entry_price) * position_quantity - fees
            
            cash += (position_quantity * exit_price) - fees
            equity = cash
            
            trades.append(TradeRecord(
                symbol=symbol,
                side="BUY",
                quantity=position_quantity,
                entry_timestamp=position_entry_time,
                exit_timestamp=last_time,
                entry_price=round(position_entry_price, 2),
                exit_price=round(exit_price, 2),
                fees=round(fees, 2),
                pnl=round(pnl, 2),
                return_percentage=round((pnl / (position_entry_price * position_quantity)) * 100.0, 2),
                exit_reason="END_OF_BACKTEST"
            ))
            equity_curve[-1].equity = round(equity, 2)

        metrics = self._calculate_metrics(trades)
        
        return BacktestResult(
            symbol=symbol,
            configuration=self.config,
            metrics=metrics,
            trades=trades,
            equity_curve=equity_curve
        )

    def _calculate_metrics(self, trades: List[TradeRecord]) -> BacktestMetrics:
        total_trades = len(trades)
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]
        
        total_pnl = sum(t.pnl for t in trades)
        final_capital = self.config.initial_capital + total_pnl
        total_return_percent = (total_pnl / self.config.initial_capital) * 100.0
        
        win_rate = (len(winning_trades) / total_trades * 100.0) if total_trades > 0 else 0.0
        avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0.0
        avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0.0
        
        gross_profit = sum(t.pnl for t in winning_trades)
        gross_loss = abs(sum(t.pnl for t in losing_trades))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf') if gross_profit > 0 else 0.0
        
        max_dd = 0.0
        peak = self.config.initial_capital
        current_eq = self.config.initial_capital
        for t in trades:
            current_eq += t.pnl
            if current_eq > peak:
                peak = current_eq
            dd = (peak - current_eq) / peak * 100.0
            if dd > max_dd:
                max_dd = dd

        returns = [t.return_percentage / 100.0 for t in trades]
        sharpe = 0.0
        if len(returns) > 1:
            mean_ret = np.mean(returns)
            std_ret = np.std(returns)
            if std_ret > 0:
                sharpe = (mean_ret / std_ret) * math.sqrt(252)

        return BacktestMetrics(
            initial_capital=round(self.config.initial_capital, 2),
            final_capital=round(final_capital, 2),
            total_pnl=round(total_pnl, 2),
            total_return_percent=round(total_return_percent, 2),
            total_trades=total_trades,
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate_percent=round(win_rate, 2),
            average_winning_trade=round(avg_win, 2),
            average_losing_trade=round(avg_loss, 2),
            profit_factor=round(profit_factor, 2),
            max_drawdown_percent=round(max_dd, 2),
            sharpe_ratio=round(sharpe, 2)
        )

    def _empty_result(self, symbol: str) -> BacktestResult:
        metrics = BacktestMetrics(
            initial_capital=self.config.initial_capital,
            final_capital=self.config.initial_capital,
            total_pnl=0.0,
            total_return_percent=0.0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate_percent=0.0,
            average_winning_trade=0.0,
            average_losing_trade=0.0,
            profit_factor=0.0,
            max_drawdown_percent=0.0,
            sharpe_ratio=0.0
        )
        return BacktestResult(
            symbol=symbol,
            configuration=self.config,
            metrics=metrics,
            trades=[],
            equity_curve=[]
        )
