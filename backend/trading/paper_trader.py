from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict

from backend import models, schemas
from backend.data.twelve_data import TwelveDataClient
from backend.schemas import BacktestConfig

class PaperTrader:
    def __init__(self, db: Session, market_client: TwelveDataClient):
        self.db = db
        self.market_client = market_client
        # Reuse BacktestConfig for fees and slippage
        self.config = BacktestConfig() 
        self.initial_capital = self.config.initial_capital

    def get_portfolio_snapshot(self) -> models.PortfolioSnapshot:
        snapshot = self.db.query(models.PortfolioSnapshot).order_by(models.PortfolioSnapshot.id.desc()).first()
        if not snapshot:
            snapshot = models.PortfolioSnapshot(
                cash=self.initial_capital,
                portfolio_value=self.initial_capital,
                realized_pnl=0.0,
                unrealized_pnl=0.0
            )
            self.db.add(snapshot)
            self.db.commit()
            self.db.refresh(snapshot)
        return snapshot

    def _create_snapshot(self, cash: float, portfolio_value: float, realized_pnl: float, unrealized_pnl: float):
        snapshot = models.PortfolioSnapshot(
            cash=cash,
            portfolio_value=portfolio_value,
            realized_pnl=realized_pnl,
            unrealized_pnl=unrealized_pnl
        )
        self.db.add(snapshot)
        self.db.commit()

    async def get_portfolio_status(self) -> schemas.PortfolioResponse:
        await self.update_prices_and_stops()
        
        snapshot = self.get_portfolio_snapshot()
        positions = self.db.query(models.Position).filter(models.Position.quantity > 0).all()
        
        pos_responses = []
        total_unrealized = 0.0
        
        for p in positions:
            # We already updated prices in update_prices_and_stops, but we'll fetch again for response
            try:
                quote = await self.market_client.get_quote(p.symbol)
                current_price = quote.price
            except:
                current_price = p.average_entry_price
            
            unrealized = (current_price - p.average_entry_price) * p.quantity
            total_unrealized += unrealized
            
            pos_responses.append(schemas.PositionResponse(
                symbol=p.symbol,
                quantity=p.quantity,
                average_entry_price=p.average_entry_price,
                current_price=current_price,
                unrealized_pnl=unrealized,
                stop_loss=p.stop_loss,
                take_profit=p.take_profit
            ))
            
        portfolio_val = snapshot.cash + sum(p.quantity * p.average_entry_price for p in positions) + total_unrealized
        
        # Save a new snapshot for accurate tracking
        self._create_snapshot(snapshot.cash, portfolio_val, snapshot.realized_pnl, total_unrealized)
        
        return schemas.PortfolioResponse(
            cash=snapshot.cash,
            portfolio_value=portfolio_val,
            realized_pnl=snapshot.realized_pnl,
            unrealized_pnl=total_unrealized,
            total_return=((portfolio_val / self.initial_capital) - 1.0) * 100.0,
            open_positions=pos_responses
        )

    async def execute_order(self, req: schemas.PaperOrderRequest):
        quote = await self.market_client.get_quote(req.symbol)
        market_price = quote.price
        
        snapshot = self.get_portfolio_snapshot()
        
        if req.side == "BUY":
            entry_price = market_price * (1.0 + self.config.slippage_percentage / 100.0)
            cost = entry_price * req.quantity
            fees = cost * (self.config.fee_percentage / 100.0)
            
            if snapshot.cash < cost + fees:
                order = models.Order(symbol=req.symbol, side="BUY", quantity=req.quantity, price=entry_price, status="REJECTED")
                self.db.add(order)
                self.db.commit()
                raise ValueError("Insufficient cash for this order.")
                
            snapshot.cash -= (cost + fees)
            
            # Record Order
            order = models.Order(symbol=req.symbol, side="BUY", quantity=req.quantity, price=entry_price, status="FILLED")
            self.db.add(order)
            
            # Record Trade
            trade = models.Trade(symbol=req.symbol, side="BUY", quantity=req.quantity, price=entry_price, fees=fees, realized_pnl=0.0)
            self.db.add(trade)
            
            # Update Position
            pos = self.db.query(models.Position).filter(models.Position.symbol == req.symbol).first()
            if not pos:
                pos = models.Position(symbol=req.symbol, quantity=req.quantity, average_entry_price=entry_price, stop_loss=req.stop_loss, take_profit=req.take_profit)
                self.db.add(pos)
            else:
                total_cost = (pos.quantity * pos.average_entry_price) + cost
                pos.quantity += req.quantity
                pos.average_entry_price = total_cost / pos.quantity
                if req.stop_loss: pos.stop_loss = req.stop_loss
                if req.take_profit: pos.take_profit = req.take_profit
                
            self.db.commit()
            
        elif req.side == "SELL":
            pos = self.db.query(models.Position).filter(models.Position.symbol == req.symbol).first()
            if not pos or pos.quantity < req.quantity:
                order = models.Order(symbol=req.symbol, side="SELL", quantity=req.quantity, price=market_price, status="REJECTED")
                self.db.add(order)
                self.db.commit()
                raise ValueError("Insufficient position quantity to sell.")
                
            exit_price = market_price * (1.0 - self.config.slippage_percentage / 100.0)
            revenue = exit_price * req.quantity
            fees = revenue * (self.config.fee_percentage / 100.0)
            pnl = (exit_price - pos.average_entry_price) * req.quantity - fees
            
            snapshot.cash += (revenue - fees)
            snapshot.realized_pnl += pnl
            
            order = models.Order(symbol=req.symbol, side="SELL", quantity=req.quantity, price=exit_price, status="FILLED")
            self.db.add(order)
            
            trade = models.Trade(symbol=req.symbol, side="SELL", quantity=req.quantity, price=exit_price, fees=fees, realized_pnl=pnl)
            self.db.add(trade)
            
            pos.quantity -= req.quantity
            if pos.quantity == 0:
                self.db.delete(pos)
                
            self.db.commit()
            
        self._create_snapshot(snapshot.cash, snapshot.portfolio_value, snapshot.realized_pnl, snapshot.unrealized_pnl)
        return {"status": "success", "message": "Order executed successfully."}

    async def update_prices_and_stops(self):
        positions = self.db.query(models.Position).filter(models.Position.quantity > 0).all()
        if not positions:
            return
            
        for pos in positions:
            try:
                quote = await self.market_client.get_quote(pos.symbol)
            except:
                continue
                
            current_price = quote.price
            
            sl_hit = pos.stop_loss and current_price <= pos.stop_loss
            tp_hit = pos.take_profit and current_price >= pos.take_profit
            
            if sl_hit or tp_hit:
                # Trigger SELL order
                try:
                    await self.execute_order(schemas.PaperOrderRequest(
                        symbol=pos.symbol,
                        side="SELL",
                        quantity=pos.quantity
                    ))
                except ValueError:
                    pass # Ignore if it failed for some reason
