from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas
from backend.data.twelve_data import TwelveDataClient
from backend.trading.paper_trader import PaperTrader

router = APIRouter(prefix="/api/paper", tags=["Paper Trading"])

def get_market_client():
    return TwelveDataClient()

@router.post("/orders")
async def place_order(
    request: schemas.PaperOrderRequest,
    db: Session = Depends(get_db),
    client: TwelveDataClient = Depends(get_market_client)
):
    trader = PaperTrader(db, client)
    try:
        result = await trader.execute_order(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to place order: {str(e)}")

@router.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(models.Order).order_by(models.Order.id.desc()).all()
    return orders

@router.get("/trades")
def get_trades(db: Session = Depends(get_db)):
    trades = db.query(models.Trade).order_by(models.Trade.id.desc()).all()
    return trades

@router.get("/positions")
def get_positions(db: Session = Depends(get_db)):
    positions = db.query(models.Position).filter(models.Position.quantity > 0).all()
    return positions

@router.get("/portfolio")
@router.get("/status")
async def get_portfolio_status(
    db: Session = Depends(get_db),
    client: TwelveDataClient = Depends(get_market_client)
):
    trader = PaperTrader(db, client)
    try:
        status = await trader.get_portfolio_status()
        return status
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio status: {str(e)}")

@router.post("/reset")
def reset_paper_trading(db: Session = Depends(get_db)):
    # Simple endpoint for development
    db.query(models.Order).delete()
    db.query(models.Trade).delete()
    db.query(models.Position).delete()
    db.query(models.PortfolioSnapshot).delete()
    db.commit()
    return {"status": "success", "message": "Paper trading data reset successfully."}

import asyncio
import logging
from backend.database import SessionLocal
from backend.trading.strategy import generate_signal

logger = logging.getLogger(__name__)

import datetime

bot_state = {
    "running": False, 
    "task": None,
    "symbol": "AAPL",
    "signal": "-",
    "last_check": None,
    "next_check": None,
    "last_action": "-",
    "error": None
}

async def run_bot_loop():
    symbol = "AAPL"
    bot_state["symbol"] = symbol
    while bot_state["running"]:
        bot_state["last_check"] = datetime.datetime.now().strftime("%H:%M:%S")
        bot_state["error"] = None
        try:
            client = TwelveDataClient()
            db = SessionLocal()
            try:
                history = await client.get_history(symbol, interval="1day", outputsize=100)
                signal_res = generate_signal(symbol, history)
                
                bot_state["signal"] = signal_res.signal
                
                if signal_res.signal in ["BUY", "SELL"]:
                    trader = PaperTrader(db, client)
                    status = await trader.get_portfolio_status()
                    current_position = next((p for p in status.open_positions if p.symbol == symbol), None)
                    
                    should_trade = False
                    reason = ""
                    if signal_res.signal == "BUY":
                        if not current_position:
                            should_trade = True
                        else:
                            reason = "Already have a position"
                    elif signal_res.signal == "SELL":
                        if current_position:
                            should_trade = True
                        else:
                            reason = "No position to sell"
                        
                    if should_trade:
                        quantity = current_position.quantity if current_position else 10
                        req = schemas.PaperOrderRequest(
                            symbol=symbol,
                            side=signal_res.signal,
                            quantity=quantity
                        )
                        try:
                            await trader.execute_order(req)
                            bot_state["last_action"] = f"{signal_res.signal} {quantity} {symbol} executed"
                        except ValueError as e:
                            bot_state["last_action"] = f"Trade rejected: {e}"
                            logger.error(f"Paper execution rejected: {e}")
                    else:
                        bot_state["last_action"] = f"No trade — {reason}"
                else:
                    bot_state["last_action"] = "No trade — waiting for signal"
            finally:
                db.close()
        except Exception as e:
            bot_state["error"] = str(e)
            bot_state["last_action"] = "Error while checking signal"
            logger.error(f"Bot loop error: {e}")
            
        next_time = datetime.datetime.now() + datetime.timedelta(seconds=60)
        bot_state["next_check"] = f"~{next_time.strftime('%H:%M:%S')}"
            
        for _ in range(60):
            if not bot_state["running"]:
                break
            await asyncio.sleep(1)

@router.post("/bot/start")
async def start_bot():
    if not bot_state["running"]:
        bot_state["running"] = True
        if bot_state["task"] is None or bot_state["task"].done():
            bot_state["task"] = asyncio.create_task(run_bot_loop())
    return {"status": "success", "message": "Bot started.", "running": True}

@router.post("/bot/stop")
async def stop_bot():
    bot_state["running"] = False
    bot_state["last_action"] = "Bot stopped"
    return {"status": "success", "message": "Bot stopped.", "running": False}

@router.get("/bot/status")
async def get_bot_status():
    return {
        "running": bot_state["running"],
        "symbol": bot_state["symbol"],
        "signal": bot_state["signal"],
        "last_check": bot_state["last_check"],
        "next_check": bot_state["next_check"],
        "last_action": bot_state["last_action"],
        "error": bot_state["error"]
    }
