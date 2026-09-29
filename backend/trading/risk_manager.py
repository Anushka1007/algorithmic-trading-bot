import math
from backend.schemas import RiskConfig, PortfolioContext, RiskAssessment

class RiskManager:
    def __init__(self, config: RiskConfig = None):
        self.config = config or RiskConfig()

    def evaluate_trade(
        self,
        signal: str,
        entry_price: float,
        atr: float,
        portfolio: PortfolioContext
    ) -> RiskAssessment:
        
        if signal not in ["BUY", "SELL"]:
            return RiskAssessment(approved=False, reason=f"Unsupported signal type: {signal}")

        if portfolio.account_equity <= 0:
            return RiskAssessment(approved=False, reason="Account equity is non-positive.")
            
        if entry_price <= 0:
            return RiskAssessment(approved=False, reason="Invalid entry price.")

        if not atr or math.isnan(atr) or atr <= 0:
            return RiskAssessment(approved=False, reason="Invalid or zero ATR.")

        # Check maximum daily loss
        total_daily_loss = portfolio.daily_realized_pnl + portfolio.daily_unrealized_pnl
        max_loss_allowed = -1 * (portfolio.account_equity * self.config.max_daily_loss_percent / 100.0)
        if total_daily_loss <= max_loss_allowed:
            return RiskAssessment(approved=False, reason="Maximum daily loss limit reached.")

        # Check maximum open positions
        if portfolio.open_positions_count >= self.config.max_open_positions:
            return RiskAssessment(approved=False, reason="Maximum open positions reached.")

        # Calculate Stops and Targets
        stop_distance = atr * self.config.stop_loss_atr_multiplier
        if stop_distance < 1e-5:
            return RiskAssessment(approved=False, reason="Stop distance is extremely small.")

        if signal == "BUY":
            stop_loss = entry_price - stop_distance
            risk_per_unit = entry_price - stop_loss
            take_profit = entry_price + (risk_per_unit * self.config.take_profit_risk_reward_ratio)
        else: # SELL
            stop_loss = entry_price + stop_distance
            risk_per_unit = stop_loss - entry_price
            take_profit = entry_price - (risk_per_unit * self.config.take_profit_risk_reward_ratio)

        # Calculate Position Size
        risk_amount = portfolio.account_equity * (self.config.risk_per_trade_percent / 100.0)
        position_size = risk_amount / risk_per_unit
        quantity = math.floor(position_size)

        if quantity <= 0:
            return RiskAssessment(approved=False, reason="Calculated position size is zero.")

        # Check Portfolio Exposure
        new_position_value = quantity * entry_price
        max_exposure = portfolio.account_equity * (self.config.max_portfolio_exposure_percent / 100.0)
        if portfolio.total_portfolio_exposure + new_position_value > max_exposure:
            return RiskAssessment(approved=False, reason="Maximum portfolio exposure exceeded.")

        return RiskAssessment(
            approved=True,
            reason="Trade approved.",
            quantity=int(quantity),
            entry_price=round(entry_price, 2),
            stop_loss=round(stop_loss, 2),
            take_profit=round(take_profit, 2),
            risk_amount=round(risk_amount, 2)
        )
