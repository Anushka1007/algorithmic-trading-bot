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

bot_state = {"running": False}

@router.post("/bot/start")
def start_bot():
    bot_state["running"] = True
    return {"status": "success", "message": "Bot started.", "running": True}

@router.post("/bot/stop")
def stop_bot():
    bot_state["running"] = False
    return {"status": "success", "message": "Bot stopped.", "running": False}

@router.get("/bot/status")
def get_bot_status():
    return {"running": bot_state["running"]}
