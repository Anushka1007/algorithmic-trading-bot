from fastapi import APIRouter, Depends, HTTPException
from backend.data.twelve_data import TwelveDataClient
from backend.schemas import BacktestRequest, BacktestResult
from backend.trading.backtester import BacktestEngine

router = APIRouter(prefix="/api/backtest", tags=["Backtest"])

def get_market_client():
    return TwelveDataClient()

@router.post("", response_model=BacktestResult)
async def run_backtest(
    request: BacktestRequest,
    client: TwelveDataClient = Depends(get_market_client)
):
    try:
        history = await client.get_history(
            symbol=request.symbol, 
            interval=request.interval, 
            outputsize=request.outputsize
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch market data: {str(e)}")

    engine = BacktestEngine(config=request.config)
    result = engine.run(symbol=request.symbol, history=history)
    return result
